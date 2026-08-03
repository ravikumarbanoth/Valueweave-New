#!/usr/bin/env python3
"""
The monitored source registry — what we watch, and what we know about watching it.

WHY THIS IS NOT source_registry/sources.csv
-------------------------------------------
That file already exists and is a different thing. It is DERIVED — regenerated
by `source_registry/build_source_registry.py` from every URL the eight released
packages cite — so it answers "what does our published knowledge depend on?"
605 rows, one per cited URL, and none of them has ever been fetched by software.

This file is AUTHORED. It answers "what do we check for changes, how often, and
what happened last time?" A row is added by a person in a pull request, because
subscribing to a source is a decision with a cost and a reviewer should see it.

The two meet at the end of the pipeline: a source monitored here, whose data is
approved and released into a package, will show up there on the next rebuild,
cited by the rows it produced. Monitoring is the front of the pipe; citation is
the back.

CONFIGURATION AND STATE ARE SEPARATE FILES, DELIBERATELY
---------------------------------------------------------
The brief lists "last checked" and "last updated" alongside "name" and "URL",
and they are not the same kind of thing. Name and URL are decisions, reviewed in
a diff. Last-checked is a fact a machine writes on every run.

Putting them in one CSV means every scheduled run dirties the file a human
authored, so the diff that should show "someone added a source" instead shows
forty timestamp changes with one real edit hidden among them — and reviewing
becomes something people stop doing. So:

    collection/registry/monitored_sources.csv   configuration. Human-authored.
    collection/state/fetch_state.json           state. Machine-written.

`load()` joins them, so a caller — and the CLI, and the monitoring output — sees
all twelve fields the brief asks for as one object. The split is an
implementation detail of how they are stored, not of how they are read.

    python3 -m collection.cli sources
    python3 -m collection.cli sources --json
"""

import csv
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / "collection" / "registry" / "monitored_sources.csv"
STATE_PATH = ROOT / "collection" / "state" / "fetch_state.json"

#: The columns of monitored_sources.csv, in order. A missing column is an error
#: rather than a default: a registry row with no `frequency` would be fetched on
#: some schedule nobody chose.
FIELDS = [
    "source_id", "name", "category", "state", "country", "url", "source_type",
    "collector", "parser", "frequency", "reliability", "status", "tags",
    "item_key", "classify_as", "notes",
]

#: What a source can be. `source_type` selects nothing by itself — the collector
#: and parser columns do that — but it is what a human reads, and a test asserts
#: the three agree, so a row claiming RSS with a CSV parser cannot be committed.
SOURCE_TYPES = {
    "RSS", "ATOM", "JSON_FEED", "XML", "REST_API", "CSV", "DATASET",
}

#: How often a source is worth checking. Hours, because the scheduler compares
#: `last_checked + frequency` against now and a cron string cannot express
#: "quarterly" without lying about which quarter.
FREQUENCY_HOURS = {
    "HOURLY": 1,
    "SIX_HOURLY": 6,
    "DAILY": 24,
    "WEEKLY": 24 * 7,
    "FORTNIGHTLY": 24 * 14,
    "MONTHLY": 24 * 30,
    "QUARTERLY": 24 * 91,
    "ANNUAL": 24 * 365,
}

#: ACTIVE                 fetched on schedule
#: PENDING_VERIFICATION   in the registry, never successfully fetched. NOT
#:                        fetched on schedule — see `runnable()`. This is the
#:                        repository's own sentinel, used here for the same
#:                        reason it is used in a dataset: a URL somebody typed
#:                        is not a URL somebody checked, and pretending
#:                        otherwise puts a dead feed on a dashboard as green.
#: PAUSED                 temporarily off, deliberately, with a reason in notes
#: RETIRED                the source is gone or superseded; kept for the audit
#:                        trail rather than deleted
STATUSES = {"ACTIVE", "PENDING_VERIFICATION", "PAUSED", "RETIRED"}

#: The categories from the brief. Adding one is adding a string here and a row
#: to the registry — no code changes anywhere. That is Phase 9's requirement
#: applied to the registry itself.
CATEGORIES = {
    "Government", "Universities", "Companies", "MSMEs", "ResearchOrganisations",
    "IndustryAssociations", "TrainingProviders", "SkillDevelopment",
    "Agriculture", "Manufacturing", "Robotics", "Semiconductors", "Electronics",
    "Defence", "Startups", "Exports", "DistrictIndustries", "Testing",
}


class RegistryError(Exception):
    """A registry row that cannot be trusted. Raised rather than skipped: a
    source silently dropped for a typo is a source nobody notices stopped
    being monitored."""


@dataclass
class FetchState:
    """What happened the last time we looked. Written by the runner, never by a
    human — `collection/state/` is machine territory."""

    last_checked: str = ""        # any attempt, successful or not
    last_ok: str = ""             # last successful fetch
    last_changed: str = ""        # last time the payload differed from before
    etag: str = ""
    last_modified: str = ""
    content_hash: str = ""
    consecutive_failures: int = 0
    last_error: str = ""
    item_count: int = 0
    #: item key -> payload hash, so change detection is per record rather than
    #: per feed. A feed whose <lastBuildDate> ticks every hour would otherwise
    #: look like it changed every hour.
    item_hashes: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, raw):
        known = {k: v for k, v in (raw or {}).items() if k in cls.__dataclass_fields__}
        return cls(**known)


@dataclass
class Source:
    source_id: str
    name: str
    category: str
    state: str
    country: str
    url: str
    source_type: str
    collector: str
    parser: str
    frequency: str
    reliability: int
    status: str
    tags: list
    item_key: str
    classify_as: str
    notes: str
    fetch: FetchState = field(default_factory=FetchState)

    @property
    def runnable(self):
        """Only ACTIVE sources run on a schedule.

        PENDING_VERIFICATION is the honest state for a URL nobody has proved
        reachable, and a scheduler that fetched them anyway would report their
        failures as incidents rather than as unfinished setup.
        """
        return self.status == "ACTIVE"

    def due(self, now=None):
        """Is it time? Never-checked is always due; otherwise last check plus
        the declared interval."""
        if not self.runnable:
            return False
        if not self.fetch.last_checked:
            return True
        now = now or datetime.now(timezone.utc)
        try:
            last = datetime.fromisoformat(self.fetch.last_checked)
        except ValueError:
            return True
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        return now - last >= timedelta(hours=FREQUENCY_HOURS[self.frequency])

    def to_dict(self):
        out = asdict(self)
        out["fetch"] = asdict(self.fetch)
        return out


def _validate(row, line):
    where = f"{REGISTRY_PATH.name}:{line}"
    missing = [f for f in FIELDS if f not in row]
    if missing:
        raise RegistryError(f"{where}: missing columns {missing}")
    for column, allowed in (("source_type", SOURCE_TYPES), ("status", STATUSES),
                            ("frequency", set(FREQUENCY_HOURS)), ("category", CATEGORIES)):
        value = (row.get(column) or "").strip()
        if value not in allowed:
            raise RegistryError(f"{where}: {column}={value!r} is not one of {sorted(allowed)}")
    if not (row.get("source_id") or "").strip():
        raise RegistryError(f"{where}: source_id is required")
    if not (row.get("url") or "").strip():
        raise RegistryError(f"{where}: url is required")
    try:
        reliability = int(row.get("reliability") or 0)
    except ValueError as exc:
        raise RegistryError(f"{where}: reliability must be an integer") from exc
    if not 0 <= reliability <= 100:
        raise RegistryError(f"{where}: reliability {reliability} outside 0-100")


def load(registry_path=None, state_path=None):
    """Every source, configuration joined to state. Ordered as authored."""
    registry_path = Path(registry_path or REGISTRY_PATH)
    state_path = Path(state_path or STATE_PATH)

    state = {}
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8")).get("sources", {})

    sources, seen = [], set()
    with open(registry_path, encoding="utf-8", newline="") as fh:
        for line, row in enumerate(csv.DictReader(fh), start=2):
            if not (row.get("source_id") or "").strip():
                continue
            _validate(row, line)
            source_id = row["source_id"].strip()
            if source_id in seen:
                raise RegistryError(f"{registry_path.name}:{line}: duplicate source_id {source_id}")
            seen.add(source_id)
            sources.append(Source(
                source_id=source_id,
                name=row["name"].strip(),
                category=row["category"].strip(),
                state=row["state"].strip(),
                country=row["country"].strip(),
                url=row["url"].strip(),
                source_type=row["source_type"].strip(),
                collector=row["collector"].strip(),
                parser=row["parser"].strip(),
                frequency=row["frequency"].strip(),
                reliability=int(row["reliability"]),
                status=row["status"].strip(),
                tags=[t.strip() for t in (row["tags"] or "").split(";") if t.strip()],
                item_key=row["item_key"].strip(),
                classify_as=row["classify_as"].strip(),
                notes=row["notes"].strip(),
                fetch=FetchState.from_dict(state.get(source_id)),
            ))
    return sources


def save_state(sources, state_path=None):
    """Write back only the state half. The registry CSV is never rewritten by
    software — if a run could edit it, a run could quietly retire a source."""
    state_path = Path(state_path or STATE_PATH)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "written_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "sources": {s.source_id: asdict(s.fetch) for s in sources},
    }
    state_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state_path


def resolve(dotted):
    """`knowledge_engine.parsers.rss_parser.RSSParser` -> the class.

    The registry names classes as strings so that adding a source is a data
    change. Import errors surface here, at load time, with the offending string
    in the message — not three stages later as an AttributeError on None.
    """
    import importlib                                                # noqa: PLC0415
    module_path, _, attribute = dotted.rpartition(".")
    if not module_path:
        raise RegistryError(f"{dotted!r} is not a dotted path to a class")
    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:
        raise RegistryError(f"cannot import {module_path}: {exc}") from exc
    try:
        return getattr(module, attribute)
    except AttributeError as exc:
        raise RegistryError(f"{module_path} has no attribute {attribute}") from exc

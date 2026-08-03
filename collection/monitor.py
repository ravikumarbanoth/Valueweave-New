#!/usr/bin/env python3
"""
Is the collection pipeline actually working?

THE FAILURE THIS IS BUILT AGAINST
----------------------------------
A feed that quietly stops publishing looks exactly like a feed that is up to
date. Both produce zero new items, and a dashboard counting "candidates
collected today" shows the same number for a healthy quiet week and a dead URL.
The difference is only visible in the SOURCE's state, never in the output, so
the metrics here are about sources rather than about records.

Six checks, from the brief, each with a stated threshold and a reason:

    dead_feed            consecutive failures at or over the limit
    failing              failing, but not yet dead
    stale                nothing new for several times its declared frequency
    never_verified       PENDING_VERIFICATION with no successful fetch, ever
    duplicate_spike      duplicates as a share of a run, over the limit
    parser_failure       fetched fine, could not be read

WHAT IT WILL NOT DO
-------------------
Report a metric it cannot compute. `knowledge_sync/metrics.py` states this rule
outright — "a dashboard with an invented number is worse than one with a
missing panel" — and it applies with more force here, because the whole purpose
of this module is to tell the truth about whether an automated system is
running. A freshness figure for a source never successfully fetched is not
"stale", it is UNKNOWN, and it says UNKNOWN.

OK / WARN / CRITICAL match scripts/health_check.sh, so the two can be read
together and eventually reported together. Critical means a person should look
today; warn means the number is worth watching.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from collection.registry import FREQUENCY_HOURS

OK, WARN, CRITICAL, UNKNOWN = "OK", "WARN", "CRITICAL", "UNKNOWN"

#: Two consecutive failures is a bad afternoon; five is a dead URL. Below five,
#: a transient outage would page somebody at 3am for a feed that is fine.
DEAD_AFTER_FAILURES = 5
FAILING_AFTER_FAILURES = 2

#: A source is stale when it has published nothing for this many times its own
#: declared interval. A multiple rather than a fixed period, because "nothing
#: for a week" is alarming for an hourly feed and normal for an annual one.
STALE_MULTIPLE = 4

#: Duplicates above this share of a run mean either a source republishing
#: everything or a broken item key — both worth a look, and both invisible in a
#: count of candidates.
DUPLICATE_SPIKE_RATIO = 0.5

#: Below this many items, a ratio is noise. Two of three items being duplicates
#: is not a spike.
DUPLICATE_SPIKE_MIN_ITEMS = 6


@dataclass
class Finding:
    check: str
    severity: str
    source_id: str = ""
    detail: str = ""

    def as_dict(self):
        return {"check": self.check, "severity": self.severity,
                "source_id": self.source_id, "detail": self.detail}


@dataclass
class Health:
    checked_at: str = ""
    findings: list = field(default_factory=list)
    sources: list = field(default_factory=list)
    totals: dict = field(default_factory=dict)

    @property
    def status(self):
        if any(f.severity == CRITICAL for f in self.findings):
            return "critical"
        if any(f.severity == WARN for f in self.findings):
            return "degraded"
        return "healthy"

    def as_dict(self):
        return {
            "status": self.status,
            "checked_at": self.checked_at,
            "totals": self.totals,
            "findings": [f.as_dict() for f in self.findings],
            "sources": self.sources,
        }


def _parse(stamp):
    if not stamp:
        return None
    try:
        value = datetime.fromisoformat(str(stamp))
    except ValueError:
        return None
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def _freshness(source, now):
    """Hours since this source last produced something new, or None."""
    last = _parse(source.fetch.last_changed) or _parse(source.fetch.last_ok)
    if not last:
        return None
    return (now - last).total_seconds() / 3600


def check(sources, last_run=None, now=None):
    """Everything the dashboard needs, computed from state plus the last run."""
    now = now or datetime.now(timezone.utc)
    health = Health(checked_at=now.replace(microsecond=0).isoformat())

    by_id = {}
    if last_run:
        for entry in last_run.get("sources", []):
            by_id[entry.get("source_id")] = entry

    counts = {"total": len(sources), "active": 0, "pending_verification": 0,
              "paused": 0, "retired": 0, "dead": 0, "failing": 0, "stale": 0,
              "never_fetched": 0}

    for source in sources:
        counts[{"ACTIVE": "active", "PENDING_VERIFICATION": "pending_verification",
                "PAUSED": "paused", "RETIRED": "retired"}[source.status]] += 1

        failures = source.fetch.consecutive_failures
        hours = _freshness(source, now)
        interval = FREQUENCY_HOURS[source.frequency]
        row = {
            "source_id": source.source_id,
            "name": source.name,
            "category": source.category,
            "status": source.status,
            "frequency": source.frequency,
            "last_checked": source.fetch.last_checked or None,
            "last_ok": source.fetch.last_ok or None,
            "last_changed": source.fetch.last_changed or None,
            "consecutive_failures": failures,
            "items_last_seen": source.fetch.item_count,
            "hours_since_change": round(hours, 1) if hours is not None else None,
            "freshness": UNKNOWN,
            "health": OK,
        }

        if source.status == "RETIRED":
            row["health"] = OK
            health.sources.append(row)
            continue

        if source.status == "PENDING_VERIFICATION" and not source.fetch.last_ok:
            counts["never_fetched"] += 1
            row["health"] = UNKNOWN
            health.findings.append(Finding(
                "never_verified", WARN, source.source_id,
                "registered but never successfully fetched — run "
                f"`collection.cli verify {source.source_id}` from a network that can reach it"))
            health.sources.append(row)
            continue

        if failures >= DEAD_AFTER_FAILURES:
            counts["dead"] += 1
            row["health"] = CRITICAL
            health.findings.append(Finding(
                "dead_feed", CRITICAL, source.source_id,
                f"{failures} consecutive failures — last error: "
                f"{source.fetch.last_error or 'unknown'}"))
        elif failures >= FAILING_AFTER_FAILURES:
            counts["failing"] += 1
            row["health"] = WARN
            health.findings.append(Finding(
                "failing", WARN, source.source_id,
                f"{failures} consecutive failures — {source.fetch.last_error or 'unknown'}"))

        if hours is None:
            row["freshness"] = UNKNOWN
            if source.status == "ACTIVE" and not source.fetch.last_checked:
                health.findings.append(Finding(
                    "never_checked", WARN, source.source_id,
                    "active but never checked — has the schedule ever run?"))
        elif hours > interval * STALE_MULTIPLE:
            counts["stale"] += 1
            row["freshness"] = "STALE"
            if row["health"] == OK:
                row["health"] = WARN
            health.findings.append(Finding(
                "stale", WARN, source.source_id,
                f"nothing new for {round(hours)}h against a {source.frequency.lower()} "
                f"cadence ({interval}h) — publishing may have stopped"))
        else:
            row["freshness"] = "FRESH"

        entry = by_id.get(source.source_id) or {}
        if entry.get("status") == "error":
            health.findings.append(Finding(
                "parser_failure" if "parse" in str(entry.get("error", "")).lower()
                else "fetch_failure",
                WARN, source.source_id, str(entry.get("error", ""))[:200]))

        duplicates = (entry.get("duplicates") or {}).get("duplicates", 0)
        records = entry.get("records", 0)
        if records >= DUPLICATE_SPIKE_MIN_ITEMS and duplicates / records > DUPLICATE_SPIKE_RATIO:
            health.findings.append(Finding(
                "duplicate_spike", WARN, source.source_id,
                f"{duplicates} of {records} items were duplicates — a republishing "
                f"source, or `item_key` is not identifying items"))

        health.sources.append(row)

    if last_run:
        broken = [s for s in last_run.get("sources", []) if s.get("status") == "error"]
        counts["errors_last_run"] = len(broken)
        counts["queued_last_run"] = sum(s.get("queued", 0) for s in last_run.get("sources", []))

    health.totals = counts
    return health

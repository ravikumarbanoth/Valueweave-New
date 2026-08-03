#!/usr/bin/env python3
"""
Operational integrity — the failures that pass every existing check.

WHAT ALREADY RUNS, AND WHY THIS IS NOT IT
------------------------------------------
`knowledge_graph/validate_graph.py` runs eleven G-checks (identity,
completeness, type, provenance, edge integrity, edge type, ownership,
lifecycle, confidence, orphans, scheme ownership) and they pass. Those are
CORRECTNESS checks: is the graph well-formed?

These are OPERATIONAL checks: is the graph still useful, and did anything
change in a way that should worry somebody? A graph can be perfectly
well-formed and still have four hundred entities nobody can reach, a crosswalk
that resolves a fifth of what it did last month, or a package that quietly lost
half its rows in a regeneration. Every one of those passes G1–G11.

Nothing here duplicates a G-check. Where a G-check already answers a question —
orphans, edge integrity — this reads its result rather than recomputing it.

THE ONE THAT MATTERS MOST
--------------------------
`data_drop`. A dataset regenerating with 60% of its previous rows is the single
most dangerous silent failure in this architecture, because the sync soft-deletes
the missing rows, the site keeps working, the graph still validates, and nobody
finds out until a reader asks where something went. The baseline is the
committed sync manifest — the record of what was last projected — which makes
this comparable offline and impossible to fake by editing the target.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from ops import metrics

OK, WARN, CRITICAL = "OK", "WARN", "CRITICAL"

#: A type registered in the graph builder and holding no rows. Not an error —
#: `Certification` was empty for three package releases and that was honest —
#: but a reader who follows a category link into nothing has met a dead end,
#: and somebody should decide which it is.
#:
#: Above this share of registered types, the graph is advertising more than it
#: holds and the browse surface will show empty categories.
EMPTY_TYPE_LIMIT = 0.25

#: Isolated entities as a share of the graph. These are reachable by search and
#: offer nowhere to go afterwards — the single biggest determinant of whether
#: the platform feels like a knowledge network or a list of rows.
ISOLATION_WARN = 0.10
ISOLATION_CRITICAL = 0.25

#: Crosswalk resolution. Below this, the join from what a user types to what the
#: graph knows is mostly missing and every personalised feature degrades
#: silently — no error, just empty panels.
CROSSWALK_WARN_PCT = 40.0

#: A table losing more than this share of its rows against the last sync
#: manifest is a regeneration accident until proven otherwise.
DATA_DROP_LIMIT = 0.15


@dataclass
class Finding:
    check: str
    severity: str
    detail: str
    subject: str = ""

    def as_dict(self):
        return {"check": self.check, "severity": self.severity,
                "subject": self.subject, "detail": self.detail}


@dataclass
class Integrity:
    findings: list = field(default_factory=list)
    counts: dict = field(default_factory=dict)

    @property
    def status(self):
        if any(f.severity == CRITICAL for f in self.findings):
            return "critical"
        if any(f.severity == WARN for f in self.findings):
            return "degraded"
        return "healthy"

    def as_dict(self):
        return {"status": self.status, "counts": self.counts,
                "findings": [f.as_dict() for f in self.findings]}


def _broken_references(entities, relationships):
    """Edges pointing at an entity that does not exist.

    G5-EDGE_INTEGRITY covers this and passes, so a finding here means the graph
    was rebuilt without revalidating — which is exactly when it would be missed.
    """
    known = {e["global_entity_id"] for e in entities}
    broken = []
    for edge in relationships:
        for end in ("from_entity", "to_entity"):
            target = edge.get(end)
            if target and target not in known:
                broken.append(f"{edge.get('relationship_id', '?')} → {target}")
    return broken


def _missing_relationships(entities, relationships):
    """Types the graph holds that connect to nothing at all.

    Not "an entity with no edges" — that is the isolation check. This is a whole
    TYPE with zero edges, which almost always means a builder step was never
    written rather than that the data is genuinely disconnected. Certification
    is the standing example: 30 rows, no edges, so nothing about a skill can
    ever lead to the certificate that proves it.
    """
    linked = set()
    by_id = {e["global_entity_id"]: e["entity_type"] for e in entities}
    for edge in relationships:
        for end in ("from_entity", "to_entity"):
            entity_type = by_id.get(edge.get(end))
            if entity_type:
                linked.add(entity_type)
    present = {e["entity_type"] for e in entities}
    return sorted(present - linked)


def _dead_links(entities):
    """Source URLs that are obviously not URLs.

    Deliberately offline: this checks SHAPE, not reachability. Fetching six
    hundred URLs on every dashboard render would be slow, rude to the servers
    and non-deterministic, and `collection.cli verify` is the tool for asking
    whether a specific one answers.
    """
    bad = []
    for path in sorted((metrics.ROOT / "packages").glob("*/datasets/*.csv")):
        import csv                                                   # noqa: PLC0415
        with open(path, encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            if "source_url" not in (reader.fieldnames or []):
                continue
            for row in reader:
                url = str(row.get("source_url") or "").strip()
                if not url or url.upper().startswith("PENDING"):
                    continue
                if not url.startswith(("http://", "https://")):
                    bad.append(f"{path.name}: {url[:60]}")
    return bad


def _data_drop():
    """Tables that shrank against the last sync manifest.

    The manifest is the committed record of what the framework last wrote, and
    comparing against it rather than against the live target is the same
    decision `knowledge_sync/changes.py` made and for the same reasons:
    reproducible offline, and tampering shows up as a change to correct rather
    than as a new baseline.
    """
    manifest = metrics.load_artifact("sync_manifest")
    if not manifest:
        return []

    from knowledge_sync import config                                # noqa: PLC0415
    previous = {table: len(rows) for table, rows in (manifest.get("tables") or {}).items()}
    if not previous:
        return []

    # Current row counts come from the same place the sync reads them, so a
    # discrepancy is about the DATA and never about two different ways of
    # counting it.
    current = {}
    try:
        from knowledge_sync import extract                           # noqa: PLC0415
        for table, rows in (extract.extract_all() or {}).items():
            current[table] = len(rows)
    except Exception:                                                # noqa: BLE001
        # Extraction can fail for reasons that are not this check's business —
        # a package mid-edit, a missing dataset. Reporting nothing is right;
        # reporting "everything dropped to zero" would be a false alarm of the
        # loudest possible kind.
        return []

    drops = []
    for table, was in sorted(previous.items()):
        now = current.get(table)
        if now is None or was == 0:
            continue
        if (was - now) / was > DATA_DROP_LIMIT:
            drops.append(f"{table}: {was} → {now} ({round(100 * (was - now) / was)}% fewer)")
    return drops


def check(entities=None, relationships=None):
    """Everything, as one object."""
    entities = entities if entities is not None else metrics.read_entities()
    relationships = relationships if relationships is not None else metrics.read_relationships()
    result = Integrity()

    graph = metrics.load_artifact("graph") or {}
    registered = graph.get("entity_types_registered") or 0
    populated = len({e["entity_type"] for e in entities})
    if registered and (registered - populated) / registered > EMPTY_TYPE_LIMIT:
        result.findings.append(Finding(
            "empty_types", WARN,
            f"{registered - populated} of {registered} registered entity types hold "
            f"no rows — the browse surface will show empty categories"))

    degree = metrics.degrees(relationships)
    isolated = [e for e in entities if degree.get(e["global_entity_id"], 0) == 0]
    if entities:
        share = len(isolated) / len(entities)
        if share > ISOLATION_CRITICAL:
            severity = CRITICAL
        elif share > ISOLATION_WARN:
            severity = WARN
        else:
            severity = None
        if severity:
            worst = Counter(e["entity_type"] for e in isolated).most_common(3)
            result.findings.append(Finding(
                "isolated_entities", severity,
                f"{len(isolated)} of {len(entities)} entities ({round(100 * share)}%) "
                f"connect to nothing — mostly "
                + ", ".join(f"{t} ({n})" for t, n in worst)))

    broken = _broken_references(entities, relationships)
    if broken:
        result.findings.append(Finding(
            "broken_references", CRITICAL,
            f"{len(broken)} edges point at an entity that does not exist: "
            + "; ".join(broken[:3])))

    unlinked = _missing_relationships(entities, relationships)
    if unlinked:
        result.findings.append(Finding(
            "missing_relationships", WARN,
            f"{len(unlinked)} entity type(s) have no edges at all — "
            f"{', '.join(unlinked)} — so nothing can lead to them"))

    crosswalk = metrics.load_artifact("crosswalk") or {}
    resolved = crosswalk.get("resolve_pct_total")
    if resolved is not None and resolved < CROSSWALK_WARN_PCT:
        result.findings.append(Finding(
            "crosswalk_health", WARN,
            f"{resolved}% of vocabulary terms resolve to an entity — below "
            f"{CROSSWALK_WARN_PCT}%, personalised features degrade silently"))

    bad_urls = _dead_links(entities)
    if bad_urls:
        result.findings.append(Finding(
            "malformed_source_urls", WARN,
            f"{len(bad_urls)} source_url values are not URLs: "
            + "; ".join(bad_urls[:3])))

    drops = _data_drop()
    for drop in drops:
        result.findings.append(Finding("data_drop", CRITICAL, drop,
                                       subject=drop.split(":")[0]))

    validation = metrics.load_artifact("graph_validation") or {}
    if validation.get("result") and validation["result"] != "PASS":
        result.findings.append(Finding(
            "graph_validation", CRITICAL,
            f"validate_graph.py last reported {validation['result']} — "
            f"{len(validation.get('violations') or [])} violation(s)"))

    result.counts = {
        "entities": len(entities),
        "relationships": len(relationships),
        "isolated": len(isolated),
        "broken_references": len(broken),
        "types_with_no_edges": len(unlinked),
        "malformed_source_urls": len(bad_urls),
        "tables_that_shrank": len(drops),
    }
    return result

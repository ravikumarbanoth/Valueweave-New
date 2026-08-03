#!/usr/bin/env python3
"""
One snapshot of how the knowledge platform is actually doing.

WHY THIS COMPOSES ARTIFACTS RATHER THAN QUERYING ANYTHING
----------------------------------------------------------
Every subsystem here already writes a summary, and every one of those summaries
is committed to Git:

    knowledge_graph/graph_summary.json          what was built
    knowledge_graph/validation_summary.json     the eleven G-checks
    governance/vocabulary/crosswalk_summary.json
    source_registry/source_summary.json         what published data cites
    knowledge_sync/state/manifest.json          what was last projected
    knowledge_sync/state/sync_log.jsonl         every run
    collection/state/*.json                     feeds, queue, backlog
    knowledge_engine/compatibility_report.json

So this reads them. Nothing is recomputed that a subsystem already computed, and
nothing needs a database, a network or a credential — which means the snapshot
is reproducible offline, identical for everyone, and diffable in a pull request.
A dashboard whose numbers cannot be reproduced is a dashboard nobody can check.

The live signals that genuinely cannot come from Git — page views, search
counts — are PASSED IN by the caller rather than fetched here. `ops/cli.py`
takes them as a JSON file. That keeps this module free of Supabase and makes
"we have no popularity data" a visible `None` rather than a zero that looks like
a measurement.

WHAT IS NEW HERE RATHER THAN COMPOSED
--------------------------------------
Three things no subsystem computes, all of them per-entity and all of them
operational rather than public:

    connectivity   degree from relationships.csv — which knowledge is a
                   dead end, which is a hub, and which is entirely unreachable
    freshness      how old a record is against how old its type usually is
    coverage gaps  a type the graph registers and does not populate
"""

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ENTITIES = ROOT / "knowledge_graph" / "entities" / "entities.csv"
RELATIONSHIPS = ROOT / "knowledge_graph" / "relationships" / "relationships.csv"

#: Artifact -> where it lives. Missing is normal and reported as missing, never
#: as a zero: "the crosswalk has 0 rows" and "the crosswalk summary has not been
#: built" are different facts and a dashboard must not merge them.
ARTIFACTS = {
    "graph": ROOT / "knowledge_graph" / "graph_summary.json",
    "graph_validation": ROOT / "knowledge_graph" / "validation_summary.json",
    "crosswalk": ROOT / "governance" / "vocabulary" / "crosswalk_summary.json",
    "cited_sources": ROOT / "source_registry" / "source_summary.json",
    "engine_compatibility": ROOT / "knowledge_engine" / "compatibility_report.json",
    "sync_manifest": ROOT / "knowledge_sync" / "state" / "manifest.json",
    "collection_run": ROOT / "collection" / "state" / "last_run.json",
    "research_backlog": ROOT / "collection" / "state" / "research_backlog.json",
}

SYNC_LOG = ROOT / "knowledge_sync" / "state" / "sync_log.jsonl"
REVIEW_QUEUE = ROOT / "collection" / "state" / "review_queue.jsonl"

#: A record older than this, with nothing newer, is worth a second look. Not a
#: deadline — public data ages at wildly different rates, and a district's area
#: does not go stale the way a scheme's application window does — so this is the
#: point at which somebody should CHECK, not the point at which it is wrong.
STALE_AFTER_DAYS = 365

#: Below this many neighbours an entity is a dead end: a page a reader lands on
#: and leaves from, because it connects to nothing. Two is the floor at which a
#: page can offer "where this leads next" at all.
DEAD_END_DEGREE = 2


def _now():
    return datetime.now(timezone.utc)


def load_artifact(name):
    path = ARTIFACTS[name]
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def read_entities(path=None):
    path = Path(path or ENTITIES)
    if not path.exists():
        return []
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def read_relationships(path=None):
    path = Path(path or RELATIONSHIPS)
    if not path.exists():
        return []
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _date(value):
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def degrees(relationships):
    """Neighbour count per entity, both directions.

    Both directions on purpose: a district that nothing points at but which
    points at forty things is not isolated, and treating direction as
    significant here would report half the graph as orphaned.
    """
    counts = Counter()
    for edge in relationships:
        if edge.get("from_entity"):
            counts[edge["from_entity"]] += 1
        if edge.get("to_entity"):
            counts[edge["to_entity"]] += 1
    return counts


def entity_operations(entities=None, relationships=None, popularity=None, now=None):
    """The operational record of every entity. Admin only — none of this is
    a public claim about anything, and most of it is about US rather than
    about the thing.

    `popularity` is `{global_entity_id or canonical_name: view_or_search_count}`
    supplied by the caller. Absent, `popularity` is None on every row and the
    quality score says so instead of scoring a zero.
    """
    now = now or _now()
    entities = entities if entities is not None else read_entities()
    relationships = relationships if relationships is not None else read_relationships()
    degree = degrees(relationships)
    popularity = popularity or {}

    rows = []
    for entity in entities:
        gid = entity["global_entity_id"]
        updated = _date(entity.get("updated_at")) or _date(entity.get("created_at"))
        age = (now - updated).days if updated else None
        views = popularity.get(gid, popularity.get(entity["canonical_name"]))
        rows.append({
            "global_entity_id": gid,
            "canonical_name": entity["canonical_name"],
            "entity_type": entity["entity_type"],
            "source_package": entity["source_package"],
            "created": entity.get("created_at") or None,
            "last_updated": entity.get("updated_at") or None,
            # No steward has reviewed anything yet — the ledger holds only its
            # header — so this is None rather than a date nobody earned.
            "last_reviewed": None,
            "confidence": int(entity.get("confidence_score") or 0),
            "verification_status": entity.get("verification_status") or "",
            "lifecycle_state": entity.get("lifecycle_state") or "",
            "connected_entities": degree.get(gid, 0),
            "age_days": age,
            "popularity": views,
            "freshness": _freshness(age),
            "research_status": _research_status(entity, degree.get(gid, 0)),
        })
    return rows


def _freshness(age_days):
    if age_days is None:
        return "UNKNOWN"
    if age_days <= 90:
        return "FRESH"
    if age_days <= STALE_AFTER_DAYS:
        return "AGEING"
    return "STALE"


def _research_status(entity, degree):
    """What a knowledge operator would say about this row in four words.

    Ordered by which problem to fix first: an unreachable record helps nobody
    however well sourced, and an unverified one is a claim we have not stood
    behind.
    """
    if degree == 0:
        return "UNREACHABLE"
    if "NEEDS_REVIEW" in str(entity.get("verification_status") or ""):
        return "UNVERIFIED"
    if degree < DEAD_END_DEGREE:
        return "THIN"
    return "OK"


def knowledge_overview(entities=None, relationships=None):
    entities = entities if entities is not None else read_entities()
    relationships = relationships if relationships is not None else read_relationships()
    graph = load_artifact("graph") or {}
    crosswalk = load_artifact("crosswalk") or {}

    packages = sorted(p.name for p in (ROOT / "packages").iterdir()
                      if p.is_dir() and (p / "package_manifest.json").exists())
    articles = len(list((ROOT / "frontend" / "content" / "research").glob("*.mdx")))

    return {
        "entities": len(entities),
        "relationships": len(relationships),
        "entity_types_populated": len({e["entity_type"] for e in entities}),
        "entity_types_registered": graph.get("entity_types_registered"),
        "by_type": dict(sorted(Counter(e["entity_type"] for e in entities).items(),
                               key=lambda kv: -kv[1])),
        "by_package": dict(sorted(Counter(e["source_package"] for e in entities).items(),
                                  key=lambda kv: -kv[1])),
        "packages": len(packages),
        "package_names": packages,
        # File-based articles only. The `research_articles` table is live
        # application data and this module does not reach for a network — the
        # count is labelled so nobody reads it as the total.
        "research_articles_in_repo": articles,
        "crosswalk_rows": crosswalk.get("terms_total"),
        "crosswalk_resolved_pct": crosswalk.get("resolve_pct_total"),
        "graph_built_at": graph.get("built_at"),
    }


def connectivity(entities=None, relationships=None, top=10):
    """Which knowledge leads somewhere, and which is a dead end.

    Part 6 of the brief asks for most-connected, least-connected and unused
    knowledge. All three are the same number read from different ends, and the
    third one — an entity with no edges at all — is the one that matters: it
    can be found by search and offers nowhere to go afterwards.
    """
    entities = entities if entities is not None else read_entities()
    relationships = relationships if relationships is not None else read_relationships()
    degree = degrees(relationships)

    ranked = sorted(entities, key=lambda e: (-degree.get(e["global_entity_id"], 0),
                                             e["canonical_name"]))
    isolated = [e for e in entities if degree.get(e["global_entity_id"], 0) == 0]
    thin = [e for e in entities
            if 0 < degree.get(e["global_entity_id"], 0) < DEAD_END_DEGREE]

    def brief(entity):
        return {"name": entity["canonical_name"], "type": entity["entity_type"],
                "degree": degree.get(entity["global_entity_id"], 0)}

    by_type = defaultdict(list)
    for entity in entities:
        by_type[entity["entity_type"]].append(degree.get(entity["global_entity_id"], 0))

    return {
        "connected": len(entities) - len(isolated),
        "connected_pct": round(100 * (len(entities) - len(isolated)) / len(entities), 1)
                         if entities else 0.0,
        "isolated": len(isolated),
        "dead_ends": len(thin),
        "median_degree": _median([degree.get(e["global_entity_id"], 0) for e in entities]),
        "most_connected": [brief(e) for e in ranked[:top]],
        "least_connected": [brief(e) for e in isolated[:top]] or
                           [brief(e) for e in ranked[-top:]],
        "isolated_by_type": dict(sorted(
            Counter(e["entity_type"] for e in isolated).items(), key=lambda kv: -kv[1])),
        "median_degree_by_type": {t: _median(v) for t, v in sorted(by_type.items())},
    }


def _median(values):
    if not values:
        return 0
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return round((ordered[middle - 1] + ordered[middle]) / 2, 1)


def freshness(rows=None, now=None):
    rows = rows if rows is not None else entity_operations(now=now)
    counts = Counter(r["freshness"] for r in rows)
    ages = [r["age_days"] for r in rows if r["age_days"] is not None]
    return {
        "fresh": counts.get("FRESH", 0),
        "ageing": counts.get("AGEING", 0),
        "stale": counts.get("STALE", 0),
        "unknown": counts.get("UNKNOWN", 0),
        "median_age_days": _median(ages),
        "oldest_days": max(ages) if ages else None,
        "stale_by_package": dict(sorted(
            Counter(r["source_package"] for r in rows if r["freshness"] == "STALE").items(),
            key=lambda kv: -kv[1])),
    }


def collection_state():
    """Feeds, the queue, and the backlog — read from collection/state/."""
    from collection import registry, review                          # noqa: PLC0415
    from collection import monitor as feed_monitor                   # noqa: PLC0415

    try:
        sources = registry.load()
    except registry.RegistryError as exc:
        return {"error": str(exc)}

    last_run = load_artifact("collection_run")
    health = feed_monitor.check(sources, last_run=last_run)
    queue = review.load(REVIEW_QUEUE) if REVIEW_QUEUE.exists() else []

    awaiting = [c for c in queue if c.state == review.NEEDS_REVIEW]
    return {
        "sources": health.totals,
        "feed_status": health.status,
        "findings": [f.as_dict() for f in health.findings],
        "queue": review.summary(queue),
        "top_of_queue": [
            {"stars": c.priority_stars, "type": c.classified_as,
             "title": c.title[:90], "source": c.source_id, "why": c.priority_reason}
            for c in awaiting[:10]
        ],
        "last_run": (last_run or {}).get("finished_at"),
    }


def sync_state(limit=20):
    """The last few sync runs, from the log the sync already writes."""
    if not SYNC_LOG.exists():
        return {"runs": [], "last_success": None, "last_failure": None}

    runs = []
    for line in SYNC_LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            runs.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    def ok(run):
        return str(run.get("result") or run.get("status") or "").upper() in ("OK", "PASS", "SUCCESS")

    successes = [r for r in runs if ok(r)]
    failures = [r for r in runs if not ok(r)]
    manifest = load_artifact("sync_manifest") or {}
    return {
        "runs_recorded": len(runs),
        "last_success": successes[-1].get("finished_at") or successes[-1].get("started_at")
                        if successes else None,
        "last_failure": failures[-1].get("finished_at") or failures[-1].get("started_at")
                        if failures else None,
        "manifest_written_at": manifest.get("synced_at"),
        "manifest_version": manifest.get("version"),
        "tables_in_manifest": len(manifest.get("tables") or {}),
        "recent": runs[-limit:],
    }


def demand(search_events=None, top=12):
    """What people are looking for. Passed in, never fetched.

    Absent, every list is empty AND `has_data` is False — so the dashboard
    prints "no search data yet" rather than an empty chart that reads as
    "nobody searched for anything".
    """
    events = search_events or []
    if not events:
        return {"has_data": False, "total": 0, "top": [], "zero_result": [],
                "unique_terms": 0}

    counts, zero = Counter(), Counter()
    for row in events:
        query = str(row.get("query") or "").strip().lower()
        if not query:
            continue
        counts[query] += 1
        if int(row.get("results_count") or 0) == 0:
            zero[query] += 1

    return {
        "has_data": True,
        "total": sum(counts.values()),
        "unique_terms": len(counts),
        "zero_result_total": sum(zero.values()),
        "zero_result_pct": round(100 * sum(zero.values()) / sum(counts.values()), 1)
                           if counts else 0.0,
        "top": [{"term": t, "count": n} for t, n in counts.most_common(top)],
        "zero_result": [{"term": t, "count": n} for t, n in zero.most_common(top)],
    }


def snapshot(search_events=None, popularity=None, now=None):
    """Everything, in one object. What the dashboard and the report both read."""
    now = now or _now()
    entities = read_entities()
    relationships = read_relationships()
    rows = entity_operations(entities, relationships, popularity=popularity, now=now)

    from ops import integrity, quality                                # noqa: PLC0415

    return {
        "generated_at": now.replace(microsecond=0).isoformat(),
        "overview": knowledge_overview(entities, relationships),
        "connectivity": connectivity(entities, relationships),
        "freshness": freshness(rows, now=now),
        "collection": collection_state(),
        "sync": sync_state(),
        "demand": demand(search_events),
        "backlog": (load_artifact("research_backlog") or {}).get("suggestions", [])[:20],
        "integrity": integrity.check(entities, relationships).as_dict(),
        "quality": quality.score(entities=entities, relationships=relationships,
                                 rows=rows, now=now).as_dict(),
        "graph_validation": (load_artifact("graph_validation") or {}).get("result"),
        "engine_compatibility": (load_artifact("engine_compatibility") or {}).get("result"),
    }

#!/usr/bin/env python3
"""
ValueWeave Platform v2.2 — API handlers (Work Package 3)

The ten endpoints, as pure functions of (path params, query params) -> payload.
No HTTP here: that lives in `app.py`, so every handler is directly testable
without binding a socket, and swapping the transport for WSGI/ASGI later touches
one file.

FOUR RULES EVERY HANDLER FOLLOWS
--------------------------------
1. **Read-only.** There is no write path. Writes go to packages, and the graph is
   derived from them (ADR-001). `app.py` refuses non-GET at the router.

2. **Provenance travels with data.** Relationship payloads carry the package,
   dataset and row that produced them. An answer that cannot be traced to a CSV
   row is not an answer this platform gives.

3. **Every response carries the verification warning.** Zero of 2,299 rows have
   human sign-off. `meta.warning` says so on every single response, and it is the
   most important field in the envelope until stewardship changes that. It is
   computed from the data, so it will disappear on its own when it stops being
   true.

4. **Unknown query parameters are an error, not a shrug.** A caller who types
   `?typ=Crop` should be told, not silently given everything.
"""

import csv
from collections import defaultdict
from pathlib import Path

from api.errors import ApiError

ROOT = Path(__file__).resolve().parent.parent
KG = ROOT / "knowledge_graph"
PACKAGES = ROOT / "packages"

MAX_LIMIT = 500
DEFAULT_LIMIT = 50


def _read(path):
    if not Path(path).exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _int(value, default=0):
    v = str(value or "").strip()
    return int(v) if v.lstrip("-").isdigit() else default


class Repository:
    """Everything the API reads, loaded once at start-up.

    Held in memory deliberately: the graph is 647 entities and 865 edges, and a
    process that reloads CSVs per request would be slower and no more correct.
    The moment this stops fitting, this class is where a database goes.
    """

    def __init__(self, kg_dir=None, packages_dir=None, search_engine=None):
        self.kg = Path(kg_dir or KG)
        self.packages_dir = Path(packages_dir or PACKAGES)

        self.entities = _read(self.kg / "entities" / "entities.csv")
        self.by_gid = {e["global_entity_id"]: e for e in self.entities}
        self.relationships = _read(self.kg / "relationships" / "relationships.csv")
        self.by_rid = {r["relationship_id"]: r for r in self.relationships}
        self.aliases = _read(self.kg / "entities" / "aliases.csv")
        self.entity_types = _read(self.kg / "entities" / "entity_types.csv")
        self.relationship_types = _read(self.kg / "relationships" / "relationship_types.csv")
        self.ownership = _read(self.kg / "ownership" / "ownership_registry.csv")

        self.aliases_by_gid = defaultdict(list)
        for a in self.aliases:
            self.aliases_by_gid[a["global_entity_id"]].append(a)

        self.out_edges = defaultdict(list)
        self.in_edges = defaultdict(list)
        for r in self.relationships:
            self.out_edges[r["from_entity"]].append(r)
            self.in_edges[r["to_entity"]].append(r)

        self.packages = self._load_packages()

        # Built lazily: the search index costs ~1748 documents to construct and
        # most API calls never touch it.
        self._search = search_engine

    def _load_packages(self):
        out = []
        for pkg in sorted(p for p in self.packages_dir.iterdir() if p.is_dir()):
            ds_dir = pkg / "datasets"
            datasets = sorted(ds_dir.glob("*.csv")) if ds_dir.exists() else []
            if not datasets:
                continue          # a directory with no datasets is not a released package
            entries, rows = [], 0
            for f in datasets:
                n = len(_read(f))
                rows += n
                entries.append({"dataset": f.name, "rows": n})
            out.append({
                "package_id": pkg.name,
                "datasets": len(datasets),
                "rows": rows,
                "entities": sum(1 for e in self.entities if e["source_package"] == pkg.name),
                "dataset_index": entries,
            })
        return out

    @property
    def search(self):
        if self._search is None:
            from search.engine import SearchEngine
            self._search = SearchEngine()
        return self._search

    # ------------------------------------------------------------ counting
    def verification_counts(self):
        c = defaultdict(int)
        for e in self.entities:
            c[e.get("verification_status", "")] += 1
        return dict(c)


# ------------------------------------------------------------------ helpers
def paginate(rows, params):
    limit = _int(params.get("limit"), DEFAULT_LIMIT)
    offset = _int(params.get("offset"), 0)
    if limit < 0 or offset < 0:
        raise ApiError.bad_request("limit and offset must not be negative",
                                   limit=limit, offset=offset)
    if limit > MAX_LIMIT:
        raise ApiError.bad_request(
            f"limit {limit} exceeds the maximum of {MAX_LIMIT}", max_limit=MAX_LIMIT)
    window = rows[offset:offset + limit] if limit else rows[offset:]
    return window, {"total": len(rows), "limit": limit, "offset": offset,
                    "returned": len(window),
                    "has_more": offset + len(window) < len(rows)}


def reject_unknown(params, allowed):
    unknown = sorted(set(params) - set(allowed) - {"limit", "offset", "pretty"})
    if unknown:
        raise ApiError.bad_request(
            f"unknown query parameter(s): {', '.join(unknown)}",
            unknown=unknown, allowed=sorted(set(allowed) | {"limit", "offset"}))


def entity_payload(repo, e, include_aliases=True):
    d = {
        "global_entity_id": e["global_entity_id"],
        "canonical_name": e["canonical_name"],
        "entity_type": e["entity_type"],
        "source_package": e["source_package"],
        "package_local_id": e.get("package_local_id", ""),
        "confidence_score": _int(e.get("confidence_score")),
        "verification_status": e.get("verification_status", ""),
        "lifecycle_state": e.get("lifecycle_state", ""),
        "status": e.get("status", ""),
    }
    if include_aliases:
        d["aliases"] = [a["alias"] for a in repo.aliases_by_gid.get(e["global_entity_id"], [])]
    return d


def relationship_payload(repo, r, expand=True):
    d = {
        "relationship_id": r["relationship_id"],
        "from_entity": r["from_entity"],
        "relationship_type": r["relationship_type"],
        "to_entity": r["to_entity"],
        "confidence": _int(r.get("confidence")),
        "provenance": {
            "package": r.get("provenance_package", ""),
            "dataset": r.get("provenance_dataset", ""),
            "row_id": r.get("provenance_row_id", ""),
            "derived_at": r.get("derived_at", ""),
        },
    }
    if r.get("notes"):
        d["notes"] = r["notes"]
    if expand:
        src, dst = repo.by_gid.get(r["from_entity"]), repo.by_gid.get(r["to_entity"])
        d["from_name"] = src["canonical_name"] if src else None
        d["to_name"] = dst["canonical_name"] if dst else None
        d["from_type"] = src["entity_type"] if src else None
        d["to_type"] = dst["entity_type"] if dst else None
    return d


# ----------------------------------------------------------------- handlers
def list_entities(repo, params, **_):
    reject_unknown(params, ["type", "package", "q", "min_confidence",
                            "verification_status"])
    rows = repo.entities
    if params.get("type"):
        rows = [e for e in rows if e["entity_type"] == params["type"]]
    if params.get("package"):
        rows = [e for e in rows if e["source_package"] == params["package"]]
    if params.get("verification_status"):
        rows = [e for e in rows if e.get("verification_status") == params["verification_status"]]
    if params.get("min_confidence"):
        floor = _int(params["min_confidence"])
        rows = [e for e in rows if _int(e.get("confidence_score")) >= floor]
    if params.get("q"):
        # Substring filter, not search. /search is the ranked, alias-aware,
        # fuzzy-capable endpoint; this is a cheap narrowing of a listing.
        needle = params["q"].lower()
        rows = [e for e in rows if needle in e["canonical_name"].lower()]

    window, page = paginate(rows, params)
    return {"data": [entity_payload(repo, e) for e in window], "page": page}


def get_entity(repo, params, entity_id=None, **_):
    reject_unknown(params, ["include"])
    e = repo.by_gid.get(entity_id)
    if not e:
        raise ApiError.not_found("entity", entity_id)
    payload = entity_payload(repo, e)
    payload["relationships"] = {
        "outgoing": [relationship_payload(repo, r) for r in repo.out_edges.get(entity_id, [])],
        "incoming": [relationship_payload(repo, r) for r in repo.in_edges.get(entity_id, [])],
    }
    payload["degree"] = (len(repo.out_edges.get(entity_id, []))
                         + len(repo.in_edges.get(entity_id, [])))
    return {"data": payload}


def list_relationships(repo, params, **_):
    reject_unknown(params, ["type", "from", "to", "entity", "package", "min_confidence"])
    rows = repo.relationships
    if params.get("type"):
        rows = [r for r in rows if r["relationship_type"] == params["type"]]
    if params.get("from"):
        rows = [r for r in rows if r["from_entity"] == params["from"]]
    if params.get("to"):
        rows = [r for r in rows if r["to_entity"] == params["to"]]
    if params.get("entity"):
        gid = params["entity"]
        rows = [r for r in rows if gid in (r["from_entity"], r["to_entity"])]
    if params.get("package"):
        rows = [r for r in rows if r.get("provenance_package") == params["package"]]
    if params.get("min_confidence"):
        floor = _int(params["min_confidence"])
        rows = [r for r in rows if _int(r.get("confidence")) >= floor]

    window, page = paginate(rows, params)
    return {"data": [relationship_payload(repo, r) for r in window], "page": page}


def get_relationship(repo, params, relationship_id=None, **_):
    reject_unknown(params, [])
    r = repo.by_rid.get(relationship_id)
    if not r:
        raise ApiError.not_found("relationship", relationship_id)
    return {"data": relationship_payload(repo, r)}


def list_packages(repo, params, **_):
    reject_unknown(params, [])
    data = [{k: v for k, v in p.items() if k != "dataset_index"} for p in repo.packages]
    window, page = paginate(data, params)
    return {"data": window, "page": page}


def get_package(repo, params, package_id=None, **_):
    reject_unknown(params, [])
    for p in repo.packages:
        if p["package_id"] == package_id:
            entity_types = defaultdict(int)
            for e in repo.entities:
                if e["source_package"] == package_id:
                    entity_types[e["entity_type"]] += 1
            out = dict(p)
            out["entity_types"] = dict(sorted(entity_types.items(), key=lambda kv: -kv[1]))
            out["owns_entity_types"] = [o["entity_type"] for o in repo.ownership
                                        if o["owner_package"] == package_id]
            return {"data": out}
    raise ApiError.not_found("package", package_id)


def search(repo, params, **_):
    reject_unknown(params, ["q", "scope", "mode", "type", "package",
                            "min_confidence", "fuzzy_threshold"])
    q = params.get("q", "").strip()
    if not q:
        raise ApiError.bad_request("the `q` parameter is required and must not be empty")
    try:
        results = repo.search.search(
            q,
            scopes=params.get("scope"),
            modes=params.get("mode"),
            entity_type=params.get("type"),
            source_package=params.get("package"),
            min_confidence=_int(params.get("min_confidence")),
            limit=None,
            fuzzy_threshold=(float(params["fuzzy_threshold"])
                             if params.get("fuzzy_threshold") else None))
    except ValueError as exc:
        raise ApiError.bad_request(str(exc)) from None

    payload = [r.to_dict() for r in results]
    window, page = paginate(payload, params)
    return {"data": window, "page": page,
            "query": {"q": q, "scope": params.get("scope", "all"),
                      "mode": params.get("mode", "all")}}


def graph(repo, params, **_):
    reject_unknown(params, [])
    by_type = defaultdict(int)
    for e in repo.entities:
        by_type[e["entity_type"]] += 1
    by_rel = defaultdict(int)
    for r in repo.relationships:
        by_rel[r["relationship_type"]] += 1
    degree = defaultdict(int)
    for r in repo.relationships:
        degree[r["from_entity"]] += 1
        degree[r["to_entity"]] += 1
    connected = sum(1 for e in repo.entities if degree[e["global_entity_id"]])
    return {"data": {
        "entities": len(repo.entities),
        "relationships": len(repo.relationships),
        "aliases": len(repo.aliases),
        "entity_types_registered": len(repo.entity_types),
        "entity_types_populated": len(by_type),
        "relationship_types_registered": len(repo.relationship_types),
        "relationship_types_populated": len(by_rel),
        "connected_entities": connected,
        "orphan_entities": len(repo.entities) - connected,
        "connectivity_pct": (round(100 * connected / len(repo.entities), 2)
                             if repo.entities else 0.0),
        "entities_by_type": dict(sorted(by_type.items(), key=lambda kv: -kv[1])),
        "relationships_by_type": dict(sorted(by_rel.items(), key=lambda kv: -kv[1])),
        "packages": len(repo.packages),
    }}


def health(repo, params, **_):
    """Liveness plus the three loads that would make the API useless if empty."""
    checks = {
        "entities_loaded": len(repo.entities) > 0,
        "relationships_loaded": len(repo.relationships) > 0,
        "packages_loaded": len(repo.packages) > 0,
    }
    ok = all(checks.values())
    return {"data": {"status": "ok" if ok else "degraded", "checks": checks,
                     "entities": len(repo.entities),
                     "relationships": len(repo.relationships),
                     "packages": len(repo.packages)},
            "_status": 200 if ok else 503}


def version(repo, params, **_):
    from api import API_VERSION
    return {"data": {
        "api_version": API_VERSION,
        "platform_version": "2.2.0",
        "graph_version": "2.0.0",
        "knowledge_engine_version": "0.1.0",
        "read_only": True,
        "authentication": "none — v2.2 ships an unauthenticated read-only scaffold",
        "endpoints": ["/entities", "/entities/{id}", "/relationships",
                      "/relationships/{id}", "/packages", "/packages/{id}",
                      "/search", "/graph", "/health", "/version"],
    }}

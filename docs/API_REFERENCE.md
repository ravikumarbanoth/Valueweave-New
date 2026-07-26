# API Reference — ValueWeave Platform v2.2

**Version:** 2.2.0 · **Status:** read-only scaffold · **Authentication:** none

```bash
python3 -m api                          # http://127.0.0.1:8000
python3 -m api --port 8080
python3 -m api --route GET /graph       # one request, no socket
```

---

## Before you build against this

Three things are true of this API and none of them are temporary oversights:

**It is read-only, permanently.** Writes go to packages; the graph is derived from
them (ADR-001). `POST`, `PUT`, `PATCH` and `DELETE` return `405` with a message
saying so. There is no plan to add write endpoints to this surface.

**There is no authentication.** The v2.1 audit named auth and rate limiting as
blocking for a public deployment, and v2.2 did not build them. Inventing a token
scheme would look like security without being it. `GET /version` reports
`"authentication": "none"` so a consumer cannot mistake the situation. **Do not
expose this on a public interface.**

**Nothing in it has been verified by a human.** Every response carries
`meta.warning`, and it is the most important field in the envelope. It is computed
from the data, not hard-coded, so it will disappear on its own the day stewardship
makes it false.

---

## Response envelope

Every successful response has the same shape:

```json
{
  "data": [ ... ] | { ... },
  "page": { "total": 647, "limit": 50, "offset": 0, "returned": 50, "has_more": true },
  "meta": {
    "api_version": "2.2.0",
    "graph_version": "2.0.0",
    "entities": 647,
    "relationships": 865,
    "verification": { "VST-NEEDS_REVIEW": 647 },
    "warning": "No row in this knowledge base has had human data-steward review. ..."
  }
}
```

`page` appears only on list endpoints.

### Errors

```json
{
  "error": {
    "code": "BAD_REQUEST",
    "message": "unknown query parameter(s): typ",
    "status": 400,
    "detail": { "unknown": ["typ"], "allowed": ["limit", "offset", "package", "q", "type", ...] }
  }
}
```

| Code | Status | When |
|---|---|---|
| `BAD_REQUEST` | 400 | unknown query parameter, bad limit/offset, invalid search mode |
| `NOT_FOUND` | 404 | the id does not exist |
| `NO_ROUTE` | 404 | the path does not exist; `detail.available` lists every route |
| `METHOD_NOT_ALLOWED` | 405 | any non-GET method |
| `INTERNAL` | 500 | unexpected; still valid JSON, never a stack trace |

**Unknown query parameters are a 400, not a shrug.** `?typ=Crop` returns an error
naming the allowed parameters rather than silently returning everything — a typo
that returns plausible-looking wrong data is worse than one that fails.

### Pagination

`limit` (default 50, max 500) and `offset` (default 0) work on every list endpoint.
`page.has_more` tells you when to keep going. `limit=0` returns everything from
`offset` onward.

---

## Endpoints

### `GET /entities`

| Parameter | Meaning |
|---|---|
| `type` | exact entity type, e.g. `Crop`, `MSME`, `GovernmentScheme` |
| `package` | owning package, e.g. `Package005_Agriculture` |
| `q` | case-insensitive substring of `canonical_name` — a filter, not search |
| `min_confidence` | integer floor on `confidence_score` |
| `verification_status` | e.g. `VST-NEEDS_REVIEW` |

`q` is a cheap narrowing of a listing. For ranked, alias-aware, typo-tolerant
lookup use `/search`.

```bash
curl 'localhost:8000/entities?type=Crop&min_confidence=75&limit=5'
```

```json
{
  "global_entity_id": "vw:crop:turmeric",
  "canonical_name": "Turmeric",
  "entity_type": "Crop",
  "source_package": "Package005_Agriculture",
  "package_local_id": "crop-035",
  "confidence_score": 77,
  "verification_status": "VST-NEEDS_REVIEW",
  "lifecycle_state": "PUBLISHED",
  "aliases": ["Curcuma longa"]
}
```

### `GET /entities/{id}`

Adds `relationships.outgoing`, `relationships.incoming` and `degree`. Entity ids
are stable across rebuilds (ADR-002), so `vw:crop:turmeric` is safe to store as an
external reference.

### `GET /relationships`

| Parameter | Meaning |
|---|---|
| `type` | relationship type, e.g. `REQUIRES_SKILL` |
| `from` / `to` | one endpoint, by entity id |
| `entity` | either endpoint — both directions |
| `package` | provenance package |
| `min_confidence` | integer floor |

Every relationship carries the package, dataset and row that produced it:

```json
{
  "relationship_id": "vwr:000156",
  "from_entity": "vw:crop:turmeric",
  "relationship_type": "PART_OF",
  "to_entity": "vw:industry:agriculture-spices",
  "confidence": 77,
  "provenance": {
    "package": "Package005_Agriculture",
    "dataset": "crops.csv",
    "row_id": "crop-035",
    "derived_at": "2026-07-26"
  },
  "from_name": "Turmeric",
  "to_name": "Agriculture: Spices"
}
```

### `GET /relationships/{id}`

One edge, same shape.

### `GET /packages`

The eight released packages with dataset and row counts. A directory with no
datasets is not a released package and is not listed — `Package006_Skills` holds
only a README and is excluded.

### `GET /packages/{id}`

Adds `dataset_index`, `entity_types` and `owns_entity_types` — the entity types
this package is the authoritative owner of, per the ownership registry.

### `GET /search`

| Parameter | Meaning |
|---|---|
| `q` | **required**; empty is a 400 |
| `scope` | `entity` \| `alias` \| `relationship` \| `package` \| `dataset` \| `all` |
| `mode` | `EXACT` \| `PREFIX` \| `ALIAS` \| `FUZZY` \| `all` |
| `type` | entity or relationship type |
| `package` | owning package |
| `min_confidence` | integer floor |
| `fuzzy_threshold` | override the similarity floor for this call |

Results carry `match_mode`, `score` and `matched_on`, strongest mode first. See
[SEARCH_GUIDE.md](SEARCH_GUIDE.md).

### `GET /graph`

Counts, type distributions and connectivity. Currently 647 entities, 865
relationships, 78.05% connectivity, 142 orphans.

### `GET /health`

`200` when entities, relationships and packages all loaded; `503` and
`status: "degraded"` otherwise, with a per-check breakdown.

### `GET /version`

API, platform, graph and Knowledge Engine versions, the endpoint list, and the
`read_only` and `authentication` facts. `GET /` returns the same document.

---

## Architecture

```
api/__main__.py   CLI: serve, or dispatch one route
api/app.py        Application (routing, envelope) + ThreadingHTTPServer
api/handlers.py   ten handlers, pure functions of (params) -> payload
api/errors.py     one error shape
```

`Application.handle(method, path, query)` returns `(status, payload)` and touches
no socket, so every endpoint is testable without binding a port —
`tests/test_api.py` does exactly that, with one class that binds a real port
because in-process success and HTTP success are different claims.

Built on `http.server` from the standard library. No third-party dependency, by
the same constraint the Knowledge Engine adopted: this platform must run and be
reviewable on a bare Python install. A production deployment puts a real WSGI/ASGI
server in front, and `create_server` is the only function that changes.

## Known limitations

| Limitation | Why it stands |
|---|---|
| No authentication, no rate limiting | Named as blocking by the v2.1 audit; not built in v2.2. Do not expose publicly. |
| No version prefix in the URL | The API is a scaffold; `/v2/` would imply a stability guarantee not yet earned. |
| Data held in memory, loaded at start-up | 647 entities. `handlers.Repository` is where a database goes. |
| No `/query/*` named-query endpoints | `query_engine/queries.py` exists as a library; exposing it is v2.3 work. |
| Zero rows verified | Not an API limitation. It is the platform's largest gap, and `meta.warning` reports it on every response. |

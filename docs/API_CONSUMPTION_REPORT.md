# API Consumption Report — Platform v3.0, Step 3

Every read the knowledge UI makes, its cost, and why no HTTP API appears in the
request path.

---

## 0. There is still no API, and that is the design

**Step 3 added zero `fetch()` calls, zero API routes and zero dependencies.** Every read
is `supabase.from(...)` on the anon client — the pattern the application already used
before any knowledge work began.

```
React server component
        │  supabase-js, anon key, db.schema = "knowledge"
        ▼
Supabase PostgREST                  RLS: read-only, no write policy exists
        ▼
knowledge.*                         8 tables, projected from Git by knowledge_sync
```

The Python API (10 endpoints, 29 tests) and the Python `SearchEngine` (27 tests) remain
**undeployed and unconsumed**. Calling them would need a service, a deployment target, an
auth layer and a CORS surface that do not exist — the "new backend architecture" the
brief rules out. `test_frontend_still_makes_no_direct_http_calls_to_a_python_service`
asserts it.

---

## 1. Query inventory

| Surface | Queries | Composition |
|---|---:|---|
| `/knowledge` index | **1** | `typeCounts()` |
| `/knowledge?type=…` | **1** | `listEntities()` — rows **and** count |
| `/knowledge/[type]/[slug]` | **4** | entity → `Promise.all(detail, out-edges, in-edges)` |
| `/schemes`, `/skills` | 1–2 | CMS; +1 only when the CMS is empty |
| `/schemes/[slug]`, `/skills/[slug]` | 1–2 | CMS; +1 on fallback |
| `/dashboard` | **5** | 4 pre-existing + `latestKnowledge()` |
| `/district/[slug]` | 2 | unchanged from Step 2 |
| `/ideas/[slug]` | ~9 | unchanged from Step 2 |
| `KnowledgeSearch` | 1 per 250 ms | debounced, server-side filter |

**Peak: 5 queries on a page. No page issues a query per row.**

---

## 2. Four techniques that keep it there

### 2.1 Count rides on the page request

```js
sb.from("kg_entities").select("*", { count: "exact" })…range(from, to)
```

Supabase returns rows and total in one response. A separate `count()` would be a second
round trip for a number the first already has — the duplicate query the brief names.

### 2.2 Neighbours are two queries, not N

`getNeighbours` reads the edges, collects the endpoint ids, and fetches them with one
`.in(...)`. Sixty edges cost **2** queries. One-per-edge would cost 61.

### 2.3 Dependent reads run concurrently

```js
const [detail, related] = await Promise.all([
  getEntityDetail(entity),
  getRelatedByType(entity.global_entity_id),
]);
```

Detail-page latency is `entity + max(detail, related)`, not the sum. The two
`getRelatedByType` directions are themselves a `Promise.all`.

### 2.4 Slug → id is arithmetic

`vw:<type>:<slug>` is deterministic, so a detail page never queries to discover the id
it is about. **One query saved on every detail page view**, and the most-visited surface
type in the app.

---

## 3. Caching

| Surface | Strategy | Rationale |
|---|---|---|
| `/knowledge` + detail | `revalidate = 300` | Projection changes only on a package release |
| `/schemes`, `/skills` | `revalidate = 300` | Pre-existing |
| `/dashboard` | none | Client component, auth-gated, per-user |
| `KnowledgeSearch` | 250 ms debounce | Pre-existing |

**Five minutes, not five seconds and not an hour.** The data behind these pages moves
when someone merges a package and runs a sync — a schedule measured in weeks. Five
minutes means a deploy-time sync is visible almost immediately without making every
visitor pay for a query.

**Dashboard is deliberately uncached.** It is per-user and auth-gated; caching it would
need a keyed cache this codebase does not have, and `API_BINDING_REPORT.md` already
recorded the refetch-on-mount behaviour as pre-existing. Measuring before adding a cache
is the right order.

---

## 4. Pagination and lazy loading

| Mechanism | Where |
|---|---|
| Server-side `range()`, 24/page | `/knowledge?type=…` |
| Link-based pager | `KnowledgePagination` — shareable URLs, working back button |
| `limit` on every read | `getNeighbours` 60–120, `latestKnowledge` 6, `searchKnowledge` 12 |
| On-demand rendering | Graph detail pages are not pre-built |
| Debounce | Search, 250 ms |

**Pagination is link-based, not client state.** A page of knowledge is shareable and the
back button behaves — which client-side paging would break for a browse surface whose
whole purpose is exploration.

**`getRelatedByType` caps at 120 per direction.** The best-connected entity in the graph
has degree 39, so the cap is headroom rather than truncation today; it exists so that a
future hub cannot make one page pull thousands of rows.

---

## 5. Performance characteristics

| Metric | Value |
|---|---|
| Largest table | `kg_relationships`, 865 rows |
| Largest browse | `Industry`, 78 rows → 4 pages |
| Indexes on `knowledge` | 34 |
| Query touching an unindexed column | search — `ILIKE %q%` |

**The one known weakness is search.** `.ilike("canonical_name", "%q%")` is a
leading-wildcard scan; the existing btree cannot serve it and `pg_trgm` appears in no
migration. At 647 entities it is invisible. Backlog **P1**; the type filter added in
Step 3 narrows the scan as a side benefit.

Nothing here is a bottleneck at current scale, and the honest reason is that the scale is
small: 1,812 rows. These figures should be re-measured at ~10,000.

---

## 6. Write path

**None.** Step 3 issues **zero writes.** No table is inserted, updated or deleted.

That is enforced by the database, not by convention: neither `knowledge` nor
`user_intelligence` has a write policy of any kind, so a write would be rejected even if
one were attempted. Projected data is derived from Git, and a hand-edit would be silently
reverted by the next sync — the situation should be impossible rather than discouraged.

---

## 7. Deployment prerequisites

| # | Requirement | If missing |
|---|---|---|
| 1 | `NEXT_PUBLIC_SUPABASE_URL` / `_ANON_KEY` | **Silent** — every read returns empty |
| 2 | `knowledge` in *API → Exposed schemas* | **Silent** — every read returns empty |
| 3 | `user_intelligence` exposed | Dashboard shows `NOT_DEPLOYED` |
| 4 | Migrations applied | `SCHEMA_UNREACHABLE` |
| 5 | `knowledge_sync sync` has run | `EMPTY` |
| 6 | `kg_vocabulary_map` schema resolved | District/skill resolution returns nothing |

**Requirements 1 and 2 fail silently and identically.** `safe()` converts every failure
into a fallback by design — that is what lets these pages ship before the migration, and
it is also what makes a misconfiguration look like an empty database. The diagnostic is
in `DEPLOYMENT_CHECKLIST.md` §4.

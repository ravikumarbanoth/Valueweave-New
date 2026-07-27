# Frontend Data Binding — Platform v3.0, Step 3

Every read the knowledge UI performs, what it binds to, and the contract that keeps
the two languages agreeing.

---

## 0. The binding chain

```
packages/*/datasets/*.csv          Git — 2,299 researched rows, source of truth
        │  knowledge_graph/build_graph.py
        ▼
knowledge_graph/entities|relationships     647 entities · 865 edges
        │  knowledge_sync  (TABLE_SPECS)
        ▼
Supabase `knowledge` schema        8 tables, 1,812 rows
        │  frontend/lib/knowledge.js       ← this document
        ▼
React server components            no API client, no fetch(), no new dependency
```

There is **no HTTP API in the request path.** Every read is `supabase.from(...)` on the
anon client, exactly as the rest of the application already works.

---

## 1. `lib/knowledge.js` — 21 exports

### Pre-existing (Step 2)

| Export | Reads | Returns on failure |
|---|---|---|
| `getEntity(id)` | `kg_entities` | `null` |
| `getEntitiesByType(type, …)` | `kg_entities` | `[]` |
| `getNeighbours(id, …)` | `kg_relationships` + `kg_entities` | `[]` |
| `getDistrictKnowledge(id)` | via `getNeighbours` | `{}` |
| `resolveTerms(kind, terms)` | `kg_vocabulary_map` | `{resolved:[],unresolved:[]}` |
| `searchKnowledge(q, …)` | `kg_entities` | `[]` |
| `knowledgeAvailable()` | `kg_entities` | `{available:false, reason}` |
| `normaliseTerm(text)` | — | `""` |

### Added in Step 3

| Export | Reads | Purpose |
|---|---|---|
| `getEntityBySlug(urlType, slug)` | `kg_entities` | Detail pages, **no id lookup** |
| `getEntityDetail(entity)` | the per-type table | Rich attributes |
| `getRelatedByType(id)` | `kg_relationships` ×2 | Both directions, grouped |
| `listEntities(type, {page,…})` | `kg_entities` | Paginated browse **+ exact count** |
| `typeCounts()` | `kg_entities` | Explorer index |
| `latestKnowledge({limit})` | `kg_entities` | Dashboard card |
| `hrefFor(entity)` | — | Canonical in-app link |
| `entityIdFor(urlType, slug)` | — | Slug → `vw:type:slug` |
| `slugOf(entityOrId)` | — | Inverse |
| `TYPE_BY_URL` / `URL_BY_TYPE` | — | 14-type routing table |
| `PACKAGE_LABELS` | — | Source-package display |

**Every function returns empty on failure and never throws.** The schema is not
deployed anywhere yet; a page that threw would be a page that could not ship before the
migration.

---

## 2. Table and column bindings

| Entity type | Detail table | Joined on | Columns rendered |
|---|---|---|---:|
| `BusinessOpportunity` | `kg_businesses` | `id` | 11 |
| `MSME` | `kg_businesses` | `business_id` | 5 |
| `GovernmentScheme` | `kg_schemes` | `scheme_id` | 10 |
| `Skill` | `kg_skills` | `skill_id` | 9 |
| `District` | `kg_districts` | `dist_id` | 8 |
| `Industry` | `kg_industries` | `category_id` | 5 |
| `Crop` | `kg_agriculture` | `crop_id` | 7 |

The join key is always `kg_entities.package_local_id`, verified against real data at
**100%** for every type. `kg_businesses` needs two key columns because Package008 keys
MSMEs on `business_id` and Package004 keys opportunities on `id` — a detail from
`knowledge_sync/config.py` that a single-key assumption would have silently broken for
half the rows.

**Bindings are tested, not assumed.** `test_detail_attribute_columns_exist_in_the_synced_tables`
checks every rendered column against `TABLE_SPECS`. A column renamed in Python would
otherwise make the field vanish and the page look merely sparse.

---

## 3. The id contract

```python
# knowledge_graph/build_graph.py
gid = f"vw:{TYPE_SLUG[etype]}:{slug(canonical_name)}"
```
```js
// frontend/lib/knowledge.js
return `vw:${type.toLowerCase()}:${slug}`;
```

`TYPE_SLUG` is `slug(entity_type)`, which for every registered type is its lowercase
form. So a URL slug reconstructs an id arithmetically and a detail page costs **one
query, not two**.

`test_entity_id_scheme_matches_the_graph_builder` asserts both halves. If the builder's
scheme ever changes, the suite fails — rather than every detail page 404ing in
production while the data is present.

---

## 4. `lib/kg-fallback.js` — the CMS bridge

| Function | Behaviour |
|---|---|
| `withGraphFallback(type, cmsItems)` | CMS rows if any, else graph entities shaped like CMS rows |
| `detailWithGraphFallback(type, slug, cmsRow)` | Same, for one record |
| `rowHref(type, row)` | `/schemes/[slug]` for CMS, `/knowledge/scheme/[slug]` for graph |

Maps only `schemes → GovernmentScheme` and `skills → Skill`. `resources` and `roadmaps`
have no graph counterpart and keep their existing behaviour — inventing a mapping to
make two more pages look populated would be the fabrication the platform forbids.

---

## 5. Recommendation binding

`user_recommendations.item_id` **is** the `global_entity_id` for graph-backed
categories:

```
business_ideas       vw:msme:sheet-metal-fabrication-unit          MSME
government_schemes   vw:governmentscheme:pm-formalisation-…        GovernmentScheme
industries           vw:industry:manufacturing                     Industry
markets              vw:market:export-channel                      Market
```

So `hrefFor({global_entity_id: item_id, entity_type: item_type})` resolves with no
lookup. Editorial and Supabase categories keep prefixed ids (`idea:`, `user:`,
`article:`) and their own routes.

---

## 6. Query budget

| Page | Queries | Note |
|---|---:|---|
| `/knowledge` index | **1** | `typeCounts()` |
| `/knowledge?type=…` | **1** | `listEntities` — rows **and** count in one request |
| `/knowledge/[type]/[slug]` | **4** | entity → (detail ∥ related×2) |
| `/dashboard` | 5 | 4 pre-existing + `latestKnowledge` |
| `/district/[slug]` | 2 | unchanged |

`listEntities` uses `select("*", { count: "exact" })` so the pager's total rides on the
same request — a second round trip for a number the first can return is exactly the
duplicate query the brief rules out.

The detail page's three dependent reads run in one `Promise.all`, so its latency is
`entity + max(detail, related)`, not the sum.

---

## 7. Caching

| Surface | Strategy |
|---|---|
| `/knowledge`, `/knowledge/[type]/[slug]` | `revalidate = 300` |
| `/schemes`, `/skills` (+ details) | `revalidate = 300` (pre-existing) |
| `/dashboard` | Client component, no cache — pre-existing, auth-gated |
| `KnowledgeSearch` | 250 ms debounce, server-side type filter |

Five minutes is right because the projection changes only when a package is released
and a sync runs — not on a timer.

**Graph detail pages are not pre-rendered.** `generateStaticParams` returns only the 56
static paths. Pre-building 647 entity pages would tie `next build` to a database that is
not deployed, and the build must keep working without one.

---

## 8. Failure and degradation

| Failure | Behaviour | Visible? |
|---|---|---|
| Env vars missing | `knowledgeClient()` → `null` → fallback | Empty state |
| Schema not exposed | Query errors → `safe()` fallback | Empty state, reason `SCHEMA_UNREACHABLE` |
| Schema empty | Query succeeds, 0 rows | Empty state, reason `EMPTY` |
| Entity not found | `getEntity` → `null` | Empty state, not a 500 |
| Detail table missing | `getEntityDetail` → `null` | Header + related render; attributes omitted |
| No related edges | `getRelatedByType` → `{}` | Named message about relationship coverage |

**Degradation is layered.** A missing detail row costs the attributes section, not the
page. That matters because 43 of 45 businesses currently have no skill edge — those
pages must still be worth opening.

---

## 9. What is deliberately not bound

| Not bound | Why |
|---|---|
| Python `SearchEngine` (4 modes, 27 tests) | No deployment target. The UI uses Postgres `ILIKE` and does not claim parity |
| Python API (10 endpoints) | Would be the "new backend architecture" the brief rules out |
| `public.kg_*` beyond schemes/skills | `resources` and `roadmaps` have no graph counterpart |
| `entity_attributes` | Does not exist — the compiler has no attribute channel yet (`COMPILER_ARCHITECTURE.md` §4) |

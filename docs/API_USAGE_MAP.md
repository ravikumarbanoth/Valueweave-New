# API Usage Map — ValueWeave v3.0

**Phase 2/5 deliverable.** For every feature: the data access path, the graph query
behind it, and whether it goes through Supabase or the Python API.

---

## 1. Two access paths, and the rule for choosing

```
                       ┌─ Supabase (projection)  → user-facing pages, 100% of them
Knowledge Platform ────┤
                       └─ Python API (api/)      → admin surfaces only, v3.0
```

**The rule:** if a signed-out visitor or an ordinary user can trigger it, it goes through
Supabase. If only an admin can, the Python API is allowed.

The reason is not preference. The v2.2 API is a stdlib `http.server` scaffold with **no
authentication**, and its own reference says *"Do not expose this on a public interface."*
Putting it on the user request path in v3.0 would mean shipping auth, rate limiting and a
production server first — a project in itself
(`SUPABASE_INTEGRATION.md` §7). Meanwhile the frontend has **zero `fetch()` calls** today,
so every user-facing feature routed through Supabase adds no new failure mode.

---

## 2. Feature → access path

| Feature | Page | Path | Query |
|---|---|---|---|
| Scheme list | `/schemes` | Supabase | `kg_schemes` where `status='published'` — **existing code, unchanged** |
| Skill list | `/skills` | Supabase | `kg_skills` — **existing code, unchanged** |
| Entity detail | `/schemes/[slug]`, `/skills/[slug]` | Supabase | `kg_*` + `kg_graph_edges` for neighbours |
| Unified search | global | Supabase | FTS + `pg_trgm` over `kg_entity_registry` |
| District intelligence | `/district/[slug]` | Supabase | `mv_district_knowledge` — one read |
| Dashboard rails | `/dashboard` | Supabase | `mv_district_knowledge` + `mv_skill_demand` — two reads |
| Skill gap | `/opportunities/[id]`, `/connections` | Supabase | `kg_vocabulary_map` ⋈ `profiles.kg_skill_ids` |
| Idea ↔ business links | `/ideas/[slug]` | Supabase | `kg_vocabulary_map` (sector) → `kg_graph_edges` |
| Business Explorer | `/explore` or new | Supabase | `kg_entity_registry` filtered by type |
| **Graph statistics** | `/admin/knowledge-graph` | **Python API** | `GET /graph` |
| **Stewardship queue** | `/admin/stewardship` | **Python API** | `stewardship.store.queue()` |
| **Fuzzy diagnostics** | `/admin/search-intelligence` | **Python API** | `GET /search?mode=FUZZY` |

Nine of twelve are Supabase. The three that are not are admin-only, low-traffic, and
degrade an internal dashboard rather than a user page when they fail.

---

## 3. Graph queries behind each feature

Written as the traversal, so the Postgres equivalent is obvious.

### 3.1 District intelligence — `/district/[slug]`

```
District ←LOCATED_IN─           Institution | MSME | BusinessOpportunity | Industry
District ←GENERATES_EMPLOYMENT─ MSME
District  →SUPPORTED_BY_SCHEME→ GovernmentScheme   (via businesses located there)
```

| Section | Relationship | Edges available |
|---|---|---:|
| Institutions | `LOCATED_IN` | 121 |
| Businesses / MSMEs | `GENERATES_EMPLOYMENT` | 32 |
| Industries | `PART_OF` | 90 |
| Schemes | `SUPPORTED_BY_SCHEME` | 92 |
| Markets | `SELLS_TO` | **12 — thin** |

One read from `mv_district_knowledge`. **Coverage caveat:** 61 districts exist in the
graph but `GENERATES_EMPLOYMENT` has only 32 edges total, so most districts will show
industries and institutions but few businesses. The UI must render that honestly rather
than implying the district has no economy.

### 3.2 Dashboard recommendations — `/dashboard`

```
profiles.city  →[district crosswalk]→ District  → rails 1 and 2
profiles.skills→[skill crosswalk]───→ Skill ←REQUIRES_SKILL─ MSME|BusinessOpportunity → rail 3
                                      └→ sibling skills of matched businesses          → rail 4
```

| Rail | Query | Crosswalk resolve rate |
|---|---|---|
| District Opportunities | `mv_district_knowledge` on the user's district | **86%** |
| Recommended Schemes | matched businesses → `SUPPORTED_BY_SCHEME` | 86% (inherits district) |
| Recommended Businesses | `mv_skill_demand` on the user's resolved skills | **12%** |
| Recommended Skills | skills of the businesses from rail 3 | 12% |

The two rates are the whole story. Rails 1–2 are shippable; rails 3–4 are not, until the
skill crosswalk exists.

### 3.3 Skill gap — `/opportunities/[id]`, `/connections`

```
required = opportunities.kg_skill_ids
have     = union of profiles.kg_skill_ids over accepted collaborators
gap      = required − have
unknown  = skills in either set with match_method = 'NO_COUNTERPART'
```

`unknown` is a first-class output, not an error. It means "this skill is real but we have
no researched data for it" — the honest answer for roughly two thirds of the vocabulary
today.

### 3.4 Idea → researched comparables — `/ideas/[slug]`

```
idea.sector       →[sector crosswalk]→ Industry ←PART_OF─ BusinessOpportunity | MSME
                                                        →SUPPORTED_BY_SCHEME→ GovernmentScheme
                                                        →REQUIRES_SKILL→ Skill →TRAINED_BY→ TrainingProvider
idea.district_fit →[district crosswalk]→ District
```

`TRAINED_BY` has **3 edges in the entire graph**. The "skills mapped to real training"
section will be empty for essentially every idea. Ship the section only when the edge
count justifies it, or render it as a known gap — do not render a stub that implies
coverage.

### 3.5 Unified search

Four scopes, one query, ranked:

| Scope | Source | Rows |
|---|---|---:|
| Ideas | `lib/idea-library/ideas.json`, client-side | 122 |
| Entities | `kg_entity_registry` FTS + trigram | 647 |
| Aliases | `kg_entity_aliases` trigram | 150 |
| Opportunities | `opportunities` `ilike` | live |

Ideas stay client-side. They are 122 static records already loaded on `/ideas`, and moving
them server-side to unify the query would be a regression for the page that matters most.

---

## 4. Python API endpoint usage

Of the ten v2.2 endpoints, **three** are used in v3.0.

| Endpoint | Used by | Status |
|---|---|---|
| `GET /graph` | `/admin/knowledge-graph` | **Step 4** |
| `GET /search` | `/admin/search-intelligence` (fuzzy diagnostics) | Step 6 |
| `GET /version` | health check for the two above | Step 4 |
| `GET /entities`, `/entities/{id}` | — | superseded by the projection |
| `GET /relationships`, `/relationships/{id}` | — | superseded by `kg_graph_edges` |
| `GET /packages`, `/packages/{id}` | — | admin curiosity, not required |
| `GET /health` | deployment probe only | Step 4 |

That is the honest accounting: **the projection makes most of the API redundant for the
frontend**, and that is the intended outcome. The API's value in v3.0 is as the reference
implementation the sync is validated against, plus three admin reads.

### Deployment prerequisites, if and when it happens

Not optional, and in this order:

1. A real WSGI/ASGI server — `http.server` is a scaffold
2. Authentication — currently **none**
3. Rate limiting — currently **none**
4. A private network path or IP allowlist, since it is admin-only
5. `NEXT_PUBLIC_KNOWLEDGE_API_URL` + a server-side token

Until 1–4 exist, `/admin/knowledge-graph` should read the projection and show a reduced
statistic set rather than deploy an unauthenticated service.

---

## 5. Data access modules

`frontend/lib/knowledge.js` — new, deliberately mirroring the existing
`lib/knowledge-graph.js` so it reads as the same codebase.

| Function | Returns | Cache |
|---|---|---|
| `getEntity(id)` | entity + aliases | `revalidate: 300` |
| `getEntitiesByType(type, opts)` | list | `revalidate: 300` |
| `getNeighbours(id, relType, direction)` | edges + resolved endpoints | `revalidate: 300` |
| `getDistrictKnowledge(districtId)` | `mv_district_knowledge` row | `revalidate: 600` |
| `getSkillDemand(skillIds)` | `mv_skill_demand` rows | `revalidate: 600` |
| `resolveTerms(kind, terms)` | crosswalk hits + `NO_COUNTERPART` | `revalidate: 3600` |
| `searchKnowledge(q, opts)` | ranked results | none |

Same conventions as the existing module: silent failure (`catch { return [] }`), anon
client for public reads, `revalidate` on server components. An engineer who knows
`lib/knowledge-graph.js` will recognise this file on sight.

### Caching

| Layer | Mechanism | TTL |
|---|---|---|
| Server components | `export const revalidate` | 300 s (entities), 600 s (views) |
| Crosswalk | `revalidate` | 3600 s — changes only when a steward edits it |
| Search | none | live |
| Client components | **none today** | see below |

**The gap.** `/dashboard` and `/ideas` are client components with no caching and no
deduplication — every mount refetches. Adding four knowledge rails to `/dashboard` on that
basis means four uncached queries per visit. The materialised views reduce this to two,
which is acceptable; anything more needs a client cache, and adding one is a new
dependency this plan otherwise avoids. Measure before deciding.

---

## 6. Error and empty states

Three distinct situations that must not look the same:

| Situation | Meaning | UI |
|---|---|---|
| Query returned rows | data exists | render |
| Query returned `[]` | no data **for this input** | *"No researched businesses recorded for Medak yet."* |
| Crosswalk says `NO_COUNTERPART` | the term is real, we have **no data on it** | *"We don't have researched data for AC Repair yet."* |
| Query failed | the system broke | *"Couldn't load this section."* + retry |

Collapsing rows 2–4 into one blank panel is the most likely way this integration
disappoints users: an empty div reads as a broken product when the honest answer is a
coverage gap. This distinction is the reason `NO_COUNTERPART` is a stored value rather
than an absent row.

---

## 7. The provenance requirement

**Non-negotiable, and it applies to every surface.** Zero of 2,299 rows have human review.

Every knowledge card carries:

- `ConfidenceBadge` — 0–100, banded, with a tooltip explaining it scores *source strength*, not correctness
- `ProvenanceLine` — `Package007 · government_schemes.csv · sch-005`
- `UnverifiedNotice` — once per page section, not once per card

The Python API already enforces this on every response via a computed `meta.warning` that
disappears on its own when verification arrives. **The Supabase path must reproduce that
behaviour**, because the projection carries `verification_status` per row: compute the
notice from the data, never hard-code it. A hard-coded disclaimer will still be sitting
there in a year, long after it stopped being true — and a stale disclaimer is its own kind
of dishonesty.

# API Binding Report — Platform v3.0, Step 2

Every data call the integrated pages make: what it reads, how it degrades, and why
there is no HTTP API in the path.

---

## 1. There is no new API, and that is the design

The brief says: do not build new backend architecture, do not duplicate APIs.

**Nothing was added to `app/api/`.** The directory still does not exist. The frontend
still makes **zero `fetch()` calls** to any service — a test greps for it.

Every binding below is a `supabase.from(...)` call through
`@supabase/supabase-js`, which the application already depends on. The Python
engines reach the frontend by *writing tables*, not by serving requests:

```
Python engine  ──writes──▶  Supabase table  ──reads──▶  React component
```

The v2.2 REST API (`api/`, 10 endpoints) is **not on this path**. It remains the
admin/analyst surface and the reference implementation; it is an unauthenticated
stdlib scaffold whose own reference says not to expose it publicly.

---

## 2. `lib/knowledge.js` — the `knowledge` schema

Client: `createClient(url, anonKey, { db: { schema: "knowledge" } })`,
no session persistence. Anonymous: this data is public research.

| Function | Reads | Returns on failure |
|---|---|---|
| `getEntity()` | `kg_entities`, `kg_relationships`, `kg_vocabulary_map` | `[]` / `null` |
| `getEntitiesByType()` | `kg_entities`, `kg_relationships`, `kg_vocabulary_map` | `[]` / `null` |
| `getNeighbours()` | `kg_entities`, `kg_relationships`, `kg_vocabulary_map` | `[]` / `null` |
| `getDistrictKnowledge()` | `kg_entities`, `kg_relationships`, `kg_vocabulary_map` | `[]` / `null` |
| `resolveTerms()` | `kg_entities`, `kg_relationships`, `kg_vocabulary_map` | `[]` / `null` |
| `normaliseTerm()` | — | `[]` / `null` |
| `searchKnowledge()` | `kg_entities`, `kg_relationships`, `kg_vocabulary_map` | `[]` / `null` |
| `knowledgeAvailable()` | `kg_entities`, `kg_relationships`, `kg_vocabulary_map` | `[]` / `null` |

Tables touched: `kg_entities`, `kg_relationships`, `kg_vocabulary_map`.

**Every query filters `sync_deleted_at is null`.** The projection soft-deletes rather
than removing, so a read that ignores it would show rows Git no longer produces. The
filter is hoisted into a `LIVE` constant so it cannot be forgotten in one place.

**`getNeighbours` uses two round trips, not N+1.** It fetches the edges, then fetches
every endpoint in one `.in(...)` — an edge list of 60 costs two queries rather than
sixty-one.

---

## 3. `lib/intelligence.js` — the `user_intelligence` schema

| Function | Reads | Notes |
|---|---|---|
| `getSkillProfile()` | one of the five tables | returns `null`/`[]` on failure |
| `getBusinessProfile()` | one of the five tables | returns `null`/`[]` on failure |
| `getLearningProfile()` | one of the five tables | returns `null`/`[]` on failure |
| `getActivitySummary()` | `user_activity_summary` | returns `null`/`[]` on failure |
| `getRecommendations()` | `user_recommendations` | returns `null`/`[]` on failure |
| `getRecommendationsByCategory()` | `user_recommendations` | returns `null`/`[]` on failure |
| `intelligenceState()` | `user_activity_summary` | returns `null`/`[]` on failure |
| `scoreLabel()` | one of the five tables | presentation helper, no query |
| `scoreTone()` | one of the five tables | presentation helper, no query |
| `confidenceBand()` | one of the five tables | presentation helper, no query |

All five engine output tables are read: `user_skill_profile`, `user_business_profile`, `user_learning_profile`, `user_recommendations`, `user_activity_summary`.
A test asserts none is orphaned.

### Authorisation is RLS, not a filter

Every policy is `auth.uid() = user_id`, **with no admin exception**. Passing another
user's id returns nothing. The `isMe` prop on `IntelligencePanel` controls *wording*,
never access — a filter this file could forget is not the security boundary.

### `intelligenceState()` — the function that prevents a lie

```js
NOT_DEPLOYED  → the schema is unreachable; nobody has run the migration
NOT_COMPUTED  → the schema exists; this user has no row yet
OK            → we have their summary
```

Without this split a page says *"we have nothing to tell you about you"* when the
truth is *"nobody has run the engine"*. Those are different sentences and the second
is not the user's problem.

### `RULES_VERSION` is part of every key

Pinned to `"1.0.0"`, matching the Python engine. Rows are keyed
`(user_id, rules_version)` so a recommendation a user acted on stays explainable
after the rules change. A drift here means reading **zero rows**, not stale ones —
which is why a test compares the two constants.

---

## 4. Bindings by page

| Page | Query | Table | Degrades to |
|---|---|---|---|
| `/dashboard` | existing feed | `opportunities` | unchanged |
| `/dashboard` | `intelligenceState` | `user_activity_summary` | not-deployed notice |
| `/dashboard` | `getRecommendationsByCategory` | `user_recommendations` | per-rail empty state |
| `/profile` | existing | `profiles`, `opportunities` | unchanged |
| `/profile` | 3 parallel reads | `user_skill_profile`, `user_business_profile`, `user_learning_profile` | "not analysed yet" |
| `/connections` | existing + `skills` | `connections`, `profiles` | unchanged |
| `/connections` | `getRecommendations` | `user_recommendations` | rail hidden |
| `/district/[slug]` | `resolveTerms` → `getDistrictKnowledge` | `kg_vocabulary_map`, `kg_entities`, `kg_relationships` | stated collection gap |
| `/ideas/[slug]` | `resolveTerms` ×3 → `getNeighbours` ×N | same | "no researched counterpart yet" |
| `KnowledgeSearch` | `searchKnowledge`, debounced 250 ms | `kg_entities` | researched group hidden |

**One round trip per rail set, not per rail.** `getRecommendationsByCategory` fetches
200 rows once and buckets them client-side, so a four-rail dashboard costs one query.

---

## 5. Query budget

| Page | Existing | Added | Total |
|---|---:|---:|---:|
| `/dashboard` | 2 | 2 | 4 |
| `/profile` | 2 | 4 | 6 |
| `/connections` | 3 | 2 | 5 |
| `/district/[slug]` | 0 (static) | 2, at build time | 2 |
| `/ideas/[slug]` | 0 (static) | 3 + N schemes | ~9 |

`/ideas/[slug]` is the one to watch: it issues one scheme query per matched business,
capped at 6. If that becomes slow, the fix is a materialised view
(`DATABASE_EXTENSION_PLAN.md` §5), not a client cache.

**`/dashboard` and `/profile` are client components with no cache**, so every mount
refetches. That is pre-existing behaviour; the additions inherit it. Measure before
adding a cache — that would be a new dependency this step otherwise avoids.

---

## 6. Failure and degradation

| Failure | Behaviour |
|---|---|
| Schema not exposed in Supabase settings | Every read returns `[]` → empty states. **The most likely cause of a silent blank.** |
| Migration not applied | Same. `intelligenceState` reports `NOT_DEPLOYED`. |
| Sync never run | `knowledgeAvailable()` reports `EMPTY`. |
| Engine never run for this user | `NOT_COMPUTED`. |
| Network error | `catch` → fallback. No error boundary is triggered. |
| RLS denies | Empty result, indistinguishable from no data. Correct: a denial should not confirm a row exists. |

Every path degrades to an explained empty state. **No page throws, and no page shows
a spinner forever.**

---

## 7. Deployment prerequisites

Non-negotiable, and the first is the one that will be missed:

1. **Expose the schemas.** Supabase → API → Exposed schemas must list `knowledge`
   and `user_intelligence`. Without this, `db: { schema }` returns nothing and every
   page looks merely empty.
2. Apply the migrations (see `SUPABASE_EXTENSION_PLAN.md`).
3. Run `knowledge_sync` to populate `knowledge`.
4. Run the intelligence engine per user to populate `user_intelligence`.
5. Confirm `RULES_VERSION` in `lib/intelligence.js` matches the engine.

Step 5 is guarded by a test. Step 1 is not guardable from here and belongs in a
deployment checklist.

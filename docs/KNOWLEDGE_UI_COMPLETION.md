# Knowledge UI Completion — Platform v3.0, Step 3

**Commit base:** `c7004ad` · **Branch:** `claude/v3-step3-knowledge-ui`

`next build` → **exit 0, 214/214 static pages, 0 prerender errors**
`tests/run_all.py` → **478 tests, 0 fail, 0 error, 0 skip** (was 458)
Frontend diff **+599 / −50** across 9 files · **11 new files, 735 lines** · **0 new dependencies**

---

## 0. The one thing to know before reading the rest

**Every surface built here renders an empty state today, and that is correct.**

```
$ ls knowledge_sync/state/
.gitignore  README.md          ← no manifest: the sync has never run
```

Supabase holds **zero** of the 1,812 researched rows. The pages are built, tested and
deployed-ready; they have no data to show until `DEPLOYMENT_CHECKLIST.md` §2, §4 and §6
run. That is a **backend dependency**, not an incomplete page — §7 lists all four.

Every empty state names *which* of the three causes applies, because
`NOT_DEPLOYED`, `EMPTY` and `NO_MATCH` look identical to a user and mean opposite
things.

---

## 1. What was built, against the ten priorities

| # | Priority | Status | Where |
|---|---|---|---|
| **1** | Dashboard | ✅ **Complete** | 6 rails + intelligence summary + latest knowledge, all linking |
| **2** | Knowledge Explorer | ✅ **Complete** | **New** `/knowledge` — browse 6 packages, 14 types, paginated |
| **3** | Business detail | ✅ **Complete** | `/knowledge/business/[slug]` — 11 attributes, 7 related types |
| **4** | Scheme detail | ✅ **Complete** | `/knowledge/scheme/[slug]` + `/schemes/[slug]` fallback |
| **5** | Skill detail | ✅ **Complete** | `/knowledge/skill/[slug]` + `/skills/[slug]` fallback |
| **6** | District explorer | ✅ **Complete** | Panel extended 6 → 8 groups, every card links |
| **7** | Search | ✅ **Complete** | 7 entity-type filters, results link, server-side filtering |
| **8** | Recommendations | ✅ **Complete** | Reason + confidence + provenance + supporting entities |
| **9** | Connections | 🟡 **Unchanged** | Step 2's collaborator rail already met the ask — §5 |
| **10** | Idea Library | ✅ **Enriched** | Editorial preserved, graph entities now linked |

---

## 2. Three decisions that avoided duplication

The brief's hardest constraint was *do not duplicate*. Three choices did the work.

### 2.1 One detail route, two namespaces

`/knowledge/[type]/[slug]` already existed, backed by `lib/static-knowledge.js` — 7
plural types, 56 pre-rendered pages. The obvious move was a second route for graph
entities. Instead:

| Namespace | Types | Backed by |
|---|---|---|
| **Plural** — `districts`, `skills`, `schemes` … | 7 | Static JSON (unchanged) |
| **Singular** — `district`, `skill`, `scheme` … | **14** | **Knowledge graph** |

They cannot collide, so one route serves both and **the 56 existing pages keep working
byte-for-byte**. A test asserts the namespaces stay disjoint.

Priorities 3, 4 and 5 are then the *same component* with different attribute maps and a
different lead ordering of related types. Three near-identical detail pages would have
drifted within a month.

### 2.2 The two knowledge systems, resolved without deleting either

`/schemes` and `/skills` read `public.kg_*` — admin-CMS tables that nothing populates.
They have always said *"will appear here after admins publish them"*, while
`knowledge.kg_schemes` holds 40 researched schemes. Two systems, colliding table names,
contradictory answers. Logged as backlog **A1**.

`lib/kg-fallback.js` resolves it **additively**:

```
CMS has rows        →  render the CMS  (an admin who publishes still wins)
CMS is empty        →  render the researched graph, and say so
Neither has rows    →  the existing empty state
```

No table dropped, no route removed, no URL changed. A test asserts the CMS still takes
precedence — otherwise this would be a replacement wearing a fallback's clothes.

### 2.3 Slug → id needs no lookup

Entity ids are `vw:<type_slug>:<name_slug>`, generated deterministically by
`build_graph.py`. So `/knowledge/skill/welding` reconstructs
`vw:skill:welding` arithmetically — **one query per detail page, not two**, and a 404
costs nothing.

A test compares the JS reconstruction against the Python builder's format string, so a
change to the id scheme fails the suite instead of 404ing every detail page in
production.

---

## 3. Priority 1 — Dashboard

| Card | Source | Links to |
|---|---|---|
| Recommended business ideas | `user_recommendations` | `/ideas/…` or `/knowledge/…` |
| Government schemes | `user_recommendations` | `/knowledge/scheme/…` |
| Skills to learn | `user_recommendations` | `/knowledge/skill/…` |
| District opportunities | `user_recommendations` | `/knowledge/msme/…` |
| **Recommended industries** | **new rail** | `/knowledge/industry/…` |
| **Where you could sell** | **new rail** | `/knowledge/market/…` |
| **Intelligence summary** | **new card** — 8 scores | `/profile` |
| **Latest knowledge** | **new card** | `/knowledge/…` |

### The bug this exposed

`RecommendationRail`'s `HREF_BUILDERS` returned `null` for every graph-backed category:

```js
government_schemes: () => null,   // before
msmes: () => null,
industries: () => null,
```

The engine has always emitted the `global_entity_id` as `item_id`
(`vw:governmentscheme:pmegp`). **The data to link was there from Step 1.5; there was
just nowhere to link to.** Now there is, and five categories became clickable by
deleting five `null`s.

`scoreLabel()` renders `—`, never `0`, when a score is `UNAVAILABLE`. Telling a user
their funding readiness is zero when the truth is that we cannot assess it is the
easiest way this platform could mislead.

---

## 4. Priorities 3–6 — the detail pages

One component, four attribute maps, sourced from `knowledge_sync/config.py`:

| Type | Attributes | Lead related types |
|---|---:|---|
| BusinessOpportunity | 11 | Skill · Certification · Scheme · Industry · Market · District · MSME |
| GovernmentScheme | 10 | Business · MSME · Skill · District · Crop · Bank |
| Skill | 9 | Provider · Certification · Business · Industry · Scheme · MSME |
| District | 8 | Industry · Business · MSME · Institution · Scheme · Crop |

A test asserts every rendered column exists in `TABLE_SPECS` — a renamed column
otherwise makes the field silently vanish and the page look merely sparse.

**Sentinels are never shown.** `AttributeGrid` skips `PENDING_VERIFICATION` and
`PENDING_GEOCODING` rather than printing them; a user seeing the literal string would
read it as a bug rather than the honest gap it is.

**`NextSteps`** turns the brief's navigation loop into a control: every detail page
offers up to three concrete next hops drawn from its own related entities.

---

## 5. Priority 9 — Connections, deliberately unchanged

Step 2 already added a collaborators rail driven by `user_intelligence`, with real
`skillOverlap` computed from `profiles.skills` on both sides of an accepted connection.

The brief asks to *"recommend people, teams, businesses, projects."* **Teams and
projects do not exist** — no route, no table with data, `teams` empty by design
(`MISSING_FEATURES.md`). Adding rails that would permanently render `NO_DATA_SOURCE`
would be adding surface without adding knowledge.

**Recommending people is done. The other three are blocked on features, not on UI**, and
I left the page alone rather than manufacture the appearance of completion.

---

## 6. General requirements

| Requirement | How |
|---|---|
| Every item names its **source package** | `SourceBadge` on the explorer, detail header and latest-knowledge card. Tested on all three |
| Every recommendation shows **reason** | `KnowledgeCard` renders it unconditionally, never truncated |
| **Confidence** | `ConfidenceBadge`, banded, with the caveat that it scores *source strength* |
| **Supporting entities** | `RelatedEntities` names each link's relationship type |
| **Knowledge source** | `ProvenanceLine` — package · dataset · row id |

---

## 7. Backend dependencies still blocking visibility

**All four are deployment, none is code.**

| # | Blocker | Effect | Fix |
|---|---|---|---|
| **B1** | **Sync has never run** | Every knowledge surface empty | `DEPLOYMENT_CHECKLIST.md` §6 |
| **B2** | **Schemas not exposed** | Every read returns empty **with no error** | §4 — the step most likely to be missed |
| **B3** | `kg_vocabulary_map` in `public`, queried via the `knowledge` client | District/skill resolution silently returns nothing | §5 |
| **B4** | Intelligence engine never run | Dashboard rails show `NOT_COMPUTED` | §7 |

Two further gaps limit content **after** deployment, and they are data, not UI:

- **`RS2-VIA_DISTRICT` and `RI3-VIA_DISTRICT` are structurally dead** — 0 scheme→district
  and 0 industry→district edges. Scheme and industry rails will stay thin for users
  whose skills do not resolve. Phase 2 `R1` recovers 305 of these from a dataset already
  in the repository.
- **2 of 45 businesses have a skill edge.** The business detail page's "required skills"
  section will be empty for 43 of them until Phase 2 `E1`/`R5` land.

**The UI is ahead of the data. That is the right order** — the pages are what make the
data's absence visible and specific, and each empty state names the gap it is waiting on.

---

## 8. What was not done, and why

| Not done | Reason |
|---|---|
| Team / project recommendations | The features do not exist. §5 |
| Pre-rendering 647 graph detail pages | Would tie the build to a database not yet deployed. Served on demand, `revalidate = 300` |
| Replacing the 122 editorial ideas | Brief says enrich, not replace. Graph entities are now linked from every idea |
| Retiring `public.kg_*` | Out of scope and destructive. The fallback makes it harmless |
| Screenshots | No deployed environment and no data to render. Route inventory and build output stand in — `PAGE_COMPLETION_REPORT.md` |

---

**Companion documents:** `FRONTEND_DATA_BINDING.md` · `PAGE_COMPLETION_REPORT.md` ·
`API_CONSUMPTION_REPORT.md` · `USER_FLOW_REPORT.md`

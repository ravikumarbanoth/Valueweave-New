# Implementation Roadmap — ValueWeave v3.0

**Phase 4 and Phase 5 deliverable.** Eight independently deployable steps, plus the gap
analysis.

**Nothing in this roadmap has been built.** This is the plan the brief asked for before
application code changes.

---

## 0. Two deviations from the brief, and why

The brief specifies six steps in this order: Search → Knowledge Cards → Recommendations →
District Dashboard → Team Intelligence → Business Explorer. This roadmap changes two
things, both forced by what the analysis found.

**Search moves after the backfill.** `/skills` and `/schemes` read `kg_*` tables that were
created with *"No seed data"*. Search over empty tables finds nothing. Filling them is
also, separately, the highest-value change available — 40 sourced schemes and 45 skills
become visible with **no UI work at all**.

**A Step 0 is inserted.** 7 of 57 onboarding skills (12%) resolve to a graph Skill.
Recommendations built on that join would be blank for nine users in ten. The crosswalk is
2–3 days and unblocks every user-facing feature.

Everything else keeps the brief's shape and its independent-deployability requirement.

---

## Step 0 — Vocabulary reconciliation ✅ **BUILT**

**low risk · blocks Steps 5, 6, 7 · delivered on `claude/v3-step0-vocabulary-crosswalk`**

The prerequisite. Without it the graph and the users speak different languages.

### Measured outcome

| Vocabulary | Terms | Resolved | Rate | Before Step 0 |
|---|---:|---:|---:|---:|
| District | 33 | 33 | **100%** | 84.8% |
| Sector | 22 | 11 | 50.0% | 27.3% |
| Skill | 147 | 39 | 26.5% | 14.3% |
| **Total** | **202** | **83** | **41.1%** | 27.2% |
| **Onboarding skills** | **57** | **13** | **22.8%** | **12.3%** |

Matchers: `EXACT_NAME` 39, `CURATED` 28, `PREFIX` 16, **`FUZZY` 0**.

**No fuzzy match cleared the 0.88 threshold unambiguously.** The two vocabularies are not
near-misses of each other — they are different vocabularies, which is why curation carried
more rows than every automatic matcher except exact naming.

**Districts hit 100% and are fully unblocked.** Dashboard rails 1–2 and the whole of Step 4
can proceed.

**Skills reached 22.8%, against the 60% target, and the remainder is not fixable here.**
110 of the 119 unresolved terms have *no counterpart in the knowledge base at all* —
`Accounting`, `Data Entry`, `Digital Marketing`, `SEO`, `Graphic Design`,
`Beautician Services`, `CCTV Installation` and 43 more skills the onboarding form actively
nudges users to claim. Lowering the threshold would produce confident wrong answers, not
coverage. **Reaching 60% requires collecting ~30 skills into Package006**; the backlog is
published in `crosswalk_summary.json → collection_backlog`.

The other 9 unresolved terms span more than one entity (`EV & Energy` covers Electric
Vehicles, Renewable Energy and Power & Utilities) and are recorded as such rather than
forced to one, with their candidates in `notes`.

### Delivered

| Deliverable | Status |
|---|---|
| `governance/vocabulary/build_crosswalk.py` | ✅ 5 matchers, `--check` mode, aborts on a broken override |
| `governance/vocabulary/curated_overrides.json` | ✅ 17 curated mappings + 9 multi-target terms, each with a reason |
| `governance/vocabulary/{skill,sector,district}_crosswalk.csv` | ✅ 202 rows |
| `governance/vocabulary/crosswalk_summary.json` | ✅ Includes the collection backlog |
| `governance/vocabulary/README.md` | ✅ |
| `frontend/migrations/009_vocabulary_crosswalk.sql` | ✅ Written — **not applied**, no database access from this environment |
| `tests/test_vocabulary.py` | ✅ 24 tests, wired into `tests/run_all.py` |

**Method.** The ADR-003 pattern reused exactly: `EXACT_NAME` → `ALIAS` → `PREFIX` →
`FUZZY` (accepted only when exactly one candidate clears 0.88) → human `CURATED`. Anything
left is `NO_COUNTERPART` — a determinate statement, not a missing row.

**Still outstanding from this step:** making `/opportunities/new` and `/onboarding`
*suggest* crosswalked terms first. It touches application code and therefore belongs with
Step 1's frontend work, but it is where the vocabulary problem is cheapest to fix — every
resolvable term entered from now on raises the join rate for every later feature at
near-zero cost.

**Verification:** `python3 governance/vocabulary/build_crosswalk.py --check` exits 0;
24 tests pass; `test_no_application_code_is_touched_by_this_step` confirms no page or
component was edited.

**Revert:** delete `governance/vocabulary/` and migration 009. Nothing depends on them yet.

---

## Step 1 — Package → Supabase sync, and fill the empty shelves

**4 days · low risk · depends on Step 0 (schema only)**

| Deliverable | Detail |
|---|---|
| Migration `008` | `kg_entity_registry`, `kg_entity_aliases`, `kg_graph_edges` |
| `scripts/sync_to_supabase.py` | One-way, idempotent, aborts rather than half-writes |
| Backfill | 40 schemes → `kg_schemes`, 45 skills → `kg_skills`, providers + institutions → `kg_resources`, 61 districts, 78 industries |
| CI job | Runs on push to `main` touching `packages/**` |
| `frontend/lib/knowledge.js` | Mirrors `lib/knowledge-graph.js` |

**Zero UI changes.** `/skills` and `/schemes` already render `PublicEntityList`; they stop
showing *"Schemes will appear here after admins publish them"* and start showing 40 real
schemes. This is the whole point of doing it first.

**Guardrails:** projected rows carry `source = 'package'` and are read-only in the admin
UI. `--check` mode exits non-zero on drift and is what CI runs. Idempotency is tested the
way `test_graph_integrity.py` tests the graph — compare two runs to each other.

**Done when:** `/schemes` shows 40 schemes, `/skills` shows 45, running the sync twice
produces no second-run diff, and `--check` is green in CI.

**Revert:** stop the CI job; drop three tables. The pages return to their empty state.

---

## Step 2 — Knowledge cards with provenance

**3 days · low risk · depends on Step 1**

| Deliverable | Detail |
|---|---|
| `KnowledgeCard`, `KnowledgeCardGrid` | Name, type, `ConfidenceBadge`, `ProvenanceLine`, link |
| `ConfidenceBadge` | 0–100 → band + tooltip: *scores source strength, not correctness* |
| `ProvenanceLine` | `Package007 · government_schemes.csv · sch-005` |
| `UnverifiedNotice` | Computed from `verification_status`, once per section |
| `RelatedEntities` | Neighbours grouped by relationship type |
| `/admin/stewardship` | The v2.2 review queue as a page |

**This is the step that makes everything after it honest.** Every later feature renders
these components, so the disclosure is built in rather than retrofitted.

The notice must be **computed, not hard-coded** — the API already does this, and a
hard-coded disclaimer will still be sitting there a year after it stopped being true.

`/admin/stewardship` is included here because it is the only path off 0% verified: it
surfaces the 40 highest-leverage entities, which cover 37.2% of all edge endpoints.

**Done when:** no knowledge is rendered anywhere without provenance and a confidence
badge, and a steward can record a review from the browser.

**Revert:** delete six components; no page depends on them yet.

---

## Step 3 — Unified search

**4 days · medium risk · depends on Step 1**

| Deliverable | Detail |
|---|---|
| Migration `011` (partial) | `pg_trgm`, `search_tsv`, GIN indexes |
| `searchKnowledge()` | FTS + trigram over entities and aliases |
| Extend `KnowledgeSearch.jsx` | Add entity results beside the existing static ones |
| Global search in `AppNavbar` | Ideas + entities + opportunities |
| Tracking | `search_events.result_kind` |

**Reuse, don't replace.** `components/platform/KnowledgeSearch.jsx` already exists and
does client-side search over `static-knowledge`. It gains a second result group. Ideas stay
client-side — 122 records already loaded on `/ideas`, and moving them server-side to unify
the query would make the page that matters most slower.

**Risk.** Postgres FTS does not reproduce `SearchEngine`'s ranked four-mode ladder. Accept
the difference and keep the Python engine as the reference and the admin tool; do not
claim parity in the UI.

**Done when:** a single box returns ideas, entities, aliases and opportunities, each
labelled by kind, and results are tracked.

**Revert:** revert the component; drop the index.

---

## Step 4 — District intelligence

**5 days · medium risk · depends on Steps 1, 2**

| Deliverable | Detail |
|---|---|
| Migration `011` | `mv_district_knowledge` |
| `DistrictIntelligencePanel` | Six sections: industries, businesses, schemes, institutions, markets, MSMEs |
| `/district/[slug]` | Panel added **below** existing editorial |
| `/admin/knowledge-graph` | Real stats (647 / 865 / 78.05%) |

**Do not migrate the editorial content.** `lib/districts-data.js` narrative is better
writing than anything the graph generates. Graph data goes below it, labelled as researched
data. Layer A owns narrative; Layer C owns facts.

**Two honest limits to render, not hide.** `SELLS_TO` has 12 edges and
`GENERATES_EMPLOYMENT` has 32 across 61 districts — most districts will show industries and
institutions but few businesses. And 47 of 61 graph districts have no page at all;
generating thin pages for them is an SEO decision, not an integration one.

**Done when:** all 14 district pages show researched data below their editorial, and every
section distinguishes "no data yet" from "failed to load".

**Revert:** remove the panel import; drop the view.

---

## Step 5 — Dashboard recommendations

**6 days · HIGH risk · depends on Steps 0, 1, 2**

| Deliverable | Detail |
|---|---|
| Migration `010` | `profiles.kg_skill_ids`, `kg_district_id`, and six more |
| Migration `011` | `mv_skill_demand` |
| Resolution pass | Populate `kg_*_ids` from existing free text via the crosswalk |
| `RecommendationRail` | With a "why this?" affordance |
| `/dashboard` | Four rails below the existing feed |
| `/profile` | Knowledge Graph Profile, Skill Profile, Recommendation Profile |

**Why this is the high-risk step.** Two of the four rails depend on a join that resolves
for **12%** of users today. Ship rails 1–2 (district-driven, 86%) first and gate 3–4 on a
measured resolve rate — a threshold agreed in advance, not decided after the fact.

**The most valuable thing on the profile page** is the list of claimed skills with **no
researched counterpart**. It is honest, it is useful to the user, and it is the collection
backlog. It is also the easiest thing to get wrong by rendering silence instead.

**Not built:** "Assessment Profile" from the brief has no data behind it — no assessment
table, no assessment package. Listed in §Phase 5 as a gap, not stubbed.

**Recommended Collaborators is not graph-driven.** `founder_matches` and
`collaborator_profiles` already do this. Knowledge adds one line of *explanation* — "also
needs Welding, which you have" — not a parallel implementation.

**Done when:** rails 1–2 render for every user with a resolvable city; rails 3–4 render or
show an explicit no-data state; nothing renders a blank div.

**Revert:** remove the rails. Columns stay (nullable, harmless).

---

## Step 6 — Business Explorer and Idea Library links

**5 days · medium risk · depends on Steps 1, 2, 3**

| Deliverable | Detail |
|---|---|
| Business Explorer | 45 `BusinessOpportunity` + 40 `MSME`, filterable |
| `/ideas/[slug]` | Comparable researched businesses, supporting schemes, skill mapping, viable districts |
| `/ideas` | "Has researched data" filter chip |
| `/opportunities/[id]` | Researched comparables |

**Link ideas to businesses; never merge them.** An idea is editorial and inspirational; a
Package004 row is researched and sourced. They are different kinds of claim and the UI must
say which is which.

**Where the Explorer lives is a product decision this plan does not make.** `/explore`,
`/discover`, `/opportunity-radar`, `/business-ideas/[district]`, `/manufacturing` and
`/district-opportunity-index` are all variations on browsing opportunities. Adding a
seventh surface entrenches the duplication; consolidating first is the better move but is
out of scope here.

**Done when:** every idea whose sector resolves shows at least one researched comparable,
and the ones that do not say so explicitly.

**Revert:** remove the route and the sections.

---

## Step 7 — Working-group skill intelligence (Teams, descoped)

**5 days · high risk · depends on Steps 0, 5**

**There is no Teams feature in this application.** No `teams` table, no `team_members`, no
`/teams` route. What exists is `connections` (opportunity-scoped, 1:1), `collaborator_profiles`
and `founder_matches`.

So this step delivers the knowledge half against the surface that actually exists:

| Deliverable | Detail |
|---|---|
| `SkillGapPanel` | Have / need / **no researched data for**, over accepted collaborators |
| `/opportunities/[id]` | Gap for the opportunity's working group |
| `/connections` | Shared vs complementary skills on an accepted connection |
| `/collaborators/[sector]` | Sector → researched industries |
| Suggested members | Explanation layered onto existing `founder_matches` |

**A first-class `teams` entity is a v3.1 product decision**, not an integration task. It
needs a table, RLS, invitations, roles and a lifecycle — larger than everything else in
this roadmap combined. Building it here would be scope the brief did not actually ask for,
under a heading that assumed it already existed.

**Done when:** an opportunity with accepted collaborators shows a real skill gap, including
the terms with no researched counterpart.

**Revert:** remove the panel.

---

## Timeline

```
Week 1   ██ Step 0  vocabulary
Week 2   ██ Step 1  sync + backfill        ← /skills and /schemes go live
Week 3   ██ Step 2  cards + provenance     ← + /admin/stewardship
Week 4   ██ Step 3  search
Week 5-6 ██ Step 4  district intelligence
Week 7-8 ██ Step 5  recommendations        ← gated on skill resolve rate
Week 9   ██ Step 6  business explorer
Week 10  ██ Step 7  working-group skills
```

**~10 weeks.** Steps 3 and 4 can run in parallel with two engineers. Step 5 cannot start
before Step 0 lands, whatever the calendar says.

---

# Phase 5 — Gap Analysis

## G1. Missing frontend components

Nine new components serve all 21 affected pages. Everything else is reuse.

| Component | Pages | Effort |
|---|---:|---|
| `KnowledgeCard` | 12 | 0.5 d |
| `KnowledgeCardGrid` | 9 | 0.5 d |
| `ProvenanceLine` | all | 0.25 d |
| `ConfidenceBadge` | all | 0.25 d |
| `UnverifiedNotice` | 8 | 0.25 d |
| `RelatedEntities` | 7 | 1 d |
| `SkillGapPanel` | 3 | 1.5 d |
| `DistrictIntelligencePanel` | 3 | 1.5 d |
| `RecommendationRail` | 2 | 1 d |

**Reused unchanged:** `PublicEntityList`, `PublicEntityDetail`, `OpportunityCard`,
`AppNavbar`, `ModuleShell`, `KnowledgeSearch`, `DistrictProfile`, `ProfileView`, `Skeleton`,
`CollaboratorCard`.

## G2. Missing APIs

| Gap | Impact | Resolution |
|---|---|---|
| No `app/api/` and zero `fetch()` calls | No pattern for HTTP data access | Avoided: Supabase for all user-facing reads |
| Python API has **no auth, no rate limiting** | Cannot be exposed | Admin-only, private path, Step 4 |
| Python API runs on `http.server` | Not production-grade | Real ASGI server before any deploy |
| No recommendation endpoint | Rails computed client-side from views | Acceptable at this size |
| No `/query/*` named-query endpoints | Five named queries stay library-only | v3.1 |
| No webhook from package release → sync | Manual trigger risk | CI on `packages/**` |

## G3. Missing database tables

| Missing | For | Migration |
|---|---|---|
| `kg_entity_registry` | every knowledge read | 008 |
| `kg_entity_aliases` | lookup by surface form | 008 |
| `kg_graph_edges` | every traversal | 008 |
| `kg_vocabulary_map` | **user ↔ graph join** | 009 |
| `mv_district_knowledge` | district page, dashboard | 011 |
| `mv_skill_demand` | recommendations, skill gap | 011 |
| `teams`, `team_members` | Teams | **not built — v3.1 decision** |
| assessment tables | "Assessment Profile" | **not built — no data exists** |

## G4. Missing indexes

21 new. Full DDL in `DATABASE_EXTENSION_PLAN.md`.

| Kind | Count | Why |
|---|---:|---|
| Entity type / package / slug | 5 | list and filter |
| Trigram (`pg_trgm`) | 2 | typo-tolerant search |
| Edge `(entity, type)` composite | 3 | every traversal filters both |
| GIN on `text[]` columns | 3 | skill and industry array membership |
| FK and `source` | 6 | join and projection filtering |
| MV unique | 2 | required for `refresh concurrently` |

**Pre-existing gap:** `search_events` has no index on `query` or `created_at`, and
`/admin/search-intelligence` reads it. Not caused by this work; worth fixing alongside.

## G5. Missing permissions

| Gap | Severity | Resolution |
|---|---|---|
| New tables need RLS | High | 12 policies, matching the existing `kg_*` shape |
| Service-role key handling | **High** | CI only, server-side only, never `NEXT_PUBLIC_*` |
| Materialised views bypass RLS | Medium | Both aggregate public data only — **stated decision, not an oversight** |
| Projected rows editable by admins | Medium | `source = 'package'` → read-only in the admin UI |
| No per-user knowledge permissions | Low | Package data is public research; none needed |
| `ADMIN_EMAILS` bootstrap allowlist | Low | Pre-existing; env-var-based admin is worth revisiting |

## G6. Missing caching

| Layer | Today | Needed |
|---|---|---|
| Server components | `revalidate = 300` where used | Extend to new reads |
| **Client components** | **none** | `/dashboard` and `/ideas` refetch on every mount |
| Crosswalk | — | 3600 s; changes only on steward edit |
| Materialised views | — | Refresh in the sync, `concurrently` |
| Search | — | None; live is correct |
| CDN | Vercel default | `revalidate` on new server components |

**The real risk.** `/dashboard` is a client component with no cache and no deduplication.
Four knowledge rails means four more uncached queries per mount. The materialised views cut
this to two, which is acceptable. Beyond that needs a client cache — a new dependency this
plan otherwise avoids. **Measure `/dashboard` before and after Step 5** rather than adding
one speculatively.

## G7. Gaps found that this project did not create

Reported because they surfaced during analysis, not because they are in scope.

| Finding | Note |
|---|---|
| `backend/server.py` (412 lines) | FastAPI + **MongoDB** + `emergentagent.com` OAuth. Referenced by nothing in `frontend/`. Superseded by Supabase. **Recommend deleting in a separate PR.** |
| `activity_log` and `platform_stats` are **views**, not tables | Defined in `006_visitor_analytics.sql` as UNIONs over five analytics tables. Correct as designed — noted only because a reader counting tables will not find them. They are unaffected by this plan. |
| Six overlapping discovery routes | `/explore`, `/discover`, `/opportunity-radar`, `/business-ideas/[district]`, `/manufacturing`, `/district-opportunity-index`. Consolidate before extending. |
| Duplicate district routes | `/district/[slug]` (14 rich profiles) vs `/districts/[slug]` (stub over a 1-record JSON). |
| `packages/Package006_Skills` | Placeholder README claiming no Skills data was released — untrue since `Package006_Skills_and_Training` shipped. |
| `frontend/data/districts.json` | **1** record, against 14 in `districts-data.js` and 61 in the graph. |
| **0 of 2,299 rows human-verified** | The platform's largest gap. Step 2's `/admin/stewardship` is the only path off it. |

---

## Success criteria

| Metric | Now | Target | Step |
|---|---:|---:|---|
| Package rows visible to users | **0** | ~250 | 1 |
| Pages showing researched knowledge | 0 | 21 | 1–7 |
| Onboarding skills resolvable | 12% → **22.8%** | ≥ 60% | 0 done; **needs ~30 new Package006 skills** |
| District terms resolvable | 86% → **100%** ✅ | 100% | 0 **done** |
| Knowledge rendered without provenance | n/a | **0** | 2 |
| Rows human-verified | **0** | ≥ 40 (37.2% of edge endpoints) | 2 |
| New runtime dependencies | — | **0** | all |
| Existing pages redesigned | — | **0** | all |
| Existing tables dropped or renamed | — | **0** | all |

The last three are constraints from the brief, tracked as metrics because that is the only
way they stay true.

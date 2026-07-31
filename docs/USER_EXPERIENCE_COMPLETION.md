# User Experience Completion

**ValueWeave Platform v3.0 · Step 4 — Frontend Knowledge Activation**

What changed for the person using the platform, phase by phase against the brief,
and the judgement calls behind the parts that did not change.

---

## The change in one paragraph

Before this step, a user walking through ValueWeave met **99 placeholder
elements** promising capabilities that, in eleven cases, already worked. The
homepage led with 56 hand-written JSON records under a banner reading "Early
static knowledge previews". Search answered from those 56 before it answered from
647 sourced entities. Thirteen district pages showed four "Coming Soon" cards
each against a graph holding 61 researched districts. Five module dashboards said
the platform had "no database tables, APIs, or business rules yet" while querying
a knowledge graph with 647 entities and 865 typed relationships.

After it: **zero** "Coming Soon" chips render, every capability declares `LIVE`,
`NOT_AVAILABLE_YET` or `NO_DATA_SOURCE`, every unavailable one names what it is
waiting for, and every one of the graph's 19 entity types has a page you can
reach.

---

## Phase-by-phase

| Phase | Asked for | Delivered |
|---|---|---|
| 1 · Discovery | Complete inventory | 99 elements across 10 patterns — `PLACEHOLDER_REMOVAL_REPORT.md` §1 |
| 2 · Wiring | Replace what a backend can power; relabel the rest with its dependency | 93 replaced, 6 relabelled. `CapabilityStatus.jsx` makes a dependency structurally required for any non-`LIVE` card |
| 3 · Dashboard | Remove placeholder widgets | None found — Step 3 had already wired it. Recommendation cards gained their fifth required element (§Phase 11) |
| 4 · Explorer | Every category live | 5 missing entity types added; 3 section headings corrected after they were found naming the wrong package |
| 5 · Search | Live data, no mock results | Static layer removed entirely. Researched projection is now the search. Filters 8 → 10 |
| 6 · Business detail | Investment, skills, schemes, markets, training centres, MSMEs, districts, related | 7 of 8 live from the graph. Lead-related types widened from 7 to 10 to include training providers, raw materials and machinery. Setup plan → `NO_DATA_SOURCE` |
| 7 · Skill pages | Training centres, businesses, schemes, industries, learning roadmap | 4 of 5 live. Learning roadmap → `NO_DATA_SOURCE`: Package006 records NSQF level and duration but **no ordering between skills**, and a roadmap built from difficulty alone would be a guess presented as a curriculum |
| 8 · Scheme pages | Eligibility, businesses, skills, district coverage, application links, related | 4 of 6 live. Eligibility and required documents → `NO_DATA_SOURCE` naming `eligibility_criteria.csv` (55 rows, researched, unprojected) |
| 9 · District pages | Industries, businesses, agriculture, schemes, training centres, MSMEs, institutions, summary | **13 placeholder dashboards replaced** with all 8 sections live. `/districts` went from 14 districts to 61 |
| 10 · Idea Library | Keep editorial, enrich it | Editorial untouched. **Resolved** skills and districts now render as links — the component was already resolving them and discarding the successes, showing only failures |
| 11 · Recommendations | Reason, confidence, supporting knowledge, related entities, source package | All five. Supporting entities were being read for a package name and then dropped; they are now navigable |
| 12 · Navigation | One connected knowledge network | 5 entity types and 50 entities had **no route at all**; `hrefFor()` was silently degrading them to a search box |

---

## The five empty states

Implemented once in `KnowledgeEmptyState.jsx` and shared by `KnowledgeCardGrid`,
so the same word means the same thing everywhere.

| State | Means | Names a dependency |
|---|---|---|
| `NOT_DEPLOYED` | Backend exists; this environment has not deployed it | yes — the checklist step |
| `EMPTY` | Schema deployed, nothing synced | yes — `run_sync.sh` |
| `NO_MATCH` | We looked; the answer is nothing | no — it is a real answer |
| `NOT_AVAILABLE_YET` | Not built | yes, per caller |
| `NO_DATA_SOURCE` | No package covers it | yes, per caller |

`NOT_COMPUTED` stays local to the card grid — it is specific to per-user
intelligence and has no shared-knowledge equivalent.

**`NOT_DEPLOYED` and `EMPTY` look identical from a browser and are deliberately
not distinguished there.** The anon client cannot tell an unexposed schema from
an empty one; claiming otherwise would be a guess. `scripts/health_check.sh`
tells an operator the difference in one command.

---

## Four judgement calls worth defending

**1 · `/ai` was left unavailable.** It would have been easy to make this page look
activated — the platform does have a recommendation engine. It is rule-based on
purpose: deterministic rules over the graph, each recommendation carrying the rule
that fired. Relabelling that "AI" would have been the most misleading single
change available in this step. The page now names it as what it is and keeps all
four advisors unavailable.

**2 · The 56 static pages were kept.** Nothing links to them and the search that
surfaced them is gone, but they are indexed URLs. Breaking them to make a point
about data quality is a worse trade than leaving them reachable — so each opens
with a notice saying it is editorial, unsourced and superseded, and links to the
researched equivalent.

**3 · The radar's scores were labelled, not replaced.** `fitScore: 91` and
`demandScore: 93` are hand-assigned editorial judgements rendered as `/100` badges
with progress bars — visually identical to the computed confidence scores
elsewhere. The ranking is editorial work the brief protects; the *presentation*
was borrowing credibility it had not earned. Both radar pages now say so.

**4 · Eligibility was not faked.** The obvious way to fill Phase 8's Eligibility
section is to compose something from the scheme's `coverage` and
`ideal_target_audience` columns. It would have looked complete. It would also
have been a fabricated eligibility rule for a government scheme, which is the one
category of error on this platform that could cost a user money. The section says
what is missing and names the file.

---

## Tests

`tests/test_frontend_activation.py` — **33 tests**, 7 classes, registered as
`frontend_activation`. **563 total across 15 suites**, up from 530.

The suite guards the regressions that render perfectly: a `Coming Soon` chip
reintroduced on a working capability, an entity type added with no route, a
recommendation that stops showing its reason. `NavigationTest` reads
`entities.csv` directly and fails if any type lacks a route, an explorer entry, a
related-list label or a recommendation-link mapping.

### Two Step-2 tests were rewritten

`test_search_uses_the_projection_without_replacing_static_search` asserted *"the
existing static search must survive"*. This brief says *"Remove every mock
result"*. Rewritten to assert the reverse, with `assertNotIn` so a future change
that reintroduces the unsourced layer fails rather than silently restoring it
above the sourced one.

`test_empty_states_are_distinguished` checked three state names inside
`KnowledgeCardGrid`. Now checks five in the shared module plus the import,
asserting the two components share one vocabulary instead of forking it.

### One bug the tests caught in themselves

`PlaceholderRemovalTest` immediately flagged `HomeVideoEmbed.jsx` — whose
`{/* … */}` JSX comment documents the phrase it had just removed. The helper
stripped `//` lines but not block comments. Fixed in the helper rather than by
rewording the comment: a future developer writing a legitimate JSX note would
have hit the same false positive.

---

## What a user gets today, honestly

**On a deployed environment:** every page above populates. Skill-driven rails
resolve for roughly one user in four (22.8% crosswalk coverage); district-driven
rails resolve for all of them. Training and market sections stay thin —
`TRAINED_BY` holds 3 edges and `SELLS_TO` holds 12.

**On this repository as it stands:** the schemas are deployed nowhere, so every
knowledge surface renders `NOT_DEPLOYED` and tells the reader so. No page in this
step has been loaded in a browser against a live database. `npx next build`
proves all 214 pages render; it does not prove they render populated. That
distinction is what `POST_DEPLOYMENT_VALIDATION.md` exists for.

---

**Companions:** `PLACEHOLDER_REMOVAL_REPORT.md` · `KNOWLEDGE_BINDING_REPORT.md` ·
`LIVE_PAGE_REPORT.md` · `REMAINING_DEPENDENCIES.md`

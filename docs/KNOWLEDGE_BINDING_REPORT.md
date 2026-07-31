# Knowledge Binding Report

**ValueWeave Platform v3.0 · Step 4 — Frontend Knowledge Activation**

Which frontend surface reads which backend, through which function, and what it
does when that backend is absent.

---

## 1 · The five backends

| Backend | Reached through | Deployed? |
|---|---|---|
| Knowledge Graph (`knowledge.kg_entities`, `kg_relationships`) | `lib/knowledge.js` | needs migration + sync |
| Knowledge Schema (6 per-type detail tables) | `lib/knowledge.js` `getEntityDetail()` | same |
| Vocabulary crosswalk (`knowledge.kg_vocabulary_map`) | `lib/knowledge.js` `resolveTerms()` | migration 011 + `load_crosswalk.sh` |
| User Intelligence (5 tables) | `lib/intelligence.js` | `run_user_intelligence.sh --apply` |
| Application tables (`public.*`) | `lib/supabase-*.js` | already live |

**Every knowledge read returns `[]` or `null` on failure and never throws.** That
contract is what lets these pages ship before the projection is deployed, and it
is why the empty states carry the weight they do — see §4.

---

## 2 · Binding table

| Surface | Function | Backend | Records available |
|---|---|---|---:|
| `/` featured knowledge | `featuredByType()` **new** | graph | 6 types, 1 each |
| `/` category counts | `typeCounts()` | graph | 647 |
| `/` search | `searchKnowledge()` | graph | 647 |
| `/knowledge` index | `typeCounts()` | graph | 19 types |
| `/knowledge?type=` | `listEntities()` | graph | paged, exact count |
| `/knowledge/<type>/<slug>` | `getEntityBySlug()` + `getEntityDetail()` + `getRelatedByType()` | graph + detail tables | 647 + 865 edges |
| `/districts` | `getEntitiesByType("District")` **new binding** | graph | 61 |
| `/districts/<slug>` | `resolveTerms()` + `getDistrictKnowledge()` **new binding** | crosswalk + graph | 61 |
| `/district/<slug>` | same | crosswalk + graph | 14 editorial |
| `/skills`, `/schemes` | `withGraphFallback()` | CMS → graph | 45 / 40 |
| `/readiness` | `typeCounts()` **new binding** | graph | 100 across 3 types |
| `/manufacturing` | `typeCounts()` **new binding** | graph | 135 across 3 types |
| `/scale` | `typeCounts()` **new binding** | graph | 61 across 3 types |
| `/network` | `typeCounts()` **new binding** | graph | 66 + marketplace |
| `/ai` | `typeCounts()` **new binding** | graph | 647 |
| `/dashboard` rails | `getRecommendationsByCategory()` | user intelligence | per user |
| `/dashboard` latest | `latestKnowledge()` | graph | 6 |
| `/ideas/<slug>` | `resolveTerms()` + `getNeighbours()` | crosswalk + graph | per idea |

**Nine new bindings.** Nothing existing was rewired.

---

## 3 · What each package now reaches

| Package | Entity types | Entities | Surfaces |
|---|---|---:|---|
| Package001_Geography | District, State, Country, ExportCountry | 93 | `/districts`, `/district/*`, `/scale`, explorer, search |
| Package002_Education | Institution | 66 | `/network`, district panels, explorer |
| Package003_Healthcare | — | **0** | none — see `REMAINING_DEPENDENCIES.md` §2 |
| Package004_Industries | Industry, BusinessOpportunity | 70 | `/manufacturing`, `/ideas/*`, explorer, dashboard |
| Package005_Agriculture | Crop, Soil, ClimateZone, Machinery, Industry | 99 | explorer, district panels, `/manufacturing` |
| Package006_Skills_and_Training | Skill, Certification, TrainingProvider | 100 | `/readiness`, `/skills`, skill detail, dashboard |
| Package007_Government_Schemes | GovernmentScheme, FinancialInstitution | 52 | `/schemes`, `/network`, `/scale`, dashboard |
| Package008_MSME | MSME, Industry, Machinery, Market, RawMaterial, FinancialInstitution | 167 | `/manufacturing`, `/scale`, explorer |

**Package003_Healthcare contributes zero entities to the graph.** That was found
in the v1.0 readiness assessment and is unchanged by this step — no frontend work
can surface entities a builder does not produce.

---

## 4 · Type routing — the defect this step closed

`TYPE_BY_URL` in `lib/knowledge.js` is the map from URL segment to entity type.
`hrefFor()` reads it; when a type is absent it returns a **search URL** rather
than a detail page.

It held **14 of the graph's 19 types**. Five were missing:

| Type | Entities | Package | Was reachable? |
|---|---:|---|---|
| ExportCountry | 29 | Package001 | no |
| Soil | 10 | Package005 | no |
| ClimateZone | 8 | Package005 | no |
| State | 2 | Package001 | no |
| Country | 1 | Package001 | no |

**50 entities with no detail page, and nothing said so.** Every link to them
silently degraded to a search box. All five are now routed (`export`, `soil`,
`climate`, `state`, `country`), listed in the explorer, labelled in related
lists, and linkable from recommendation evidence.

`NavigationTest` in `tests/test_frontend_activation.py` reads
`knowledge_graph/entities/entities.csv` directly and fails if any entity type
lacks a route, an explorer entry, a related-list label, or a recommendation-link
mapping — and also if a route points at a type the graph does not have. A future
builder adding a type cannot reintroduce this defect silently.

---

## 5 · Explorer section headings — a second correction

The explorer grouped types by "the package that owns each type" and put a
`SourceBadge` on every heading. Three of those headings were **wrong**, because
three types span packages:

| Type | Actual split |
|---|---|
| Industry | 25 Package004 · 20 Package005 · 33 Package008 |
| Machinery | 16 Package005 · 53 Package008 |
| FinancialInstitution | 12 Package007 · 9 Package008 |

`Industry` sat under a Package004 badge while **two thirds** of it came from
elsewhere. Grouping is by domain now, and provenance stays where it is accurate:
on each entity's own card, carrying the package that produced that row.

---

## 6 · Failure behaviour

Every binding degrades to a **named** state, never a blank panel:

| Condition | State | What the user is told |
|---|---|---|
| No `NEXT_PUBLIC_SUPABASE_*` | `NOT_DEPLOYED` | not switched on here; names the checklist step |
| Schema not exposed | `NOT_DEPLOYED` | same — indistinguishable from the client, correctly |
| Schema exposed, sync not run | `EMPTY` | 1,812 rows waiting in Git; names `run_sync.sh` |
| Query returned nothing | `NO_MATCH` | a real answer about coverage |
| Capability not built | `NOT_AVAILABLE_YET` | names what it waits on |
| No package covers it | `NO_DATA_SOURCE` | the research does not exist |
| Engine has not run for this user | `NOT_COMPUTED` | names `run_user_intelligence.sh` |

The first two are indistinguishable from the browser and are deliberately not
distinguished. Claiming to know which would be a guess, and `health_check.sh`
tells an operator the difference in one command.

---

**Companions:** `PLACEHOLDER_REMOVAL_REPORT.md` · `LIVE_PAGE_REPORT.md` ·
`REMAINING_DEPENDENCIES.md` · `USER_EXPERIENCE_COMPLETION.md`

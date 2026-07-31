# Live Page Report

**ValueWeave Platform v3.0 · Step 4 — Frontend Knowledge Activation**

Every route in the application, reviewed. The brief's instruction was *"Do not
finish until every frontend page has been reviewed"*, so this lists all **80**,
including the ones nothing changed on and the ones that never should.

---

## Summary

| | Before Step 4 | After |
|---|---:|---:|
| Total routes | 80 | 80 |
| Reading the knowledge graph | 8 | **14** |
| Reading user intelligence | 3 | 3 |
| Reading the CMS with a graph fallback | 4 | 4 |
| Reading only static/editorial data | 11 | **5** |
| Rendering placeholder dashboards | 6 | **0** |
| Build | 214/214 static pages, exit 0 | 214/214, exit 0 |

**No route was added or removed.** `NoDuplicationTest` asserts the count stays at
80, so a future change cannot quietly add a page in a step whose brief forbids it.

**Legend** — `KG` knowledge graph · `UI` user intelligence · `CMS` `public.kg_*`
admin tables · `FB` CMS→graph fallback · `APP` application tables ·
`ED` editorial (idea library, district narratives, radar)

---

## 1 · Public routes changed by this step (14)

| Route | Sources | What changed |
|---|---|---|
| `/` | KG · APP · ED | Featured knowledge now live (`featuredByType` + `typeCounts`); 6 `Planned` chips → `NO_DATA_SOURCE` with dependencies; search reads the projection only; 2 stray placeholder strings replaced |
| `/knowledge` | KG | 5 missing entity types added; sections regrouped by domain after 3 headings were found naming the wrong package |
| `/knowledge/<type>/<slug>` | KG · ED | Lead-related types widened for 3 entity kinds; `category` attribute added to 4; 4 declared-but-unsourced sections named; legacy static pages get a "superseded" notice |
| `/districts` | KG · ED | Listed 14, now lists 14 editorial **+ 47 researched** |
| `/districts/<slug>` | KG · ED | **13 placeholder dashboards replaced** with live district knowledge |
| `/readiness` | KG | 3 of 4 cards live (45 skills, 30 certifications, 25 providers) |
| `/manufacturing` | KG | 3 of 4 cards live (45 opportunities, 69 machinery, 21 raw materials) |
| `/scale` | KG | 3 of 4 cards live (29 export destinations, 11 markets, 21 capital sources) |
| `/network` | KG · APP | 2 of 4 cards live (marketplace, 66 institutions) |
| `/ai` | KG | 2 cards live (graph, rule engine); 4 advisors stay unavailable, deliberately |
| `/dashboard` | KG · UI · APP | Recommendation cards gained the fifth required element — supporting entities as links |
| `/ideas/<slug>` | KG · ED | **Resolved** skills and districts now rendered as links; previously only failures showed |
| `/opportunity-radar` | ED | Methodology disclosure: fit/demand are editorial, not measured |
| `/opportunity-radar/<segment>` | ED | Same disclosure, next to the `/100` badges |

---

## 2 · Public routes already live, unchanged (5)

Wired in Step 2 or 3, reviewed and correct.

| Route | Sources | Why unchanged |
|---|---|---|
| `/district/<slug>` | KG · ED | Editorial profile + `DistrictIntelligencePanel`. The pattern `/districts/<slug>` was rebuilt to match. |
| `/connections` | KG · UI · APP | Reads both projections already. |
| `/profile` | UI · APP | Intelligence panel with per-score `UNAVAILABLE` handling. |
| `/skills`, `/schemes` (+ details) | CMS · FB | `withGraphFallback()` already serves 45 skills and 40 schemes when the CMS is empty, which it is until an admin publishes. Backlog A1, closed in Step 3. |

---

## 3 · Public routes reading application data only (18)

Real Supabase tables and real user content. Not knowledge surfaces, correctly
untouched: `/explore` · `/opportunities/new` · `/opportunities/<id>` ·
`/opportunities/<id>/<district>` · `/collaborators` · `/collaborators/<sector>` ·
`/network/collaborators` · `/questions` · `/questions/<id>` · `/notifications` ·
`/onboarding` · `/signin` · `/get-started` · `/discover` · `/profile/<id>` ·
`/district-opportunity-index` · `/business-ideas/<district>` · `/ideas`

`/discover` is 1,024 lines of assessment flow writing to `collaborator_profiles`.
It contains no placeholder and no mock knowledge.

---

## 4 · Public routes with no knowledge dimension (8)

`/about` · `/privacy` · `/terms` · `/research` · `/research/<slug>` ·
`/resources` · `/resources/<slug>` · `/roadmaps` · `/roadmaps/<slug>`

Static content and MDX articles. `/resources` and `/roadmaps` read `public.kg_*`
CMS tables, which have no researched counterpart — there is no "resource" or
"roadmap" entity type in any package, so `kg-fallback.js` correctly does not
cover them. Recorded in `REMAINING_DEPENDENCIES.md` §3.

---

## 5 · Admin routes (31)

Excluded from this step by scope. They are operator tooling behind
`lib/admin.js`, and the brief is about what a user meets. `tests/
test_frontend_activation.py` excludes `admin/` from its placeholder scan for the
same reason — holding a CMS editor to a product's placeholder rules produces
noise, not signal.

> ⚠️ Unrelated but still open: `lib/admin.js:10` returns `isAdmin: true`
> unconditionally when `NODE_ENV === "development"`. Backlog S1, carried from the
> v1.0 readiness assessment.

---

## 6 · Verification

### Build

```
✓ Generating static pages (214/214)
exit 0 · 0 prerender errors
```

Run four times during this step — after the empty states, after the module
dashboards, after the district rebuild, and after the radar disclosures. Green
each time. **The build succeeds without database access**, which is the property
that lets these pages ship before the projection is deployed.

### Tests

```
frontend_activation          33     0    0     0   0.08  PASS
frontend_integration         59     0    0     0   0.11  PASS
------------------------------------------------------------------------
TOTAL                       563     0    0     0   4.67  PASS
```

**563 across 15 suites**, up from 530. Two Step-2 tests were rewritten rather
than deleted, because this brief reverses what they asserted — see
`USER_EXPERIENCE_COMPLETION.md` §4.

### What was not verified

**No page was loaded in a browser against a live database.** The `knowledge` and
`user_intelligence` schemas are not deployed to any environment reachable from
here, so every knowledge surface in this repository currently renders its
`NOT_DEPLOYED` state. The build proves each page renders; it does not prove each
page renders *populated*.

That is the honest limit of this step, and it is the same limit
`POST_DEPLOYMENT_VALIDATION.md` was written for: nine surfaces, checked by a
person in a browser, after `scripts/verify_deployment.sh` passes.

---

**Companions:** `PLACEHOLDER_REMOVAL_REPORT.md` · `KNOWLEDGE_BINDING_REPORT.md` ·
`REMAINING_DEPENDENCIES.md` · `USER_EXPERIENCE_COMPLETION.md`

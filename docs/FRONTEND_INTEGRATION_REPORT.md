# Frontend Integration Report — Platform v3.0, Step 2

**End-to-end integration of the knowledge platform into the existing Next.js
application.** Eight phases, 11 new components, 6 files touched,
**+361 / −7** lines.

Verified by `next build`: **exit 0, 213/213 static pages, 0 prerender errors.**

---

## 1. The architectural question, and the answer

The engines are **Python**. The frontend is **JavaScript** and makes **zero
`fetch()` calls** — every read is `supabase.from(...)`. There was no API client, no
error-boundary convention and no deployment target for a Python service.

Three ways to bridge that, and only one that respects "do not build new backend
architecture":

| Option | Verdict |
|---|---|
| Port the engines to JavaScript | **No.** Duplicates 23 scoring rules and 21 recommendation rules into a second language that would immediately drift. |
| Deploy the Python API and `fetch()` it | **No.** A service, a deployment, an auth layer, a CORS surface and a new failure mode — all at once, in a codebase with none of them. |
| **Engines write Supabase; frontend reads it** | **Yes.** Uses the client the app already has. Exactly what Step 1 and Step 1.5 were built for. |

```
packages/ + knowledge_graph/      Git — source of truth
        │  knowledge_sync (Step 1)
        ▼
Supabase `knowledge` schema        8 tables, 1,812 rows
        │
        │  user_intelligence engine (Step 1.5)
        ▼
Supabase `user_intelligence`      5 tables
        │  supabase.from(...) — the pattern already in use
        ▼
Next.js pages                     no new dependency, no new failure mode
```

**Net new runtime dependencies: zero.** A test asserts `package.json` is unchanged.

---

## 2. What was added

### Two data-access modules

| File | Reads | Contract |
|---|---|---|
| `lib/knowledge.js` | `knowledge` schema | Returns `[]`/`null` on any failure, never throws |
| `lib/intelligence.js` | `user_intelligence` schema | Same, plus `intelligenceState()` distinguishing `NOT_DEPLOYED` from `NOT_COMPUTED` |

Both deliberately mirror the existing `lib/knowledge-graph.js`: same anon-client
pattern, same silent-failure contract, same naming. An engineer who knows that file
recognises these.

### 11 components, all in `components/knowledge/`

| Component | Purpose |
|---|---|
| `BusinessKnowledgeSection` | Packages 004/006/007/008 for one idea |
| `ConfidenceBadge` | 0–100 with the caveat in a tooltip; renders `editorial` for unsourced content |
| `DistrictIntelligencePanel` | Six sections of district knowledge |
| `IntelligencePanel` | The profile block: five scores, skill profile, roadmap |
| `KnowledgeCard` | One row, carrying both provenance and confidence |
| `KnowledgeCardGrid` | The grid, and the three empty states that must not look alike |
| `ProvenanceLine` | `package · dataset · row_id` |
| `RecommendationRail` | One dashboard rail, always showing *why* |
| `ScoreCard` | One score; never renders `UNAVAILABLE` as zero |
| `SkillGapPanel` | Have / need / **no researched data** |
| `UnverifiedNotice` | The no-human-review disclosure, **computed** so it self-removes |

Every one uses the app's existing Tailwind tokens (`card-base`, `chip`, `bg-cream`,
`text-ink`, `text-muted`) and `lucide-react`. **No new colour, font or dependency.**

---

## 3. Additive, verified

| File | Added | Removed |
|---|---:|---:|
| `app/connections/page.js` | +93 | −2 |
| `app/dashboard/page.js` | +103 | −0 |
| `app/district/[slug]/page.js` | +41 | −1 |
| `app/ideas/[slug]/page.js` | +10 | −1 |
| `app/profile/page.js` | +30 | −0 |
| `components/platform/KnowledgeSearch.jsx` | +84 | −3 |
| **Total** | **+361** | **−7** |

All 7 removed lines are ones replaced by a superset:

| Removed | Replaced with |
|---|---|
| 2× `connections` select | the same select plus `skills` on both profile joins |
| `export default function DistrictPage` | `export default async function DistrictPage` |
| `<RequestContentWidget` | unchanged, moved below the new panel |
| `import { useMemo, useState }` | `useMemo, useState, useEffect` |
| 2 copy strings in `KnowledgeSearch` | updated placeholder and description |

**No component, export, query, `data-testid` or user-visible feature was removed.**
`tests/test_frontend_integration.py::AdditiveTest` enforces all of it, including a
ceiling on removed lines per file.

---

## 4. The three empty states

The single most likely way this integration disappoints users is by rendering one
blank panel for three different situations:

| State | Means | Rendered as |
|---|---|---|
| `NO_DATA_SOURCE` | We have nothing here, and know why | *"We don't have this data yet"* + the reason |
| `NO_MATCHES` | We looked; nothing matched you | *"Nothing scored above the match floor"* |
| `NOT_COMPUTED` | Nobody has run the analysis | *"We have not analysed your profile yet"* |
| `NOT_DEPLOYED` | The projection is not switched on | *"Not switched on for this deployment"* |

`KnowledgeCardGrid` owns this distinction so no page has to re-derive it. A blank
div reads as a bug; a sentence reads as honesty.

---

## 5. What is on screen today, and what changes when the migrations run

**The migrations are not applied.** No database access exists in this environment,
so `knowledge` and `user_intelligence` do not exist anywhere yet.

| Surface | Today | After the migrations + sync |
|---|---|---|
| Dashboard | Existing feed, plus *"Personalised recommendations are not switched on yet"* | Four rails with reasons and provenance |
| Profile | Existing profile | Five scores, skill profile, learning roadmap |
| District | Existing editorial profile, plus a stated collection gap | Six sections of researched entities |
| Search | Existing static search, unchanged | Plus a researched-entity group |
| Idea detail | Existing detail, plus *"no researched counterpart yet"* | Comparable businesses and supporting schemes |
| Connections | Existing list, plus skill complementarity **(works today)** | Plus engine-ranked suggestions |

Skill complementarity on `/connections` works **now**, because it compares two
`profiles.skills` arrays and needs no projection. It is the one feature in this step
that is live on merge.

---

## 6. The contract between two languages

Nothing in `next build` catches a Python↔JS disagreement, and a disagreement is
silent: a renamed column makes a query return nothing and the page renders its empty
state as though the user had no data.

`tests/test_frontend_integration.py::ContractTest` is that missing check — 11 tests
asserting schema names, table names, `RULES_VERSION` (`1.0.0`), status
enums and the `NO_DATA_SOURCE` sentinel all agree.

The sharpest one **executes both implementations**:

```
test_javascript_normalisation_matches_python
```

It runs `normaliseTerm()` under Node and `KnowledgeSnapshot.normalise()` in Python
over eight adversarial cases — `&` folding, accents, parentheticals, hyphens — and
requires identical output. The Step 0 crosswalk join depends on it entirely; a
divergence would make every free-text skill lookup miss, and the page would look
merely empty.

---

## 7. Honest limits

| Limit | Detail |
|---|---|
| **Not run against a live Supabase** | Verified by `next build` and 39 structural tests. No page has rendered real projected data. |
| Migrations not applied | Three now written and unapplied: `009` (crosswalk), `010` (missing features), plus the two schema migrations from Steps 1 and 1.5. |
| **Non-`public` schemas need exposing** | Supabase only serves schemas listed in *API → Exposed schemas*. `knowledge` and `user_intelligence` must be added there, or every read returns nothing. This is the most likely cause of a silent blank after deployment. |
| 22.8% skill resolve rate | Step 0's ceiling. Skill-driven rails will be thin for most users; the UI says so rather than showing a blank. |
| `next@14.2.15` has a published advisory | Pre-existing. Upgrading is a framework change, not an integration, and is out of scope here — but it should be scheduled. |
| No E2E test | The app has no Playwright or Cypress setup. Adding one is a larger commitment than this step. |

---

## 8. Companion reports

| Report | Contents |
|---|---|
| `PAGE_STATUS_REPORT.md` | All 79 routes, and what changed on each |
| `API_BINDING_REPORT.md` | Every query, its table and its degradation path |
| `MISSING_FEATURES.md` | The four absent features, and what each blocks |
| `SUPABASE_EXTENSION_PLAN.md` | Migrations, deployment order, RLS |
| `IMPLEMENTATION_LOG.md` | What was done, in order, with verification |

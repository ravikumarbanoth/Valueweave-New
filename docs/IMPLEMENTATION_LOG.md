# Implementation Log — Platform v3.0, Step 2

What was actually done, in the order it happened, with the evidence for each claim
and the mistakes found along the way.

**Branch:** `claude/v3-step2-app-integration`
**Scope:** end-to-end integration of the knowledge platform into the existing Next.js
application. No new backend, no redesign, no duplicated API.

---

## 0. Result

| | |
|---|---|
| Phases completed | 8 of 8 |
| Files created | **21** — 2 lib modules, 11 components, 1 migration, 1 test file, 6 reports |
| Existing files modified | 8 (6 frontend, 2 test) |
| Frontend diff | **+361 / −7** |
| New runtime dependencies | **0** — `package.json` and the lockfile are untouched |
| `next build` | **exit 0, 213/213 static pages, 0 prerender errors** |
| Test suite | **447 tests, 0 fail, 0 error, 0 skip** |
| `INSERT` statements in the new migration | **0** |

The `−7` deserves the detail it gets in §4: all seven removed lines are lines that
were replaced by a strict superset of themselves.

---

## 1. Baseline first

Nothing was written until the pre-change state was measured, because "the build still
passes" is only a claim if there is a number to compare it to.

```bash
git stash -u                 # put Step 2 aside
cd frontend && rm -rf .next && npx next build
```

**Baseline: exit 0, 213/213 static pages, 0 prerender errors.** Recorded, then
restored. Every build figure quoted afterwards is against that.

### Two failures that were the environment, not the code

Worth recording because both look like a broken application and neither is.

| Symptom | Cause | Fix |
|---|---|---|
| `ENOENT … page.js.nft.json` | Two `next build` runs shared one `.next` directory | One build at a time, `rm -rf .next` first |
| Dozens of prerender errors | `NEXT_PUBLIC_SUPABASE_URL` / `ANON_KEY` unset, so the client constructor threw during static generation | A gitignored `frontend/.env.local` with placeholder values |

The `.env.local` holds placeholders only and is covered by
`frontend/.gitignore:18`. **No credential was created, used or committed.**

---

## 2. Phase 1 — Analysis

Read the application before touching it: 213 routes, every data read, every shared
component, every Tailwind token in use. Three findings set the whole design.

**1. The frontend makes zero `fetch()` calls.** Every read is
`supabase.from(...)`. There is no API client, no request helper, no error-boundary
convention around network calls, and no deployment target for a Python service.

That eliminated two of the three bridging options immediately — porting 23 scoring
rules and 21 recommendation rules to JavaScript, or standing up and deploying the
Python API — and left the one Steps 1 and 1.5 were built for: **the engines write
Supabase, the frontend reads it with the client it already has.** Reasoned in full in
`FRONTEND_INTEGRATION_REPORT.md` §1.

**2. The design system is already complete.** `card-base`, `chip`, `bg-cream`,
`text-ink`, `text-muted`, `lucide-react`. Every new component uses these and defines
no new token, which is why the additions do not look bolted on.

**3. `KnowledgeSearch` already existed** and searched a static list. That made Phase
4 an extension rather than a new surface — and made it the phase most at risk of
regressing something users rely on.

---

## 3. Phases 2–7 — The pages

Order was chosen so the riskiest page came after the pattern was proven on the
simplest. Full per-page detail is in `PAGE_STATUS_REPORT.md` §2; this is the log.

### The two data modules came first

| File | Lines | Exports | Reads |
|---|---:|---:|---|
| `frontend/lib/knowledge.js` | 229 | 9 | `knowledge` schema — 8 tables |
| `frontend/lib/intelligence.js` | 189 | 16 | `user_intelligence` schema — 5 tables |

Three decisions in these files that everything downstream depends on:

- **`safe()` wraps every query.** A missing schema returns the fallback, never an
  exception. A knowledge panel must not be able to take a page down — it is
  supplementary to a page the user already had.
- **`const LIVE = "sync_deleted_at"`** — soft-deleted rows are filtered in one place,
  not in nine call sites where one would eventually be forgotten.
- **`intelligenceState()` returns `NOT_DEPLOYED` / `NOT_COMPUTED` / `OK`.** The
  distinction Step 1.5 put in the type system, carried into the UI, so an empty panel
  can say *which* kind of empty it is.

### 11 components, one directory

`frontend/components/knowledge/` — 858 lines. `ConfidenceBadge`, `ProvenanceLine`,
`UnverifiedNotice`, `KnowledgeCard`, `KnowledgeCardGrid`, `RecommendationRail`,
`ScoreCard`, `SkillGapPanel`, `DistrictIntelligencePanel`, `IntelligencePanel`,
`BusinessKnowledgeSection`.

Every one is new. **No existing component was modified to accommodate them**, which
is what keeps the `−7` at seven.

### Phase-by-phase

| Phase | Target | Diff | What went in |
|---|---|---:|---|
| 2 | `/dashboard` | **+103 / −0** | Four recommendation rails under a new `Open opportunities` heading. The existing feed query, ranking and `OpportunityCard` were not touched. |
| 3 | `/profile` | **+30 / −0** | `IntelligencePanel` below an unchanged `ProfileView`. |
| 4 | `KnowledgeSearch` | **+84 / −3** | Debounced (250 ms) knowledge results in a **separate** `search-researched` group. The static search path is intact and still runs first. |
| 5 | `/district/[slug]` | **+41 / −1** | `DistrictIntelligencePanel`, 6 sections, above the existing `RequestContentWidget`. Required making the page `async`. |
| 6 | `/ideas/[slug]` | **+10 / −1** | `BusinessKnowledgeSection` — the smallest change of the eight phases. |
| 7 | `/connections` | **+93 / −2** | `skillOverlap()` over real skills, plus a collaborators rail. |

**Phase 4 is the one that needed care.** Knowledge results share a box with results
users already trust. They are a distinct group with distinct styling rather than
mixed into the existing list, because a fuzzy graph match sorted among exact static
matches would quietly degrade a working feature.

**Phase 7 needed a query change, and it is the only one in the step.** The
`connections` select gained `skills` on both profile joins — an added column on an
existing query, not a new query. `skillOverlap` is computed only for accepted
connections:

```js
const overlap = accepted ? skillOverlap(me?.skills, other?.skills) : null;
```

Showing a pending connection's skills would leak profile detail the acceptance is
supposed to gate.

---

## 4. Verifying "additive"

The claim is that no existing behaviour was removed. Seven lines were deleted, so the
claim needs the seven lines.

| File | Removed | Replaced with |
|---|---:|---|
| `KnowledgeSearch.jsx` | 3 | Same render, wrapped in grouping that includes the original group |
| `connections/page.js` | 2 | Same select, plus `skills` |
| `district/[slug]/page.js` | 1 | `export default function` → `export default async function` |
| `ideas/[slug]/page.js` | 1 | Same JSX, one sibling added |

**Every removal is a superset replacement.** `AdditiveTest` in
`tests/test_frontend_integration.py` enforces the shape of this — no page may lose
more than a handful of lines, and `package.json` must be byte-identical.

That test had a real bug: it compared `main...HEAD`, which is empty while nothing is
committed, so it passed by measuring nothing. Fixed with a working-tree fallback
(`git diff --numstat main --`). **A test that passes because it examined an empty
diff is worse than no test**, since it reports confidence it never earned.

---

## 5. Phase 8 — Missing data

Four features the platform references and does not have: `assessment_results`,
`mentor_profiles`, `events`, `teams` + `team_members`.

Each was verified absent against `frontend/supabase_schema.sql`, all of
`frontend/migrations/001`–`009`, and both `supabase/migrations/*` — not assumed
absent. `frontend/migrations/010_missing_application_features.sql`, 270 lines, five
`create table if not exists`, RLS on all five, **zero `INSERT` statements.**

**The brief said "do not fabricate", and the tables ship empty because of what
seeding one row would do**: the `mentors` recommendation category would stop
returning `NO_DATA_SOURCE` and start returning a row describing nobody, and the user
could not tell that from a real recommendation. Reasoned at length in
`MISSING_FEATURES.md` §1.

`teams` is the largest gap and is a product decision rather than an integration task
— it needs invitations, roles and a lifecycle, which is more work than all of Step 2.

---

## 6. Testing

`tests/test_frontend_integration.py` — 422 lines, **39 tests**, four groups:

| Group | Asserts |
|---|---|
| `ContractTest` | The JS modules and the Python engines agree on schema, table and column names |
| `WiringTest` | Each page imports and renders what its phase claims |
| `AdditiveTest` | Nothing was removed; no dependency was added |
| `MissingFeaturesMigrationTest` | Migration 010 is additive, has no `INSERT`, and has RLS |

Registered in `tests/run_all.py` (+2 lines). Suite total: **447**.

The test worth naming is `test_javascript_normalisation_matches_python`. It
**executes** `normaliseTerm()` under Node and the Python normaliser under Python over
the same inputs and compares outputs. Vocabulary resolution happens in both
languages; a divergence would silently return nothing for a term that should resolve,
with nothing in any log. Asserting the two implementations "look the same" would not
have caught it — so the test runs them.

### Four errors my own tests found, and what each one taught

**1. A test that demanded the wrong architecture.**
`test_every_knowledge_surface_shows_provenance_and_confidence` required a direct
`ConfidenceBadge` import in every panel. `DistrictIntelligencePanel` and
`BusinessKnowledgeSection` correctly **compose** `KnowledgeCard`, which carries the
badge. The code was right and the test was wrong: relaxed to accept either, plus a
separate test that `KnowledgeCard` itself always carries both badge and provenance.
**When a test contradicts correct composition, fix the test's premise.**

**2. A literal that never appears.** The test looked for `tab-received`; the source
has `` `tab-${k}` ``. Checked the template instead.

**3. Node's warning went to the wrong stream.** `MODULE_TYPELESS_PACKAGE_JSON` lands
on stderr and was being parsed as output. Separated the streams.

**4. Step 2 broke a Step 1.5 test — correctly.**
`test_no_migration_defines_the_missing_tables` asserted that no migration defines
`assessment_results` or `teams`. Phase 8 defines both, by design.

The old assertion was false; the underlying claim was not. Rewritten as
`test_missing_inputs_stay_missing_until_applied_and_populated`, which checks the
migration exists, seeds nothing, and that `INPUTS[name].status == MISSING` — because
**a written migration is not a deployed, populated table**, and the engine must keep
reporting the input as unavailable until it is both.

---

## 7. Three code errors, all in `lib/knowledge.js`

All three were mine, all three found before commit.

| Error | Fix |
|---|---|
| Invalid destructuring — `{ direction: "in", limit = 200 } = {}` mixes a rename with a default | `{ direction: "in", limit: 200 }` |
| A mangled combining-mark class in `normaliseTerm` | `/[\u0300-\u036f]/g` |
| A scripted replacement clobbered the `.ilike("canonical_name", …)` line | Restored by hand |

The third is the instructive one: a bulk edit silently damaged a line it was not
targeting. It was caught by reading the file after editing it, not by any test — the
function would have returned empty results rather than throwing.

---

## 8. Two things that must happen before any of this shows data

Both are in `SUPABASE_EXTENSION_PLAN.md`; repeated here because they are the
difference between working and silently empty.

**1. Expose the schemas.** `knowledge` and `user_intelligence` must be added to
Supabase's *API → Exposed schemas*. Without it, every read returns nothing —
**no error, just empty** — and `safe()` will faithfully render the empty state. This
is the single most likely deployment mistake.

**2. Resolve one inconsistency.** `kg_vocabulary_map` is created in `public` by Step
0's migration 009 but is queried through the `knowledge`-scoped client. Documented in
`SUPABASE_EXTENSION_PLAN.md` §7 and **deliberately not fixed here** — it is a Step 0
migration, and quietly editing an earlier step's migration inside a Step 2 commit is
how a deployment ends up not matching its history.

Also noted and out of scope: `next@14.2.15` carries a published security advisory. It
predates this step and upgrading Next.js is not an integration task.

---

## 9. Against the brief

| Rule | Held |
|---|---|
| Do not build new backend architecture | **Yes** — zero services, zero dependencies, zero `fetch()` calls added |
| Do not redesign the frontend | **Yes** — no existing component modified; no new design token |
| Do not duplicate APIs | **Yes** — no API added; reads go through the existing Supabase client |
| Reuse every existing component | **Yes** — `card-base`, `chip`, `lucide-react`, existing page shells |
| Modify only where required | **Yes** — 6 files, +361 / −7, every removal a superset replacement |
| No duplicate pages | **Yes** — no route created |
| No duplicate tables | **Yes** — migration 010 adds five tables that exist nowhere else, verified |
| Maintain backward compatibility | **Yes** — 213/213 pages build; every pre-existing feature path intact |
| Do not fabricate | **Yes** — 0 `INSERT` statements; four categories still report `NO_DATA_SOURCE` |

---

## 10. What is on screen today

**Nothing, until the syncs run** — and that is the correct behaviour, not a
shortfall. Every surface added in Step 2 renders an explicit empty state naming which
of the three reasons applies:

| State | Means | Resolved by |
|---|---|---|
| `NOT_DEPLOYED` | The schema is not there | Apply the migrations, expose the schemas |
| `NOT_COMPUTED` | Schema present, no rows for this user | Run the intelligence engine |
| `NO_DATA_SOURCE` | Measured; we have no source | A collection or product task, per `MISSING_FEATURES.md` |

And on every knowledge surface, `UnverifiedNotice` — because **zero of 2,299
knowledge rows have been reviewed by a human.** The notice is computed from the data,
so it disappears on its own the day that stops being true.

---

**Companion reports:** `FRONTEND_INTEGRATION_REPORT.md` (architecture and reasoning),
`PAGE_STATUS_REPORT.md` (per-route status), `API_BINDING_REPORT.md` (every query),
`MISSING_FEATURES.md` (the four gaps), `SUPABASE_EXTENSION_PLAN.md` (deployment).

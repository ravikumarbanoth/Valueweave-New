# ValueWeave — Version 1.0 Product Backlog

**53 items · 58–75 days · Critical path to pilot: 10–13 days**

Derived from `VERSION1_READINESS_REPORT.md`. Every item traces to a measured finding,
not a preference. Effort is one competent person, working days.

Priority means:

| | Meaning |
|---|---|
| **Critical** | The pilot cannot run, or would mislead a user, without it |
| **High** | v1.0 is materially incomplete without it |
| **Medium** | Needed for a general launch, not for the pilot |
| **Low** | Cleanup, or genuinely deferrable |

---

## Critical — 12 items, 10–13 days

### Deployment (D) — 1–2 days total

| ID | Task | Effort | Evidence |
|---|---|---|---|
| **D1** | Apply all 5 migration sets in documented order | 2 h | 50 tables across 3 directories, no single runbook until now |
| **D2** | Add `knowledge` + `user_intelligence` to Supabase *API → Exposed schemas* | 15 m | Omission makes every read return empty **with no error** |
| **D3** | `knowledge_sync sync --full --target supabase`, then re-run to prove idempotency | 2 h | `knowledge_sync/state/` has no manifest — never run |
| **D4** | Run the intelligence engine per user; write its 5 tables | 3 h | All 5 `user_intelligence` tables empty |
| **D5** | Configure Google OAuth redirect URIs | 30 m | Journey stage 1 blocked without it |
| **D6** | Set `ADMIN_EMAILS`; promote first `profiles.is_admin` | 30 m | Otherwise no admin can reach 33 admin routes |
| **D7** | Fix `kg_vocabulary_map`: created in `public` (migration 009), queried via the `knowledge` client | 2 h | Vocabulary resolution silently returns nothing |

D3 must be rehearsed. Nothing has ever run against real Postgres —
`OPERATIONS_GUIDE.md` §2 step 7 is the check that matters: a second consecutive sync
must report **0 inserted, 0 updated**.

### Knowledge (K) — 8–10 days

| ID | Task | Effort | Evidence |
|---|---|---|---|
| **K5** | **Complete Package006** — write `VERSION`, `README.md`, `CHANGELOG.md`, `package_manifest.json`, `validate.py`; populate the empty `metadata/` and `registry/`; delete the `Package006_Skills/` duplicate | 1 d | Missing 5 files that every other package has; `metadata/` and `registry/` are **empty directories**. Commit `9393f00` claims "v1.0.0 to Stable"; the artefacts were never written (open tasks #38–40) |
| **K1** | Collect ~40 backlog skills **with edges to businesses/districts** | 3–4 d | Onboarding resolve rate **22.8%** (13 of 57). The backlog is the audience's real skills: Accounting, Data Entry, Digital Marketing, Sales, Teaching, Graphic Design, GST Filing, Retail Management |
| **K2** | Human-review the 40 highest-leverage entities | 2 d | **0 of 2,299 rows reviewed.** Those 40 cover 37.2% of edge endpoints (`audit/reports/DATA_STEWARDSHIP.md`) |
| **K3** | Connect the 21 orphan government schemes | 2 d | GovernmentScheme: 40 entities, **19 connected (47.5%), median degree 0.** All 21 rules are traversals, so an orphan is unrecommendable |

**K1 is the highest-leverage item in the entire backlog** — the difference between a
student seeing 1 of 10 categories and seeing 4–5.

**K5 must precede K1, and that is why it moved out of High.** K1 writes new skills
*into Package006*, and Package006 currently has no `validate.py` and no manifest — so
K1's output could not be validated the way every other package's is. Doing K1 first
means collecting 40 skills into the one package with no quality harness.

### Honesty (H) — 0.5 days

| ID | Task | Effort | Evidence |
|---|---|---|---|
| **H1** | Label the 500 seeded opportunities as illustrative, or remove them | 4 h | `003_seed_opportunities.sql`, `created_by='system_seed'`, template-generated, **no provenance**, on the first screen a user sees. The platform's rule is *never fabricate*; this is the one place it is not held |

Either action is acceptable. Leaving them unlabelled is not — they are
indistinguishable from the 40 researched MSMEs that carry full provenance.

---

## High — 13 items, 14–18 days

### Knowledge

| ID | Task | Effort | Evidence |
|---|---|---|---|
| K4 | Register Package003_Healthcare entity types in `build_graph.py` | 1 d | **146 rows → 0 entities, 0 edges.** Stable v1.0.0 and completely invisible |
| K6 | Deepen the 12 pilot districts past median degree 1 | 3 d | 45 of 61 districts score <30; **median 0** |
| K7 | Connect 30 certifications + 22 training providers | 2 d | Certification **0% connected**; TrainingProvider **12%** |

### Application

| ID | Task | Effort | Evidence |
|---|---|---|---|
| A1 | **Resolve the two-knowledge-system collision.** Point `/schemes` `/skills` `/resources` `/roadmaps` at `knowledge.*`, or retire them | 3 d | `public.kg_*` (admin CMS, empty, no writer) vs `knowledge.kg_*` (1,812 rows, provenance). Colliding names, contradictory answers |
| A2 | Unify the four district lists behind Package001's 61 | 2 d | 61 (package) / 19 (idea-library) / **14 (`districts-data.js`)** / 22 (seeds). `/district/[slug]` covers **23%** of districts |
| A3 | Persist the assessment by default | 1 d | `/discover` (1,024 lines) saves only via opt-in inside a secondary tab, requires sign-in, and the route is not auth-gated — anonymous users lose their result |
| A4 | Wire assessment output into the engine as `assessment_results` | 2 d | `INPUTS["assessment_results"] = MISSING` while a working assessment already computes archetype and `ep_score` |

### Platform

| ID | Task | Effort | Evidence |
|---|---|---|---|
| S1 | Gate the admin dev-bypass on an explicit variable, not `NODE_ENV` | 2 h | `lib/admin.js:10` returns `isAdmin: true` unconditionally in development — 33 admin routes |
| S2 | Restrict `images.remotePatterns` from `hostname: "**"` | 1 h | Open image proxy: bandwidth abuse, internal-endpoint probing |
| S3 | Fix `kg_roadmap_steps` / `kg_relationships` `using (true)` read policies | 2 h | Parent gated on `status='published'`; children readable unconditionally — draft content leak |
| O1 | Add CI: 447 tests + `next build` + `generate_migration.py --check` | 1 d | **No `.github/workflows/` at all** |
| O2 | Write `.env.example` | 1 h | Four required variables discoverable only by reading source; two fail *silently* |
| O3 | Add `frontend/migrations/README.md` explaining the missing 008 | 1 h | Sequence runs 001–007, 009, 010. Intentional (superseded by the `knowledge` schema) but reads as a lost file |

---

## Medium — 16 items, 20–26 days

### Features

| ID | Task | Effort | Note |
|---|---|---|---|
| F1 | **Teams**: route, invitations, roles, lifecycle | 8 d | Tables exist (migration 010, empty). Journey stage 8 is **BLOCKED**. A product, not an integration |
| F2 | **Startup Workspace** | 6 d | **Does not exist in any form.** No table, route, or placeholder. Journey stage 9 |
| F3 | `/admin/stewardship` review UI | 3 d | Review is Python-CLI-only; K2 will not scale without it |
| F4 | Mentor opt-in flow | 2 d | `mentor_profiles` empty; 1 of 10 categories permanently `NO_DATA_SOURCE` |
| F5 | Events collection (scheme deadlines) | 2 d | The one gap with a plausible external source — scheme portals publish deadlines |

### Knowledge

| ID | Task | Effort | Note |
|---|---|---|---|
| K8 | Verify AP's 28 districts against the 26 notified in April 2022 | 2 h | Markapuram and Polavaram appear to be proposals, not notified districts |
| K10 | Raise sector resolve above 50% (6 backlog sectors) | 2 d | Beauty & Wellness, Climate Tech, Drone Tech, Events, Repair Economy, Sports & Fitness |
| K11 | Reduce `PENDING_VERIFICATION` below 3% of cells | 4 d | Currently **2,456 cells (6.02%)** |
| K12 | Resolve 272 `PENDING_GEOCODING` cells | 2 d | 136 latitude + 136 longitude |
| K13 | Expand district onboarding vocabulary past 19 distinct entities | 2 d | 33 terms resolve, but to only 19 of 61 districts |

### Performance

| ID | Task | Effort | Note |
|---|---|---|---|
| P1 | Add `pg_trgm` + GIN index for `canonical_name` | 4 h | `.ilike("%q%")` cannot use the existing btree. `pg_trgm` appears in **no** migration — it was scoped to the abandoned 008 |
| P2 | Cache dashboard/profile reads | 1 d | Client components refetch on every mount |
| P3 | Collapse `/ideas/[slug]` N+1 scheme queries into a view | 1 d | ~9 queries; 1 per matched business |
| P4 | Index `user_intelligence` profile tables | 2 h | **4 indexes across 5 tables**; 3 have nothing beyond their PK |

### Platform

| ID | Task | Effort | Note |
|---|---|---|---|
| O4 | Upgrade `next@14.2.15` (published advisory) | 1 d | Pre-existing; needs a full regression pass |
| O5 | Decide the Python API's fate: deploy it or document it as internal | 2 d | 10 endpoints, 29 tests, **no deployment target**. Same for the 27-test search engine, which the frontend does not use |

---

## Low — 12 items, 14–18 days

| ID | Task | Effort | Note |
|---|---|---|---|
| L1 | Delete `backend/` (412 lines, FastAPI + MongoDB + `emergentagent` OAuth) | 2 h | Referenced by nothing. Recommended for deletion in v3.0 planning and still present. Pulls in `motor`, `pymongo`, `emergentintegrations` |
| L2 | Build or retire the 7 `ModuleShell` placeholders | 5 d | `/ai` `/manufacturing` `/readiness` `/scale` `/network` `/districts` `/districts/[slug]`. They say so honestly, which buys time but not indefinitely |
| L3 | `/readiness` is the natural home of the assessment — decide | 1 d | Currently a shell; journey stage 3 has no obvious route |
| L4 | Collect `mandal.csv` (0 rows) + AP revenue divisions (0 rows) | 2 d | TG revenue divisions has 75; AP has none |
| L5 | Migrate `lib/static-knowledge.js` (56 paths) to the graph | 2 d | A third knowledge surface at `/knowledge/[type]/[slug]` |
| L6 | Migrate the 122 editorial ideas into a package with provenance | 3 d | The most-shown recommendation category runs at **confidence 0** |
| L7 | Consolidate `/district` and `/districts` | 1 d | Two route trees for one concept |
| L8 | Consolidate `/network` and `/connections` | 4 h | `/network` is a shell |
| L9 | Retire or wire the 9 `public.kg_*` CMS tables | 2 d | Follows A1 |
| L10 | Deduplicate `/explore` / `/discover` / `/opportunity-radar` | 2 d | Three discovery surfaces |
| L11 | Reduce 25+ `force-dynamic` admin pages | 1 d | Every admin page view is fully uncached |
| L12 | Document `stewardship`, `query_engine`, `source_registry` as internal | 4 h | Zero frontend references; no deployment |

---

## Sequencing

### Week 1 — make it real (D1–D7, H1, S1–S3, O1–O3)

Deployment plus the three security defects plus honesty labelling. **Ends with a
platform that has data in it** and a CI that catches the next regression.

Parallel: **K5 on day 1** (it gates K1), then K1 and K2 — they are the schedule, and
they need a domain person rather than an engineer.

### Week 2 — make it useful (K5, K1, K2, K3 complete)

Skills collection, human review, orphan schemes. **Re-run the six-profile simulation
in `VERSION1_READINESS_REPORT.md` §0 as the gate.** Target: every profile fills ≥3 of
10 categories and no profile scores 0 on skills.

### Weeks 3–4 — pilot (see `PILOT_PLAN.md`)

Only K4–K7 and A1–A4 run during the pilot, and only if they do not disturb it.

### Post-pilot — v1.1

F1 (Teams) and F2 (Startup Workspace) are v1.1. They are 14 days of product work
between them and should be shaped by pilot feedback, not guessed at now.

---

## What the backlog deliberately does not contain

**A recommendation-engine calibration task.** The 23 scoring weights are documented as
*reasoned, not calibrated* — and nothing in the platform records whether a
recommendation was useful, so there is no outcome data to fit them to. The v2.1 audit
named this as the blocker and it is still true.

Adding "tune the weights" would be inventing work with no signal to do it against.
**The pilot's real deliverable is that signal** — which is why `PILOT_PLAN.md` makes
recommendation-outcome capture a launch requirement rather than an analytics nicety.

# Frontend Integration Plan — ValueWeave Platform v3.0

**Phase 1 deliverable.** Repository analysis and integration strategy.
**No application code was changed to produce this document.**

---

## 0. The finding that should change the plan

Before anything else, one measured result:

> **7 of the 57 skills the onboarding form suggests (12%) resolve to a Skill in the
> knowledge graph.** For the Idea Library the number is 9 of 46 (20%), and only 2 match
> by exact name. Of 22 idea sectors, 9 resolve to a graph `Industry`.

Every feature in the brief that connects a *user* to the *graph* — Recommended Skills,
Skill Gap Analysis, Recommended Collaborators, Business Match — runs through that join.
Built today, those features would return nothing for roughly nine users in ten, and the
failure would be silent: an empty panel, not an error.

This does not block integration. It reorders it. **Vocabulary reconciliation is Step 0,
not a detail inside Step 3.** The repository already has the right pattern for it — the
ADR-003 scheme crosswalk, where 79 domain rows were matched to 40 canonical schemes by
four named matchers that refuse rather than guess. The same technique applies here, and
§6 specifies it.

---

## 1. What exists — measured, not assumed

### 1.1 The frontend

| | |
|---|---|
| Framework | Next.js 14.2.15, App Router, JavaScript (no TypeScript) |
| Styling | TailwindCSS 3.4, custom design tokens (`cream`, `ink`, `muted`, `card-base`, `chip`) |
| Auth | Supabase Auth via `@supabase/ssr`, Google Sign-In, middleware-enforced |
| Routes | **79** `page.js` files |
| Components | **49** `.jsx` files across 7 directories |
| Lib modules | **22** under `frontend/lib/` |
| Dependencies | 11 runtime. No data-fetching library, no state manager, no UI kit |

**Route families**

| Family | Routes | Data source |
|---|---:|---|
| `/admin/*` | 30 | Supabase (analytics, CMS, ops) |
| Public knowledge (`/skills`, `/schemes`, `/resources`, `/roadmaps`, `/districts`) | 10 | `kg_*` Supabase tables |
| Static knowledge (`/knowledge/[type]/[slug]`, `/district/[slug]`) | 6 | JS/JSON files in the repo |
| Idea Library (`/ideas`, `/ideas/[slug]`) | 2 | `lib/idea-library/*.json` |
| Social graph (`/dashboard`, `/connections`, `/network`, `/collaborators`, `/profile`) | 8 | Supabase user tables |
| Marketing, legal, misc | 23 | static |

### 1.2 The data access pattern — and the one that is absent

```
$ grep -rn "fetch(" frontend/app frontend/components frontend/lib
(no matches)
```

**The frontend makes zero HTTP calls.** Every read is `supabase.from(...)`, either from a
browser client (`lib/supabase-browser.js`) or a server client (`lib/supabase-server.js`).
There is no `app/api/` directory, no route handler, no API client, no caching layer, no
error-boundary convention for a failed request.

This is the central architectural fact of the integration. The Knowledge Platform ships a
Python REST API (`api/`, 10 endpoints), and pointing the frontend at it would introduce a
new dependency, a new deployment target, a new failure mode and a new error-handling
convention **all at once, in a codebase that has none of them**. §4 rejects that as the
default path.

Environment surface is equally small — four variables:
`NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `NEXT_PUBLIC_BASE_URL`,
`ADMIN_EMAILS`.

### 1.3 Supabase schema

**30 tables across 9 migration files.**

| Group | Tables |
|---|---|
| Identity & social | `profiles`, `opportunities`, `connections`, `collaborator_profiles`, `opportunity_interests`, `founder_matches` |
| Content | `research_articles`, `questions`, `answers`, `announcements`, `subscriptions`, `weekly_digests`, `notifications`, `admin_notifications` |
| Analytics | `page_views`, `search_events`, `visitor_sessions`, `opportunity_views`, `user_feedback`, `user_requests`, `activity_log` |
| Ops | `platform_settings` |
| **Knowledge CMS** | `kg_district_profiles`, `kg_skills`, `kg_resources`, `kg_schemes`, `kg_roadmaps`, `kg_roadmap_steps`, `kg_industry_sectors`, `kg_collaborator_types`, `kg_relationships` |

RLS is enabled throughout. Admin is `profiles.is_admin`, with `public.is_valueweave_admin()`
as the policy predicate and an `ADMIN_EMAILS` env allowlist as bootstrap.

### 1.4 The Knowledge Platform

| | |
|---|---|
| Packages | 8 released, 77 datasets, **2,299 rows** |
| Graph | **647 entities**, **865 relationships**, 150 aliases, 19 entity types, 15 populated relationship types |
| Query engine | `query_engine/` — traversal primitives plus 5 named business questions |
| Search | `search/` — 1,747 documents, 4 match modes |
| API | `api/` — 10 read-only endpoints on stdlib `http.server` |
| Stewardship | `stewardship/` — 7-state lifecycle, ledger currently empty |
| Verification | **0 of 2,299 rows reviewed by a human** |

---

## 2. Three knowledge layers already exist

This is the problem to solve. It is not "the app has no knowledge" — it has three
incompatible sets of it, and a naive integration creates a fourth.

| # | Layer | Location | Volume | Authored by | Reaches users via |
|---|---|---|---:|---|---|
| **A** | Static knowledge | `frontend/data/*.json`, `lib/districts-data.js`, `lib/idea-library/` | 56 records + 14 districts + **122 ideas** | Hand-written, in Git | `/knowledge/*`, `/district/[slug]`, `/ideas` |
| **B** | Knowledge CMS | `kg_*` Supabase tables | **Seeded empty** | Admins, through `/admin/*` | `/skills`, `/schemes`, `/resources`, `/roadmaps`, `/districts` |
| **C** | Knowledge Platform | `packages/`, `knowledge_graph/` | 2,299 rows / 647 entities | Researched, provenance-complete, in Git | **nothing — no user-facing surface** |

### The immediate consequence

Layer B's migration says it plainly: *"No seed data: content is added gradually through
the admin dashboard."* So `/skills` and `/schemes` today render their `emptyText`:

> *"Schemes will appear here after admins publish them from the Government Scheme CMS."*

Meanwhile **Package007 holds 40 sourced government schemes and Package006 holds 45
skills**, sitting in Git with full provenance, invisible to every user.

**The single highest-value, lowest-risk integration in this entire project is to fill
Layer B from Layer C.** It requires no new page, no new component, no new API, no new
dependency, and no design change — `PublicEntityList` and `PublicEntityDetail` already
render those tables. It is a data-loading job.

That observation is what makes Step 1 of the roadmap a backfill rather than a search bar.

---

## 3. Overlap and conflict register

| Concern | Layer A | Layer B | Layer C | Resolution |
|---|---|---|---|---|
| Districts | 14 (`districts-data.js`) + 1 (`data/districts.json`) | `kg_district_profiles` (empty) | 61 `District` entities | **C is canonical for facts; A stays canonical for editorial narrative.** 12 of 14 join by name (§6). |
| Schemes | 6 (`data/schemes.json`) | `kg_schemes` (empty) | 40 `GovernmentScheme` | **C canonical.** Already settled by ADR-003. |
| Skills | 10 (`data/skills.json`) + 44 (idea-library groups) + 57 (onboarding) | `kg_skills` (empty) | 45 `Skill` | **C canonical, but see §0 — the vocabularies barely overlap.** |
| Industries/sectors | 8 (`data/industries.json`) + 22 idea sectors | `kg_industry_sectors` (empty) | 78 `Industry` | **C canonical**, needs a sector→Industry map. |
| Business ideas | 122 (`ideas.json`) | — | 45 `BusinessOpportunity` + 40 `MSME` | **Neither is canonical.** These are different things: ideas are editorial and inspirational, Package004/008 are researched and sourced. Link them; do not merge them. |
| Relationships | — | `kg_relationships` (generic, free-form) | 865 typed, provenance-carrying edges | **C canonical.** `kg_relationships` becomes a *user-scoped* edge store only (§ SUPABASE_INTEGRATION). |

**The rule this implies:** Layer C owns *facts*. Layer A owns *narrative*. Layer B becomes
a **projection** of C plus admin-authored editorial, not an independent source. Nothing in
Layer A or B is deleted in v3.0.

---

## 4. How the frontend reaches Layer C

Four options were considered. The recommendation is a deliberate split, not a single
mechanism.

| Option | Mechanism | Verdict |
|---|---|---|
| **1. Deploy the Python API** and `fetch()` it | New service on Fly/Railway/Render | **Rejected as the default.** Introduces a service, a deployment, a secret, a CORS surface, a latency budget and a failure mode into a frontend with zero existing `fetch()` calls. Worth doing later for admin tooling; wrong as the first step. |
| **2. Import CSVs at build time** | Next.js reads `packages/` during `next build` | **Rejected.** `frontend/` and `packages/` are separate roots; Vercel's build would need the whole repo, and 2,299 rows of CSV parsed at build inflates bundle and build time for data that changes rarely. Also gives no query capability. |
| **3. Sync Layer C into Supabase** | A generator writes package data into Postgres tables | **Recommended for read paths.** Uses the pattern the app already has — `supabase.from(...)`, RLS, `revalidate`. Zero new dependencies. Gives real indexes and joins against `profiles`. |
| **4. Next.js Route Handlers** calling a co-located Python service | `app/api/*` proxying | **Rejected for v3.0.** Same costs as 1, plus a proxy hop. |

### Recommendation: Option 3 as the spine, Option 1 as a later, narrow addition

```
packages/ + knowledge_graph/        (Git — canonical, versioned, provenance-complete)
            │
            │  sync generator, run in CI on package change
            ▼
Supabase  kg_* projection tables    (read path for the app)
            │
            │  supabase.from(...)  ← the pattern the frontend already uses
            ▼
Next.js frontend                    (no new dependency, no new failure mode)
```

The Python `api/` and `search/` layers keep their role: **they remain the reference
implementation and the admin/analyst surface**, and they are what the sync generator and
future recommendation work are built on. They are not on the user request path in v3.0.

**Why this is not "replacing" the Knowledge Platform with Supabase.** Git stays canonical.
Supabase holds a *derived projection*, exactly as `knowledge_graph/` holds a derived
projection of `packages/` (ADR-001). The sync is one-way and idempotent; the projection is
disposable and rebuildable. If the two disagree, Git wins and the projection is rebuilt.

---

## 5. What must not change

Taken directly from the brief, and confirmed against the code:

| Constraint | How the plan honours it |
|---|---|
| No second frontend | Nothing new is scaffolded. All work lands in `frontend/app` and `frontend/components`. |
| No page redesign | New knowledge appears as **additive sections** below existing content. No existing JSX block is restyled. |
| Supabase stays | It gains projection tables. Auth, RLS, and every existing table are untouched. |
| Auth is not rebuilt | `middleware.js`, `lib/admin.js` and the `handle_new_user` trigger are read-only in this plan. |
| No duplicate functionality | `PublicEntityList`, `PublicEntityDetail`, `OpportunityCard`, `AppNavbar`, `ModuleShell`, `KnowledgeSearch` are **reused**, not re-implemented. §PAGE_BY_PAGE_MAPPING names the component for every insertion point. |
| Preserve UX | Tailwind tokens (`card-base`, `chip`, `bg-cream`, `text-ink`) are reused verbatim. No new colour, no new font. |

---

## 6. Step 0 — vocabulary reconciliation (the prerequisite)

Nothing in §PAGE_BY_PAGE_MAPPING that touches a *user* works until this exists.

### Measured join feasibility, today

| Join | Method | Resolves | Rate |
|---|---|---|---|
| static district → graph `District` | exact name | 12 / 14 | 86% |
| idea `district_fit` → graph `District` | exact name | 16 / 19 | 84% |
| idea `sector` → graph `Industry` | search, 4 modes | 9 / 22 | 41% |
| idea `skills_needed` → graph `Skill` | exact name | 2 / 46 | 4% |
| idea `skills_needed` → graph `Skill` | `Resolver.resolve()` | 7 / 46 | 15% |
| idea `skills_needed` → graph `Skill` | search, 4 modes | 9 / 46 | 20% |
| **onboarding `SKILL_SUGGESTIONS` → graph `Skill`** | search, 4 modes | **7 / 57** | **12%** |

Districts are nearly solved — the two failures are `Vijayawada` (a city, not a district)
and `Nellore` (the graph holds the full official name). Both are one crosswalk row each.

Skills are not solved and cannot be solved by a better matcher. `AC Repair`,
`Beautician Services`, `CCTV Installation` and `Data Entry` have **no counterpart in
Package006 at all**. No similarity threshold conjures a row that does not exist.

### The deliverable

A curated crosswalk, built and governed exactly like `governance/ownership/scheme_crosswalk.csv`:

```
governance/vocabulary/skill_crosswalk.csv
governance/vocabulary/district_crosswalk.csv
governance/vocabulary/sector_crosswalk.csv
```

with the same discipline: every row records the matcher that produced it
(`EXACT_NAME` / `ALIAS` / `CURATED` / `NO_COUNTERPART`), unmatched terms are recorded as
`NO_COUNTERPART` rather than force-matched, and a validator fails the build on an
unresolvable reference.

`NO_COUNTERPART` is a **product decision, surfaced**: it means "we have no researched data
for this skill", and the UI must say that rather than show an empty panel. It is also a
collection backlog — 39 skills users actually claim, that Package006 does not cover.

**Estimated effort: 2–3 days.** ~120 crosswalk rows, most decided in seconds.

---

## 7. Dead code found during analysis

Reported, not removed — removal is out of scope for a planning phase.

| Path | Finding |
|---|---|
| `backend/server.py` (412 lines) | FastAPI + **MongoDB** + `emergentagent.com` OAuth. Referenced by nothing in `frontend/`. Superseded by the Supabase migration. Depends on `motor`, `pymongo`, `emergentintegrations`. **Recommend: delete in a separate PR**, after confirming no deployment targets it. |
| `packages/Package006_Skills` | Placeholder holding one README that says *"No Skills package data has been released yet"* — untrue since `Package006_Skills_and_Training` shipped. Already excluded from the v2.2 search index and API. |
| `frontend/data/districts.json` | Contains **1** record while `lib/districts-data.js` has 14 and the graph has 61. Serves `/knowledge/districts/[slug]` only. |

---

## 8. Risk register

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R1 | Skill/sector joins fail silently, features look broken | **High** | Step 0 crosswalk before any recommendation work. UI renders an explicit "no researched data for X" state, never an empty div. |
| R2 | Unverified data presented as authoritative to end users | **High** | 0/2,299 rows are human-reviewed. Every knowledge card carries a provenance line and a confidence badge; §PAGE_BY_PAGE_MAPPING specifies the component. Non-negotiable. |
| R3 | A fourth knowledge layer is created | **High** | Layer B becomes a projection of C, not a peer. The sync generator is the only writer of projected rows; a `source` column marks them. |
| R4 | Supabase projection drifts from Git | Medium | One-way, idempotent, CI-triggered on package change. A drift check compares row counts and content hashes. Git always wins. |
| R5 | Page weight and build time regress | Medium | Knowledge sections are server components with `revalidate`; no new client bundle. Measure before/after on `/dashboard` and `/ideas/[slug]`. |
| R6 | Admin CMS and sync fight over the same row | Medium | Projected rows are read-only in the admin UI and carry `source = 'package'`. Admin-authored rows carry `source = 'admin'`. The sync never touches the latter. |
| R7 | RLS gap exposes unpublished projected rows | Medium | Projection tables inherit the existing `status = 'published' or is_valueweave_admin()` policy shape. Covered in DATABASE_EXTENSION_PLAN §RLS. |
| R8 | "Teams" is specified but does not exist | Medium | See §9. |

---

## 9. Scope correction: Teams

The brief's Phase 2 asks for a **Team Page** with "Members", to be extended with Skill Gap
Analysis and Suggested Members.

**There is no Teams feature in this application.** There is no `teams` table, no
`team_members` table, and no `/teams` route. What exists is:

- `connections` — opportunity-scoped, 1:1, `pending`/`accepted`/`rejected`
- `collaborator_profiles` — a self-declared archetype, sectors and budget per user
- `founder_matches` — an admin-computed pairwise match score

So "Team Intelligence" is not an integration; it is **a new feature that happens to
consume knowledge**. Building it is a larger commitment than anything else in the brief.

**Recommendation.** Deliver the knowledge half against the surface that already exists —
skill-gap analysis over the *accepted connections* for an opportunity, which is the real
working group today — and treat a first-class `teams` entity as a separate v3.1 product
decision. `IMPLEMENTATION_ROADMAP.md` Step 5 is scoped that way, and says so.

---

## 10. Recommended sequence

Each step is independently deployable and independently revertible.

| Step | Delivers | Depends on | Effort | Risk |
|---|---|---|---|---|
| **0** | Vocabulary crosswalks | — | 2–3 d | Low |
| **1** | Package → Supabase sync; `/skills` and `/schemes` stop being empty | 0 | 3–4 d | Low |
| **2** | Knowledge cards with provenance and confidence | 1 | 2–3 d | Low |
| **3** | Unified search across ideas + knowledge | 1 | 3–4 d | Medium |
| **4** | District intelligence dashboard | 1, 2 | 4–5 d | Medium |
| **5** | Dashboard recommendations | 0, 1, 2 | 5–6 d | **High** |
| **6** | Business Explorer; Idea ↔ Package004/008 links | 1, 2, 3 | 4–5 d | Medium |
| **7** | Connection/working-group skill gap (Teams, descoped) | 0, 5 | 4–5 d | High |

Note the reordering against the brief: **search moves after the backfill** (searching empty
tables finds nothing) and **recommendations move after the crosswalk** (§0).

---

## 11. Companion documents

| Document | Answers |
|---|---|
| `PAGE_BY_PAGE_MAPPING.md` | For each of 79 routes: what it does now, what knowledge is injected, which component renders it |
| `SUPABASE_INTEGRATION.md` | Git vs Supabase vs API-only, and the sync contract |
| `DATABASE_EXTENSION_PLAN.md` | Exact DDL: tables, columns, indexes, RLS policies |
| `API_USAGE_MAP.md` | Endpoint and graph query behind every feature |
| `IMPLEMENTATION_ROADMAP.md` | The seven steps in detail, plus Phase 5 gap analysis |

# ValueWeave — Version 1.0 Readiness Assessment

**Date:** 2026-07-26 · **Commit:** `6fec48a` · **Assessed as a product, not as a codebase.**

No code was modified. Every figure below was measured against the repository at this
commit; the commands are reproducible and named where it matters.

---

## 0. Recommendation

# ⚠️ CONDITIONAL GO — narrow pilot only

**GO** for a **Hyderabad-anchored pilot** with the four pre-launch items in §10.
**NO-GO** for a general Telangana + Andhra Pradesh launch.

The engineering is genuinely finished. The knowledge is not, and the gap is not
uniform — it is concentrated in exactly the places a pilot cohort will land first.

### The three numbers that decide it

| Measured | Value | Why it decides |
|---|---:|---|
| Districts scoring ≥30 on district opportunity | **16 of 61** (26%) | Median district scores **0**. A student outside 16 districts sees an empty platform. |
| Onboarding skill terms that resolve to the graph | **13 of 57** (22.8%) | ~3 in 4 skills a real user types hit `NO_COUNTERPART`. |
| Knowledge rows reviewed by a human | **0 of 2,299** | Every surface is showing unreviewed research to students. |

### What a pilot user actually gets today

Six profiles run through the live engine (`user_intelligence`, real graph):

| Profile | Skills entered | Categories filled | Skill score |
|---|---|---:|---:|
| Student — commerce | Digital Marketing, Accounting, Data Entry | **1 of 10** | **0** |
| Student — ITI trades | Welding, Electrician, Plumbing | 4 of 10 | 42 |
| Student — arts | Teaching, Content Writing, Graphic Design | **2 of 10** | **0** |
| Entrepreneur — agri | Dairy Management, Poultry Management | **2 of 10** | **0** |
| Faculty — browsing | *(none)* | 1 of 10 | 0 |
| Best case | Welding, Food Processing, Tailoring | 5 of 10 | 75 |

**Four of six score zero on skills.** And the one category that fills for everyone —
`business_ideas` — is served from a **static 122-item editorial JSON at
`confidence = 0`**, not from the researched knowledge graph.

The most common skill set in the target audience (commerce/marketing/data entry)
produces the emptiest experience in the platform.

### Why this is still a GO, narrowly

Nothing here is broken. The platform is *honest* about being empty: every gap renders
an explicit reason (`NOT_DEPLOYED` / `NOT_COMPUTED` / `NO_DATA_SOURCE`), no figure is
fabricated, and provenance reaches a CSV row on every claim. That is a far better
place to launch from than a plausible-looking platform with invented content — and it
means a Hyderabad pilot can run without misleading anyone.

**Full backlog:** `PRODUCT_BACKLOG.md` · **Deployment:** `DEPLOYMENT_CHECKLIST.md` ·
**Pilot:** `PILOT_PLAN.md`

---

## 1. Deployment readiness — **NOT READY**

### The blocking fact

```
$ ls knowledge_sync/state/
.gitignore  README.md
```

**No manifest. The sync has never run.** Supabase therefore holds **zero** of the
1,812 knowledge rows and zero of the 5 user-intelligence tables. Every knowledge
surface built in Step 2 currently renders `NOT_DEPLOYED`.

That is one command away from fixed — but it is not done, and it must be done before
any pilot user signs in.

### Remaining deployment tasks

| # | Task | Blocking? |
|---|---|---|
| D1 | Apply 5 migration sets in order (§`DEPLOYMENT_CHECKLIST.md`) | **Yes** |
| D2 | Add `knowledge` + `user_intelligence` to Supabase *API → Exposed schemas* | **Yes** |
| D3 | `knowledge_sync sync --full --target supabase` (1,812 rows) | **Yes** |
| D4 | Run the intelligence engine per user and write its 5 tables | **Yes** |
| D5 | Configure Google OAuth redirect URIs in Supabase | **Yes** |
| D6 | Set `ADMIN_EMAILS` and promote the first `profiles.is_admin` | **Yes** |
| D7 | Resolve `kg_vocabulary_map` schema mismatch (§7 below) | **Yes** |
| D8 | Add CI — none exists (§below) | No, but do it |
| D9 | Write `.env.example` — none exists | No |
| D10 | Delete stray `backend/` (412 lines, MongoDB) | No |

### Supabase configuration

**50 tables across 4 schemas**, created by 5 migration sets in 3 directories:

| Source | Tables | RLS | Policies | Indexes |
|---|---:|---:|---:|---:|
| `frontend/supabase_schema.sql` | 3 | 3 | 10 | 5 |
| `frontend/migrations/001`–`010` | 23 | 23 | 53 | 72 |
| `supabase/migrations/*` | 10 | 10 | 8 | 3 |
| `knowledge_sync/migrations/001` | 9 | 9 | 9 | 34 |
| `user_intelligence/migrations/001` | 5 | 5 | 5 | 4 |
| **Total** | **50** | **50** | **85** | **118** |

RLS is enabled on **all 50**. No table ships unprotected.

**Migration 008 does not exist.** `frontend/migrations/` runs 001–007, then 009, 010.
This is not a lost file: `DATABASE_EXTENSION_PLAN.md:34` planned
`008_knowledge_platform_projection.sql`, and Step 1 superseded it with the dedicated
`knowledge` schema. The gap is intentional and **undocumented in the migrations
directory** — a deployer will reasonably think a file is missing. It also has a real
consequence, in §6: the abandoned 008 was where `pg_trgm` was going to come from.

### Environment variables

Only **four** are read by application source (`process.env` outside `node_modules`):

| Variable | Used by | Required |
|---|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | 12 sites incl. `lib/supabase-{browser,server}.js` | **Yes** |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | same | **Yes** |
| `NEXT_PUBLIC_BASE_URL` | `lib/seo.js`, `lib/knowledge-graph.js` | Yes — canonical URLs |
| `ADMIN_EMAILS` | `lib/admin.js` bootstrap allowlist | Recommended |

Server-side, for the engines only: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`.

**There is no `.env.example`.** A new deployer has to read source to discover four
variables, two of which cause a *silent* empty render when absent rather than an error.

### Production risks

| Risk | Severity | Evidence |
|---|---|---|
| **Exposed-schemas step missed** → every knowledge read returns empty **with no error** | **High** | `safe()` in `lib/knowledge.js` converts failure to a fallback by design |
| **Admin bypass if `NODE_ENV ≠ production`** | **High** | `lib/admin.js:10` returns `isAdmin: true` unconditionally in development — opens all 33 `/admin/*` routes |
| **500 synthetic opportunities on the main feed** | **High** | `003_seed_opportunities.sql`, `created_by='system_seed'`, template-generated |
| Open image proxy | Medium | `next.config.js`: `remotePatterns: [{ hostname: "**" }]` |
| `next@14.2.15` published advisory | Medium | Pre-existing; upgrade is not an integration task |
| No CI | Medium | No `.github/workflows/` — 447 tests run only when someone remembers |
| Sync has never touched real Postgres | Medium | `OPERATIONS_GUIDE.md` §0 states this plainly; §2 step 7 is the rehearsal |

---

## 2. Knowledge completeness — **THIN**

### Package coverage

| Package | Datasets | Rows | Graph entities | Edges | Version |
|---|---:|---:|---:|---:|---|
| Package001_Geography | 5 | 138 | 93 | 63 | 1.0.0 |
| Package002_Education | 4 | 141 | 66 | 58 | 1.0.0 |
| **Package003_Healthcare** | 4 | 146 | **0** | **0** | 1.0.0 |
| Package004_Industries | 5 | 63 | 70 | 45 | 1.0.0 |
| Package005_Agriculture | 16 | 388 | 99 | 254 | 1.0.0 |
| **Package006_Skills** | **0** | **0** | 0 | 0 | **none** |
| Package006_Skills_and_Training | 10 | 291 | 100 | 40 | **none** |
| Package007_Government_Schemes | 15 | 655 | 52 | 38 | 1.0.0 |
| Package008_MSME | 18 | 477 | 167 | 367 | 1.0.0 |
| **Total** | **77** | **2,299** | **647** | **865** | |

Three findings in that table.

**Package003_Healthcare is invisible.** 146 rows — hospitals, medical colleges,
regulatory bodies, health insurance schemes — promoted to Stable v1.0.0, and
`knowledge_graph/build_graph.py` registers **no entity type for it**. Zero entities,
zero edges, zero user-facing surfaces. 6.4% of all research is unreachable.

**Package006 exists twice, and neither copy is finished.** `Package006_Skills/`
contains only a `README.md`. `Package006_Skills_and_Training/` has 10 datasets and 291
rows and is missing most of what every other package has:

| Artefact | P006 | P008 (reference) |
|---|---|---|
| `VERSION` | **absent** | ✓ |
| `README.md` | **absent** | ✓ |
| `CHANGELOG.md` | **absent** | ✓ |
| `package_manifest.json` | **absent** | ✓ |
| `validate.py` | **absent** | ✓ |
| `metadata/` | **empty dir** | ✓ populated |
| `registry/` | **empty dir** | ✓ populated |

A merge commit (`9393f00`) reads *"Merge Package006_Skills_and_Training v1.0.0 to
Stable"*, but the promotion artefacts were never written — the state matches open tasks
#38–40 exactly.

**This has a sequencing consequence that changes the backlog.** Skills are the primary
matching axis, and K1 (collect ~40 backlog skills) writes *into this package*. With no
`validate.py` and no manifest, K1's output cannot be validated the way every other
package's is. **Completing Package006 is a prerequisite for the highest-value item in
the backlog**, which is why it is Critical rather than High.

**Row-to-entity ratio is 28.1%**, which is expected rather than alarming — mapping
datasets produce *edges*, not entities (Package008: 477 rows → 167 entities but 367
edges). Package007 at 8% is the outlier worth a look.

### Per-dimension coverage

| Dimension | Entities | Connected | Median degree | Verdict |
|---|---:|---:|---:|---|
| District | 61 | 61 (100%) | **1** | Complete list, thin links |
| Skill | 45 | 40 (89%) | 2 | **Too few** — see resolve rate |
| BusinessOpportunity | 45 | 45 (100%) | 1 | Adequate for a pilot |
| **GovernmentScheme** | 40 | **19 (47.5%)** | **0** | **Half unrecommendable** |
| MSME | 40 | 40 (100%) | 6 | Best-connected in the graph |
| Industry | 78 | 61 (78%) | 1 | Adequate |
| Certification | 30 | **0 (0%)** | 0 | Entirely orphaned |
| TrainingProvider | 25 | 3 (12%) | 0 | Nearly orphaned |

**142 of 647 entities (21.9%) have no edges at all.** Every recommendation rule is a
traversal, so an orphan entity can never be recommended by any of the 21 rules. That
includes **21 of 40 government schemes** — the single most valuable content type for
this audience is 52.5% unreachable.

### District coverage

61 districts: **33 Telangana** (complete) + **28 Andhra Pradesh**.

AP's April 2022 reorganisation notified **26** districts. The dataset carries 28,
the extras being **Markapuram** and **Polavaram** — announced as proposals. Flagged
for verification, not asserted as an error; it is exactly the kind of claim the
platform's own `PENDING_VERIFICATION` discipline exists for.

Two Package001 datasets are **header-only**: `mandal.csv` (0 rows) and
`revenue_division_andhra_pradesh.csv` (0 rows). `revenue_division_telangana.csv` has
75. Sub-district geography is half-collected.

Scored across all 61 districts with a resolving skill:

| district_opportunity | Districts |
|---|---:|
| ≥70 | **1** (Hyderabad, 85) |
| 50–69 | 3 (Guntur 59, Tirupati 51, Visakhapatnam 50) |
| 30–49 | 12 |
| **<30** | **45** |

**Median: 0.** Mean 11.9. The eight worst — Adilabad, Kumuram Bheem Asifabad,
Mancherial, Nirmal, Jagtial, Peddapalli, Kamareddy, Rajanna Sircilla — score 0 and
return 6 recommendation rows against Hyderabad's 25.

### Vocabulary resolution — the sharpest gap

`governance/vocabulary/crosswalk_summary.json`:

| Vocabulary | Terms | Resolved | Rate |
|---|---:|---:|---:|
| District | 33 | 33 | **100%** |
| Sector | 22 | 11 | 50% |
| Skill | 147 | 39 | **26.5%** |
| **Onboarding skills specifically** | **57** | **13** | **22.8%** |
| Total | 202 | 83 | 41.1% |

108 skill terms and 6 sector terms sit in a documented collection backlog. The backlog
is a roll-call of the target audience's actual skills: *Accounting, Data Entry,
Digital Marketing, Sales, Teaching, Graphic Design, Retail Management, Logistics, GST
Filing, Photography, Social Media Management.*

Note also that the 33 district terms resolve to only **19 distinct entities** — the
onboarding vocabulary reaches under a third of the 61 districts in the graph.

### Verification and confidence

| | |
|---|---|
| `VST-NEEDS_REVIEW` | **2,299 rows — 100%** |
| Any other status | **0** |
| Confidence | mean 72.4, median 72, range 50–92 |
| Rows below confidence 60 | 67 |
| `PENDING_VERIFICATION` cells | 2,456 (**6.02%** of 40,799 cells) |
| `PENDING_GEOCODING` cells | 272 (0.67%) |

**Not one row has been reviewed by a human.** This is not a missing table or missing
code — it is missing *work*, and it is the largest credibility gap in the product.
`audit/reports/DATA_STEWARDSHIP.md` sizes a first pass at ~2 days: the 40
highest-leverage entities cover 37.2% of all edge endpoints.

### Missing knowledge required for v1.0

| # | Gap | Effort | Priority |
|---|---|---|---|
| K1 | ~40 common skills from the backlog, with edges | 3–4 d | **Critical** |
| K2 | Human review of the top 40 entities | 2 d | **Critical** |
| K3 | Connect 21 orphan schemes to districts/businesses | 2 d | **Critical** |
| K4 | Register Package003 entity types in the graph builder | 1 d | High |
| K5 | **Complete Package006**: 5 missing artefacts, 2 empty dirs, delete duplicate | 1 d | **Critical** — gates K1 |
| K6 | Deepen 12 pilot districts beyond median degree 1 | 3 d | High |
| K7 | Connect 30 certifications + 22 training providers | 2 d | Medium |
| K8 | Verify AP's 28 vs 26 districts | 2 h | Medium |
| K9 | Collect `mandal.csv`, AP revenue divisions | 2 d | Low |

---

## 3. Application completeness — **BROAD, PARTLY HOLLOW**

**79 routes**: 46 user-facing, 33 under `/admin`. `next build` → exit 0, 213/213
static pages, 0 prerender errors.

### Implemented, real, working

| Feature | Evidence |
|---|---|
| Google OAuth + session | `signInWithOAuth({provider:"google"})`, `auth/callback/route.js`, middleware refresh |
| Onboarding (name, city, skills, interests, intent, bio) | `app/onboarding/page.js`, 232 lines |
| Profile + public profile | `/profile`, `/profile/[id]` |
| "Discover Yourself" assessment | `/discover`, **1,024 lines** — largest page in the app |
| Connections (request/accept/reject, 1:1) | `/connections`, 242 lines, real skill overlap |
| Collaborator marketplace | `/collaborators`, `/collaborators/[sector]` |
| Opportunity feed + detail + create | `/dashboard`, `/opportunities/*` |
| Idea library — 122 curated ideas | `lib/idea-library/ideas.json`, 152 KB |
| Research articles + admin CMS | `migrations/001`, `/admin/research/*` |
| Notifications, questions, analytics | `migrations/005`–`007`, 33 admin routes |
| Step 2 knowledge surfaces | 11 components; render empty states until D1–D4 |

### Placeholder features

Seven routes render `ModuleShell` — a styled shell with no data path. To their credit
they **say so**: `/ai` reads *"No AI features are implemented yet."*

| Route | Says |
|---|---|
| `/ai` | "Reserved architecture… No AI features are implemented yet." |
| `/manufacturing` | "A modular manufacturing foundation for future…" |
| `/readiness` | "A future readiness layer for skills, training, mentors…" |
| `/scale` | "A future expansion layer…" |
| `/network`, `/districts`, `/districts/[slug]` | Shell only |

**`/readiness` matters more than the others** — it is the natural home of the
assessment stage in the stated journey, and it is a shell.

### Disabled / empty-by-construction

**Four public routes read a knowledge system that has no data and no writer.**
`/schemes`, `/skills`, `/resources`, `/roadmaps` call `getKgEntities()` →
`public.kg_*` CMS tables, gated on `status='published'`. Nothing populates them except
an admin typing entries by hand, so all four show *"…will appear here after admins
publish them."*

Meanwhile `knowledge.kg_schemes` holds 40 researched schemes and
`knowledge.kg_skills` holds 45 researched skills.

> **The most important structural finding in this report.** There are **two knowledge
> systems with colliding table names**, separated only by Postgres schema:
>
> | | `public.kg_*` (9 tables) | `knowledge.kg_*` (8 tables) |
> |---|---|---|
> | Author | Admin, by hand | Git packages, generated |
> | Rows today | 0 | 0 (1,812 ready to sync) |
> | Read by | `/schemes` `/skills` `/resources` `/roadmaps` | Step 2 surfaces |
> | Provenance | none | 6 columns, to CSV row |
>
> A user visiting `/skills` is told skills don't exist yet. A user on `/dashboard`
> is shown skills from the graph. Same platform, same nouns, two answers.

### Missing user flows

| Flow | Status |
|---|---|
| **Teams / team workspace** | **No route.** `/teams` absent, `teams` table empty (migration 010) |
| **Startup workspace** | **Absent entirely** — no route, no table, no component |
| Assessment → engine | Assessment exists; output is not an engine input (`assessment_results` = `MISSING`) |
| Mentor discovery | `mentor_profiles` empty; category returns `NO_DATA_SOURCE` |
| Events / deadlines | `events` empty; same |
| Stewardship review UI | Python CLI only; no `/admin/stewardship` route |

### Four district lists, four answers

| Source | Districts | Drives |
|---|---:|---|
| `packages/Package001/district.csv` | **61** | Knowledge graph |
| `lib/idea-library/districts.json` | 19 | `/ideas`, `/business-ideas/[district]` |
| `lib/districts-data.js` | **14** | `/district/[slug]`, `/districts/[slug]` |
| `003_seed_opportunities.sql` | 22 | The dashboard feed |

`/district/[slug]` therefore generates **14 of 61 districts (23%)**. A pilot student
in the other 47 has no district page at all.

---

## 4. User journey validation

| # | Stage | Status | Evidence |
|---|---|---|---|
| 1 | **Google Login** | 🟢 **READY** | `signInWithOAuth`, callback exchanges code, routes to `/onboarding` or `/dashboard` by `profile_complete`. Needs D5 only. |
| 2 | **Profile** | 🟢 **READY** | Onboarding writes `profiles`; `/profile` renders; public `/profile/[id]`. RLS correct. |
| 3 | **Assessment** | 🟡 **PARTIAL** | `/discover` works (1,024 lines) but **persists only via an opt-in button inside a secondary "network" tab**, requires sign-in, and `/discover` is not auth-gated — an anonymous user completes it and loses it. Output feeds `collaborator_profiles`, **not** the intelligence engine. |
| 4 | **Recommendations** | 🔴 **BLOCKED** | Engine correct and reproducible, but **no data is synced** (D1–D4). Post-sync it fills **1–5 of 10 categories** depending on skill resolution; 2 categories always return `NO_DATA_SOURCE`. |
| 5 | **Search** | 🟡 **PARTIAL** | Static search works. Knowledge search blocked on sync, and `.ilike("%q%")` has no trigram index (§6). |
| 6 | **Business Explorer** | 🟡 **PARTIAL** | 122 editorial ideas work today at **confidence 0**. The 45 researched businesses need sync. |
| 7 | **Connections** | 🟢 **READY** | Full request/accept/reject; real `skillOverlap`; skills gated behind acceptance. |
| 8 | **Teams** | 🔴 **BLOCKED** | No route, no UI, empty table. Needs invitations, roles, lifecycle — a product, not an integration. |
| 9 | **Startup Workspace** | 🔴 **BLOCKED** | **Does not exist in any form.** Not a table, not a route, not a placeholder. The largest single gap in the journey. |
| 10 | **Dashboard** | 🟡 **PARTIAL** | Renders and ranks today — from **500 synthetic seeded opportunities**. Four knowledge rails blocked on sync. |

**3 READY · 4 PARTIAL · 3 BLOCKED.**

The journey as stated cannot be completed end to end. It breaks first at stage 4 for
deployment reasons (fixable in a day) and permanently at stages 8–9 for product
reasons (weeks).

---

## 5. Data readiness

### Tables with production data (user-generated, real)

`profiles`, `connections`, `collaborator_profiles`, `research_articles`,
`visitor_sessions`, plus the analytics/engagement tables from migrations 004–007.
All 11 that the intelligence engine registers as `AVAILABLE` are genuine.

### Tables with demo data — **1, and it is the visible one**

| Table | Rows | Nature |
|---|---:|---|
| `public.opportunities` | **500** | Template-generated by `scripts/generate-opportunity-seeds.mjs`; `created_by = 'system_seed'`; 100 each across 5 categories, 22 districts |

These are **synthetic**, they carry no provenance, and they are the primary content of
`/dashboard`, `/explore` and `/opportunities/*`. In a platform whose stated rule is
*never fabricate data*, this is the one place the rule is not held — and it is the
first screen a pilot user sees.

### Empty tables — 27

| Group | Tables | Blocked on |
|---|---:|---|
| `knowledge.*` | 8 (+`sync_runs`) | D1–D3 |
| `user_intelligence.*` | 5 | D4 |
| `public.kg_*` CMS | 9 | An admin typing, or retirement |
| Migration 010 | 5 | Product features |
| `kg_vocabulary_map` | 1 | D7 |

### Static file dependencies — 13 JSON + 4 JS modules

| File | Items | Drives |
|---|---:|---|
| `lib/idea-library/ideas.json` | **122** | `/ideas`, and the `business_ideas` recommendation category |
| `lib/idea-library/sectors.json` | 22 | Sector vocabulary |
| `lib/idea-library/districts.json` | 19 | District vocabulary |
| `lib/districts-data.js` (697 lines) | **14** | `/district/[slug]`, `/districts/[slug]` |
| `lib/static-knowledge.js` | 56 paths | `/knowledge/[type]/[slug]` |
| `data/*.json` (7 files) | 6–15 each | Module landing sections |
| `lib/radar-data.js`, `opportunity-templates.js` | — | `/opportunity-radar`, seeds |

**The most-used recommendation category in the product is served from a static file at
`confidence = 0`.** That is correctly labelled (`ConfidenceBadge` renders *editorial*)
and enforced by test — but it means the recommendation engine's most visible output is
not knowledge-graph-derived.

### Missing datasets

`assessment_results`, `mentor_profiles`, `events`, `teams`, `team_members` — schemas
exist in migration 010 with **0 `INSERT` statements**, deliberately. Detail and
reasoning in `MISSING_FEATURES.md`.

---

## 6. Performance readiness — **ADEQUATE AT PILOT SCALE**

### API calls per page

No HTTP API exists in the request path. Every read is `supabase.from(...)`; a test
asserts no `fetch()` to a Python service.

| Page | Queries | Note |
|---|---:|---|
| `/dashboard` | 4 | Client component, **no cache — refetches every mount** |
| `/profile` | 6 | Same |
| `/connections` | 5 | |
| `/district/[slug]` | 2 | Build time |
| `/ideas/[slug]` | **~9** | 1 scheme query **per matched business**, capped at 6 |

At 130 pilot users this is fine. `/ideas/[slug]` is the one to watch; the fix is a
materialised view, not a client cache.

### Caching

| | |
|---|---|
| Pages with `revalidate` | **16** of 79 (mostly `revalidate = 300`) |
| Pages with `force-dynamic` | **25+**, nearly all `/admin/*` |
| Knowledge surfaces | Inherit their host page — dashboard/profile uncached |

### Indexes — 118 total, one real gap

| Schema | Indexes | Assessment |
|---|---:|---|
| `knowledge` | **34** across 9 tables | Well covered: `live`, `source`, type and name per table |
| `user_intelligence` | **4** across 5 tables | **Under-indexed** — 3 of 5 tables have none beyond their PK |
| `public` (app) | 72 | Good; GIN on `collaborator_profiles.top_sectors`, `mentor_profiles.expertise_skills` |

### The bottleneck, and its cause

```js
// frontend/lib/knowledge.js:208
.ilike("canonical_name", `%${q.replace(/[%,]/g, "")}%`)
```

A **leading-wildcard `ILIKE` with no trigram index.** `kg_entities_canonical_name_idx`
is a btree and cannot serve `%q%`, so every keystroke — debounced to 250 ms — is a
sequential scan of `kg_entities`.

At 647 rows this is invisible. The finding is *why* the index is absent:
`DATABASE_EXTENSION_PLAN.md:410` lists `pg_trgm` as an extension of the planned
migration **008**, which Step 1 replaced with the dedicated `knowledge` schema. The
trigram index was lost in the substitution. `pg_trgm` appears **nowhere** in any
migration in the repository.

Note also that a 27-test Python search engine exists — exact/prefix/alias/fuzzy with
tuned weights — and the frontend does not use it. It has no deployment target.

### Bottlenecks, ranked

| # | Bottleneck | Bites at |
|---|---|---|
| P1 | `%ILIKE%` with no `pg_trgm` | ~5k entities |
| P2 | Dashboard/profile refetch on every mount | Immediately, on mobile |
| P3 | `/ideas/[slug]` N+1 scheme queries | ~6 matched businesses |
| P4 | `user_intelligence` under-indexed | Many rows per user |
| P5 | 25+ `force-dynamic` admin pages | Concurrent admins |

---

## 7. Security review — **SOUND, three defects**

### RLS — the strongest part of the platform

| Schema | Read | Write |
|---|---|---|
| `knowledge.*` | Authenticated read | **No write policy exists at all** |
| `user_intelligence.*` | `auth.uid() = user_id`, **no admin exception** | **None** |
| `public.*` app tables | Per-table owner/participant | Owner + `is_admin()` |
| `public.kg_*` CMS | `status='published' or is_valueweave_admin()` | Admin only |

RLS on **50 of 50** tables. 85 policies. Granting no write policy on the projected
schemas is the right call: hand-editing a projected row is a situation that should be
*impossible*, not merely discouraged — the next sync would silently revert it.

`user_intelligence` having **no admin read exception** is a deliberate privacy
decision: an admin cannot read a user's computed profile. Worth preserving.

### Defect 1 — development admin bypass (**High**)

```js
// frontend/lib/admin.js:10
if (process.env.NODE_ENV === "development") {
  return { user: { email: "dev@localhost" }, isAdmin: true, dev: true };
}
```

Unconditional admin on any non-production `NODE_ENV`, opening all 33 `/admin/*`
routes. Mitigated by RLS at the database (the file says so, correctly) and by Next.js
setting `NODE_ENV=production` in production builds — but a preview deploy or a
misconfigured container inverts that assumption. Should be gated on an explicit
opt-in variable, not on `NODE_ENV`.

### Defect 2 — draft CMS content readable (**Low today, High if used**)

```sql
create policy "kg roadmap steps public read"
  on public.kg_roadmap_steps for select using (true);
```

`kg_roadmaps` is gated on `status='published'`. Its **steps are not** — `using (true)`.
An unpublished roadmap's step titles, descriptions, costs and required skills are
readable by any anonymous client. `kg_relationships` has the same unconditional read.

Low severity only because the tables are empty. It becomes a content leak the day an
admin drafts a roadmap.

### Defect 3 — open image proxy (**Medium**)

```js
images: { remotePatterns: [{ protocol: "https", hostname: "**" }] }
```

Any HTTPS host may be fetched through the Next.js image optimizer — an open proxy
usable for bandwidth abuse and internal-endpoint probing. Restrict to known hosts.

### API exposure

**Correct, with one required action.** No HTTP API is exposed; the Python API is not
deployed. The anon key is public by design and safe because RLS is the boundary. The
service role key exists only in the sync, is never in a `NEXT_PUBLIC_*` variable, and
nothing else in the platform holds it.

**Action:** exposing the `knowledge` schema (D2) makes 1,812 rows readable by any anon
client. That is intended — it is public reference data — but it should be a decision
someone makes knowingly, not a side effect of a settings toggle.

### Authentication / authorization

Google OAuth via Supabase; PKCE code exchange server-side; middleware refreshes
session on every matched request and redirects 6 protected path groups. Two layers of
authorization: `getAdminStatus()` for routing/UX and `is_admin()` / `auth.uid()` in
RLS for enforcement. The right shape — the database is the boundary and the app gate
is cosmetic.

### One unresolved inconsistency (D7)

`kg_vocabulary_map` is created in **`public`** by migration 009 but queried through
the **`knowledge`**-scoped client. One of the two must move. Deliberately not fixed
inside a Step 2 commit; it must be fixed before deployment or vocabulary resolution
silently returns nothing.

---

## 8. Version 1.0 backlog

Full detail, ownership and sequencing in **`PRODUCT_BACKLOG.md`**. Summary:

| Priority | Items | Effort |
|---|---:|---|
| **Critical** | 12 | **10–13 days** |
| **High** | 13 | 14–18 days |
| **Medium** | 16 | 20–26 days |
| **Low** | 12 | 14–18 days |
| **Total** | **53** | **58–75 days** |

**Critical path to a pilot: 10–13 days.** Seven of the twelve Critical items are
deployment or data-loading tasks measured in hours; the schedule is dominated by two
knowledge tasks (K1 skills, K2 human review) that cannot be parallelised away because
they need a person who knows the domain.

---

## 9. Pilot launch plan

Full plan in **`PILOT_PLAN.md`**. The headline decision:

> **Anchor the pilot on Hyderabad, Guntur, Visakhapatnam and Tirupati** — the only 4
> districts scoring ≥50 — and recruit the 100 students from institutions in them.
>
> Recruiting 100 students across all 61 districts means ~74% of them land in a district
> whose opportunity score is under 30, and the honest empty state they see will read as
> a broken product rather than an incomplete one.

Cohort: 100 students · 10 faculty · 20 entrepreneurs. Four weeks, three gates.

---

## 10. Go / No-Go

### GO, conditional on four items

| # | Condition | Effort | Why non-negotiable |
|---|---|---|---|
| **1** | Deploy: D1–D7 — migrations, exposed schemas, full sync, engine run, OAuth, admin, vocabulary schema fix | **1–2 d** | Without it every knowledge surface is empty and the product is only its pre-Step-2 self |
| **2** | Human-review the top 40 entities | **2 d** | 0 of 2,299 rows reviewed. Showing students unreviewed research about government schemes is the one failure that costs trust permanently |
| **3** | Collect ~40 backlog skills with edges | **3–4 d** | At 22.8% resolve, 3 in 4 pilot users get a zero skill score. This single number gates the whole recommendation experience |
| **4** | Label the 500 seeded opportunities as illustrative, or remove them | **0.5 d** | They are synthetic, unsourced, and on the first screen. Either is acceptable; leaving them unlabelled is not |

**Total: 7.5–9.5 days.**

### NO-GO for a general launch, on three grounds

1. **74% of districts are effectively empty** — 45 of 61 score below 30, median 0.
2. **Two journey stages do not exist** — Teams and Startup Workspace are not
   partially built; they are absent. Weeks of product work, not integration.
3. **Two knowledge systems answer the same question differently** — `/skills` says
   skills don't exist while the dashboard recommends them. Confusing at 130 users;
   indefensible at 10,000.

### What is genuinely ready

Worth stating plainly, because the report above is mostly gaps:

- `next build` → exit 0, 213/213 static pages, 0 prerender errors
- **447 tests**, 0 failures, 0 errors, 0 skips
- RLS on 50 of 50 tables; 85 policies; no write path into projected data
- Provenance from any claim to a CSV row, through 6 mandatory columns
- Reproducible recommendations — no randomness, no AI, no DB access in the engine
- Honest empty states: `NOT_DEPLOYED` / `NOT_COMPUTED` / `NO_DATA_SOURCE` are
  distinguished in the type system, in the API, and on screen
- Zero fabricated knowledge rows, enforced by test

**The platform's engineering is v1.0. Its knowledge base is v0.4.** Ship the narrow
pilot, use it to find out which of the 108 backlog skills actually matter, and let
that decide what v1.1 collects.

---

**Companion documents:** `PRODUCT_BACKLOG.md` · `DEPLOYMENT_CHECKLIST.md` ·
`PILOT_PLAN.md` · `RELEASE_NOTES_DRAFT.md`

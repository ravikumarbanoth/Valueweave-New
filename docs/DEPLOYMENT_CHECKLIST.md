# ValueWeave — Version 1.0 Deployment Checklist

**Print this. Tick every box. Do not skip step 4.**

For someone deploying ValueWeave to a fresh Supabase project and Vercel deployment.
Assessment behind it: `VERSION1_READINESS_REPORT.md` §1.

**Two warnings before you start.**

1. **Nothing here has ever run against a real Supabase.** No credentials exist in the
   environment this was built in; every path is exercised against an in-memory target.
   Treat the first run as a rehearsal — every step below is verifiable and reversible.
2. **Step 4 fails silently.** Skip it and the application looks *exactly* as it does
   now, with nothing in any log to say why.

---

## 0 · Prerequisites

- [ ] Supabase project created; `DATABASE_URL` (direct Postgres) to hand
- [ ] `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` exported in a **shell that does not log history**
- [ ] Python 3.11+ · Node 18+
- [ ] Repository at a known commit — record it: `git rev-parse HEAD`

```bash
python3 tests/run_all.py --quiet      # expect: TOTAL 447, 0 fail, 0 err, 0 skip
cd frontend && npx next build         # expect: exit 0, 213/213, 0 prerender errors
```

- [ ] Both pass **before** you touch the database

### The service role key

Bypasses RLS entirely. It is the only credential that can write to the `knowledge`
schema, and that is the only reason it exists.

- [ ] CI secret or server-side env var **only**
- [ ] **Never** in a `NEXT_PUBLIC_*` variable, a client component, or a committed file
- [ ] Nothing else in the platform holds it, so rotating it breaks only the sync

---

## 1 · Environment variables

There is **no `.env.example`** in the repository (backlog O2). These four are read by
application source:

| Variable | Where | Required | If missing |
|---|---|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | Vercel | **Yes** | **Silent** — every read returns empty |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Vercel | **Yes** | **Silent** — same |
| `NEXT_PUBLIC_BASE_URL` | Vercel | Yes | Wrong canonical URLs, broken sitemap |
| `ADMIN_EMAILS` | Vercel (server) | Recommended | No admin can bootstrap |

Server-side, engines only:

| `SUPABASE_URL` · `SUPABASE_SERVICE_ROLE_KEY` | CI / operator shell | For sync + engine |

- [ ] All four set in Vercel, for **Production and Preview**
- [ ] `NEXT_PUBLIC_BASE_URL` has **no trailing slash**
- [ ] `ADMIN_EMAILS` is comma-separated, lowercase

> ⚠️ The two `NEXT_PUBLIC_SUPABASE_*` variables fail **silently**, not loudly. A
> deployment with them missing builds, serves, and shows an empty platform.

---

## 2 · Migrations — order matters

50 tables across 4 schemas, from **5 migration sets in 3 directories**. Later sets
hold foreign keys into earlier ones.

```bash
# ── 2.1 base application schema
psql "$DATABASE_URL" -f frontend/supabase_schema.sql          # profiles, opportunities, connections

# ── 2.2 application migrations, in numeric order
psql "$DATABASE_URL" -f frontend/migrations/001_research_articles.sql
psql "$DATABASE_URL" -f frontend/migrations/002_collaboration_marketplace.sql
psql "$DATABASE_URL" -f frontend/migrations/003_seed_opportunities.sql     # ← see §3
psql "$DATABASE_URL" -f frontend/migrations/004_admin_analytics.sql
psql "$DATABASE_URL" -f frontend/migrations/005_growth_intelligence.sql
psql "$DATABASE_URL" -f frontend/migrations/006_visitor_analytics.sql
psql "$DATABASE_URL" -f frontend/migrations/007_engagement_retention.sql
#   NOTE: there is no 008. Intentional — see below.
psql "$DATABASE_URL" -f frontend/migrations/009_vocabulary_crosswalk.sql
psql "$DATABASE_URL" -f frontend/migrations/010_missing_application_features.sql

# ── 2.3 platform settings + admin CMS knowledge tables
psql "$DATABASE_URL" -f supabase/migrations/202606200001_geo_video_devops.sql
psql "$DATABASE_URL" -f supabase/migrations/202606200002_entrepreneurship_knowledge_graph.sql

# ── 2.4 the knowledge projection (dedicated schema)
python3 knowledge_sync/generate_migration.py --check          # DDL must match the specs
psql "$DATABASE_URL" -f knowledge_sync/migrations/001_knowledge_schema.sql

# ── 2.5 the intelligence schema
psql "$DATABASE_URL" -f user_intelligence/migrations/001_user_intelligence.sql
```

> **There is no migration 008.** `DATABASE_EXTENSION_PLAN.md:34` planned
> `008_knowledge_platform_projection.sql`; Step 1 superseded it with the dedicated
> `knowledge` schema. Do not go looking for it. One casualty: 008 was where `pg_trgm`
> was going to come from, and it exists in no migration today (backlog P1).

### Verify

```bash
psql "$DATABASE_URL" -c "\dt knowledge.*"                     # 9 tables
psql "$DATABASE_URL" -c "\dt user_intelligence.*"             # 5 tables
psql "$DATABASE_URL" -c "select count(*) from pg_tables where schemaname in ('public','knowledge','user_intelligence');"
```

- [ ] 9 tables in `knowledge`
- [ ] 5 tables in `user_intelligence`
- [ ] **50** tables total
- [ ] Every one reports `rowsecurity = true`:

```sql
select schemaname, tablename from pg_tables
 where schemaname in ('public','knowledge','user_intelligence')
   and rowsecurity = false;
-- expect: 0 rows
```

---

## 3 · Decide about the 500 seeded opportunities

`003_seed_opportunities.sql` inserts **500 template-generated opportunities** with
`created_by = 'system_seed'`, across 5 categories and 22 districts. They are
**synthetic and carry no provenance**, and they are the primary content of
`/dashboard`, `/explore` and `/opportunities/*` — the first screen a user sees.

Pick one. Do not skip the decision.

**Option A — label them (recommended for the pilot)**

```sql
update public.opportunities
   set description = '[Illustrative example — not a verified opportunity] ' || description
 where created_by = 'system_seed';
```

**Option B — leave them out**

```bash
# simply do not run 003; or afterwards:
psql "$DATABASE_URL" -c "delete from public.opportunities where created_by = 'system_seed';"
```

- [ ] Option A applied, **or** Option B applied
- [ ] Recorded which, and who decided

> The platform's stated rule is *never fabricate data*, and it holds everywhere except
> here. Leaving 500 unlabelled synthetic rows indistinguishable from 40 fully-sourced
> researched MSMEs is the one deployment choice that contradicts the product's own
> discipline.

---

## 4 · ⚠️ EXPOSE THE SCHEMAS ⚠️

**Supabase Dashboard → Project Settings → API → Exposed schemas**

Add:

```
knowledge, user_intelligence
```

- [ ] `knowledge` added
- [ ] `user_intelligence` added
- [ ] Setting **saved**

### Why this is boxed off on its own

Supabase serves only listed schemas. Without this,
`createClient(url, key, { db: { schema: "knowledge" } })` errors on every query,
`safe()` in `lib/knowledge.js` catches it by design and returns `[]`, and every page
renders its empty state.

**The application will look exactly as it does today and nothing will indicate why.**

### Diagnostic

```sql
select count(*) from knowledge.kg_entities;                    -- 647 after step 6
select count(*) from user_intelligence.user_activity_summary;
```

If those return rows and the app still shows nothing, **the schema is not exposed.**

### Know what you are exposing

Exposing `knowledge` makes 1,812 rows readable by any anonymous client. That is
intended — it is public reference data with public sources — but make it a decision
someone takes knowingly, not a side effect of a toggle.

`user_intelligence` is protected by `auth.uid() = user_id` **with no admin
exception**. Neither schema has any write policy at all.

---

## 5 · Fix the vocabulary schema mismatch

**Blocking.** `kg_vocabulary_map` is created in `public` by migration 009 (Step 0) and
queried through the `knowledge`-scoped client by `lib/knowledge.js` (Step 2). One of
the two must move, or vocabulary resolution silently returns nothing — and vocabulary
resolution is what turns a user's typed skill into a graph entity.

Pick one:

**Option A — move the table (recommended; no code change)**

```sql
alter table public.kg_vocabulary_map set schema knowledge;
```

Re-grant the migration's policies in the new schema afterwards.

**Option B — give `resolveTerms()` its own `public` client**

A one-function change in `frontend/lib/knowledge.js`. Requires a code change and a
redeploy, so it is not a deployment-time fix.

- [ ] Option A or B applied
- [ ] `select count(*) from <chosen schema>.kg_vocabulary_map;` runs without error

Then load the crosswalk from the committed CSVs:

```bash
# governance/vocabulary/{skill,sector,district}_crosswalk.csv -> kg_vocabulary_map
```

- [ ] 202 crosswalk rows loaded (33 district + 22 sector + 147 skill)

---

## 6 · Populate the knowledge projection

```bash
python3 -m knowledge_sync plan
```

- [ ] Reports **1,812 rows**, **0 errors**
- [ ] Reports **4 governed `V6-OWNERSHIP` warnings** — expected, declared in
      `known_overlaps.csv` under ADR-005. Any *other* warning stops the deployment.

**Sync one small table first.**

```bash
python3 -m knowledge_sync sync --table kg_schemes --target supabase
psql "$DATABASE_URL" -c "select count(*) from knowledge.kg_schemes;"     # 40
psql "$DATABASE_URL" -c "select scheme_id, scheme_name, confidence_score,
       verification_status, sync_source_package, sync_pending_fields
  from knowledge.kg_schemes limit 3;"
```

- [ ] 40 rows
- [ ] Provenance columns populated; `verification_status` reads `VST-NEEDS_REVIEW`

**Then the rest.**

```bash
python3 -m knowledge_sync sync --target supabase
```

| Table | Expect |
|---|---:|
| `kg_relationships` | 865 |
| `kg_entities` | 647 |
| `kg_businesses` | 85 |
| `kg_districts` | 61 |
| `kg_skills` | 45 |
| `kg_agriculture` | 45 |
| `kg_schemes` | 40 |
| `kg_industries` | 24 |
| **Total** | **1,812** |

- [ ] All eight counts match

### The step that actually matters

```bash
python3 -m knowledge_sync sync --target supabase        # run it a SECOND time
```

- [ ] Reports **0 inserted, 0 updated, 1,812 skipped**

If the second run reports updates, something round-trips differently through Postgres
than through the content hash — usually a numeric returning as a string or a date as a
timestamp. **Understand it before putting the sync on a schedule.** This is the failure
mode most likely to appear on first contact with a real database.

---

## 7 · Generate per-user intelligence

```bash
python3 -m user_intelligence capabilities        # which inputs are AVAILABLE
python3 -m user_intelligence run --fixture resolving_user
```

- [ ] Runs clean, produces a `result_hash`
- [ ] Running twice produces the **same** hash (`generated_at` is excluded by design)

Then per real user, writing the 5 `user_intelligence` tables.

- [ ] `select count(*) from user_intelligence.user_activity_summary;` > 0
- [ ] Rows are keyed `(user_id, rules_version)` — `1.0.0`

**Expect partial results, and expect them to be correct.** Depending on skill
resolution a user fills **1–5 of 10** categories; `mentors` and `events` always return
`NO_DATA_SOURCE`. Empty is the honest answer, not a bug — see
`VERSION1_READINESS_REPORT.md` §0.

---

## 8 · Authentication

- [ ] Supabase → Authentication → Providers → **Google** enabled
- [ ] Google Cloud OAuth client created; authorised redirect URI:
      `https://<project>.supabase.co/auth/v1/callback`
- [ ] Site URL and additional redirect URLs set to the Vercel domain
- [ ] Sign-in tested end to end: `/signin` → Google → `/onboarding` → `/dashboard`
- [ ] A **second** sign-in goes straight to `/dashboard` (`profile_complete` respected)

### Bootstrap the first admin

```sql
update public.profiles set is_admin = true where email = '<your email>';
select id, email, is_admin from public.profiles where is_admin;
```

- [ ] At least one admin exists
- [ ] `/admin` reachable as that user, **and 404/redirects for a non-admin**

> ⚠️ `lib/admin.js:10` returns `isAdmin: true` unconditionally when
> `NODE_ENV === "development"`. Confirm your deployment runs with
> `NODE_ENV=production` — a preview deploy that does not opens all 33 admin routes.
> Backlog S1 fixes this properly.

---

## 9 · Security verification

Run these as an **anonymous** client, not as service role.

```sql
-- another user's computed intelligence must be invisible
select * from user_intelligence.user_skill_profile;              -- expect 0 rows
-- knowledge is public reference data
select count(*) from knowledge.kg_entities;                      -- expect 647
-- and it must be read-only
insert into knowledge.kg_entities (global_entity_id) values ('x'); -- expect DENIED
```

- [ ] Anonymous read of another user's intelligence returns 0 rows
- [ ] Anonymous read of `knowledge` works
- [ ] **Any** write to `knowledge` is denied — no write policy exists on any table
- [ ] `/dashboard`, `/profile`, `/connections`, `/admin` all redirect when signed out

Known defects to accept knowingly for the pilot (backlog S2, S3):

- [ ] `next.config.js` allows images from `hostname: "**"` — open image proxy
- [ ] `kg_roadmap_steps` and `kg_relationships` have `select using (true)` while their
      parent is gated on `status='published'` — draft CMS content is readable.
      Harmless while those 9 tables are empty; **do not let an admin draft a roadmap
      until fixed.**

---

## 10 · Post-deployment smoke test

Do this as a real user in a browser, not with `curl`.

- [ ] `/` loads; `HomepageStats` shows real counts or its empty labels — **never invented numbers**
- [ ] Sign in with Google → `/onboarding`
- [ ] Complete onboarding with skills **`Welding, Food Processing, Tailoring`** (these resolve)
- [ ] `/dashboard` — feed renders **and** at least one knowledge rail has content
- [ ] `/profile` — `IntelligencePanel` shows scores, not `NOT_DEPLOYED`
- [ ] Search "welding" in `KnowledgeSearch` — a `search-researched` group appears
- [ ] `/district/hyderabad` — `DistrictIntelligencePanel` renders 6 sections
- [ ] `/ideas/<any-slug>` — `BusinessKnowledgeSection` renders
- [ ] Every knowledge card shows a **confidence badge** and a **provenance line**
- [ ] `UnverifiedNotice` is visible — it should be; **0 of 2,299 rows are reviewed**
- [ ] Now repeat with skills **`Digital Marketing, Accounting, Data Entry`**

> The second profile is the honest test. Those skills do **not** resolve — only 22.8%
> of onboarding skill terms do — so expect one filled category and a zero skill score.
> **If that looks like a broken product rather than an incomplete one, do not launch
> to a general cohort.** It is the reason `PILOT_PLAN.md` anchors on 4 districts.

---

## 11 · Rollback

Each layer reverses independently.

```bash
# knowledge projection — undo the last sync
python3 -m knowledge_sync snapshots
python3 -m knowledge_sync rollback <run_id> --dry-run
python3 -m knowledge_sync rollback <run_id>
```

Total reset of the derived layers — safe by construction, because both contain nothing
but projections of Git:

```sql
drop schema knowledge cascade;
drop schema user_intelligence cascade;
```

Then re-apply §2.4–2.5 and re-run §6–7.

- [ ] Rollback rehearsed **once**, on the small table, before the pilot

**What rollback cannot do:** restore a row someone edited by hand in the Supabase
console. That edit is in no snapshot and the next sync would overwrite it — which is
why no write policy is granted on any projected table. The situation should be
impossible, not merely discouraged.

---

## 12 · Not blocking, but do it in week one

| | Item | Backlog |
|---|---|---|
| ☐ | CI: 447 tests + `next build` + `generate_migration.py --check` on every PR | O1 |
| ☐ | `.env.example` with the four variables | O2 |
| ☐ | `frontend/migrations/README.md` explaining the absent 008 | O3 |
| ☐ | Delete `backend/` — 412 lines of FastAPI + MongoDB, referenced by nothing | L1 |
| ☐ | Add `pg_trgm` + GIN on `canonical_name` before the entity count grows | P1 |
| ☐ | Nightly `knowledge_sync plan`; alert if it reports changes | — |

---

## Sign-off

| | | |
|---|---|---|
| Deployed by | | |
| Date | | |
| Commit | `git rev-parse HEAD` | |
| Seeded opportunities | ☐ labelled ☐ removed | |
| Vocabulary map | ☐ Option A ☐ Option B | |
| Second sync reported 0/0 | ☐ | |
| Smoke test, resolving skills | ☐ | |
| Smoke test, **non-resolving** skills | ☐ | |
| Go / No-Go for pilot | | |

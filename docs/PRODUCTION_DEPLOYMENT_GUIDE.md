# Production Deployment Guide

**ValueWeave Platform** · fresh clone → live · commit `a274785`

Everything below was verified against this repository. Commands were executed; the
outputs quoted are real.

---

## 0. Read this before you start

> ### Three blockers will stop a first deployment. None is documented anywhere else.
>
> **B1 — Migration 009 cannot apply.** It declares a foreign key to
> `public.kg_entity_registry`, a table **no migration creates**. Applying migrations in
> order fails at 009 with `relation "public.kg_entity_registry" does not exist`.
> Fix in §5.2 — one line.
>
> **B2 — Nothing loads the vocabulary crosswalk.** 202 rows sit in
> `governance/vocabulary/*.csv` and there is **no loader script**. Without them, district
> and skill resolution silently returns nothing. Fix in §7 — a `\copy`.
>
> **B3 — The intelligence engine has no Supabase writer.** `python3 -m user_intelligence
> run` computes and prints JSON to stdout; there is no `--target supabase`. The five
> `user_intelligence` tables must be filled by a pipeline you supply. §9.

Everything else in this guide is routine. These three are the reason it exists.

**Expected end state:** the application serves 1,812 researched rows. **Expect empty
personalised rails** for most users — 22.8% skill resolution and two structurally dead
recommendation rules are data gaps, not deployment failures. `POST_DEPLOYMENT_VALIDATION.md`
says which empty states are correct.

---

## 1. Fresh clone

```bash
git clone https://github.com/ravikumarbanoth/Valueweave-New.git
cd Valueweave-New
git rev-parse HEAD          # record this — every rollback references it
```

| Requirement | Verified working | Note |
|---|---|---|
| Python | **3.11.15** | 3.11+. **Standard library only** — no `pip install` |
| Node | **22.22.2** | 18+ |
| npm | **10.9.7** | |
| `psql` | any | Or the Supabase SQL editor |

`frontend/package.json` declares no `engines` field, so nothing enforces the Node
version at install time. Use 18 or newer.

---

## 2. Install

```bash
cd frontend && npm ci && cd ..
```

`npm ci`, not `npm install` — the lockfile is committed and a first deployment should
install exactly what was tested.

```bash
python3 tests/run_all.py --quiet
```

**Expected:** `TOTAL 478 0 0 0 PASS` across 13 suites.

A failure here means the clone is wrong or the toolchain differs. **Do not continue** —
every later step assumes this passes.

---

## 3. Environment variables

Four are read by application source. There is **no `.env.example`**; this table is the
reference.

| Variable | Scope | Required | If missing |
|---|---|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | Vercel, browser | **Yes** | **Silent** — every read empty |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Vercel, browser | **Yes** | **Silent** — every read empty |
| `NEXT_PUBLIC_BASE_URL` | Vercel, build | Yes | Wrong canonical URLs, broken sitemap |
| `ADMIN_EMAILS` | Vercel, server | Recommended | No admin can bootstrap |

Operator shell only, never in Vercel:

| `SUPABASE_URL` · `SUPABASE_SERVICE_ROLE_KEY` · `DATABASE_URL` |
|---|

> **The service role key bypasses RLS.** It is the only credential that can write to the
> `knowledge` schema, and that is the only reason it exists. Never in a `NEXT_PUBLIC_*`
> variable, never in a committed file, never in shell history — source a gitignored
> `.env`. Nothing else in the platform holds it, so rotating it breaks only the sync.

```bash
set -a; . ./.env.deploy; set +a      # gitignore .env.deploy first
echo "${SUPABASE_URL:?}" "${DATABASE_URL:?}" > /dev/null && echo "env ok"
```

---

## 4. Supabase configuration

1. Create the project. Record the region — it cannot be changed later.
2. **Authentication → Providers → Google**: enable, paste the OAuth client id/secret.
3. Google Cloud → authorised redirect URI:
   `https://<project>.supabase.co/auth/v1/callback`
4. **Authentication → URL Configuration**: Site URL = your Vercel domain; add it to
   redirect URLs too.
5. Leave **API → Exposed schemas** alone for now — §6.

---

## 5. Schema

### 5.1 Order

Later sets hold foreign keys into earlier ones. **50 tables across 4 schemas, from 5
migration sets in 3 directories.**

```bash
psql "$DATABASE_URL" -f frontend/supabase_schema.sql                      # 3 tables
psql "$DATABASE_URL" -f frontend/migrations/001_research_articles.sql
psql "$DATABASE_URL" -f frontend/migrations/002_collaboration_marketplace.sql
psql "$DATABASE_URL" -f frontend/migrations/003_seed_opportunities.sql    # ← see §5.3
psql "$DATABASE_URL" -f frontend/migrations/004_admin_analytics.sql
psql "$DATABASE_URL" -f frontend/migrations/005_growth_intelligence.sql
psql "$DATABASE_URL" -f frontend/migrations/006_visitor_analytics.sql
psql "$DATABASE_URL" -f frontend/migrations/007_engagement_retention.sql
#   there is no 008 — planned, then superseded by the `knowledge` schema
psql "$DATABASE_URL" -f frontend/migrations/009_vocabulary_crosswalk.sql  # ← FAILS, see 5.2
psql "$DATABASE_URL" -f frontend/migrations/010_missing_application_features.sql
psql "$DATABASE_URL" -f supabase/migrations/202606200001_geo_video_devops.sql
psql "$DATABASE_URL" -f supabase/migrations/202606200002_entrepreneurship_knowledge_graph.sql
psql "$DATABASE_URL" -f knowledge_sync/migrations/001_knowledge_schema.sql      # 9 tables
psql "$DATABASE_URL" -f user_intelligence/migrations/001_user_intelligence.sql  # 5 tables
```

### 5.2 ⚠️ Blocker B1 — migration 009 will fail

```sql
-- frontend/migrations/009_vocabulary_crosswalk.sql:30
global_entity_id text references public.kg_entity_registry(global_entity_id) on delete restrict,
```

**`public.kg_entity_registry` is created by no migration in this repository.** It was to
come from the abandoned migration 008; Step 1 replaced that plan with the dedicated
`knowledge` schema and 009 kept the reference.

```
ERROR:  relation "public.kg_entity_registry" does not exist
```

**Fix — drop the foreign key, keep the column.** The referent now lives in
`knowledge.kg_entities`, a different schema, and a cross-schema FK to a table the sync
soft-deletes from would block legitimate deletes:

```bash
sed 's| references public\.kg_entity_registry(global_entity_id) on delete restrict||' \
    frontend/migrations/009_vocabulary_crosswalk.sql > /tmp/009_patched.sql
psql "$DATABASE_URL" -f /tmp/009_patched.sql
```

**Integrity is not lost.** `009` already carries a
`kg_vocab_resolution_is_coherent` CHECK — a resolved row must have an entity id, an
unresolved row must not — and `tests/test_vocabulary.py` enforces the same rule against
the CSVs at build time.

**Do not "fix" this by creating an empty `kg_entity_registry`.** A second entity table in
`public`, alongside the CMS `kg_*` tables and the real `knowledge.kg_entities`, is a
third knowledge system.

### 5.3 Decide about the 500 seeded opportunities

`003_seed_opportunities.sql` inserts **500 template-generated opportunities**
(`created_by = 'system_seed'`), synthetic and without provenance, and they are the main
content of `/dashboard` and `/explore`.

Label them, or skip the migration:

```sql
update public.opportunities
   set description = '[Illustrative example — not a verified opportunity] ' || description
 where created_by = 'system_seed';
```

The platform's rule is *never fabricate*. This is the one place it is not held, and
leaving 500 unlabelled synthetic rows next to 40 fully-sourced MSMEs is a deployment
choice, not an oversight.

### 5.4 Verify

```bash
psql "$DATABASE_URL" -c "\dt knowledge.*"                # 9
psql "$DATABASE_URL" -c "\dt user_intelligence.*"        # 5
psql "$DATABASE_URL" -c \
  "select count(*) from pg_tables
    where schemaname in ('public','knowledge','user_intelligence');"   # 50
psql "$DATABASE_URL" -c \
  "select tablename from pg_tables
    where schemaname in ('public','knowledge','user_intelligence')
      and rowsecurity = false;"                          # 0 rows
```

---

## 6. ⚠️ Schema exposure — the step that fails silently

**Supabase Dashboard → Project Settings → API → Exposed schemas**, add:

```
knowledge, user_intelligence
```

Without it, `createClient(url, key, { db: { schema: "knowledge" } })` errors on every
query, `safe()` in `lib/knowledge.js` catches it by design and returns `[]`, and every
page renders its empty state.

**The application will look exactly as it does before deployment, and nothing anywhere
will say why.** No console error, no log line, no failed request the user can see.

Diagnostic — if these return rows and the app shows nothing, the schema is not exposed:

```sql
select count(*) from knowledge.kg_entities;      -- 647 after §8
```

**Know what you are exposing.** This makes 1,812 rows readable by any anonymous client.
That is intended — public reference data with public sources — but make it a decision
someone takes, not a side effect of a toggle. `user_intelligence` is gated on
`auth.uid() = user_id` with **no admin exception**; neither schema has any write policy.

---

## 7. ⚠️ Blocker B2 — load the vocabulary crosswalk

**No loader script exists.** `governance/vocabulary/` holds `build_crosswalk.py` (which
*generates* the CSVs from packages) and the three CSVs. Nothing writes them to Postgres.

Without this, `resolveTerms()` returns nothing and **every district and skill a user
types fails to resolve** — the dashboard, district pages and skill matching all go quiet.

```bash
# 202 rows: 33 district + 22 sector + 147 skill
for kind in district sector skill; do
  psql "$DATABASE_URL" -c "\copy public.kg_vocabulary_map(
      term_kind, source_vocab, source_term, normalised_term,
      global_entity_id, entity_type, canonical_name,
      match_method, match_score, notes)
    from 'governance/vocabulary/${kind}_crosswalk.csv' with (format csv, header true)"
done

psql "$DATABASE_URL" -c "select term_kind, count(*) from public.kg_vocabulary_map group by 1;"
```

**Expected:** `district 33 · sector 22 · skill 147`.

### The related schema mismatch

`kg_vocabulary_map` lives in **`public`** (migration 009) and `lib/knowledge.js` queries
it through the **`knowledge`**-scoped client. Loading it is necessary and not sufficient.

**Recommended — move the table, no code change:**

```sql
alter table public.kg_vocabulary_map set schema knowledge;
```

Then re-grant 009's policies in the new schema. The alternative is a code change to give
`resolveTerms()` its own `public` client, which needs a redeploy and is therefore not a
deployment-time fix.

---

## 8. Knowledge Engine build and sync

### 8.1 Rebuild the graph (optional — artifacts are committed)

```bash
python3 knowledge_graph/build_graph.py
python3 knowledge_graph/validate_graph.py
```

**Expected from the validator** *(real output)*:

```
  entities ................. 647
  relationships ............ 865
  connectivity ............. 505/647 (78.05%)
WARNINGS (1):
  [G10-ORPHANS] 142 entities have no relationships: …
PASS — graph is structurally sound, provenance-complete and ownership-clean.
```

**The orphan warning is expected**, not a deployment failure — `GRAPH_VALIDATION_REPORT.md`.

The rebuild rewrites `created_at`/`updated_at` to today, so `git status` will show a diff
in the graph artifacts even when nothing changed. **On a deployment host, skip the
rebuild and use the committed artifacts** unless a package changed.

### 8.2 Plan the sync — no credentials needed

```bash
python3 knowledge_sync/generate_migration.py --check
python3 -m knowledge_sync plan
```

**Expected** *(real output)*:

```
  001_knowledge_schema.sql: matches the specs
  extract    kg_entities: 647 rows          … 8 tables, 1,812 rows total
  validate   0 error(s), 4 warning(s)
  kg_entities  insert=647  update=0  delete=0  skip=0
```

**The 4 warnings are expected** — declared cross-package overlaps governed by ADR-005.
**Any error, or a fifth warning, stops the deployment.**

### 8.3 One table first

```bash
python3 -m knowledge_sync sync --table kg_schemes --target supabase
psql "$DATABASE_URL" -c "select count(*) from knowledge.kg_schemes;"    # 40
psql "$DATABASE_URL" -c "select scheme_name, confidence_score, verification_status,
                                sync_source_package
                           from knowledge.kg_schemes limit 3;"
```

`verification_status` must read `VST-NEEDS_REVIEW`. **All 2,299 rows are unreviewed** —
correct, and the reason `UnverifiedNotice` renders everywhere.

### 8.4 The rest, then prove idempotency

```bash
python3 -m knowledge_sync sync --target supabase
python3 -m knowledge_sync sync --target supabase     # run it TWICE
```

| Table | Rows |
|---|---:|
| `kg_relationships` | 865 |
| `kg_entities` | 647 |
| `kg_businesses` | 85 |
| `kg_districts` | 61 |
| `kg_skills` · `kg_agriculture` | 45 each |
| `kg_schemes` | 40 |
| `kg_industries` | 24 |
| **Total** | **1,812** |

**The second run must report `0 inserted, 0 updated, 1812 skipped`.**

If it reports updates, something round-trips differently through Postgres than through
the content hash — usually a numeric returning as a string or a date as a timestamp.
**Understand it before putting the sync on a schedule.** This is the failure mode most
likely to appear on first contact with a real database, and nothing in this repository has
ever run against one.

---

## 9. ⚠️ Blocker B3 — per-user intelligence

**The engine has no Supabase writer.** `python3 -m user_intelligence run` reads Git,
computes, and prints. There is no `--target supabase`.

```bash
python3 -m user_intelligence capabilities
python3 -m user_intelligence run --fixture resolving --explain | head -40
```

**Expected:** 8 scores, 10 categories, `mentors` and `events` reporting `NO DATA` —
correct, no source exists for either.

To populate the five tables you must supply a pipeline:

```
for each user:
  1. read profiles/connections/collaborator_profiles  (service role)
  2. write a rows JSON
  3. python3 -m user_intelligence --json run --profile-json <file> --table <t>
  4. upsert stdout into user_intelligence.<t>, keyed (user_id, rules_version)
```

`--table` selects which table's rows to emit; `--json` is a **top-level** flag and must
precede the subcommand.

**Until that pipeline exists, `/dashboard` shows `NOT_COMPUTED` for every user.** The
page renders correctly and says so. This is the largest piece of missing deployment
tooling in the platform, and it is a build task, not a documentation gap.

---

## 10. Bootstrap the first admin

```sql
update public.profiles set is_admin = true where email = '<your email>';
select id, email, is_admin from public.profiles where is_admin;
```

> ⚠️ `lib/admin.js:10` returns `isAdmin: true` unconditionally when
> `NODE_ENV === "development"`. Confirm production runs with `NODE_ENV=production` — a
> preview deploy that does not opens all 33 `/admin/*` routes. RLS still gates the
> database; this is the routing gate. Backlog S1.

---

## 11. Frontend deployment

```bash
cd frontend && npm ci && npm run build
```

**Expected:** `exit 0`, `✓ Generating static pages (214/214)`, **0 prerender errors**.

The build must succeed **without database access** — graph detail pages are rendered on
demand for exactly this reason. If it fails on a Supabase call, something regressed.

**Vercel:** root directory `frontend`, framework Next.js, build `npm run build`, install
`npm ci`. Set the four §3 variables for **Production and Preview**. Never set
`SUPABASE_SERVICE_ROLE_KEY` in Vercel.

Self-hosted: `npm run start` (port 3000) behind a TLS terminator.

---

## 12. Verification

Full script in `POST_DEPLOYMENT_VALIDATION.md`. The two-minute version:

```bash
psql "$DATABASE_URL" -c "select count(*) from knowledge.kg_entities;"        # 647
psql "$DATABASE_URL" -c "select count(*) from public.kg_vocabulary_map;"     # 202
curl -sI https://<domain>/knowledge | head -1                                # 200
```

Then sign in with Google, complete onboarding with **`Welding, Food Processing,
Tailoring`** (these resolve), and confirm `/dashboard` shows at least one populated rail.

**Then repeat with `Digital Marketing, Accounting, Data Entry`** — these do *not* resolve,
and that is the honest test. If the result reads as broken rather than incomplete, read
`PILOT_PLAN.md` before inviting a general cohort.

---

## 13. Order of operations

```
1  clone + npm ci + tests            478 pass
2  environment variables             4 app + 3 operator
3  Supabase project + Google OAuth
4  migrations 1–14                   ⚠️ patch 009 first (§5.2)
5  EXPOSE SCHEMAS                    ⚠️ silent if skipped (§6)
6  load crosswalk + move table       ⚠️ no loader exists (§7)
7  sync one table, then all, twice   1,812 rows; second run 0/0
8  bootstrap admin
9  build + deploy frontend           214/214
10 validate                          POST_DEPLOYMENT_VALIDATION.md
```

Steps 4, 5 and 6 are where a first deployment fails. Two of the three fail **silently**.

---

**Companion documents:** `FIRST_DEPLOYMENT_CHECKLIST.md` (per-step commands, expected
output, validation, rollback) · `POST_DEPLOYMENT_VALIDATION.md` ·
`OPERATIONAL_RUNBOOK.md` · `PRODUCTION_MONITORING.md`

`DEPLOYMENT_CHECKLIST.md` remains the sign-off sheet from the v1.0 readiness assessment.
**Where the two disagree, this guide is newer** — it was written by executing the
commands, and it is what surfaced B1, B2 and B3.

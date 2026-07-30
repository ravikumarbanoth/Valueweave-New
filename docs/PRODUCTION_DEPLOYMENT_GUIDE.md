# Production Deployment Guide

**ValueWeave Platform** · fresh clone → live · revised for the Operational Completion Sprint

Everything below was verified against this repository. Commands were executed; the
outputs quoted are real.

---

## 0. Read this before you start

This guide was written by executing a first deployment against the repository, and it
found three blockers. **All three are now closed in code.** They are still described
below — you are deploying a database that may be in the *pre*-repair state, and knowing
what the repair does is the difference between running it and trusting it.

> ### The three blockers, and what closed each
>
> **B1 — Migration 009 could not apply.** It declares a foreign key to
> `public.kg_entity_registry`, a table **no migration creates**. Applying migrations in
> order failed at 009 with `relation "public.kg_entity_registry" does not exist`.
> **Closed by `frontend/migrations/011_repair_vocabulary_crosswalk.sql`** — a forward
> migration. 009 is unmodified and stays in history. §5.2.
>
> **B2 — Nothing loaded the vocabulary crosswalk.** 202 rows sit in
> `governance/vocabulary/*.csv` with no loader. Without them, district and skill
> resolution silently returns nothing. **Closed by `scripts/load_crosswalk.sh`** —
> staged, idempotent, row-count-verified. §7.
>
> **B3 — The intelligence engine had no Supabase writer.** `python3 -m user_intelligence
> run` computed and printed JSON to stdout; there was no way to persist it. **Closed by
> `user_intelligence/writer.py`**, driven by `python3 -m user_intelligence write --target
> supabase` or `scripts/run_user_intelligence.sh`. §9.

### The scripted path

Nine scripts in `scripts/` execute what the rest of this guide describes by hand. They
share `scripts/_common.sh` (`set -Eeuo pipefail`, `DRY_RUN=1`, `VW_ASSUME_YES`), print a
step summary, and are safe to re-run.

| Script | Does |
|---|---|
| `first_deploy.sh` | Orchestrates the whole sequence below, with a manual gate at §6 |
| `run_graph_build.sh` | Rebuilds and validates the graph; `--check` detects date-only churn |
| `load_crosswalk.sh` | §7 — loads 202 crosswalk rows into `knowledge.kg_vocabulary_map` |
| `run_sync.sh` | §8 — plan, sync, then re-run and require `0 inserted, 0 updated` |
| `run_user_intelligence.sh` | §9 — computes and (with `--apply`) writes the five tables |
| `verify_deployment.sh` | §12 — eight sections of post-deployment assertions |
| `health_check.sh` | Ongoing — JSON out, exit `0` healthy / `1` degraded / `2` failed |
| `rollback.sh` | Five-level ladder; level 5 (PITR) is documented, not scripted |

Read the section before running its script. Every script honours `DRY_RUN=1`, which
prints the commands it would run and touches nothing:

```bash
DRY_RUN=1 scripts/first_deploy.sh
```

Everything else in this guide is routine. These three blockers are the reason it exists.

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
psql "$DATABASE_URL" -f frontend/migrations/009_vocabulary_crosswalk.sql  # ← fails; 011 repairs
psql "$DATABASE_URL" -f frontend/migrations/010_missing_application_features.sql
psql "$DATABASE_URL" -f frontend/migrations/011_repair_vocabulary_crosswalk.sql  # ← see §5.2
psql "$DATABASE_URL" -f supabase/migrations/202606200001_geo_video_devops.sql
psql "$DATABASE_URL" -f supabase/migrations/202606200002_entrepreneurship_knowledge_graph.sql
psql "$DATABASE_URL" -f knowledge_sync/migrations/001_knowledge_schema.sql      # 9 tables
psql "$DATABASE_URL" -f user_intelligence/migrations/001_user_intelligence.sql  # 5 tables
```

`first_deploy.sh` runs this list, **expects 009 to fail**, and continues to 011. Any other
migration failing stops it.

### 5.2 Blocker B1 — migration 009 fails, and 011 repairs it

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

**009 is not modified.** It stays in history exactly as it shipped. The repair is a
forward migration:

```bash
psql "$DATABASE_URL" -f frontend/migrations/011_repair_vocabulary_crosswalk.sql
```

011 handles all four states a database can be in — 009 never applied, 009 applied on a
pre-existing database, 011 already applied, and both copies present — so it is safe to run
repeatedly and safe to run before you have worked out which state you are in. It:

* creates `knowledge.kg_vocabulary_map`, **with no foreign key**;
* if a `public.kg_vocabulary_map` exists, drops its FK and copies the rows across
  (`on conflict do nothing`, so the projected row wins);
* keeps the `kg_vocab_resolution_is_coherent` CHECK from 009;
* adds the lookup, entity and method indexes;
* enables RLS with a read-only policy and no write policy at all;
* comments the `public` table as superseded — **it is not dropped**, so rollback is
  `drop table knowledge.kg_vocabulary_map;` with no data loss.

**This also fixes the second, quieter defect.** 009 created the table in `public` while
`frontend/lib/knowledge.js` queries it through a `knowledge`-scoped client — so even a
*successful* 009 would have produced a table nothing could read. §7 no longer needs a
schema move; 011 puts the table where the code looks.

**No FK is re-added, deliberately.** The referent is `knowledge.kg_entities`, which
`knowledge_sync` soft-deletes from and never hard-deletes, so a real FK would never fire
in normal operation — and on the one path where it could, `sync --full` after a restore,
it would block a legitimate rebuild. Integrity is enforced by the CHECK, by
`tests/test_vocabulary.py` against `entities.csv`, and by `health_check.sh`, which reports
crosswalk rows whose entity is missing from the projection.

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

## 7. Blocker B2 — load the vocabulary crosswalk

`governance/vocabulary/` holds `build_crosswalk.py` (which *generates* the CSVs from
packages) and the three CSVs. **`scripts/load_crosswalk.sh` writes them to Postgres.**

Without this, `resolveTerms()` returns nothing and **every district and skill a user
types fails to resolve** — the dashboard, district pages and skill matching all go quiet.
Nothing errors; the pages simply render their empty states.

```bash
DRY_RUN=1 scripts/load_crosswalk.sh      # see the SQL first
scripts/load_crosswalk.sh
```

**Expected:** `district 33 · sector 22 · skill 147`, total **202**.

The script stages each CSV into a temporary table and then `insert … on conflict
(term_kind, source_vocab, normalised_term) do update`, so a re-run corrects drifted rows
rather than duplicating or failing. It refuses to finish unless the final count is exactly
`EXPECTED_TOTAL=202` — a partially loaded crosswalk resolves some terms and not others,
which reads as missing data rather than as a broken load.

It targets `knowledge.kg_vocabulary_map`, which **migration 011 must have created first**
(§5.2). Running it against a database where only the `public` copy exists fails loudly.

The manual `\copy` this replaces is preserved in git history; there is no reason to use it.

---

## 8. Knowledge Engine build and sync

### 8.1 Rebuild the graph (optional — artifacts are committed)

```bash
scripts/run_graph_build.sh            # build + validate
scripts/run_graph_build.sh --check    # validate only; fails if the build would change anything
```

Equivalent to `python3 knowledge_graph/build_graph.py && python3
knowledge_graph/validate_graph.py`, with one addition: `--check` compares the rebuilt
artifacts against the committed ones **with the `built_at` date normalised**, so it can
tell a real content change from the date-only churn described below.

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
scripts/run_sync.sh --plan-only
```

Wrapping `python3 knowledge_sync/generate_migration.py --check` and `python3 -m
knowledge_sync plan`.

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
scripts/run_sync.sh
```

The script plans first and **refuses to sync unless the plan reports exactly the four
governed warnings and zero errors**. It asks for confirmation if the plan would delete
more than 50 rows. Then it syncs, and **runs the sync a second time automatically**,
failing if that run is not `0 inserted, 0 updated` — the idempotency proof below is not
something you have to remember to do.

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

## 9. Blocker B3 — per-user intelligence

`python3 -m user_intelligence run` reads Git, computes, and prints. **`user_intelligence
write` persists that result to the `user_intelligence` schema** — the writer that did not
exist.

Dry run first, against the in-memory target, with no credentials:

```bash
python3 -m user_intelligence capabilities
python3 -m user_intelligence run --fixture resolving --explain | head -40
scripts/run_user_intelligence.sh                       # fixture, memory target, writes nothing
```

**Expected:** 8 scores, 10 categories, `mentors` and `events` reporting `NO DATA` —
correct, no source exists for either.

Then, for real:

```bash
# read every profile from the database, compute, and write
scripts/run_user_intelligence.sh --from-db --apply

# or one user at a time
python3 -m user_intelligence write --target supabase --profile-json <file>
```

`--apply` is the only thing that requires `SUPABASE_SERVICE_ROLE_KEY`; without it the
script says so and uses the in-memory target. `--from-db` selects only the columns the
engine reads — a `select *` would pull personal data into a temp file for no reason.

### What the writer guarantees

* **Upsert, not insert.** Conflict keys are `(user_id, rules_version)` for the four
  single-row tables and `(user_id, rules_version, category, item_id)` for
  `user_recommendations`.
* **Idempotent by result hash.** A user whose inputs have not changed costs one read and
  writes nothing. `--force` overrides.
* **Recommendations are pruned, always.** Items no longer recommended are deleted, and
  the prune runs even when the new result has zero recommendations — dropping to zero is a
  result, not an absence of one.
* **Retry.** Three attempts per step, backing off 1s then 4s.
* **`user_activity_summary` is written last.** It is the row `/dashboard` reads to decide
  whether intelligence exists, so a partial failure leaves the user reading
  `NOT_COMPUTED` and replays cleanly, rather than showing half a profile as if it were
  whole.
* **Append-only log** at `user_intelligence/state/writer_log.jsonl` — one JSON line per
  run with per-step outcomes. Gitignored; it is runtime state, not source.

Before this ran, `/dashboard` showed `NOT_COMPUTED` for every user. That is still the
correct state for any user the writer has not yet processed, and the page says so.

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

```bash
scripts/verify_deployment.sh          # eight sections, one pass/fail per assertion
scripts/health_check.sh               # JSON; exit 0 healthy / 1 degraded / 2 failed
```

`verify_deployment.sh` is the scripted form of `POST_DEPLOYMENT_VALIDATION.md`. It checks
schemas and table counts, that the `knowledge` schema is **exposed to the anon key** (the
§6 failure, which nothing else surfaces), crosswalk row counts by kind, the 1,812 synced
rows, sync idempotency, user-intelligence population, and that search and recommendations
return results. It marks the 0 scheme→district edges as a **`KNOWN GAP`** rather than a
failure — that is a data gap tracked in `GRAPH_CONNECTIVITY_PLAN.md`, not a bad deploy.

`health_check.sh` is the same idea reduced to something a monitor can poll. It performs
the exposure check with the **anon key** and an `Accept-Profile: knowledge` header,
because the service-role key can read a schema that is not exposed and would report
healthy while every page renders empty.

The two-minute manual version:

```bash
psql "$DATABASE_URL" -c "select count(*) from knowledge.kg_entities;"          # 647
psql "$DATABASE_URL" -c "select count(*) from knowledge.kg_vocabulary_map;"   # 202
curl -sI https://<domain>/knowledge | head -1                                  # 200
```

Then sign in with Google, complete onboarding with **`Welding, Food Processing,
Tailoring`** (these resolve), and confirm `/dashboard` shows at least one populated rail.

**Then repeat with `Digital Marketing, Accounting, Data Entry`** — these do *not* resolve,
and that is the honest test. If the result reads as broken rather than incomplete, read
`PILOT_PLAN.md` before inviting a general cohort.

---

## 13. Order of operations

```
1  clone + npm ci + tests            530 pass
2  environment variables             4 app + 3 operator
3  Supabase project + Google OAuth
4  migrations 1–15                   009 fails, 011 repairs it        (§5.2)
5  EXPOSE SCHEMAS                    ⚠️ silent if skipped             (§6)
6  load crosswalk                    scripts/load_crosswalk.sh        (§7)
7  sync, then prove idempotent       scripts/run_sync.sh              (§8)
8  compute user intelligence         scripts/run_user_intelligence.sh (§9)
9  bootstrap admin
10 build + deploy frontend           214/214
11 validate                          scripts/verify_deployment.sh     (§12)
```

`scripts/first_deploy.sh` runs 4 and 6–8 and 11, stopping at a **manual gate before 5** —
exposing a schema is a dashboard toggle and a decision about what becomes publicly
readable, so no script does it for you.

Step 5 is now the only step of these that fails silently, and it is the one a script
cannot take.

---

## 14. Rollback

```bash
scripts/rollback.sh --help        # the ladder
scripts/rollback.sh list          # available rollback points
```

Five levels, and you stop at the first one that works:

| # | Level | Command | Cost |
|---|---|---|---|
| 1 | frontend | Vercel → Deployments → Promote previous | not scripted |
| 2 | sync run | `scripts/rollback.sh sync <run_id>` | loses that run |
| 3 | knowledge schema | `scripts/rollback.sh knowledge` | loses nothing — rebuilt from Git |
| 4 | user intelligence | `scripts/rollback.sh intelligence` | loses computed rows, all reproducible |
| 5 | `public` schema | Supabase point-in-time restore | **destroys user data** |

Levels 3 and 4 are cheap precisely because Git is the source of truth: the `knowledge`
schema is a projection and the `user_intelligence` schema is a computation, so both can be
dropped and rebuilt. **Level 5 is deliberately not scripted** — it is the only level that
destroys something a user created, and it needs a decision rather than a command.

---

**Companion documents:** `FIRST_DEPLOYMENT_CHECKLIST.md` (per-step commands, expected
output, validation, rollback) · `POST_DEPLOYMENT_VALIDATION.md` ·
`OPERATIONAL_RUNBOOK.md` · `PRODUCTION_MONITORING.md`

`DEPLOYMENT_CHECKLIST.md` remains the sign-off sheet from the v1.0 readiness assessment.
**Where the two disagree, this guide is newer** — it was written by executing the
commands, and it is what surfaced B1, B2 and B3.

**Where this guide and the scripts disagree, the scripts are newer.** They are covered by
`tests/test_deployment.py`; prose is not.

# Manual Deployment Plan — creating the knowledge schema

**ValueWeave v1.0 · everything below is read from the migration files, not recalled**

---

## The three questions, answered

### 1. Is `scripts/first_deploy.sh` intended to create the knowledge schema?

**Yes.** Step 4 of the script applies exactly the two migrations that create it:

```bash
step "4 · Derived schemas"
psql_file "$VW_ROOT/knowledge_sync/migrations/001_knowledge_schema.sql"
psql_file "$VW_ROOT/user_intelligence/migrations/001_user_intelligence.sql"
```

The script's own header is explicit about what it does *not* do:

> It does NOT: create the Supabase project, configure Google OAuth, expose the
> schemas, or deploy the frontend. Three of those are dashboard actions and one
> belongs to Vercel; a script that pretended to do them would report success for
> work it never did.

### 2. Can it be executed automatically from GitHub Actions?

**The SQL half can. One step cannot, and it is the step that is currently blocking you.**

| Requirement | In GitHub Actions |
|---|---|
| `need_cmd psql python3` | ✅ `ubuntu-latest` ships `psql` |
| `need_env DATABASE_URL` | ✅ already a secret |
| Steps 0–4, 6–9 | ✅ non-interactive, idempotent |
| **Step 5 — expose the schemas** | ❌ **a Supabase Dashboard action. No SQL can do it.** |

Step 5 calls `confirm`, which in a non-interactive shell does this:

```bash
if [[ ! -t 0 ]]; then
  fail "$prompt
  Refusing in a non-interactive shell. Set VW_ASSUME_YES=1 to proceed."
fi
```

`VW_ASSUME_YES=1` makes the *prompt* pass. It does not expose the schema — it
just stops asking. Running the script in CI with that flag would sail past the
one thing that must be true and fail later, further from the cause.

### 3. Is it intentionally designed to be run once, manually?

**Partly, and the manual part is deliberate.** The migrations are automatable
and idempotent. Schema exposure is a dashboard toggle and a decision about what
becomes publicly readable — the script asks a human rather than pretending.

---

## ⚠️ The finding that changes your plan

**Exposing the `knowledge` schema is not only for the frontend. Your sync cannot
write without it either.**

`knowledge_sync/adapters.py` writes through the Supabase SDK:

```python
self._client = create_client(self.url, self.key)
...
self.client.schema(self.schema).table(table)
```

That is PostgREST, not a Postgres connection. PostgREST only serves schemas
listed in **Exposed schemas**, and that is a server config, **not a permission
check** — so the service-role key does not bypass it the way it bypasses RLS.
Against an unexposed schema every request returns:

```
PGRST106  The schema must be one of the following: public, graphql_public
```

So the order is: **create the tables, then expose the schema, then re-run the
sync.** Creating the tables alone will not unblock Apply.

---

## What I could not verify

**I cannot tell you what your Supabase project already contains.** This
environment has no `SUPABASE_URL`, no `SUPABASE_SERVICE_ROLE_KEY`, no
`DATABASE_URL`, and `supabase.com` returns HTTP 000. `frontend/.env.local`
contains placeholder values.

Run §A below in the SQL Editor and it will tell you exactly which of the steps
in §C you still need. **Do not skip it** — several migrations behave differently
depending on what already exists.

---

## ⚠️ A prerequisite found by executing the migrations

`knowledge_sync/migrations/001_knowledge_schema.sql` **cannot be run on its own.**
Its final statement is a policy on `knowledge.sync_runs` that calls
`public.is_valueweave_admin()`:

```
ERROR:  function public.is_valueweave_admin() does not exist
```

That function is created by
`supabase/migrations/202606200002_entrepreneurship_knowledge_graph.sql`, which in
turn needs `public.profiles`.

**This matters more than it looks, because 001 is not transactional.** Applying
it without the function creates 9 tables, 34 indexes and 8 of 9 policies, then
errors — leaving a schema that looks complete in the table list and has
`sync_runs` unprotected. Verified by doing exactly that against a real
PostgreSQL 16; the verification query reports it as `PARTIAL — 6 table(s)
missing` with 8 policies rather than 15.

`user_intelligence/migrations/001_user_intelligence.sql` has the same shape: it
carries a foreign key to `public.profiles` and fails without it.

**Your application is running, so `public.profiles` almost certainly exists.
Whether `is_valueweave_admin()` does depends on whether 202606200002 was ever
applied — that same file creates the `public.kg_*` CMS tables behind `/skills`
and `/schemes`.** §A tells you.

---

## A · Audit first — paste this into the Supabase SQL Editor

**Use `sql/verify_knowledge_schema.sql`** — the full version, tested against a
real PostgreSQL 16 in all three states (clean, partial, complete). It checks
prerequisites, schemas, all 15 tables, index counts, policy counts, RLS,
unexpected write policies, grants, row counts, and prints a one-line verdict.

The short version, if you just want the shape of it:

```sql
-- What exists today?
select
  (select count(*) from information_schema.schemata
    where schema_name = 'knowledge')                        as knowledge_schema,
  (select count(*) from information_schema.schemata
    where schema_name = 'user_intelligence')                as ui_schema,
  (select count(*) from pg_tables where schemaname = 'knowledge')          as knowledge_tables,
  (select count(*) from pg_tables where schemaname = 'user_intelligence')  as ui_tables,
  (select count(*) from pg_tables where schemaname = 'public')             as public_tables,
  (select count(*) from pg_policies where schemaname = 'knowledge')        as knowledge_policies,
  (select to_regclass('public.kg_vocabulary_map') is not null)             as old_crosswalk_exists,
  (select to_regclass('public.kg_entity_registry') is not null)            as registry_exists;

-- Which of the 9 knowledge tables are present?
select t.name,
       to_regclass('knowledge.' || t.name) is not null as exists
from (values ('kg_entities'),('kg_relationships'),('kg_districts'),('kg_skills'),
             ('kg_schemes'),('kg_businesses'),('kg_industries'),('kg_agriculture'),
             ('kg_vocabulary_map'),('sync_runs')) as t(name)
order by 2, 1;
```

**Expected on a database where nothing has been done:** every count `0`, every
`exists` false.

| If you see | It means | Do |
|---|---|---|
| `knowledge_tables = 0` | nothing created | all of §C |
| `knowledge_tables = 9`, no `kg_vocabulary_map` | `001` ran, `011` did not | §C step 3 only |
| `knowledge_tables = 10`, `knowledge_policies = 10` | both ran | skip to §D |
| `old_crosswalk_exists = true` | `009` succeeded on an older database | run `011` — it migrates those rows across |
| `registry_exists = true` | someone created the phantom table | **do not use it.** See §E |

---

## B · Execution order

From `scripts/first_deploy.sh`, in the order it applies them. **You only need
steps 2–4 for the knowledge schema.** Steps marked "application" are probably
already applied, since your app is running.

| # | File | Creates | Needed for the sync? |
|---|---|---|---|
| 1 | `frontend/supabase_schema.sql` | 3 tables | application |
| 2 | `frontend/migrations/001`–`007` | 17 tables | application |
| 3 | `frontend/migrations/009_vocabulary_crosswalk.sql` | — | **expected to FAIL** |
| 4 | `frontend/migrations/010_missing_application_features.sql` | 5 tables | application |
| **5** | **`frontend/migrations/011_repair_vocabulary_crosswalk.sql`** | `knowledge.kg_vocabulary_map` | **YES** |
| 6 | `supabase/migrations/202606200001_geo_video_devops.sql` | 1 table | application |
| 7 | `supabase/migrations/202606200002_entrepreneurship_knowledge_graph.sql` | 9 CMS tables | application |
| **8** | **`knowledge_sync/migrations/001_knowledge_schema.sql`** | 9 tables | **YES** |
| **9** | **`user_intelligence/migrations/001_user_intelligence.sql`** | 5 tables | for `/dashboard` |

**009 failing is correct and expected.** It declares a foreign key to
`public.kg_entity_registry`, which no migration in this repository creates. It
is run anyway so the attempt is on record, and `011` repairs whatever state it
leaves. `first_deploy.sh` encodes this:

```bash
if psql ... -f .../009_vocabulary_crosswalk.sql 2>/dev/null; then
  ok "009 applied (pre-existing kg_entity_registry)"
else
  info "009 failed as expected — missing public.kg_entity_registry. 011 repairs this."
fi
```

**`011` and `001` are order-independent.** Both begin `create schema if not
exists knowledge;`, so either may run first.

---

## C · The manual steps, in order

### Step 0 — only if §A says `admin_fn_exists = false`

Apply `supabase/migrations/202606200002_entrepreneurship_knowledge_graph.sql`
first. It creates `public.is_valueweave_admin()` and the 9 CMS `kg_*` tables.
Without it, step 1 fails on its last statement and leaves a partial schema.

### Step 1 — `knowledge_sync/migrations/001_knowledge_schema.sql`

Open the file, copy the whole thing, paste into the SQL Editor, run.

Creates **9 tables, 34 indexes, 9 RLS policies, 3 grants**, all in schema
`knowledge`:

| Table | Rows after sync |
|---|---:|
| `kg_entities` | 647 |
| `kg_relationships` | 865 |
| `kg_districts` | 61 |
| `kg_skills` | 45 |
| `kg_schemes` | 40 |
| `kg_businesses` | 85 |
| `kg_industries` | 24 |
| `kg_agriculture` | 45 |
| `sync_runs` | 1 per run |
| | **1,812 + audit** |

**Indexes (34).** Four patterns per table: `<table>_live_idx` (partial, on
`sync_row_key where sync_deleted_at is null`), `<table>_source_idx`, and one or
two on the natural lookup columns — `kg_entities_entity_type_idx`,
`kg_entities_canonical_name_idx`, `kg_relationships_from_entity_idx`,
`kg_relationships_to_entity_idx`, `kg_relationships_relationship_type_idx`, and
`<table>_category_name_idx` / `<table>_<name>_idx` on each detail table. Plus
`sync_runs_started_idx`.

**RLS: enabled on all 9 tables, with 9 SELECT policies** —
`"kg_entities public read"`, `"kg_relationships public read"`, and so on, plus
`"sync runs admin read"`. **No INSERT, UPDATE or DELETE policy exists on any
table, deliberately.** The sync writes with the service role, which bypasses
RLS; `anon` and `authenticated` therefore cannot write at all, enforced by the
absence of a policy rather than by convention.

**Grants (3):** `usage on schema knowledge to anon, authenticated`;
`select on all tables in schema knowledge to anon, authenticated`; and a default
privilege so tables added later inherit `select`.

**Functions: none. Triggers: none.** The whole schema is tables, indexes,
policies and grants.

**Idempotent** — all 9 tables are `create table if not exists`, all 34 indexes
are `create index if not exists`, and each policy is preceded by
`drop policy if exists`. Safe to re-run. It is **not** wrapped in a
transaction, so if it fails part-way, fix the cause and run it again.

### Step 2 — `user_intelligence/migrations/001_user_intelligence.sql`

Creates **5 tables, 4 indexes, 5 RLS policies, 3 grants** in schema
`user_intelligence`: `user_skill_profile`, `user_business_profile`,
`user_learning_profile`, `user_recommendations`, `user_activity_summary`.

Every policy is a SELECT scoped to `auth.uid() = user_id`, **with no admin
exception**. Grants go to `authenticated` only — not `anon`.

Needed for `/dashboard` personal suggestions, **not** for the knowledge sync.
You can defer this one.

### Step 3 — `frontend/migrations/011_repair_vocabulary_crosswalk.sql`

Creates `knowledge.kg_vocabulary_map` — **1 table, 3 indexes, 1 RLS policy,
2 grants**, plus a `do $$ … $$` block that migrates rows from
`public.kg_vocabulary_map` if that table exists, dropping its unbuildable
foreign key first.

Indexes: `kg_vocab_lookup_idx (term_kind, normalised_term)`,
`kg_vocab_entity_idx (global_entity_id) where not null`, `kg_vocab_method_idx`.

**This one IS wrapped in `begin; … commit;`** — a half-repaired crosswalk
resolves some terms and not others, which is worse than none resolving.

Handles all four possible starting states, so it is safe whatever §A told you.

### Step 4 — ⚠️ EXPOSE THE SCHEMAS (this is what unblocks Apply)

**Dashboard → Project Settings → API → Exposed schemas**

Add: `knowledge`, `user_intelligence` — then **Save**.

Without this, PostgREST refuses every request naming those schemas, including
requests carrying the service-role key. **Your Apply step will keep failing
even with all the tables created.**

---

## D · Then re-run

Trigger the **Knowledge sync** workflow (Actions → Run workflow), or locally:

```bash
scripts/run_sync.sh
```

It now checks all eight tables exist before applying and names this document if
any are missing.

**Expected:** `1812 inserted` on the first run, and — the check that matters —
`0 inserted, 0 updated` on the automatic second run.

### Verify

```sql
select 'kg_entities' t, count(*) from knowledge.kg_entities
union all select 'kg_relationships', count(*) from knowledge.kg_relationships
union all select 'kg_districts',     count(*) from knowledge.kg_districts
union all select 'kg_skills',        count(*) from knowledge.kg_skills
union all select 'kg_schemes',       count(*) from knowledge.kg_schemes
union all select 'kg_businesses',    count(*) from knowledge.kg_businesses
union all select 'kg_industries',    count(*) from knowledge.kg_industries
union all select 'kg_agriculture',   count(*) from knowledge.kg_agriculture
order by 1;
```

Expect 647 / 865 / 61 / 45 / 40 / 85 / 24 / 45.

Then the crosswalk, which is loaded separately by `scripts/load_crosswalk.sh`:

```sql
select term_kind, count(*) from knowledge.kg_vocabulary_map group by 1;
-- district 33 · sector 22 · skill 147  (202 total)
```

**Confirm exposure worked** — this is the check the service role cannot make for
you, because it must be done with the **anon** key:

```bash
curl -s -H "apikey: $ANON_KEY" -H "Accept-Profile: knowledge" \
  "$SUPABASE_URL/rest/v1/kg_entities?select=global_entity_id&limit=1"
```

A row means exposure and RLS are both right. `PGRST106` means the schema is
still not exposed. `[]` with a 200 means exposed but empty.

---

## E · Two things not to do

**Do not create `public.kg_entity_registry`.** Migration 009 references it and
no migration creates it; that is the defect 011 exists to repair. Creating an
empty one would give the platform a third entity table alongside the CMS `kg_*`
tables and the real `knowledge.kg_entities`.

**Do not hand-edit rows in the `knowledge` schema.** Git is the source of truth
and Supabase is a read-optimised cache. The next sync reverts any edit and the
change is lost from source control. That is why no write policy exists.

---

## Summary — the shortest path

1. Run `sql/verify_knowledge_schema.sql` — read the last block first.
2. If `admin_fn_exists` is false, apply `supabase/migrations/202606200002_…`.
3. Run `knowledge_sync/migrations/001_knowledge_schema.sql`.
4. Run `frontend/migrations/011_repair_vocabulary_crosswalk.sql`.
5. *(deferrable)* `user_intelligence/migrations/001_user_intelligence.sql`.
6. Re-run `sql/verify_knowledge_schema.sql` — expect `SCHEMA COMPLETE`.
7. **Expose `knowledge` and `user_intelligence`.** ← without this Apply still fails.
8. Re-run the workflow.

# Deploying the ValueWeave Knowledge Engine

Everything needed to take the workflow past its current failure, in the order it
has to happen.

**Status of this document.** The SQL described here was executed against a real
PostgreSQL 16 while it was written — clean, partial, repeated, and against a
**replica built from your production schema dump** — so the object counts, grants
and idempotency below are measured, not predicted. What has *not* happened is a
run against your Supabase project: this environment cannot reach it.

```
api.supabase.com:443  →  HTTP 000 (proxy: "gateway answered 403 to CONNECT")
supabase.co:443       →  HTTP 000 (same)
frontend/.env.local   →  NEXT_PUBLIC_SUPABASE_ANON_KEY=placeholder…
```

The network policy for this environment blocks Supabase outright, and no real
credentials exist here. So steps 6–9 below are yours to run. Everything that can
be done without the network has been.

For the architecture decision this deployment implements — which of the two
knowledge systems is canonical, and what happens to the other — see
`KNOWLEDGE_ARCHITECTURE_DECISION.md`.

---

## Verified against your actual schema

Your dump was turned into a local replica (30 tables, 70 policies,
`is_valueweave_admin()` present, no `knowledge` schema) and the deployment run
against it:

| Check | Result |
|---|---|
| Deployment exit code | **0**, no errors |
| `public` schema after | **byte-identical** — same 30 tables, 70 policies, same column fingerprint |
| `is_valueweave_admin()` | **not replaced** — same OID before and after (the 16 CMS policies are untouched) |
| `knowledge` / `user_intelligence` | created — 15 tables, 58 indexes, 15 policies |
| `public.kg_skills` vs `knowledge.kg_skills` | coexist as distinct objects (22 vs 29 columns) |
| Sync plan | 647 entities, 865 relationships, **0 errors** |

---

## The one-page checklist

- [ ] **1 · Verify the current database** — run `sql/verify_knowledge_schema.sql`
- [ ] **2 · Apply the prerequisite** — handled inside the script (PHASE 0 and 1)
- [ ] **3 · Deploy the Knowledge schema** — run `sql/deploy_knowledge.sql`
- [ ] **4 · Deploy the Vocabulary migration** — same script, PHASE 3
- [ ] **5 · Deploy User Intelligence** — same script, PHASE 4
- [ ] **6 · Expose the schemas in Supabase** — Dashboard, cannot be done in SQL
- [ ] **7 · Run the GitHub Knowledge Sync** — Actions → Knowledge sync → apply
- [ ] **8 · Verify rows imported** — re-run the verifier, `actual` matches `expected`
- [ ] **9 · Verify the frontend shows real data** — the pages listed in Phase 7
- [ ] **10 · Confirm the Knowledge Engine is production-ready**

Steps 2–5 are one paste. They are listed separately because they are separate
things that can each fail, not because they are separate runs.

> **Step 6 is not last, and that is the correction that matters most.** It was
> previously understood as a frontend concern to be done after the import. It is
> not: the sync itself writes through PostgREST, so an unexposed schema stops the
> import too. Do step 6 before step 7 or step 7 fails.

---

## Phase 1 · Verify what is actually there

```
sql/verify_knowledge_schema.sql
```

Read-only, and enforced as such by a test: every statement must begin `select` or
`with`. Safe to run against production, before and after, as often as you like.

It reports prerequisites (`public.profiles`, `public.is_valueweave_admin()`),
which schemas exist, every expected table with its index and policy counts as
`actual/expected`, any unexpected write policy, the grant matrix including
`service_role`, row counts against expected totals, and a one-line verdict.

Run it first. The verdict tells you which of the states below you are in.

---

## Phase 2 · Deployment order, and why it is what it is

Determined by executing the migrations, not by reading them. Two dependencies
only show up when you run them:

1. **`001_knowledge_schema.sql` needs `public.is_valueweave_admin()`.** Its last
   statement is the admin read policy on `knowledge.sync_runs`. The function is
   created by `supabase/migrations/202606200002_…`, a CMS migration nothing else
   here depends on. Applied without it, 001 leaves **9 tables, 34 indexes, 8 of 9
   policies, and `sync_runs` with RLS enabled and no policy** — reachable by
   nobody, and no error unless you were watching. 001 is not wrapped in a
   transaction, so the failure does not roll back.

2. **`is_valueweave_admin()` needs `public.profiles.is_admin`.** The function body
   reads `p.is_admin`, PostgreSQL validates a `language sql` body at CREATE time,
   and that column is added by `frontend/migrations/001_research_articles.sql` —
   not by the base schema. On a database without it you get `column p.is_admin
   does not exist` partway in.

Hence the order:

| Phase | What | Source |
|---|---|---|
| 0 | Preflight — abort unless `profiles` and `profiles.is_admin` exist | — |
| 1 | `public.is_valueweave_admin()` | `supabase/migrations/202606200002_…` |
| 2 | Knowledge schema — 9 tables, 34 indexes, 9 policies | `knowledge_sync/migrations/001_knowledge_schema.sql` |
| 3 | Vocabulary crosswalk repair | `frontend/migrations/011_repair_vocabulary_crosswalk.sql` |
| 4 | User intelligence — 5 tables | `user_intelligence/migrations/001_user_intelligence.sql` |
| 5 | Commit | — |

**No assumption of an empty database.** Every object is `create … if not exists`
or `create or replace`, and every policy is dropped before it is created. Objects
that already exist are skipped by PostgreSQL itself rather than by a version
table that could disagree with reality.

---

## Phase 3 · The deployment script

```
sql/deploy_knowledge.sql          ← paste this into the Supabase SQL Editor
```

**It is generated, not hand-written** — `scripts/build_deployment_sql.py` assembles
it from the four migration files. A transcribed copy would be a second source of
truth that drifts the first time someone edits a migration, and the drift stays
invisible until a deployment produces a schema the sync does not recognise. A test
regenerates it and fails if the checked-in file differs.

It makes exactly three changes to the migrations, each recorded in the generator:

1. The PHASE 0 preflight, which does not exist in any migration.
2. `is_valueweave_admin()` lifted out of `202606200002` and placed first.
3. `011`'s own `begin;`/`commit;` removed, and the whole script wrapped in one
   transaction instead. Nested transaction control inside a larger batch either
   errors or commits early depending on the client. The outer wrapper is
   *stronger* than 011's: the entire deployment is now all-or-nothing.

### What was measured

Against PostgreSQL 16 with Supabase's roles and `auth.uid()` stood in:

| Scenario | Result |
|---|---|
| No `public.profiles` | aborts, **0 objects created** |
| `profiles` without `is_admin` | aborts, **0 objects created** |
| Clean database | exit 0 — **15 tables, 58 indexes, 15 policies** |
| Partial (001 applied, its last policy missing) | repaired to 15/58/15 |
| Re-run ×2 | exit 0, shape unchanged, **rows preserved** |

Per table, `indexes/policies` (index counts include the primary key):

```
knowledge.kg_entities        5/1   knowledge.kg_relationships   6/1
knowledge.kg_districts       5/1   knowledge.kg_skills          5/1
knowledge.kg_schemes         5/1   knowledge.kg_businesses      6/1
knowledge.kg_industries      4/1   knowledge.kg_agriculture     5/1
knowledge.kg_vocabulary_map  5/1   knowledge.sync_runs          2/1
user_intelligence.user_activity_summary 2/1   user_business_profile 1/1
user_intelligence.user_learning_profile 1/1   user_skill_profile    1/1
user_intelligence.user_recommendations  5/1
```

**Zero write policies** on either schema, and RLS on all 15 tables. "Never edit
package data inside Supabase" is enforced by the absence of a policy rather than
by convention.

### One defect this found, which would have failed the sync anyway

The migrations granted `service_role` nothing, on the stated grounds that it
"bypasses grants and RLS alike". Half true. `service_role` has `BYPASSRLS`, so
row-level security does not stop it — but **BYPASSRLS is not superuser, and GRANT
checks still apply.** PostgreSQL exempts only superusers from privilege checks,
and Supabase's service role is deliberately not one. Supabase's default grants
cover `public`; a schema created by a migration gets none.

Measured: with the grants absent, `set role service_role` then any statement
against `knowledge` returns

```
ERROR:  permission denied for schema knowledge
```

on **SELECT as well as INSERT** — after a deployment where tables, indexes,
policies and the verifier's own verdict all looked perfect. The grants are now in
the migrations (and therefore in the generated script), and the verifier checks
for them:

| Schema | Role | Privileges |
|---|---|---|
| `knowledge` | `anon`, `authenticated` | SELECT |
| `knowledge` | `service_role` | SELECT, INSERT, UPDATE — **no DELETE** |
| `user_intelligence` | `authenticated` | SELECT |
| `user_intelligence` | `service_role` | SELECT, INSERT, UPDATE, DELETE |
| `user_intelligence` | `anon` | *nothing* |

DELETE is withheld on `knowledge` on purpose: `knowledge_sync/adapters.py` has no
hard delete — removal is `sync_deleted_at = now()`. A bug in the sync can mark the
projection, not destroy it. `user_intelligence` gets DELETE because its writer
genuinely hard-deletes a user's stale recommendations before rewriting them. A
test asserts both, and asserts the asymmetry stays justified by the code.

---

## Phase 4 · What SQL cannot do

Two Dashboard actions. One is required.

### Required — expose the schemas

**Project Settings → API → Exposed schemas** → add `knowledge` and
`user_intelligence` alongside `public` → Save → wait ~30 s for PostgREST to
reload.

This is PostgREST's `db-schemas` allowlist. PostgREST validates the requested
schema against it **before it authenticates anything**, so an unlisted schema
returns `PGRST106` whichever key is presented — the service-role key does not
route around it. It is a server configuration, not a permission, and there is no
SQL statement, grant or policy that substitutes for it.

Both the sync and the browser go through PostgREST, so until this is done:

* every frontend query fails and every page shows "being prepared";
* **and the import fails too.** Do this before running the sync.

### Not required — anything else

Checked, and nothing else needs changing:

* **Connection pooling / direct connection** — not needed. The sync uses the
  PostgREST client, not a Postgres socket.
* **Database extensions** — none required. No `pgvector`, no `postgis`. The
  script uses only core types plus `jsonb`.
* **RLS toggle** — the script enables RLS per table itself.
* **API key rotation** — no. Reuse the existing `anon` and `service_role` keys.
* **Realtime / Storage / Edge Functions** — untouched, no setting needed.
* **Statement timeout** — the script completes in well under a second on an empty
  database; the default is ample.

`SUPABASE_SERVICE_ROLE_KEY` bypasses RLS. It belongs in GitHub Actions secrets or
a server-side environment variable and nowhere else — never in a `NEXT_PUBLIC_*`
variable, never in a client component, never in a committed file. Source a
gitignored `.env` rather than typing it into a shell.

---

## Phase 5 · Verify after deploying

The same file as Phase 1:

```
sql/verify_knowledge_schema.sql
```

After the deployment and before the sync, expect: both schemas present, 15/15
tables, every row `ok`, 0 unexpected write policies, the full grant matrix
including `service_role`, all row counts `0`, and

```
SCHEMA COMPLETE — next: expose `knowledge` and `user_intelligence` under
Project Settings -> API -> Exposed schemas, then run the sync
```

After the sync, the `rows` block is the one to read — `actual` should match
`expected`:

| Table | Expected |
|---|---|
| `kg_entities` | 647 |
| `kg_relationships` | 865 |
| `kg_districts` | 61 |
| `kg_businesses` | 85 |
| `kg_skills` | 45 |
| `kg_agriculture` | 45 |
| `kg_schemes` | 40 |
| `kg_industries` | 24 |
| `kg_vocabulary_map` | 202 |

The verdict has a state specifically for the failure that is otherwise invisible:

```
TABLES AND POLICIES OK, BUT THE SYNC CANNOT WRITE — service_role has no USAGE …
```

Everything can look complete while the sync cannot write a single row. That is
why it is checked before the success case.

---

## Phase 6 · The GitHub workflow

**The workflow needed one change, and now has it.**

`.github/workflows/knowledge-sync.yml` was already correct in every part this
review could test: full-history checkout, Node present for the JS/Python parity
test, the sync SDK installed *after* the tests so the "engine holds no database
client" test still means something, a secrets preflight, plan before apply, an
idempotency re-run inside `run_sync.sh`, a health check through the **anon** key,
and the run log uploaded on failure.

What it was missing was a check for the one thing most likely to stop it next. If
`knowledge` is not exposed, the failure surfaced partway through Apply as a raw
`PGRST106` from inside `supabase-py` — which reads like a library fault rather
than a one-checkbox setting. A preflight step now runs before Apply and
distinguishes:

* **200** — exposed and reachable, continue;
* **401/403** — the service-role key was rejected;
* **PGRST106** — the schema is not exposed, with the exact Dashboard path;
* **PGRST205** — exposed but the tables are missing, pointing at
  `sql/deploy_knowledge.sql`.

All four branches were exercised against canned responses. Two comments claiming
the service role "bypasses the exposed-schemas setting" were corrected, in the
workflow and in `scripts/health_check.sh` — that belief is what put step 6 after
step 7.

**With that step added, the GitHub workflow is production-ready.**

Three secrets are still required, and this environment cannot confirm they are
set: `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`. The workflow
fails its first preflight with a clear message if any is missing.

---

## Phase 7 · Will the frontend show the data by itself?

**Yes. No further wiring is required.** Every page that reads the projection picks
it up on its own after the sync — but the reason was not what the code claimed,
and one part of it was accidental.

### How each page reads

`frontend/lib/knowledge.js` builds a Supabase client with `db: { schema:
"knowledge" }` using the **anon** key, so `anon` needs SELECT (it has it) and the
schema must be exposed (Phase 4). `lib/intelligence.js` does the same for
`user_intelligence`. Every query goes through `safe()`, which returns `[]` rather
than throwing — which is why the site serves 200s with empty panels instead of
errors when the schema is missing.

### When each page picks up new data

Measured from `.next/prerender-manifest.json` after a production build:

| Route | Mode | Picks up new data |
|---|---|---|
| `/`, `/knowledge`, `/knowledge/<type>/<slug>` | dynamic | immediately |
| `/dashboard`, `/connections`, `/profile` | client fetch | immediately |
| `/districts`, `/districts/<slug>`, `/district/<slug>` | ISR | ≤ 60 s |
| `/ai`, `/manufacturing`, `/network`, `/readiness`, `/scale` | ISR | ≤ 60 s |

So the 14 district pages and the five module pages refresh within a minute. No
redeploy is needed.

**The part that was accidental.** Six of those pages declared no `revalidate` at
all. They were refreshing only because the shared `Footer` calls
`getPlatformSettings()` — an `unstable_cache` with `revalidate: 60` — and Next
takes the *lowest* revalidate in a segment. Every page in the app was inheriting
60 s from a component that has nothing to do with knowledge. Remove the footer's
cache and those six freeze at build time, showing "being prepared" forever with
nothing in any log to say so.

They now declare `export const revalidate = 300` themselves. Behaviour today is
unchanged — 60 is lower and still wins — but the pages no longer depend on an
unrelated component to stay alive. A test enumerates every server page that
reaches `lib/knowledge` or `lib/intelligence` and fails if one declares neither
`revalidate` nor `dynamic`.

A comment in `app/district/[slug]/page.js` claiming the knowledge load "runs at
build time … and gains content the day the sync runs" was corrected: those two
clauses contradict each other, and only the second is true.

### What will still look empty, and is not a bug

Two things the import cannot fix, both previously measured:

* **34 of 61 districts have no incoming relationships.** Their pages will render
  the district profile and an honest empty state for linked opportunities. Medak
  has exactly one.
* **Search matches `canonical_name` only.** "Dairy" returns nothing despite 11
  package rows, because no entity is *named* Dairy. The copy in
  `KnowledgeSearch.jsx` already says it is substring matching.

Neither is a deployment defect. Both are content and search-ranking work.

---

## If something goes wrong

| Symptom | Cause | Fix |
|---|---|---|
| `public.profiles does not exist` | wrong project, or base schema not applied | connect to the right project; apply `frontend/supabase_schema.sql` |
| `profiles exists but has no is_admin` | `001_research_articles.sql` never applied | apply it, or `alter table public.profiles add column if not exists is_admin boolean not null default false;` |
| `function public.is_valueweave_admin() does not exist` | you ran a migration directly, not `deploy_knowledge.sql` | run `sql/deploy_knowledge.sql` — it is idempotent and repairs the partial state |
| `PGRST106` | schema not exposed | Phase 4 |
| `permission denied for schema knowledge` | pre-fix database, missing service_role grant | re-run `sql/deploy_knowledge.sql` |
| Sync succeeds, pages still empty | schema not exposed to the **anon** key | Phase 4; then `scripts/health_check.sh` |
| Pages empty for a minute after the sync | ISR window | wait 60 s |

Rollback is `drop schema knowledge cascade; drop schema user_intelligence
cascade;` — both schemas are derived, Git remains the single source of truth, and
neither can reach an application table.

---

**Related:** `sql/deploy_knowledge.sql` · `sql/verify_knowledge_schema.sql` ·
`scripts/build_deployment_sql.py` · `scripts/health_check.sh` ·
`.github/workflows/knowledge-sync.yml`

# Supabase Extension Plan — Platform v3.0, Step 2

Everything that must happen in Postgres for the integrated pages to show data, in
order, with the failure mode of each step.

**None of it has been applied.** No database access exists in this environment.

---

## 1. The four schemas

| Schema | Owner | Contents | Written by |
|---|---|---|---|
| `public` | the application | 30 pre-existing tables + 5 new empty ones | users, admins |
| `knowledge` | knowledge_sync | 8 projection tables, ~1,812 rows | the sync, service role only |
| `user_intelligence` | the intelligence engine | 5 derived tables | the engine, service role only |
| `auth` | Supabase | untouched | — |

Two of these are **disposable by design**:

```sql
drop schema knowledge cascade;          -- rebuild with knowledge_sync
drop schema user_intelligence cascade;   -- rebuild by re-running the engine
```

Both are derived from Git plus a profile. Neither can reach an application table,
which is why the separate schemas exist at all.

---

## 2. Migration inventory

| File | Status |
|---|---|
| `001_research_articles.sql` | pre-existing |
| `002_collaboration_marketplace.sql` | pre-existing |
| `003_seed_opportunities.sql` | pre-existing |
| `004_admin_analytics.sql` | pre-existing |
| `005_growth_intelligence.sql` | pre-existing |
| `006_visitor_analytics.sql` | pre-existing |
| `007_engagement_retention.sql` | pre-existing |
| `009_vocabulary_crosswalk.sql` | new in Step 0 |
| `010_missing_application_features.sql` | **new in Step 2** |

Plus two outside `frontend/migrations/`, generated from code:

| File | Creates |
|---|---|
| `knowledge_sync/migrations/001_knowledge_schema.sql` | schema `knowledge`, 8 tables + `sync_runs` |
| `user_intelligence/migrations/001_user_intelligence.sql` | schema `user_intelligence`, 5 tables |

Both are **generated**, and `--check` fails CI on drift. A hand-edited migration
would silently diverge from the code that writes to it.

---

## 3. Deployment order

Each step is verifiable, and the order matters — later steps hold foreign keys into
earlier ones.

```bash
# 1 — application tables (Step 0 crosswalk, Step 2 missing features)
psql "$DATABASE_URL" -f frontend/migrations/009_vocabulary_crosswalk.sql
psql "$DATABASE_URL" -f frontend/migrations/010_missing_application_features.sql

# 2 — the knowledge projection
psql "$DATABASE_URL" -f knowledge_sync/migrations/001_knowledge_schema.sql
psql "$DATABASE_URL" -c "\dt knowledge.*"        # expect 9 tables

# 3 — the intelligence schema
psql "$DATABASE_URL" -f user_intelligence/migrations/001_user_intelligence.sql

# 4 — EXPOSE THE SCHEMAS  ← see §4. Everything looks broken without this.

# 5 — populate the projection
python3 -m knowledge_sync plan                      # expect 1,812 rows, 0 errors
python3 -m knowledge_sync sync --target supabase
python3 -m knowledge_sync sync --target supabase    # must report 0 inserted

# 6 — populate the crosswalk from the committed CSVs
#     (governance/vocabulary/*_crosswalk.csv -> public.kg_vocabulary_map)

# 7 — per-user intelligence
python3 -m user_intelligence run --profile-json <user rows>   # then write the tables
```

**Note on step 6.** `kg_vocabulary_map` lives in `public` (migration 009, written in
Step 0) while the projection lives in `knowledge`. `lib/knowledge.js` queries it
through the `knowledge` client, so **either** the table moves into `knowledge`
**or** `resolveTerms()` needs its own `public` client. This is a real inconsistency
introduced across two steps and it must be resolved before step 4 — see §7.

---

## 4. Expose the schemas — the step that will be missed

Supabase only serves schemas listed under **API → Exposed schemas**. Add:

```
knowledge, user_intelligence
```

Without it, `createClient(url, key, { db: { schema: "knowledge" } })` returns an
error for every query, `lib/knowledge.js` catches it and returns `[]`, and every page
renders its empty state.

**The application will look exactly as it does today, and nothing will indicate
why.** This is the single most likely cause of a silent failure after deployment, and
it is not detectable from the frontend — which is why it is called out here rather
than left to a runbook.

Diagnose with:

```sql
select count(*) from knowledge.kg_entities;         -- 647 when populated
select count(*) from user_intelligence.user_activity_summary;
```

If those return rows but the app shows nothing, the schema is not exposed.

---

## 5. RLS summary

| Schema | Read | Write |
|---|---|---|
| `knowledge.*` | `anon`, `authenticated` where `sync_deleted_at is null` | **no policy** — service role only |
| `user_intelligence.*` | `auth.uid() = user_id`, no admin exception | **no policy** — service role only |
| `public.assessment_results` | own rows | own rows |
| `public.mentor_profiles` | active mentors publicly; own row always | own row |
| `public.events` | `status = 'published'` or admin | admin |
| `public.teams` | members and owner | owner |
| `public.team_members` | self, or the team owner | team owner |

**Two schemas have no write policy at all.** With RLS enabled and no policy,
`anon` and `authenticated` cannot write — *"never edit package data in Supabase"* is
enforced by the **absence** of a policy rather than by convention, which is the
strongest form available because there is nothing to misconfigure.

The service role bypasses RLS and exists only in CI, only for the sync and the
engine. It must never appear in a `NEXT_PUBLIC_*` variable.

---

## 6. What was NOT changed

| Table | Status |
|---|---|
| `profiles` | **unchanged.** No column added, none renamed. |
| `connections` | **unchanged.** Step 2 added `skills` to a *select*, not to the table. |
| `opportunities`, `collaborator_profiles`, `founder_matches` | unchanged |
| All 14 content and analytics tables | unchanged |
| `kg_*` CMS tables in `public` | unchanged — the projection is in its own schema precisely to avoid them |
| `auth.*` | unchanged |

**Zero `alter table` against a pre-existing table across all of Step 2.** A test
asserts it for migration 010.

The earlier `DATABASE_EXTENSION_PLAN.md` (v3.0 planning) proposed eight nullable
columns on `profiles` and `opportunities`. **Step 2 did not add them** — they were not
needed once resolution happened at read time through the crosswalk, and not adding a
column beats adding one that turns out to be unnecessary.

---

## 7. Known inconsistency to resolve before deployment

`kg_vocabulary_map` is created in `public` by Step 0's migration 009, but
`lib/knowledge.js` queries it through the `knowledge`-scoped client. One of these
must change:

| Option | Effect |
|---|---|
| **Move the table to `knowledge`** (recommended) | One migration; the crosswalk is derived from Git like everything else in that schema |
| Give `resolveTerms()` a `public` client | Two clients in one module; works, but muddies the boundary |

Recommended because the crosswalk **is** projected data: it is generated by
`governance/vocabulary/build_crosswalk.py` from the graph, not authored by a user. It
belongs beside the projection it describes.

Flagged rather than fixed here because it changes a Step 0 migration, and doing that
inside a Step 2 commit would obscure both.

---

## 8. Rollback

| To undo | Command | Loses |
|---|---|---|
| The projection | `drop schema knowledge cascade;` | Nothing — rebuild from Git |
| Per-user intelligence | `drop schema user_intelligence cascade;` | Nothing — recompute |
| Missing-feature tables | `drop table public.team_members, teams, events, mentor_profiles, assessment_results;` | Nothing — they are empty |
| The frontend integration | `git revert` the Step 2 merge | Pages return to their pre-Step-2 state |

Every step is reversible, and none of it touches user data. That is the property the
separate schemas were chosen to guarantee.

---

## 9. Storage

| Schema | Rows | Size |
|---|---:|---:|
| `knowledge` | ~1,812 | < 3 MB with indexes |
| `user_intelligence` | ~40 per user | < 50 KB per user |
| new `public` tables | 0 | negligible |

At 1,000 users the intelligence schema is roughly 50 MB. The indexes exist for query
*shape*, not volume.

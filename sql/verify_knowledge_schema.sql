-- ValueWeave — verify the knowledge deployment.
--
-- READ-ONLY. Creates nothing, changes nothing, locks nothing. Safe to run on a
-- production database at any time, before or after deployment.
--
-- Run it BEFORE you deploy to see what already exists — several of the
-- migrations behave differently depending on the starting state, and one of
-- them (001_knowledge_schema.sql) is not transactional, so a run that fails
-- part-way leaves a partial schema that looks fine until you query it.
--
-- Run it AFTER to confirm every object landed.
--
-- Every expected number below was measured against a real PostgreSQL 16 with
-- these exact migration files applied — not read off the SQL by eye.
--
--   Supabase SQL Editor: paste and run. Read the last block first.

-- ── 1 · Prerequisites ───────────────────────────────────────────────────────
-- knowledge_sync/migrations/001_knowledge_schema.sql fails at its final
-- statement without public.is_valueweave_admin(), which is created by
-- supabase/migrations/202606200002_entrepreneurship_knowledge_graph.sql and in
-- turn needs public.profiles. Applying 001 without it creates 9 tables and 34
-- indexes and then errors on the last policy — a partial schema.
select
  'prerequisites'                                                as check,
  to_regclass('public.profiles') is not null                     as profiles_exists,
  to_regproc('public.is_valueweave_admin') is not null           as admin_fn_exists,
  case
    when to_regproc('public.is_valueweave_admin') is null
      then 'APPLY supabase/migrations/202606200002_… FIRST'
    else 'ok'
  end                                                            as action;

-- ── 2 · Schemas ─────────────────────────────────────────────────────────────
select 'schemas' as check,
       coalesce(bool_or(nspname = 'knowledge'), false)         as knowledge,
       coalesce(bool_or(nspname = 'user_intelligence'), false) as user_intelligence
from pg_namespace;

-- ── 3 · Tables, indexes, policies, RLS — expected vs actual ─────────────────
-- Index counts INCLUDE the primary key, which is why they are one higher than
-- the `create index` count in the migration file.
with expected(schema_name, table_name, idx, pol) as (values
  ('knowledge','kg_entities',5,1),      ('knowledge','kg_relationships',6,1),
  ('knowledge','kg_districts',5,1),     ('knowledge','kg_skills',5,1),
  ('knowledge','kg_schemes',5,1),       ('knowledge','kg_businesses',6,1),
  ('knowledge','kg_industries',4,1),    ('knowledge','kg_agriculture',5,1),
  ('knowledge','sync_runs',2,1),        ('knowledge','kg_vocabulary_map',5,1),
  ('user_intelligence','user_skill_profile',1,1),
  ('user_intelligence','user_business_profile',1,1),
  ('user_intelligence','user_learning_profile',1,1),
  ('user_intelligence','user_recommendations',5,1),
  ('user_intelligence','user_activity_summary',2,1)
)
select
  e.schema_name || '.' || e.table_name                                as object,
  c.oid is not null                                                   as exists,
  coalesce((select count(*) from pg_index i where i.indrelid = c.oid), 0)
    || '/' || e.idx                                                   as indexes,
  coalesce((select count(*) from pg_policies p
             where p.schemaname = e.schema_name and p.tablename = e.table_name), 0)
    || '/' || e.pol                                                   as policies,
  coalesce(c.relrowsecurity, false)                                   as rls,
  case
    when c.oid is null then 'MISSING — migration not applied'
    when not c.relrowsecurity then 'RLS OFF — table is world-readable'
    when (select count(*) from pg_policies p
           where p.schemaname = e.schema_name and p.tablename = e.table_name) = 0
      then 'RLS ON, NO POLICY — nobody can read this'
    when (select count(*) from pg_index i where i.indrelid = c.oid) < e.idx
      then 'fewer indexes than expected'
    else 'ok'
  end                                                                 as verdict
from expected e
left join pg_class c
  on c.relname = e.table_name
 and c.relnamespace = to_regnamespace(e.schema_name)
 and c.relkind = 'r'
order by e.schema_name, e.table_name;

-- ── 4 · Write policies must NOT exist ───────────────────────────────────────
-- Git is the source of truth and Supabase is a cache. The sync writes with the
-- service role, which bypasses RLS; anon and authenticated must be unable to
-- write at all, enforced by the absence of a policy rather than by convention.
-- Any row here is a security finding.
select 'unexpected write policy' as check, schemaname, tablename, policyname, cmd
from pg_policies
where schemaname in ('knowledge','user_intelligence')
  and cmd <> 'SELECT';

-- ── 5 · Grants ──────────────────────────────────────────────────────────────
-- Expected, exactly:
--   knowledge          -> SELECT                        anon (10), authenticated (10)
--   knowledge          -> SELECT, INSERT, UPDATE        service_role (10 each)
--   user_intelligence  -> SELECT                        authenticated (5)
--   user_intelligence  -> SELECT, INSERT, UPDATE, DELETE service_role (5 each)
--   user_intelligence  -> nothing at all                anon
--
-- service_role is included because its absence is a silent, specific failure.
-- Supabase's service role has BYPASSRLS, which exempts it from row-level
-- security but NOT from GRANT checks — only a superuser skips those, and the
-- service role is deliberately not one. A `knowledge` schema with perfect tables,
-- indexes and policies but no service_role grant looks completely healthy in
-- every other block of this file, and the sync still dies on its first statement
-- with `permission denied for schema knowledge`. If the service_role rows below
-- are missing, the schema is NOT ready, whatever the verdict at the end says.
--
-- DELETE on `knowledge` is expected to be ABSENT: the sync soft-deletes by
-- setting sync_deleted_at. A DELETE row here means someone widened the grant.
select 'grants' as check, table_schema, grantee, privilege_type, count(*) as tables
from information_schema.role_table_grants
where table_schema in ('knowledge','user_intelligence')
  and grantee in ('anon','authenticated','service_role')
group by 1,2,3,4
order by table_schema, grantee, privilege_type;

-- Schema-level USAGE. A table grant is useless without it, and this is the one
-- that fails first.
select 'schema usage' as check, n.nspname as schema, r.rolname as role,
       has_schema_privilege(r.rolname, n.nspname, 'usage') as granted
from pg_namespace n
cross join (values ('anon'),('authenticated'),('service_role')) as r(rolname)
where n.nspname in ('knowledge','user_intelligence')
  and exists (select 1 from pg_roles where rolname = r.rolname)
order by n.nspname, r.rolname;

-- ── 6 · Row counts ──────────────────────────────────────────────────────────
-- Before the sync every count is 0 and that is correct. After it, the numbers
-- in the `expected` column are what a complete sync produces.
-- to_regclass guards each one so this block still runs on a partial schema.
select 'rows' as check, t.name, t.expected,
       case when to_regclass('knowledge.' || t.name) is null then null
            else (xpath('/row/c/text()',
                   query_to_xml(format('select count(*) as c from knowledge.%I', t.name),
                                false, true, '')))[1]::text::bigint
       end as actual
from (values ('kg_entities',647), ('kg_relationships',865), ('kg_districts',61),
             ('kg_skills',45),    ('kg_schemes',40),        ('kg_businesses',85),
             ('kg_industries',24),('kg_agriculture',45),    ('kg_vocabulary_map',202)
     ) as t(name, expected)
order by t.name;

-- ── 7 · Verdict ─────────────────────────────────────────────────────────────
-- Read this one first.
with expected(schema_name, table_name) as (values
  ('knowledge','kg_entities'),('knowledge','kg_relationships'),
  ('knowledge','kg_districts'),('knowledge','kg_skills'),
  ('knowledge','kg_schemes'),('knowledge','kg_businesses'),
  ('knowledge','kg_industries'),('knowledge','kg_agriculture'),
  ('knowledge','sync_runs'),('knowledge','kg_vocabulary_map'),
  ('user_intelligence','user_skill_profile'),
  ('user_intelligence','user_business_profile'),
  ('user_intelligence','user_learning_profile'),
  ('user_intelligence','user_recommendations'),
  ('user_intelligence','user_activity_summary')
), present as (
  select e.*, to_regclass(e.schema_name || '.' || e.table_name) is not null as ok
  from expected e
)
select
  count(*) filter (where ok)                                    as tables_present,
  count(*)                                                      as tables_expected,
  (select count(*) from pg_policies
     where schemaname in ('knowledge','user_intelligence'))     as policies,
  case
    when count(*) filter (where ok) = 0
      then 'NOTHING DEPLOYED — run sql/deploy_knowledge.sql'
    when count(*) filter (where ok) < count(*)
      then 'PARTIAL — ' || (count(*) - count(*) filter (where ok))
           || ' table(s) missing. Re-run sql/deploy_knowledge.sql; it is idempotent '
           || 'and will not touch the rows already imported.'
    when (select count(*) from pg_policies
            where schemaname in ('knowledge','user_intelligence')) < 15
      then 'TABLES OK, POLICIES INCOMPLETE — re-run sql/deploy_knowledge.sql'
    -- Checked before the success case, because everything above can be perfect
    -- while the sync is still unable to write a single row.
    when exists (select 1 from pg_roles where rolname = 'service_role')
     and not (has_schema_privilege('service_role','knowledge','usage')
              and has_schema_privilege('service_role','user_intelligence','usage'))
      then 'TABLES AND POLICIES OK, BUT THE SYNC CANNOT WRITE — service_role has no '
           || 'USAGE on knowledge and/or user_intelligence. It will fail with '
           || '"permission denied for schema knowledge". Re-run sql/deploy_knowledge.sql, '
           || 'which now grants it (BYPASSRLS does not bypass GRANT checks).'
    else 'SCHEMA COMPLETE — next: expose `knowledge` and `user_intelligence` '
         || 'under Project Settings -> API -> Exposed schemas, then run the sync'
  end                                                           as verdict
from present;

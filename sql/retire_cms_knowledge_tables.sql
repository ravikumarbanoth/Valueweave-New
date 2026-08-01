-- Retire the duplicate CMS knowledge tables.
--
-- RUN THIS ONLY AFTER sql/deploy_knowledge.sql AND A SUCCESSFUL SYNC.
--
-- WHAT PROBLEM THIS CLOSES
-- ------------------------
-- The production database carries two knowledge systems with colliding names:
--
--   public.kg_skills        an admin-authored CMS table, 22 columns
--   knowledge.kg_skills     the researched projection, 29 columns
--
-- Same for kg_schemes, and kg_resources has an equivalent in the graph too. A
-- user asking "what skills are there" could get two different answers depending
-- on which page they landed on. The frontend now always prefers the researched
-- graph (see frontend/lib/kg-fallback.js), so the CMS copies are unreferenced
-- for reading — but an unused table with the right name is a trap for the next
-- person, and the brief asked for one source of truth.
--
-- WHAT IT WILL NOT TOUCH, AND WHY
-- -------------------------------
--   kg_district_profiles     read by the public /district-opportunity-index page
--   kg_relationships         same page, and /admin/opportunity-mapping INSERTS
--                            into it — this is a live feature, not a duplicate
--   kg_roadmaps              no equivalent in the graph. A roadmap is an ordered
--   kg_roadmap_steps         sequence of costed steps and nothing projects one,
--                            so dropping these would remove a capability rather
--                            than a duplicate
--   kg_industry_sectors      small controlled vocabularies used by the admin UI
--   kg_collaborator_types
--
-- Only the three genuinely superseded tables are dropped.
--
-- IT REFUSES TO DESTROY CONTENT
-- -----------------------------
-- Every target is checked for rows first and the whole thing aborts if any is
-- non-empty. The repository's own note says nothing populates these tables, but
-- that is a claim about the code, not about your database — if somebody did
-- publish a scheme by hand, this stops rather than deleting their work, and
-- tells you which table to look at.
--
-- PAIR THIS WITH THE FRONTEND CHANGE
-- ----------------------------------
-- Dropping these tables breaks /admin/skills, /admin/schemes and
-- /admin/resources, which edit them. Run this script FIRST: if it aborts, the
-- tables have content and the admin screens must stay. If it succeeds, remove
-- those three admin routes in the same deploy.
--
-- Reversible: these tables are empty by definition once this succeeds, so
-- re-running supabase/migrations/202606200002_… recreates them.

begin;

-- ── 1 · Report, so the abort below has context ──────────────────────────────
select 'cms row counts' as check, t.name,
       case when to_regclass('public.' || t.name) is null then null
            else (xpath('/row/c/text()',
                   query_to_xml(format('select count(*) as c from public.%I', t.name),
                                false, true, '')))[1]::text::bigint
       end as rows,
       t.disposition
from (values
        ('kg_skills',             'DROP — superseded by knowledge.kg_skills'),
        ('kg_schemes',            'DROP — superseded by knowledge.kg_schemes'),
        ('kg_resources',          'DROP — superseded by TrainingProvider/FinancialInstitution/Institution'),
        ('kg_district_profiles',  'KEEP — /district-opportunity-index reads it'),
        ('kg_relationships',      'KEEP — /admin/opportunity-mapping writes it'),
        ('kg_roadmaps',           'KEEP — no equivalent in the graph'),
        ('kg_roadmap_steps',      'KEEP — no equivalent in the graph'),
        ('kg_industry_sectors',   'KEEP — controlled vocabulary for the admin UI'),
        ('kg_collaborator_types', 'KEEP — controlled vocabulary for the admin UI')
     ) as t(name, disposition)
order by t.disposition desc, t.name;

-- ── 2 · Refuse if any target holds content ──────────────────────────────────
do $$
declare
  tbl  text;
  n    bigint;
begin
  foreach tbl in array array['kg_skills','kg_schemes','kg_resources'] loop
    if to_regclass('public.' || tbl) is null then
      raise notice 'public.% does not exist — nothing to retire.', tbl;
      continue;
    end if;
    execute format('select count(*) from public.%I', tbl) into n;
    if n > 0 then
      raise exception using
        message = format('public.%s holds %s row(s) — refusing to drop it.', tbl, n),
        hint    = 'Somebody published records through the admin CMS. Either keep '
                  'these tables and leave the admin screens in place, or export '
                  'the rows into the research packages in Git (which is the '
                  'single source of truth) and re-run the sync before retrying.';
    end if;
    raise notice 'public.% is empty — will be dropped.', tbl;
  end loop;
end $$;

-- ── 3 · Drop ────────────────────────────────────────────────────────────────
-- `restrict`, not `cascade`: if something still depends on these, that is a fact
-- worth learning here rather than discovering afterwards from what disappeared.
drop table if exists public.kg_skills    restrict;
drop table if exists public.kg_schemes   restrict;
drop table if exists public.kg_resources restrict;

-- ── 4 · Confirm ─────────────────────────────────────────────────────────────
select 'after' as check,
       to_regclass('public.kg_skills')          is null as kg_skills_gone,
       to_regclass('public.kg_schemes')         is null as kg_schemes_gone,
       to_regclass('public.kg_resources')       is null as kg_resources_gone,
       to_regclass('knowledge.kg_skills')   is not null as projection_intact,
       to_regclass('public.kg_district_profiles') is not null as kept_district_profiles,
       to_regclass('public.kg_relationships')     is not null as kept_relationships;

commit;

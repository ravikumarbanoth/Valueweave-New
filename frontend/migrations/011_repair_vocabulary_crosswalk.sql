-- ValueWeave — migration 011: repair the vocabulary crosswalk table.
--
-- WHAT THIS REPAIRS
-- -----------------
-- `009_vocabulary_crosswalk.sql` declares
--
--     global_entity_id text references public.kg_entity_registry(global_entity_id)
--
-- and `public.kg_entity_registry` is created by no migration in this repository. It
-- was to come from the planned `008_knowledge_platform_projection.sql`; Platform v3.0
-- Step 1 replaced that plan with the dedicated `knowledge` schema, and 009 kept a
-- reference to a table that was never built. Applying the migrations in order fails:
--
--     ERROR:  relation "public.kg_entity_registry" does not exist
--
-- Migration 009 is NOT modified. It stays in history exactly as it shipped, and this
-- migration moves forward from whatever state the database is actually in.
--
-- THE SECOND DEFECT, FIXED HERE TOO
-- ---------------------------------
-- 009 creates the table in `public`. `frontend/lib/knowledge.js` queries it through a
-- client scoped to the `knowledge` schema, so even a successfully applied 009 would
-- have produced a table nothing could read. Vocabulary resolution is the only bridge
-- from a user's typed skill to a graph entity, so this is not cosmetic: without it
-- every district and skill silently fails to resolve.
--
-- The table belongs in `knowledge` — it is derived from `governance/vocabulary/*.csv`
-- by the same generate-and-project pipeline as the rest of that schema.
--
-- FOUR STATES THIS MUST HANDLE
-- ----------------------------
--   A  fresh database, 009 failed        -> create in `knowledge`
--   B  009 applied (pre-existing DB)     -> drop the FK, move to `knowledge`
--   C  011 already applied               -> do nothing
--   D  both `public` and `knowledge` copies exist -> keep `knowledge`, leave `public`
--
-- Every statement is guarded, so this file is safe to run repeatedly. It is written
-- as one transaction: a half-repaired crosswalk resolves some terms and not others,
-- which is worse than none resolving, because the failure looks like missing data.
--
-- NO FOREIGN KEY IS RE-ADDED, DELIBERATELY
-- ----------------------------------------
-- The referent is `knowledge.kg_entities`, which `knowledge_sync` soft-deletes from
-- (`sync_deleted_at`), never hard-deletes. A real FK would therefore never fire in
-- normal operation, and on the one path where it could — `sync --full` after a
-- restore — it would block a legitimate rebuild.
--
-- Integrity is enforced where it can be, and it is enough:
--   * `kg_vocab_resolution_is_coherent` CHECK — a resolved row must name an entity,
--     an unresolved row must not. Carried over from 009.
--   * `tests/test_vocabulary.py` — every resolved row points at a real entity of the
--     right type, checked against `entities.csv` on every test run.
--   * `scripts/health_check.sh` — reports crosswalk rows whose entity is missing
--     from the projection, so drift is visible rather than silently blocking writes.

begin;

create schema if not exists knowledge;

-- ── State A · the table does not exist anywhere ────────────────────────────
create table if not exists knowledge.kg_vocabulary_map (
  id               bigserial   primary key,
  term_kind        text        not null check (term_kind in ('skill','sector','district','tag')),
  source_vocab     text        not null,
  source_term      text        not null,
  normalised_term  text        not null,

  -- No FK. See the header.
  global_entity_id text,
  entity_type      text,
  canonical_name   text,

  match_method     text        not null check (match_method in
                     ('EXACT_NAME','ALIAS','PREFIX','FUZZY','CURATED','NO_COUNTERPART')),
  match_score      numeric(6,4),
  notes            text,

  synced_at        timestamptz not null default now(),

  -- Carried over from 009. The invariant the dropped FK was reaching for:
  -- a resolved row points somewhere, an unresolved row points nowhere.
  constraint kg_vocab_resolution_is_coherent check (
    (match_method = 'NO_COUNTERPART' and global_entity_id is null)
    or (match_method <> 'NO_COUNTERPART' and global_entity_id is not null)
  ),

  unique (term_kind, source_vocab, normalised_term)
);

-- ── State B · 009 applied, so a `public` copy exists ───────────────────────
do $$
declare
  has_public   boolean;
  moved_rows   bigint;
begin
  select exists (
    select 1 from information_schema.tables
     where table_schema = 'public' and table_name = 'kg_vocabulary_map'
  ) into has_public;

  if not has_public then
    raise notice '011: no public.kg_vocabulary_map — nothing to migrate (state A or C)';
    return;
  end if;

  -- Drop the unbuildable foreign key wherever it landed. Named dynamically
  -- because Postgres generates the constraint name.
  execute (
    select coalesce(string_agg(
      format('alter table public.kg_vocabulary_map drop constraint %I;', conname), ' '), '')
      from pg_constraint
     where conrelid = 'public.kg_vocabulary_map'::regclass
       and contype = 'f'
  );

  -- Copy rows across. `on conflict do nothing` makes state D safe: if a
  -- `knowledge` copy already holds a term, the projected row wins.
  insert into knowledge.kg_vocabulary_map
        (term_kind, source_vocab, source_term, normalised_term,
         global_entity_id, entity_type, canonical_name,
         match_method, match_score, notes)
  select term_kind, source_vocab, source_term, normalised_term,
         global_entity_id, entity_type, canonical_name,
         match_method, match_score, notes
    from public.kg_vocabulary_map
      on conflict (term_kind, source_vocab, normalised_term) do nothing;

  get diagnostics moved_rows = row_count;
  raise notice '011: migrated % row(s) from public to knowledge', moved_rows;

  -- The `public` table is left in place, empty of purpose but not dropped.
  --
  -- Dropping a table in a repair migration is how a rollback becomes
  -- irreversible. Anything still reading `public.kg_vocabulary_map` keeps
  -- working, and retiring it is a separate, reviewable decision.
  comment on table public.kg_vocabulary_map is
    'SUPERSEDED by knowledge.kg_vocabulary_map (migration 011). Retained for '
    'rollback safety; no application code reads this table. Safe to drop once '
    '011 is confirmed in every environment.';
end $$;

-- ── Indexes ────────────────────────────────────────────────────────────────
-- `resolveTerms()` looks up by (term_kind, normalised_term) and by nothing else,
-- so that index is the one that matters. The entity index serves the reverse
-- question — "what did users call this?" — used by the health check.
create index if not exists kg_vocab_lookup_idx
  on knowledge.kg_vocabulary_map (term_kind, normalised_term);
create index if not exists kg_vocab_entity_idx
  on knowledge.kg_vocabulary_map (global_entity_id)
  where global_entity_id is not null;
create index if not exists kg_vocab_method_idx
  on knowledge.kg_vocabulary_map (match_method);

-- ── RLS ────────────────────────────────────────────────────────────────────
-- Same posture as the rest of the `knowledge` schema: public reference data,
-- readable by anyone, writable by nobody. The crosswalk is derived from Git, so a
-- hand-edit would be reverted by the next load and lost from source control. No
-- write policy exists, which makes that impossible rather than discouraged.
alter table knowledge.kg_vocabulary_map enable row level security;

drop policy if exists kg_vocabulary_map_read on knowledge.kg_vocabulary_map;
create policy kg_vocabulary_map_read
  on knowledge.kg_vocabulary_map for select
  using (true);

grant usage on schema knowledge to anon, authenticated;
grant select on knowledge.kg_vocabulary_map to anon, authenticated;

-- The sync writes this table too, and Supabase's service_role is not a superuser:
-- BYPASSRLS exempts it from row-level security, not from GRANT checks. Without
-- these it fails with `permission denied for schema knowledge`. Same posture as
-- the rest of the schema — no DELETE, because the sync soft-deletes.
grant usage on schema knowledge to service_role;
grant select, insert, update on knowledge.kg_vocabulary_map to service_role;
grant usage on all sequences in schema knowledge to service_role;

commit;

-- ── Verify ─────────────────────────────────────────────────────────────────
--   select count(*) from knowledge.kg_vocabulary_map;            -- 202 after load
--   select term_kind, count(*) from knowledge.kg_vocabulary_map  -- 33 / 22 / 147
--    group by 1 order by 1;
--   select count(*) from pg_constraint                           -- 0
--    where conrelid = 'knowledge.kg_vocabulary_map'::regclass and contype = 'f';
--
-- Rollback: `drop table knowledge.kg_vocabulary_map;`. The `public` copy is intact,
-- so this migration is reversible without data loss.

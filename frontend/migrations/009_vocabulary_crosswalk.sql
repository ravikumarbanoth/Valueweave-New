-- ValueWeave — Vocabulary Crosswalk (Platform v3.0, Step 0)
-- Run AFTER 008_knowledge_platform_projection.sql
--
-- WHY THIS TABLE EXISTS
-- ---------------------
-- profiles.skills is free text. The knowledge graph names skills differently.
-- Measured before this table existed: 7 of the 57 skills the onboarding form
-- suggests resolved to a graph Skill. Every feature joining a user to the graph
-- ran through that, so all of them would have returned nothing for most users,
-- silently.
--
-- This table is that join, made explicit and reviewable. It is populated by
-- governance/vocabulary/build_crosswalk.py, which is the source of truth; this
-- table is a projection of the three committed CSVs.
--
-- NO_COUNTERPART IS A VALUE, NOT AN ABSENCE
-- -----------------------------------------
-- It means "this term is real and the knowledge base has no researched data for
-- it" -- true of 50 skills users are actively nudged to claim. Storing it lets
-- the UI say so instead of rendering an empty panel, and makes the collection
-- backlog a query rather than a spreadsheet.

create table if not exists public.kg_vocabulary_map (
  id               bigserial   primary key,
  term_kind        text        not null check (term_kind in ('skill','sector','district','tag')),
  source_vocab     text        not null,   -- onboarding | idea_library | idea_library_groups | static_districts
  source_term      text        not null,
  normalised_term  text        not null,   -- lowercase, & -> and, punctuation collapsed

  global_entity_id text        references public.kg_entity_registry(global_entity_id) on delete restrict,
  entity_type      text,
  canonical_name   text,

  -- How this row was decided. Never null: a row with no recorded method is a guess.
  match_method     text        not null check (match_method in
                     ('EXACT_NAME','ALIAS','PREFIX','FUZZY','CURATED','NO_COUNTERPART')),
  match_score      numeric(6,4),
  notes            text,

  synced_at        timestamptz not null default now(),

  unique (term_kind, source_vocab, normalised_term),

  -- A resolved row must point somewhere; an unresolved one must not. This makes
  -- the incoherent state unrepresentable rather than merely discouraged.
  constraint kg_vocab_resolution_is_coherent check (
    (match_method =  'NO_COUNTERPART' and global_entity_id is null)
    or
    (match_method <> 'NO_COUNTERPART' and global_entity_id is not null)
  )
);

-- The hot path: "resolve these free-text skills for this user".
create index if not exists kg_vocab_lookup_idx
  on public.kg_vocabulary_map(term_kind, normalised_term);

-- Reverse: "which user-facing terms point at this entity?"
create index if not exists kg_vocab_entity_idx
  on public.kg_vocabulary_map(global_entity_id)
  where global_entity_id is not null;

-- The collection backlog query. Partial, because someone will run it often and
-- it should stay fast as the resolved set grows.
create index if not exists kg_vocab_unresolved_idx
  on public.kg_vocabulary_map(term_kind, source_vocab)
  where match_method = 'NO_COUNTERPART';

alter table public.kg_vocabulary_map enable row level security;

-- Readable by everyone: the UI needs it to explain why a term has no data.
drop policy if exists "kg vocab public read" on public.kg_vocabulary_map;
create policy "kg vocab public read"
  on public.kg_vocabulary_map for select using (true);

-- Written only by the sync (service role, bypasses RLS) or an admin.
drop policy if exists "kg vocab admin write" on public.kg_vocabulary_map;
create policy "kg vocab admin write"
  on public.kg_vocabulary_map for all
  using (public.is_valueweave_admin())
  with check (public.is_valueweave_admin());

comment on table public.kg_vocabulary_map is
  'Maps free-text application vocabulary to knowledge graph entities. Projection of '
  'governance/vocabulary/*_crosswalk.csv; Git is canonical. NO_COUNTERPART is a '
  'determinate statement that no researched data exists for the term.';

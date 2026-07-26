# Database Extension Plan — ValueWeave v3.0

**Phase 3/5 deliverable.** Exact schema changes: new tables, extended columns, indexes,
RLS policies, and migration order.

**Every change is additive.** No table is dropped, no column is renamed or removed, no
constraint on existing data is tightened. A rollback is `drop table` on the new objects
plus `drop column` on eight nullable additions.

Migrations continue the existing numbering in `frontend/migrations/` (last: `007`).

---

## 1. Summary

| | Count |
|---|---:|
| New tables | 6 |
| Existing tables extended | 4 (8 nullable columns) |
| Existing tables unchanged | 26 |
| New indexes | 21 |
| New RLS policies | 12 |
| New materialised views | 2 |
| Migrations | 4 (`008`–`011`) |
| Estimated projected rows | ~1,900 |

---

## 2. Migration `008` — entity and edge registries

The two tables everything else references.

```sql
-- ─── 008_knowledge_platform_projection.sql ───────────────────────────
-- Projection of knowledge_graph/ into Postgres. Written ONLY by
-- scripts/sync_to_supabase.py using the service role. Disposable and
-- rebuildable: packages/ in Git remains canonical (ADR-001).

create table if not exists public.kg_entity_registry (
  global_entity_id    text primary key,          -- vw:crop:turmeric — stable (ADR-002)
  entity_type         text not null,
  canonical_name      text not null,
  entity_slug         text not null,
  source_package      text not null,
  package_local_id    text,
  confidence_score    smallint not null default 0
                        check (confidence_score between 0 and 100),
  verification_status text not null default 'VST-NEEDS_REVIEW',
  lifecycle_state     text not null default 'PUBLISHED',
  status              text not null default 'published'
                        check (status in ('draft','published')),
  source              text not null default 'package'
                        check (source in ('package','admin')),
  synced_at           timestamptz not null default now()
);
```

`global_entity_id` is the primary key rather than a surrogate uuid. It is deterministic
and stable across rebuilds (ADR-002), which means a rebuild of the projection does not
invalidate any foreign key pointing at it — and every extension column in §4 points at it.
A uuid would be regenerated on every rebuild and break exactly that.

```sql
create table if not exists public.kg_entity_aliases (
  alias_id         text primary key,
  global_entity_id text not null
                     references public.kg_entity_registry(global_entity_id) on delete cascade,
  alias            text not null,
  alias_type       text,
  source_package   text,
  synced_at        timestamptz not null default now()
);

create table if not exists public.kg_graph_edges (
  relationship_id     text primary key,          -- vwr:000156
  from_entity         text not null
                        references public.kg_entity_registry(global_entity_id) on delete cascade,
  relationship_type   text not null,
  to_entity           text not null
                        references public.kg_entity_registry(global_entity_id) on delete cascade,
  confidence          smallint not null default 0
                        check (confidence between 0 and 100),
  -- Provenance: an edge that cannot name its source row is not written.
  provenance_package  text not null,
  provenance_dataset  text not null,
  provenance_row_id   text not null,
  derived_at          date,
  notes               text,
  synced_at           timestamptz not null default now(),
  constraint kg_graph_edges_no_self_loop check (from_entity <> to_entity),
  unique (from_entity, relationship_type, to_entity)
);
```

The two constraints mirror graph checks G5 (no self-loops) and the duplicate-triple check.
They are cheap here and mean a sync bug cannot produce a graph the validator would reject.

**Why a separate table from `kg_relationships`:** see `SUPABASE_INTEGRATION.md` §4. The
existing table is generic, untyped and admin-writable; these edges are typed and carry
provenance. Overloading one table means either dropping provenance or adding six columns
that are null for every admin row.

### Indexes

```sql
create index if not exists kg_entity_type_idx      on public.kg_entity_registry(entity_type);
create index if not exists kg_entity_package_idx   on public.kg_entity_registry(source_package);
create index if not exists kg_entity_slug_idx      on public.kg_entity_registry(entity_slug);
create index if not exists kg_entity_name_trgm_idx on public.kg_entity_registry
  using gin (canonical_name gin_trgm_ops);        -- typo-tolerant search (§5)
create index if not exists kg_entity_type_conf_idx on public.kg_entity_registry(entity_type, confidence_score desc);

create index if not exists kg_alias_entity_idx     on public.kg_entity_aliases(global_entity_id);
create index if not exists kg_alias_trgm_idx       on public.kg_entity_aliases using gin (alias gin_trgm_ops);

create index if not exists kg_edges_from_idx       on public.kg_graph_edges(from_entity, relationship_type);
create index if not exists kg_edges_to_idx         on public.kg_graph_edges(to_entity, relationship_type);
create index if not exists kg_edges_type_idx       on public.kg_graph_edges(relationship_type);
```

`kg_edges_from_idx` and `kg_edges_to_idx` are composite on `(entity, type)` rather than on
the entity alone, because every real query filters both — "outgoing `REQUIRES_SKILL` edges
of this business" is the shape of nearly every traversal in
`PAGE_BY_PAGE_MAPPING.md`. `pg_trgm` is enabled by `create extension if not exists pg_trgm`.

---

## 3. Migration `009` — vocabulary crosswalk

The table that makes Step 0 of the roadmap real. Without it,
`profiles.skills` — free text — cannot reach the graph.

```sql
-- ─── 009_vocabulary_crosswalk.sql ────────────────────────────────────
create table if not exists public.kg_vocabulary_map (
  id               bigserial primary key,
  term_kind        text not null check (term_kind in ('skill','sector','district','tag')),
  source_vocab     text not null,   -- 'onboarding' | 'idea_library' | 'profiles' | 'static_districts'
  source_term      text not null,
  normalised_term  text not null,   -- lowercase, punctuation collapsed, & -> and

  global_entity_id text references public.kg_entity_registry(global_entity_id) on delete restrict,
  entity_type      text,

  -- How this row was decided. NO_COUNTERPART is a determinate statement, not a gap.
  match_method     text not null check (match_method in
                     ('EXACT_NAME','ALIAS','PREFIX','FUZZY','CURATED','NO_COUNTERPART')),
  match_score      numeric(5,4),
  decided_by       text,
  decided_at       timestamptz not null default now(),
  notes            text,

  unique (term_kind, source_vocab, normalised_term),
  -- A resolved row must point somewhere; NO_COUNTERPART must not.
  constraint kg_vocab_resolution_is_coherent check (
    (match_method = 'NO_COUNTERPART' and global_entity_id is null)
    or (match_method <> 'NO_COUNTERPART' and global_entity_id is not null)
  )
);

create index if not exists kg_vocab_lookup_idx on public.kg_vocabulary_map(term_kind, normalised_term);
create index if not exists kg_vocab_entity_idx on public.kg_vocabulary_map(global_entity_id);
create index if not exists kg_vocab_unresolved_idx on public.kg_vocabulary_map(term_kind)
  where match_method = 'NO_COUNTERPART';
```

Three details that carry the design:

- **`on delete restrict`**, not cascade. If an entity disappears from the graph, the sync
  must fail loudly rather than silently void a curated decision.
- **The `check` constraint** makes the incoherent state unrepresentable: a resolved row
  with no target, or a `NO_COUNTERPART` row that points somewhere.
- **The partial index** on unresolved terms is the collection backlog query — "what do
  users claim that we have no data for?" — and it should be fast because someone will run
  it often.

### Expected initial contents

| `term_kind` | Source terms | Resolvable today | `NO_COUNTERPART` |
|---|---:|---:|---:|
| `skill` | 57 onboarding + 46 idea (~80 distinct) | ~12 | **~68** |
| `sector` | 22 idea sectors | 9 | 13 |
| `district` | 14 static + 19 idea (~20 distinct) | ~18 | ~2 |
| **Total** | **~122** | **~39** | **~83** |

Two thirds of the table will be `NO_COUNTERPART` on day one. That is the accurate picture
and the reason it must be a first-class value rather than a missing row.

---

## 4. Migration `010` — extend existing tables

Eight nullable columns across four tables. Every one is `add column if not exists`, so the
migration is re-runnable and no existing row changes.

```sql
-- ─── 010_link_users_to_knowledge.sql ─────────────────────────────────
alter table public.profiles
  add column if not exists kg_skill_ids       text[] not null default '{}',
  add column if not exists kg_district_id     text references public.kg_entity_registry(global_entity_id),
  add column if not exists kg_resolved_at     timestamptz;

alter table public.opportunities
  add column if not exists kg_industry_id     text references public.kg_entity_registry(global_entity_id),
  add column if not exists kg_district_id     text references public.kg_entity_registry(global_entity_id),
  add column if not exists kg_skill_ids       text[] not null default '{}';

alter table public.collaborator_profiles
  add column if not exists kg_industry_ids    text[] not null default '{}';

alter table public.search_events
  add column if not exists result_kind        text;   -- 'idea' | 'entity' | 'opportunity' | 'article'
```

**`profiles.skills` is not touched.** It stays the free-text array the onboarding form
writes. `kg_skill_ids` is the *resolved* view of it, recomputed by a trigger or a
background pass. Two representations, one writable by the user, one derived — the same
split as Git and the projection.

**Why arrays rather than join tables.** `kg_skill_ids text[]` costs one GIN index and no
join for the read pattern that dominates: "show me this user's skills". A join table would
be correct for a many-to-many with attributes, but there are no attributes on the link —
`profiles.skills` is already `text[]` and this mirrors it, which is the pattern the
codebase already uses.

```sql
create index if not exists profiles_kg_skills_idx    on public.profiles using gin (kg_skill_ids);
create index if not exists profiles_kg_district_idx  on public.profiles(kg_district_id);
create index if not exists opportunities_kg_ind_idx  on public.opportunities(kg_industry_id);
create index if not exists opportunities_kg_dist_idx on public.opportunities(kg_district_id);
create index if not exists opportunities_kg_skl_idx  on public.opportunities using gin (kg_skill_ids);
create index if not exists collab_kg_industries_idx  on public.collaborator_profiles using gin (kg_industry_ids);
```

### Marking projected rows in the existing CMS tables

```sql
do $$
declare t text;
begin
  foreach t in array array['kg_district_profiles','kg_skills','kg_resources',
                           'kg_schemes','kg_industry_sectors'] loop
    execute format($f$
      alter table public.%I
        add column if not exists source text not null default 'admin'
          check (source in ('package','admin')),
        add column if not exists global_entity_id text
          references public.kg_entity_registry(global_entity_id) on delete set null,
        add column if not exists source_package text,
        add column if not exists source_dataset text,
        add column if not exists source_row_id text,
        add column if not exists confidence_score smallint,
        add column if not exists verification_status text
    $f$, t);
    execute format('create index if not exists %I on public.%I(source)', t || '_source_idx', t);
  end loop;
end $$;
```

`default 'admin'` matters: every row that exists **before** this migration was authored by
an admin, and the default states that correctly without an UPDATE. The sync only ever
writes `source = 'package'` rows, so risk R6 — sync and admin overwriting each other — is
prevented by construction rather than by convention.

`confidence_score` and `verification_status` are nullable here on purpose: admin-authored
rows genuinely have neither, and a default of 0 or `'VST-NEEDS_REVIEW'` would be a
fabricated claim about editorial content.

---

## 5. Migration `011` — search and materialised views

### Unified search

```sql
create extension if not exists pg_trgm;

alter table public.kg_entity_registry
  add column if not exists search_tsv tsvector
    generated always as (to_tsvector('english', coalesce(canonical_name, ''))) stored;

create index if not exists kg_entity_fts_idx on public.kg_entity_registry using gin (search_tsv);
```

Postgres FTS plus `pg_trgm` covers exact, prefix and typo-tolerant matching, and joins
natively against `profiles` and `opportunities`. It does **not** reproduce
`SearchEngine`'s ranked four-mode ladder, and the UI should not pretend it does — the
Python engine stays the reference implementation and the admin tool
(`SUPABASE_INTEGRATION.md` §7).

### Materialised views

Two, both for read patterns that would otherwise be a recursive query on every page load.

```sql
-- District → everything located in it. Powers /district/[slug] and dashboard rail 1.
create materialized view if not exists public.mv_district_knowledge as
select
  d.global_entity_id            as district_id,
  d.canonical_name              as district_name,
  e.entity_type,
  count(*)                      as entity_count,
  jsonb_agg(
    jsonb_build_object('id', e.global_entity_id, 'name', e.canonical_name,
                       'confidence', e.confidence_score)
    order by e.confidence_score desc
  ) filter (where e.global_entity_id is not null) as entities
from public.kg_entity_registry d
join public.kg_graph_edges g
  on g.to_entity = d.global_entity_id
 and g.relationship_type in ('LOCATED_IN','GENERATES_EMPLOYMENT')
join public.kg_entity_registry e on e.global_entity_id = g.from_entity
where d.entity_type = 'District'
group by 1, 2, 3;

create unique index if not exists mv_district_knowledge_pk
  on public.mv_district_knowledge(district_id, entity_type);

-- Skill → what requires it. Powers dashboard rails 3 and 4, and SkillGapPanel.
create materialized view if not exists public.mv_skill_demand as
select
  s.global_entity_id  as skill_id,
  s.canonical_name    as skill_name,
  count(*)            as required_by_count,
  jsonb_agg(
    jsonb_build_object('id', b.global_entity_id, 'name', b.canonical_name,
                       'type', b.entity_type, 'confidence', g.confidence)
    order by g.confidence desc
  ) as required_by
from public.kg_entity_registry s
join public.kg_graph_edges g
  on g.to_entity = s.global_entity_id and g.relationship_type = 'REQUIRES_SKILL'
join public.kg_entity_registry b on b.global_entity_id = g.from_entity
where s.entity_type = 'Skill'
group by 1, 2;

create unique index if not exists mv_skill_demand_pk on public.mv_skill_demand(skill_id);
```

The unique indexes exist so both can be refreshed `concurrently` — the sync must not lock
a view that a user page is reading.

Refreshed by the sync, after step 6 of its ordering:

```sql
refresh materialized view concurrently public.mv_district_knowledge;
refresh materialized view concurrently public.mv_skill_demand;
```

Materialised views are the right shape here because the underlying data changes on a
commit cadence, not a request cadence. A plain view would re-aggregate 865 edges on every
dashboard load for data that changes weekly.

---

## 6. RLS policies

Every new table follows the shape `kg_*` already uses. Nothing invents a new pattern.

```sql
alter table public.kg_entity_registry enable row level security;
alter table public.kg_entity_aliases  enable row level security;
alter table public.kg_graph_edges     enable row level security;
alter table public.kg_vocabulary_map  enable row level security;

-- Entities: published to everyone, everything to admins.
create policy "kg entity public read" on public.kg_entity_registry
  for select using (status = 'published' or public.is_valueweave_admin());
create policy "kg entity admin write" on public.kg_entity_registry
  for all using (public.is_valueweave_admin()) with check (public.is_valueweave_admin());

-- Aliases and edges are meaningless without their entities and carry no
-- independent sensitivity, so they read openly — matching the existing
-- "kg relationships public read" policy.
create policy "kg alias public read" on public.kg_entity_aliases for select using (true);
create policy "kg alias admin write"  on public.kg_entity_aliases
  for all using (public.is_valueweave_admin()) with check (public.is_valueweave_admin());

create policy "kg edges public read" on public.kg_graph_edges for select using (true);
create policy "kg edges admin write" on public.kg_graph_edges
  for all using (public.is_valueweave_admin()) with check (public.is_valueweave_admin());

-- Crosswalk: readable (the UI needs it to explain a NO_COUNTERPART), admin-writable.
create policy "kg vocab public read" on public.kg_vocabulary_map for select using (true);
create policy "kg vocab admin write" on public.kg_vocabulary_map
  for all using (public.is_valueweave_admin()) with check (public.is_valueweave_admin());
```

**Materialised views do not honour RLS.** Both views here aggregate only published,
public-by-policy entity data, so this is acceptable — but it must be a stated decision,
not an oversight. If a projected entity ever becomes non-public, these views must be
rebuilt as security-invoker functions.

**The service role bypasses RLS entirely.** It exists only in CI, only for the sync. It
must never appear in a `NEXT_PUBLIC_*` variable or a client component.

### The gap this leaves

There is **no per-user permission model for knowledge**, and none is needed: package data
is public research. The existing admin/non-admin split is the only distinction. If
district- or organisation-scoped knowledge is ever introduced, this is where it lands, and
it will need a real rethink rather than another policy.

---

## 7. Migration order and rollback

| # | File | Depends on | Reversible by |
|---|---|---|---|
| 008 | `008_knowledge_platform_projection.sql` | `pg_trgm` | `drop table kg_graph_edges, kg_entity_aliases, kg_entity_registry cascade` |
| 009 | `009_vocabulary_crosswalk.sql` | 008 | `drop table kg_vocabulary_map` |
| 010 | `010_link_users_to_knowledge.sql` | 008 | `alter table ... drop column` ×8, plus the `kg_*` column loop |
| 011 | `011_search_and_views.sql` | 008, 010 | `drop materialized view`, `drop column search_tsv` |

Run in order. 008 must precede 009 and 010 because both add foreign keys into
`kg_entity_registry`.

**Rollback is genuinely clean.** No existing row is modified by any of these migrations —
the only writes to pre-existing tables are `add column` with a default, and `default` on
`add column` does not rewrite the table in Postgres 11+.

---

## 8. Storage and performance

| Table | Rows | Est. size |
|---|---:|---:|
| `kg_entity_registry` | 647 | ~250 KB with indexes |
| `kg_entity_aliases` | 150 | ~40 KB |
| `kg_graph_edges` | 865 | ~400 KB |
| `kg_vocabulary_map` | ~122 | ~30 KB |
| Backfilled `kg_*` CMS rows | ~250 | ~1 MB (rich text) |
| Materialised views | ~200 | ~500 KB |
| **Total** | **~2,300** | **< 3 MB** |

This is a small dataset. The indexes exist for query *shape*, not volume — a sequential
scan of 647 rows is fast today and will not be when the graph is ten times larger.

**Query budget.** Every page addition in `PAGE_BY_PAGE_MAPPING.md` should cost at most two
round trips: one for the entity, one for its edges — or a single read from a materialised
view. The dashboard's four rails must be **one** query against `mv_district_knowledge` and
**one** against `mv_skill_demand`, not eight. If a page needs more than three queries, the
view is missing.

---

## 9. What is deliberately not built

| Not built | Why |
|---|---|
| Per-user knowledge permissions | Package data is public research. No requirement exists. |
| Write path from app to packages | Violates ADR-001. Corrections go through the release process. |
| A `teams` table | See `FRONTEND_INTEGRATION_PLAN.md` §9 — a product decision, not an integration. |
| Assessment tables | The brief's "Assessment Profile" has no data behind it in any package. |
| Realtime subscriptions on projected tables | Package data changes by commit, not by the second. |
| A recommendations table | Recommendations are computed at read time from the views. Persisting them adds a staleness problem before there is any evidence the computation is too slow. |

-- ValueWeave — Collaborator Marketplace & Opportunity Ecosystem
-- Run once in the Supabase SQL Editor, AFTER 001_research_articles.sql
-- (it reuses public.is_admin() defined there).
--
-- Extends the EXISTING public.opportunities table (no parallel table):
-- `category` is the sector field; new columns are nullable so all
-- existing rows and the existing post form keep working unchanged.

-- ─── EXTEND OPPORTUNITIES ───────────────────────────────────
alter table public.opportunities
  add column if not exists district         text,
  add column if not exists state            text,
  add column if not exists founder_role     text,
  add column if not exists investment_range text,
  add column if not exists status           text not null default 'open'
    check (status in ('open','filled','closed')),
  add column if not exists created_by       text not null default 'user'
    check (created_by in ('user','system_seed'));

-- System-seeded opportunities have no owning user
alter table public.opportunities alter column owner_id drop not null;

create index if not exists opportunities_district_idx on public.opportunities(district);
create index if not exists opportunities_state_idx    on public.opportunities(state);
create index if not exists opportunities_status_idx   on public.opportunities(status);
-- category (sector) index already exists: opportunities_category_idx

-- Admins can manage system-seeded rows (owner policies don't cover null owner)
drop policy if exists "Admins manage seeded opportunities" on public.opportunities;
create policy "Admins manage seeded opportunities"
  on public.opportunities for all
  using (created_by = 'system_seed' and public.is_admin())
  with check (created_by = 'system_seed' and public.is_admin());

-- ─── COLLABORATOR PROFILES (from Discover Yourself assessment) ──
create table if not exists public.collaborator_profiles (
  user_id             uuid primary key references public.profiles(id) on delete cascade,
  archetype           text not null,
  secondary_archetype text,
  founder_role        text,
  district            text,
  state               text,
  top_sectors         text[] default '{}',
  top_idea            text,
  budget              text,
  ep_score            integer,
  open_to_collaborate boolean not null default true,
  created_at          timestamptz not null default now(),
  updated_at          timestamptz not null default now()
);

create index if not exists collaborator_profiles_district_idx on public.collaborator_profiles(district);
create index if not exists collaborator_profiles_state_idx    on public.collaborator_profiles(state);
create index if not exists collaborator_profiles_sectors_idx  on public.collaborator_profiles using gin(top_sectors);

drop trigger if exists trg_collaborator_profiles_updated on public.collaborator_profiles;
create trigger trg_collaborator_profiles_updated
  before update on public.collaborator_profiles
  for each row execute function public.research_set_updated_at();

alter table public.collaborator_profiles enable row level security;

drop policy if exists "Collaborator profiles are viewable by everyone" on public.collaborator_profiles;
create policy "Collaborator profiles are viewable by everyone"
  on public.collaborator_profiles for select
  using (open_to_collaborate = true or auth.uid() = user_id);

drop policy if exists "Users manage own collaborator profile" on public.collaborator_profiles;
create policy "Users manage own collaborator profile"
  on public.collaborator_profiles for all
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

-- ─── OPPORTUNITY INTERESTS ──────────────────────────────────
-- "Express interest" on system-seeded opportunities, which have no owner
-- to receive a connection request (user↔user posts keep using the
-- existing public.connections flow).
create table if not exists public.opportunity_interests (
  id             uuid primary key default gen_random_uuid(),
  opportunity_id uuid not null references public.opportunities(id) on delete cascade,
  user_id        uuid not null references public.profiles(id) on delete cascade,
  message        text,
  status         text not null default 'pending' check (status in ('pending','contacted','closed')),
  created_at     timestamptz not null default now(),
  unique (opportunity_id, user_id)
);

create index if not exists opportunity_interests_opp_idx  on public.opportunity_interests(opportunity_id);
create index if not exists opportunity_interests_user_idx on public.opportunity_interests(user_id);

alter table public.opportunity_interests enable row level security;

drop policy if exists "Users see own interests" on public.opportunity_interests;
create policy "Users see own interests"
  on public.opportunity_interests for select
  using (auth.uid() = user_id or public.is_admin());

drop policy if exists "Users express own interest" on public.opportunity_interests;
create policy "Users express own interest"
  on public.opportunity_interests for insert
  with check (auth.uid() = user_id);

drop policy if exists "Users withdraw own interest" on public.opportunity_interests;
create policy "Users withdraw own interest"
  on public.opportunity_interests for delete
  using (auth.uid() = user_id);

drop policy if exists "Admins update interest status" on public.opportunity_interests;
create policy "Admins update interest status"
  on public.opportunity_interests for update
  using (public.is_admin());

-- NOTE on business_ideas (Phase 6): the Idea Library ships as versioned
-- JSON in frontend/lib/idea-library/ (122 ideas) and serves /ideas via
-- SSG. A business_ideas table would duplicate that working system, so it
-- is intentionally NOT created. The JSON is structured for a drop-in
-- Supabase migration later if write-access is ever needed.

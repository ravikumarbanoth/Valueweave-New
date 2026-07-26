-- ValueWeave — Missing application features (Platform v3.0, Step 2, Phase 8)
-- Run AFTER 009_vocabulary_crosswalk.sql
--
-- WHAT THIS IS
-- ------------
-- Four features the platform references but does not have. Each was verified
-- absent against every migration in the repository before being added here:
--
--   assessment_results   referenced by the brief's "Assessment Profile"; no table,
--                        no UI, no scoring logic anywhere
--   mentor_profiles      the user_intelligence `mentors` category returns
--                        NO_DATA_SOURCE for every user because nothing records a
--                        mentor. `collaborator_profiles.archetype` holds
--                        self-declared archetypes, none of which means "mentor"
--   events               the `events` category likewise returns NO_DATA_SOURCE;
--                        no Event entity, no table, no calendar source
--   teams / team_members the brief's Team Page assumes these. `connections` is
--                        opportunity-scoped and 1:1, which is a different shape
--
-- WHAT THIS IS NOT
-- ----------------
-- **There is no seed data in this file, deliberately.** Inserting a plausible
-- mentor or a plausible event would make the corresponding recommendation category
-- start returning rows that describe nobody. The whole platform is built on the
-- rule that an unsourced claim is worse than a stated gap, and a fabricated mentor
-- is an unsourced claim about a person.
--
-- These tables therefore ship empty. The recommendation categories keep returning
-- NO_DATA_SOURCE until a real feature populates them, which is the correct
-- behaviour and is asserted by tests/test_user_intelligence.py.
--
-- WHY CREATE THEM AT ALL
-- ----------------------
-- So the shape is agreed and reviewable before a feature is built on top of it,
-- and so the intelligence engine's `INPUTS` registry can move each one from
-- MISSING to AVAILABLE by changing one line rather than by a redesign.

-- ─── ASSESSMENTS ────────────────────────────────────────────────────────────
-- A completed assessment for one user. Deliberately generic about *what* was
-- assessed: no assessment feature exists yet, so pinning the schema to a
-- particular question set would be guessing at a product that has not been
-- designed.
create table if not exists public.assessment_results (
  id              uuid        primary key default gen_random_uuid(),
  user_id         uuid        not null references public.profiles(id) on delete cascade,
  assessment_key  text        not null,          -- e.g. 'entrepreneur_readiness_v1'
  assessment_version text     not null default 'v1',
  -- 0-100 so it composes with the intelligence engine's score range without a
  -- conversion nobody would remember to apply.
  score           smallint    check (score between 0 and 100),
  -- Per-dimension results. jsonb rather than columns because the dimensions are
  -- unknown until an assessment is designed, and a migration per dimension is a
  -- worse outcome than a documented jsonb shape.
  dimensions      jsonb       not null default '{}'::jsonb,
  answers         jsonb       not null default '{}'::jsonb,
  completed_at    timestamptz not null default now(),
  created_at      timestamptz not null default now(),
  unique (user_id, assessment_key, assessment_version)
);

create index if not exists assessment_results_user_idx
  on public.assessment_results (user_id, completed_at desc);

alter table public.assessment_results enable row level security;

-- Own rows only. An assessment result is about a person and is not public.
drop policy if exists "assessment own read" on public.assessment_results;
create policy "assessment own read"
  on public.assessment_results for select using (auth.uid() = user_id);

drop policy if exists "assessment own insert" on public.assessment_results;
create policy "assessment own insert"
  on public.assessment_results for insert with check (auth.uid() = user_id);

drop policy if exists "assessment own update" on public.assessment_results;
create policy "assessment own update"
  on public.assessment_results for update using (auth.uid() = user_id);

-- ─── MENTORS ────────────────────────────────────────────────────────────────
-- Opt-in, and one row per user at most. Modelled as an extension of `profiles`
-- rather than a separate directory of people: a mentor IS a user who has offered
-- to mentor, and a parallel people table would immediately drift from `profiles`.
create table if not exists public.mentor_profiles (
  user_id           uuid        primary key references public.profiles(id) on delete cascade,
  -- Explicit opt-in. Nobody becomes a mentor by inference from their profile,
  -- which is exactly what the intelligence engine refused to do.
  is_active         boolean     not null default false,
  headline          text,
  expertise_areas   text[]      not null default '{}',
  -- Where possible these should be crosswalked skill terms, so mentor matching can
  -- use the same vocabulary as everything else. Free text is allowed because
  -- forcing a controlled vocabulary at 22.8% resolve rate would reject real
  -- expertise.
  expertise_skills  text[]      not null default '{}',
  districts_served  text[]      not null default '{}',
  languages         text[]      not null default '{}',
  years_experience  smallint    check (years_experience between 0 and 80),
  capacity_per_month smallint   check (capacity_per_month between 0 and 100),
  engagement_mode   text        check (engagement_mode in ('online','in_person','both')),
  -- Whether a human has checked this person is who they say they are. Defaults to
  -- false and is never set by an automated process, matching the platform's
  -- verification discipline.
  verified_by_admin boolean     not null default false,
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now()
);

create index if not exists mentor_profiles_active_idx
  on public.mentor_profiles (is_active) where is_active;
create index if not exists mentor_profiles_skills_idx
  on public.mentor_profiles using gin (expertise_skills);

alter table public.mentor_profiles enable row level security;

-- Active mentors are publicly readable: the point of opting in is to be found.
drop policy if exists "mentors public read" on public.mentor_profiles;
create policy "mentors public read"
  on public.mentor_profiles for select
  using (is_active or auth.uid() = user_id or public.is_valueweave_admin());

drop policy if exists "mentors own write" on public.mentor_profiles;
create policy "mentors own write"
  on public.mentor_profiles for all
  using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- ─── EVENTS ─────────────────────────────────────────────────────────────────
create table if not exists public.events (
  id            uuid        primary key default gen_random_uuid(),
  slug          text        unique not null,
  title         text        not null,
  description   text,
  event_type    text        check (event_type in
                  ('workshop','webinar','meetup','training','expo','deadline')),
  -- A scheme application deadline is an event a user needs to know about, so the
  -- table can point at a knowledge entity. Nullable: most events are not scheme
  -- deadlines.
  related_entity_id text,
  district      text,
  venue         text,
  is_online     boolean     not null default false,
  starts_at     timestamptz not null,
  ends_at       timestamptz,
  registration_url text,
  organiser     text,
  -- Same discipline as every other table in this platform: an event with no source
  -- is an event nobody should act on.
  data_source   text,
  source_url    text,
  status        text        not null default 'draft'
                  check (status in ('draft','published','cancelled')),
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

create index if not exists events_upcoming_idx
  on public.events (starts_at) where status = 'published';
create index if not exists events_district_idx on public.events (district);

alter table public.events enable row level security;

drop policy if exists "events public read" on public.events;
create policy "events public read"
  on public.events for select
  using (status = 'published' or public.is_valueweave_admin());

drop policy if exists "events admin write" on public.events;
create policy "events admin write"
  on public.events for all
  using (public.is_valueweave_admin()) with check (public.is_valueweave_admin());

-- ─── TEAM WORKSPACE ─────────────────────────────────────────────────────────
-- The brief's Team Page. `connections` cannot serve this: it is opportunity-scoped,
-- strictly 1:1, and has no notion of a role or a persistent group.
--
-- Kept deliberately minimal. A workspace needs invitations, roles, permissions and
-- a lifecycle, and designing all of that here — with no feature to check it
-- against — would produce a schema that the eventual product has to fight.
create table if not exists public.teams (
  id            uuid        primary key default gen_random_uuid(),
  name          text        not null,
  slug          text        unique not null,
  description   text,
  -- A team usually forms around an opportunity that already exists. Nullable so a
  -- team can also exist on its own.
  opportunity_id uuid       references public.opportunities(id) on delete set null,
  district      text,
  sector        text,
  owner_id      uuid        not null references public.profiles(id) on delete cascade,
  status        text        not null default 'forming'
                  check (status in ('forming','active','paused','archived')),
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

create table if not exists public.team_members (
  team_id       uuid        not null references public.teams(id) on delete cascade,
  user_id       uuid        not null references public.profiles(id) on delete cascade,
  role          text        not null default 'member'
                  check (role in ('owner','admin','member','advisor')),
  -- What this person is expected to cover. Enables a real team-level skill gap
  -- rather than the connection-level approximation Step 1.5 had to use.
  covers_skills text[]      not null default '{}',
  status        text        not null default 'invited'
                  check (status in ('invited','active','left','removed')),
  joined_at     timestamptz,
  created_at    timestamptz not null default now(),
  primary key (team_id, user_id)
);

create index if not exists teams_owner_idx on public.teams (owner_id);
create index if not exists team_members_user_idx on public.team_members (user_id, status);

alter table public.teams enable row level security;
alter table public.team_members enable row level security;

-- Membership drives visibility. A team is readable by its members; the owner
-- manages it. Kept simple on purpose — a richer permission model belongs with the
-- feature, not ahead of it.
drop policy if exists "teams member read" on public.teams;
create policy "teams member read"
  on public.teams for select
  using (
    auth.uid() = owner_id
    or exists (
      select 1 from public.team_members m
      where m.team_id = teams.id and m.user_id = auth.uid() and m.status = 'active'
    )
  );

drop policy if exists "teams owner write" on public.teams;
create policy "teams owner write"
  on public.teams for all
  using (auth.uid() = owner_id) with check (auth.uid() = owner_id);

drop policy if exists "team members read" on public.team_members;
create policy "team members read"
  on public.team_members for select
  using (
    auth.uid() = user_id
    or exists (select 1 from public.teams t
               where t.id = team_members.team_id and t.owner_id = auth.uid())
  );

drop policy if exists "team members owner write" on public.team_members;
create policy "team members owner write"
  on public.team_members for all
  using (exists (select 1 from public.teams t
                 where t.id = team_members.team_id and t.owner_id = auth.uid()))
  with check (exists (select 1 from public.teams t
                      where t.id = team_members.team_id and t.owner_id = auth.uid()));

-- ─── NO SEED DATA ───────────────────────────────────────────────────────────
-- Intentionally none. Five tables created, zero rows inserted.
--
-- Until a real feature populates them:
--   user_intelligence `mentors` -> NO_DATA_SOURCE
--   user_intelligence `events`  -> NO_DATA_SOURCE
--   Assessment Profile          -> not rendered
--   Team skill gap              -> falls back to accepted connections
--
-- That is the intended behaviour, not a gap to paper over.

comment on table public.assessment_results is
  'Empty by design. No assessment feature exists yet; this fixes the shape.';
comment on table public.mentor_profiles is
  'Empty by design. Opt-in only: nobody becomes a mentor by inference.';
comment on table public.events is
  'Empty by design. No event source exists yet.';
comment on table public.teams is
  'Empty by design. connections is 1:1 and opportunity-scoped; this is the real group.';

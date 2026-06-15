-- ValueWeave — Admin Analytics & Control Center (Phase 3)
-- Run AFTER 003_seed_opportunities.sql
-- Adds: page_views, search_events, user_requests, user_feedback, founder_matches

-- ─── PAGE VIEWS ─────────────────────────────────────────────
create table if not exists public.page_views (
  id          uuid        primary key default gen_random_uuid(),
  page_type   text        not null check (page_type in ('research','idea','opportunity','district','collaborator','other')),
  page_slug   text        not null,
  page_title  text,
  district    text,
  sector      text,
  user_id     uuid        references public.profiles(id) on delete set null,
  session_id  text,
  referrer    text,
  created_at  timestamptz not null default now()
);

create index if not exists page_views_page_type_idx   on public.page_views(page_type);
create index if not exists page_views_page_slug_idx   on public.page_views(page_slug);
create index if not exists page_views_created_at_idx  on public.page_views(created_at);
create index if not exists page_views_district_idx    on public.page_views(district);
create index if not exists page_views_sector_idx      on public.page_views(sector);

alter table public.page_views enable row level security;

drop policy if exists "Admins read page_views" on public.page_views;
create policy "Admins read page_views" on public.page_views
  for select using (public.is_admin());

drop policy if exists "Anyone insert page_views" on public.page_views;
create policy "Anyone insert page_views" on public.page_views
  for insert with check (true);

-- ─── SEARCH EVENTS ───────────────────────────────────────────
create table if not exists public.search_events (
  id             uuid        primary key default gen_random_uuid(),
  query          text        not null,
  page           text,
  results_count  integer     default 0,
  clicked_result text,
  district       text,
  sector         text,
  user_id        uuid        references public.profiles(id) on delete set null,
  created_at     timestamptz not null default now()
);

create index if not exists search_events_query_idx      on public.search_events(lower(query));
create index if not exists search_events_created_at_idx on public.search_events(created_at);
create index if not exists search_events_page_idx       on public.search_events(page);

alter table public.search_events enable row level security;

drop policy if exists "Admins read search_events" on public.search_events;
create policy "Admins read search_events" on public.search_events
  for select using (public.is_admin());

drop policy if exists "Anyone insert search_events" on public.search_events;
create policy "Anyone insert search_events" on public.search_events
  for insert with check (true);

-- ─── USER REQUESTS ───────────────────────────────────────────
create table if not exists public.user_requests (
  id          uuid        primary key default gen_random_uuid(),
  type        text        not null default 'general'
                check (type in ('idea','opportunity','research','collaborator','district','general')),
  title       text        not null,
  description text,
  district    text,
  sector      text,
  user_id     uuid        references public.profiles(id) on delete set null,
  status      text        not null default 'pending'
                check (status in ('pending','fulfilled','dismissed')),
  created_at  timestamptz not null default now()
);

create index if not exists user_requests_type_idx       on public.user_requests(type);
create index if not exists user_requests_status_idx     on public.user_requests(status);
create index if not exists user_requests_created_at_idx on public.user_requests(created_at);
create index if not exists user_requests_sector_idx     on public.user_requests(sector);

alter table public.user_requests enable row level security;

drop policy if exists "Admins manage user_requests" on public.user_requests;
create policy "Admins manage user_requests" on public.user_requests
  for all using (public.is_admin());

drop policy if exists "Users insert own requests" on public.user_requests;
create policy "Users insert own requests" on public.user_requests
  for insert with check (auth.uid() = user_id or user_id is null);

drop policy if exists "Users read own requests" on public.user_requests;
create policy "Users read own requests" on public.user_requests
  for select using (auth.uid() = user_id);

-- ─── USER FEEDBACK ───────────────────────────────────────────
create table if not exists public.user_feedback (
  id          uuid        primary key default gen_random_uuid(),
  type        text        not null default 'general'
                check (type in ('general','bug','feature','content','other')),
  message     text        not null,
  page        text,
  rating      integer     check (rating between 1 and 5),
  user_id     uuid        references public.profiles(id) on delete set null,
  status      text        not null default 'unread'
                check (status in ('unread','read','actioned')),
  created_at  timestamptz not null default now()
);

create index if not exists user_feedback_created_at_idx on public.user_feedback(created_at);
create index if not exists user_feedback_status_idx     on public.user_feedback(status);
create index if not exists user_feedback_type_idx       on public.user_feedback(type);

alter table public.user_feedback enable row level security;

drop policy if exists "Admins manage user_feedback" on public.user_feedback;
create policy "Admins manage user_feedback" on public.user_feedback
  for all using (public.is_admin());

drop policy if exists "Anyone insert user_feedback" on public.user_feedback;
create policy "Anyone insert user_feedback" on public.user_feedback
  for insert with check (true);

-- ─── FOUNDER MATCHES ─────────────────────────────────────────
create table if not exists public.founder_matches (
  id          uuid        primary key default gen_random_uuid(),
  user1_id    uuid        not null references public.profiles(id) on delete cascade,
  user2_id    uuid        not null references public.profiles(id) on delete cascade,
  match_score integer     not null default 0 check (match_score between 0 and 100),
  match_type  text        not null default 'co-founder'
                check (match_type in ('co-founder','team','mentor')),
  sector      text,
  district    text,
  notes       text,
  status      text        not null default 'pending'
                check (status in ('pending','approved','ignored','contacted')),
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now(),
  unique (user1_id, user2_id)
);

create index if not exists founder_matches_status_idx on public.founder_matches(status);
create index if not exists founder_matches_score_idx  on public.founder_matches(match_score desc);

drop trigger if exists trg_founder_matches_updated on public.founder_matches;
create trigger trg_founder_matches_updated
  before update on public.founder_matches
  for each row execute function public.research_set_updated_at();

alter table public.founder_matches enable row level security;

drop policy if exists "Admins manage founder_matches" on public.founder_matches;
create policy "Admins manage founder_matches" on public.founder_matches
  for all using (public.is_admin());

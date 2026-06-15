-- ValueWeave — Visitor Analytics & Activity Intelligence (Phase 5)
-- Run AFTER 005_growth_intelligence.sql
-- Adds: visitor_sessions, platform_stats (view), activity_log

-- ─── VISITOR SESSIONS ────────────────────────────────────────
create table if not exists public.visitor_sessions (
  id           uuid        primary key default gen_random_uuid(),
  session_id   text        not null,
  visitor_id   text        not null,
  user_id      uuid        references public.profiles(id) on delete set null,
  page_path    text        not null,
  referrer     text,
  device_type  text        check (device_type in ('mobile','desktop','tablet','other')),
  browser      text,
  created_at   timestamptz not null default now()
);

create index if not exists visitor_sessions_session_idx    on public.visitor_sessions(session_id);
create index if not exists visitor_sessions_visitor_idx    on public.visitor_sessions(visitor_id);
create index if not exists visitor_sessions_created_at_idx on public.visitor_sessions(created_at desc);
create index if not exists visitor_sessions_device_idx     on public.visitor_sessions(device_type);
create index if not exists visitor_sessions_page_idx       on public.visitor_sessions(page_path);

alter table public.visitor_sessions enable row level security;

drop policy if exists "Admins read visitor_sessions" on public.visitor_sessions;
create policy "Admins read visitor_sessions" on public.visitor_sessions
  for select using (public.is_admin());

drop policy if exists "Anyone insert visitor_sessions" on public.visitor_sessions;
create policy "Anyone insert visitor_sessions" on public.visitor_sessions
  for insert with check (true);

-- ─── PLATFORM STATS VIEW ─────────────────────────────────────
-- Real-time platform stats for the homepage social proof section
create or replace view public.platform_stats as
select
  (select count(distinct visitor_id) from public.visitor_sessions) as total_unique_visitors,
  (select count(*)                   from public.visitor_sessions)  as total_sessions,
  (select count(*) from public.collaborator_profiles)               as total_collaborators,
  (select count(*) from public.opportunities where status = 'open') as total_opportunities,
  (select count(distinct district)
     from public.collaborator_profiles
     where district is not null)                                     as total_districts_covered,
  (select count(*) from public.research_articles where status = 'published') as total_articles;

-- Admins can query this view
drop policy if exists "Admins read platform_stats" on public.platform_stats;

-- ─── ACTIVITY LOG VIEW ───────────────────────────────────────
-- Unified feed of recent user actions for the admin activity dashboard
-- Pulls from page_views, search_events, user_requests, user_feedback,
-- visitor_sessions in a single UNION
create or replace view public.activity_log as

  select
    'page_view'                           as event_type,
    page_title                            as summary,
    page_slug                             as detail,
    district,
    sector,
    created_at
  from public.page_views
  where created_at > now() - interval '7 days'

union all

  select
    'search'                              as event_type,
    'Searched: ' || query                 as summary,
    page                                  as detail,
    district,
    sector,
    created_at
  from public.search_events
  where created_at > now() - interval '7 days'

union all

  select
    'content_request'                     as event_type,
    'Requested: ' || title                as summary,
    type                                  as detail,
    district,
    sector,
    created_at
  from public.user_requests
  where created_at > now() - interval '7 days'

union all

  select
    'feedback'                            as event_type,
    'Feedback: ' || left(message, 80)     as summary,
    type                                  as detail,
    null                                  as district,
    null                                  as sector,
    created_at
  from public.user_feedback
  where created_at > now() - interval '7 days'

union all

  select
    'visitor'                             as event_type,
    'Visited: ' || page_path              as summary,
    device_type                           as detail,
    null                                  as district,
    null                                  as sector,
    created_at
  from public.visitor_sessions
  where created_at > now() - interval '7 days';

-- Grant select on the views to authenticated and anon (RLS on underlying tables handles access)
grant select on public.platform_stats to authenticated, anon;

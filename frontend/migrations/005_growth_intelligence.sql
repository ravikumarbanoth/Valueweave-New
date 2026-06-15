-- ValueWeave — Growth Intelligence Engine (Phase 4)
-- Run AFTER 004_admin_analytics.sql
-- Adds: admin_notifications, opportunity_views, auto-notification triggers

-- ─── ADMIN NOTIFICATIONS ─────────────────────────────────────
create table if not exists public.admin_notifications (
  id          uuid        primary key default gen_random_uuid(),
  type        text        not null,
  title       text        not null,
  body        text,
  entity_type text,
  entity_id   uuid,
  status      text        not null default 'unread'
                check (status in ('unread','read','archived')),
  priority    text        not null default 'normal'
                check (priority in ('low','normal','high')),
  created_at  timestamptz not null default now()
);

create index if not exists admin_notif_status_idx     on public.admin_notifications(status);
create index if not exists admin_notif_created_at_idx on public.admin_notifications(created_at desc);
create index if not exists admin_notif_type_idx       on public.admin_notifications(type);
create index if not exists admin_notif_priority_idx   on public.admin_notifications(priority);

alter table public.admin_notifications enable row level security;

drop policy if exists "Admins manage admin_notifications" on public.admin_notifications;
create policy "Admins manage admin_notifications" on public.admin_notifications
  for all using (public.is_admin());

-- ─── OPPORTUNITY VIEWS ───────────────────────────────────────
-- Granular tracking per opportunity (supplements page_views)
create table if not exists public.opportunity_views (
  id              uuid        primary key default gen_random_uuid(),
  opportunity_id  uuid        not null references public.opportunities(id) on delete cascade,
  user_id         uuid        references public.profiles(id) on delete set null,
  session_id      text,
  district        text,
  sector          text,
  created_at      timestamptz not null default now()
);

create index if not exists opp_views_opp_id_idx    on public.opportunity_views(opportunity_id);
create index if not exists opp_views_created_at_idx on public.opportunity_views(created_at);
create index if not exists opp_views_district_idx  on public.opportunity_views(district);
create index if not exists opp_views_sector_idx    on public.opportunity_views(sector);

alter table public.opportunity_views enable row level security;

drop policy if exists "Admins read opportunity_views" on public.opportunity_views;
create policy "Admins read opportunity_views" on public.opportunity_views
  for select using (public.is_admin());

drop policy if exists "Anyone insert opportunity_views" on public.opportunity_views;
create policy "Anyone insert opportunity_views" on public.opportunity_views
  for insert with check (true);

-- ─── NOTIFICATION TRIGGER FUNCTION ───────────────────────────
create or replace function public.create_admin_notification()
returns trigger language plpgsql security definer as $$
begin
  -- New user registration
  if tg_table_name = 'profiles' and tg_op = 'INSERT' then
    insert into public.admin_notifications (type, title, body, entity_type, entity_id, priority)
    values (
      'new_user',
      'New User Registration',
      'User ' || coalesce(new.name, new.email, 'Unknown') || ' joined ValueWeave',
      'profile', new.id, 'normal'
    );

  -- New collaborator profile
  elsif tg_table_name = 'collaborator_profiles' and tg_op = 'INSERT' then
    insert into public.admin_notifications (type, title, body, entity_type, entity_id, priority)
    values (
      'new_collaborator',
      'New Collaborator Profile',
      'Archetype: ' || coalesce(new.archetype, 'Unknown') ||
        case when new.district is not null then ' · ' || new.district else '' end,
      'collaborator_profile', new.user_id, 'normal'
    );

  -- New opportunity interest
  elsif tg_table_name = 'opportunity_interests' and tg_op = 'INSERT' then
    insert into public.admin_notifications (type, title, body, entity_type, entity_id, priority)
    values (
      'new_interest',
      'New Opportunity Interest',
      coalesce(new.message, 'Someone expressed interest in an opportunity'),
      'opportunity_interest', new.id, 'high'
    );

  -- New user request
  elsif tg_table_name = 'user_requests' and tg_op = 'INSERT' then
    insert into public.admin_notifications (type, title, body, entity_type, entity_id, priority)
    values (
      'new_request',
      'New Content Request: ' || coalesce(new.title, 'Untitled'),
      coalesce(new.description, 'New request in ' || coalesce(new.sector, 'general')),
      'user_request', new.id, 'high'
    );

  -- New feedback
  elsif tg_table_name = 'user_feedback' and tg_op = 'INSERT' then
    insert into public.admin_notifications (type, title, body, entity_type, entity_id, priority)
    values (
      'new_feedback',
      'New ' || coalesce(new.type, 'general') || ' Feedback',
      left(coalesce(new.message, 'Feedback submitted'), 120),
      'user_feedback', new.id, 'normal'
    );

  -- New founder match
  elsif tg_table_name = 'founder_matches' and tg_op = 'INSERT' then
    insert into public.admin_notifications (type, title, body, entity_type, entity_id, priority)
    values (
      'new_match',
      'New Founder Match (Score: ' || new.match_score || ')',
      'Type: ' || new.match_type ||
        case when new.sector is not null then ' · ' || new.sector else '' end,
      'founder_match', new.id,
      case when new.match_score >= 80 then 'high' when new.match_score >= 60 then 'normal' else 'low' end
    );

  -- Article published
  elsif tg_table_name = 'research_articles' and tg_op = 'UPDATE'
       and new.status = 'published' and old.status != 'published' then
    insert into public.admin_notifications (type, title, body, entity_type, entity_id, priority)
    values (
      'article_published',
      'Article Published: ' || coalesce(new.title, 'Untitled'),
      coalesce(new.excerpt, 'New article published on ValueWeave Research Hub'),
      'research_article', new.id, 'low'
    );
  end if;

  return new;
end;
$$;

-- ─── ATTACH TRIGGERS ─────────────────────────────────────────
drop trigger if exists trg_notify_new_user on public.profiles;
create trigger trg_notify_new_user
  after insert on public.profiles
  for each row execute function public.create_admin_notification();

drop trigger if exists trg_notify_new_collaborator on public.collaborator_profiles;
create trigger trg_notify_new_collaborator
  after insert on public.collaborator_profiles
  for each row execute function public.create_admin_notification();

drop trigger if exists trg_notify_new_interest on public.opportunity_interests;
create trigger trg_notify_new_interest
  after insert on public.opportunity_interests
  for each row execute function public.create_admin_notification();

drop trigger if exists trg_notify_new_request on public.user_requests;
create trigger trg_notify_new_request
  after insert on public.user_requests
  for each row execute function public.create_admin_notification();

drop trigger if exists trg_notify_new_feedback on public.user_feedback;
create trigger trg_notify_new_feedback
  after insert on public.user_feedback
  for each row execute function public.create_admin_notification();

drop trigger if exists trg_notify_new_match on public.founder_matches;
create trigger trg_notify_new_match
  after insert on public.founder_matches
  for each row execute function public.create_admin_notification();

drop trigger if exists trg_notify_article_published on public.research_articles;
create trigger trg_notify_article_published
  after update on public.research_articles
  for each row execute function public.create_admin_notification();

-- ValueWeave — Engagement & Retention Engine (Phase 6)
-- Run AFTER 006_visitor_analytics.sql
-- Adds: announcements, notifications, subscriptions, weekly_digests, questions, answers

-- ─── ANNOUNCEMENTS ───────────────────────────────────────────
create table if not exists public.announcements (
  id          uuid        primary key default gen_random_uuid(),
  title       text        not null,
  message     text        not null,
  link        text,
  link_label  text,
  is_active   boolean     not null default false,
  priority    text        not null default 'normal'
                check (priority in ('low','normal','high')),
  created_at  timestamptz not null default now(),
  expires_at  timestamptz
);

create index if not exists announcements_is_active_idx  on public.announcements(is_active);
create index if not exists announcements_priority_idx   on public.announcements(priority);
create index if not exists announcements_expires_at_idx on public.announcements(expires_at);

alter table public.announcements enable row level security;

drop policy if exists "Admins manage announcements" on public.announcements;
create policy "Admins manage announcements" on public.announcements
  for all using (public.is_admin());

drop policy if exists "Anyone read active announcements" on public.announcements;
create policy "Anyone read active announcements" on public.announcements
  for select using (
    is_active = true
    and (expires_at is null or expires_at > now())
  );

-- ─── USER NOTIFICATIONS ──────────────────────────────────────
create table if not exists public.notifications (
  id          uuid        primary key default gen_random_uuid(),
  user_id     uuid        not null references public.profiles(id) on delete cascade,
  title       text        not null,
  message     text,
  type        text        not null default 'general'
                check (type in ('opportunity','collaborator','research','district','announcement','general')),
  link        text,
  is_read     boolean     not null default false,
  created_at  timestamptz not null default now()
);

create index if not exists notifications_user_id_idx    on public.notifications(user_id);
create index if not exists notifications_is_read_idx    on public.notifications(is_read);
create index if not exists notifications_created_at_idx on public.notifications(created_at desc);
create index if not exists notifications_type_idx       on public.notifications(type);

alter table public.notifications enable row level security;

drop policy if exists "Admins manage notifications" on public.notifications;
create policy "Admins manage notifications" on public.notifications
  for all using (public.is_admin());

drop policy if exists "Users read own notifications" on public.notifications;
create policy "Users read own notifications" on public.notifications
  for select using (auth.uid() = user_id);

drop policy if exists "Users update own notifications" on public.notifications;
create policy "Users update own notifications" on public.notifications
  for update using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

-- ─── SUBSCRIPTIONS ───────────────────────────────────────────
create table if not exists public.subscriptions (
  id          uuid        primary key default gen_random_uuid(),
  user_id     uuid        not null references public.profiles(id) on delete cascade,
  type        text        not null
                check (type in ('district','sector','research_category','opportunity_category')),
  value       text        not null,
  created_at  timestamptz not null default now(),
  unique (user_id, type, value)
);

create index if not exists subscriptions_user_id_idx on public.subscriptions(user_id);
create index if not exists subscriptions_type_idx    on public.subscriptions(type);
create index if not exists subscriptions_value_idx   on public.subscriptions(value);

alter table public.subscriptions enable row level security;

drop policy if exists "Admins read subscriptions" on public.subscriptions;
create policy "Admins read subscriptions" on public.subscriptions
  for select using (public.is_admin());

drop policy if exists "Users manage own subscriptions" on public.subscriptions;
create policy "Users manage own subscriptions" on public.subscriptions
  for all using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

-- ─── WEEKLY DIGESTS ──────────────────────────────────────────
create table if not exists public.weekly_digests (
  id            uuid        primary key default gen_random_uuid(),
  week_start    date        not null,
  week_end      date        not null,
  district      text,
  sector        text,
  new_opps      integer     not null default 0,
  new_articles  integer     not null default 0,
  new_collabs   integer     not null default 0,
  new_searches  integer     not null default 0,
  digest_data   jsonb,
  created_at    timestamptz not null default now(),
  unique (week_start, district, sector)
);

create index if not exists weekly_digests_week_idx    on public.weekly_digests(week_start desc);
create index if not exists weekly_digests_district_idx on public.weekly_digests(district);
create index if not exists weekly_digests_sector_idx  on public.weekly_digests(sector);

alter table public.weekly_digests enable row level security;

drop policy if exists "Admins manage weekly_digests" on public.weekly_digests;
create policy "Admins manage weekly_digests" on public.weekly_digests
  for all using (public.is_admin());

-- ─── QUESTIONS ───────────────────────────────────────────────
create table if not exists public.questions (
  id          uuid        primary key default gen_random_uuid(),
  user_id     uuid        references public.profiles(id) on delete set null,
  title       text        not null,
  body        text,
  district    text,
  sector      text,
  upvotes     integer     not null default 0,
  answer_count integer    not null default 0,
  status      text        not null default 'open'
                check (status in ('open','closed','removed')),
  created_at  timestamptz not null default now()
);

create index if not exists questions_status_idx     on public.questions(status);
create index if not exists questions_created_at_idx on public.questions(created_at desc);
create index if not exists questions_district_idx   on public.questions(district);
create index if not exists questions_sector_idx     on public.questions(sector);
create index if not exists questions_upvotes_idx    on public.questions(upvotes desc);

alter table public.questions enable row level security;

drop policy if exists "Anyone read open questions" on public.questions;
create policy "Anyone read open questions" on public.questions
  for select using (status = 'open');

drop policy if exists "Authenticated users insert questions" on public.questions;
create policy "Authenticated users insert questions" on public.questions
  for insert with check (auth.uid() = user_id);

drop policy if exists "Admins manage questions" on public.questions;
create policy "Admins manage questions" on public.questions
  for all using (public.is_admin());

-- ─── ANSWERS ─────────────────────────────────────────────────
create table if not exists public.answers (
  id          uuid        primary key default gen_random_uuid(),
  question_id uuid        not null references public.questions(id) on delete cascade,
  user_id     uuid        references public.profiles(id) on delete set null,
  body        text        not null,
  upvotes     integer     not null default 0,
  is_accepted boolean     not null default false,
  created_at  timestamptz not null default now()
);

create index if not exists answers_question_id_idx  on public.answers(question_id);
create index if not exists answers_created_at_idx   on public.answers(created_at);
create index if not exists answers_upvotes_idx      on public.answers(upvotes desc);

alter table public.answers enable row level security;

drop policy if exists "Anyone read answers" on public.answers;
create policy "Anyone read answers" on public.answers
  for select using (true);

drop policy if exists "Authenticated users insert answers" on public.answers;
create policy "Authenticated users insert answers" on public.answers
  for insert with check (auth.uid() = user_id);

drop policy if exists "Admins manage answers" on public.answers;
create policy "Admins manage answers" on public.answers
  for all using (public.is_admin());

-- Update answer_count when an answer is inserted/deleted
create or replace function public.sync_answer_count()
returns trigger language plpgsql security definer as $$
begin
  if tg_op = 'INSERT' then
    update public.questions set answer_count = answer_count + 1 where id = new.question_id;
    return new;
  elsif tg_op = 'DELETE' then
    update public.questions set answer_count = greatest(0, answer_count - 1) where id = old.question_id;
    return old;
  end if;
  return null;
end;
$$;

drop trigger if exists trg_sync_answer_count on public.answers;
create trigger trg_sync_answer_count
  after insert or delete on public.answers
  for each row execute function public.sync_answer_count();

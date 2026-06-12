-- ValueWeave — Research Publisher schema
-- Run once in the Supabase SQL Editor (style matches supabase_schema.sql).
--
-- After running, grant yourself admin access:
--   update public.profiles set is_admin = true where email = 'you@example.com';

-- ─── ADMIN FLAG ON EXISTING PROFILES ────────────────────────
alter table public.profiles
  add column if not exists is_admin boolean not null default false;

-- security definer so RLS policies can check admin status without
-- recursive policy evaluation on profiles
create or replace function public.is_admin()
returns boolean
language sql stable security definer set search_path = public as $$
  select coalesce(
    (select is_admin from public.profiles where id = auth.uid()),
    false
  )
$$;

-- ─── RESEARCH ARTICLES ──────────────────────────────────────
create table if not exists public.research_articles (
  id              uuid primary key default gen_random_uuid(),
  title           text not null,
  slug            text unique not null,
  excerpt         text,
  content         text,
  category        text,
  district        text,
  author          text default 'ValueWeave Research Team',
  cover_image     text,
  status          text not null default 'draft' check (status in ('draft','published')),
  published_at    timestamptz,
  -- AI-ready optional SEO fields (architecture prepared, generation not implemented)
  seo_title       text,
  seo_description text,
  keywords        text[] default '{}',
  faq_json        jsonb default '[]'::jsonb,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);

create index if not exists research_articles_status_idx
  on public.research_articles(status);
create index if not exists research_articles_category_idx
  on public.research_articles(category);
create index if not exists research_articles_published_at_idx
  on public.research_articles(published_at desc);
-- slug already indexed via unique constraint

-- ─── UPDATED_AT TRIGGER ─────────────────────────────────────
create or replace function public.research_set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end; $$;

drop trigger if exists trg_research_articles_updated on public.research_articles;
create trigger trg_research_articles_updated
  before update on public.research_articles
  for each row execute function public.research_set_updated_at();

-- ─── ROW LEVEL SECURITY ─────────────────────────────────────
alter table public.research_articles enable row level security;

-- Public (incl. anonymous) can read only published articles; admins read all
drop policy if exists "Public read published research" on public.research_articles;
create policy "Public read published research"
  on public.research_articles for select
  using (status = 'published' or public.is_admin());

drop policy if exists "Admins insert research" on public.research_articles;
create policy "Admins insert research"
  on public.research_articles for insert
  with check (public.is_admin());

drop policy if exists "Admins update research" on public.research_articles;
create policy "Admins update research"
  on public.research_articles for update
  using (public.is_admin())
  with check (public.is_admin());

drop policy if exists "Admins delete research" on public.research_articles;
create policy "Admins delete research"
  on public.research_articles for delete
  using (public.is_admin());

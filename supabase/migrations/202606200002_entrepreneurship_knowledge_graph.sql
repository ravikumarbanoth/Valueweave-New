-- District-focused entrepreneurship knowledge graph foundation.
-- No seed data: content is added gradually through the admin dashboard.

create extension if not exists pgcrypto;

create table if not exists public.kg_district_profiles (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  name text not null,
  state text not null,
  population bigint,
  major_industries text[] not null default '{}',
  key_crops text[] not null default '{}',
  economic_activities text[] not null default '{}',
  skill_gaps text[] not null default '{}',
  opportunity_gaps text[] not null default '{}',
  msme_presence text,
  logistics_score integer,
  education_score integer,
  healthcare_score integer,
  industrial_score integer,
  tourism_score integer,
  summary text,
  ai_summary text,
  rich_text text,
  meta_title text,
  meta_description text,
  faq_json jsonb not null default '[]'::jsonb,
  structured_data jsonb not null default '{}'::jsonb,
  status text not null default 'draft' check (status in ('draft','published')),
  published_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.kg_skills (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  name text not null,
  category text,
  description text,
  required_training text,
  tools_needed text[] not null default '{}',
  income_range text,
  future_demand text,
  difficulty_level text,
  investment_needed text,
  summary text,
  ai_summary text,
  rich_text text,
  meta_title text,
  meta_description text,
  faq_json jsonb not null default '[]'::jsonb,
  structured_data jsonb not null default '{}'::jsonb,
  status text not null default 'draft' check (status in ('draft','published')),
  published_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.kg_resources (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  name text not null,
  type text,
  description text,
  provider_name text,
  location text,
  contact_url text,
  cost_range text,
  summary text,
  ai_summary text,
  rich_text text,
  meta_title text,
  meta_description text,
  faq_json jsonb not null default '[]'::jsonb,
  structured_data jsonb not null default '{}'::jsonb,
  status text not null default 'draft' check (status in ('draft','published')),
  published_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.kg_schemes (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  name text not null,
  department text,
  eligibility text,
  subsidy text,
  loan_amount text,
  target_group text,
  application_link text,
  summary text,
  ai_summary text,
  rich_text text,
  meta_title text,
  meta_description text,
  faq_json jsonb not null default '[]'::jsonb,
  structured_data jsonb not null default '{}'::jsonb,
  status text not null default 'draft' check (status in ('draft','published')),
  published_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.kg_roadmaps (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  title text not null,
  description text,
  estimated_cost text,
  summary text,
  ai_summary text,
  rich_text text,
  meta_title text,
  meta_description text,
  faq_json jsonb not null default '[]'::jsonb,
  structured_data jsonb not null default '{}'::jsonb,
  status text not null default 'draft' check (status in ('draft','published')),
  published_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.kg_roadmap_steps (
  id uuid primary key default gen_random_uuid(),
  roadmap_id uuid not null references public.kg_roadmaps(id) on delete cascade,
  step_number integer not null,
  title text not null,
  description text,
  resources_needed text[] not null default '{}',
  skills_needed text[] not null default '{}',
  estimated_cost text,
  created_at timestamptz not null default now(),
  unique(roadmap_id, step_number)
);

create table if not exists public.kg_industry_sectors (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  name text not null,
  description text,
  status text not null default 'draft' check (status in ('draft','published')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.kg_collaborator_types (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  name text not null,
  description text,
  status text not null default 'draft' check (status in ('draft','published')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.kg_relationships (
  id uuid primary key default gen_random_uuid(),
  source_type text not null,
  source_id uuid,
  source_external_id text,
  target_type text not null,
  target_id uuid,
  target_external_id text,
  relationship_type text not null,
  weight numeric(5,2) not null default 1,
  notes text,
  created_at timestamptz not null default now(),
  unique(source_type, source_id, source_external_id, target_type, target_id, target_external_id, relationship_type)
);

create index if not exists kg_relationships_source_idx on public.kg_relationships(source_type, source_id, source_external_id);
create index if not exists kg_relationships_target_idx on public.kg_relationships(target_type, target_id, target_external_id);

create or replace function public.kg_touch_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

do $$
declare table_name text;
begin
  foreach table_name in array array['kg_district_profiles','kg_skills','kg_resources','kg_schemes','kg_roadmaps','kg_industry_sectors','kg_collaborator_types'] loop
    execute format('drop trigger if exists trg_%s_updated_at on public.%I', table_name, table_name);
    execute format('create trigger trg_%s_updated_at before update on public.%I for each row execute function public.kg_touch_updated_at()', table_name, table_name);
  end loop;
end $$;

alter table public.kg_district_profiles enable row level security;
alter table public.kg_skills enable row level security;
alter table public.kg_resources enable row level security;
alter table public.kg_schemes enable row level security;
alter table public.kg_roadmaps enable row level security;
alter table public.kg_roadmap_steps enable row level security;
alter table public.kg_industry_sectors enable row level security;
alter table public.kg_collaborator_types enable row level security;
alter table public.kg_relationships enable row level security;

create or replace function public.is_valueweave_admin()
returns boolean language sql stable as $$
  select exists (
    select 1 from public.profiles p
    where p.id = auth.uid() and coalesce(p.is_admin, false) = true
  );
$$;

do $$
declare table_name text;
begin
  foreach table_name in array array['kg_district_profiles','kg_skills','kg_resources','kg_schemes','kg_roadmaps','kg_industry_sectors','kg_collaborator_types'] loop
    execute format('drop policy if exists "%s public published read" on public.%I', table_name, table_name);
    execute format('create policy "%s public published read" on public.%I for select using (status = ''published'' or public.is_valueweave_admin())', table_name, table_name);
    execute format('drop policy if exists "%s admin write" on public.%I', table_name, table_name);
    execute format('create policy "%s admin write" on public.%I for all using (public.is_valueweave_admin()) with check (public.is_valueweave_admin())', table_name, table_name);
  end loop;
end $$;

drop policy if exists "kg roadmap steps public read" on public.kg_roadmap_steps;
create policy "kg roadmap steps public read" on public.kg_roadmap_steps for select using (true);
drop policy if exists "kg roadmap steps admin write" on public.kg_roadmap_steps;
create policy "kg roadmap steps admin write" on public.kg_roadmap_steps for all using (public.is_valueweave_admin()) with check (public.is_valueweave_admin());

drop policy if exists "kg relationships public read" on public.kg_relationships;
create policy "kg relationships public read" on public.kg_relationships for select using (true);
drop policy if exists "kg relationships admin write" on public.kg_relationships;
create policy "kg relationships admin write" on public.kg_relationships for all using (public.is_valueweave_admin()) with check (public.is_valueweave_admin());

insert into public.platform_settings (key, value, type, category) values
  ('modules.skills.enabled', 'true'::jsonb, 'boolean', 'Platform'),
  ('modules.schemes.enabled', 'true'::jsonb, 'boolean', 'Platform'),
  ('modules.resources.enabled', 'true'::jsonb, 'boolean', 'Platform'),
  ('modules.roadmaps.enabled', 'true'::jsonb, 'boolean', 'Platform'),
  ('modules.opportunity_index.enabled', 'true'::jsonb, 'boolean', 'Platform'),
  ('homepage.sections.skills.enabled', 'true'::jsonb, 'boolean', 'Homepage'),
  ('homepage.sections.schemes.enabled', 'true'::jsonb, 'boolean', 'Homepage'),
  ('homepage.sections.resources.enabled', 'true'::jsonb, 'boolean', 'Homepage'),
  ('navigation.skills.enabled', 'true'::jsonb, 'boolean', 'Navigation'),
  ('navigation.schemes.enabled', 'true'::jsonb, 'boolean', 'Navigation'),
  ('navigation.resources.enabled', 'true'::jsonb, 'boolean', 'Navigation'),
  ('navigation.roadmaps.enabled', 'true'::jsonb, 'boolean', 'Navigation')
on conflict (key) do nothing;

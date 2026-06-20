-- GEO, research video, and platform configuration support.

alter table if exists public.research_articles
  add column if not exists youtube_url text,
  add column if not exists video_title text,
  add column if not exists video_description text,
  add column if not exists video_view_count integer not null default 0;

create table if not exists public.platform_settings (
  key text primary key,
  value jsonb not null default 'null'::jsonb,
  type text not null default 'text',
  category text not null default 'Platform',
  updated_at timestamptz not null default now()
);

create index if not exists platform_settings_category_idx on public.platform_settings(category);

create or replace function public.set_platform_settings_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists trg_platform_settings_updated_at on public.platform_settings;
create trigger trg_platform_settings_updated_at
before update on public.platform_settings
for each row execute function public.set_platform_settings_updated_at();

alter table public.platform_settings enable row level security;

drop policy if exists "platform settings public read" on public.platform_settings;
create policy "platform settings public read"
  on public.platform_settings for select
  using (true);

drop policy if exists "platform settings admin write" on public.platform_settings;
create policy "platform settings admin write"
  on public.platform_settings for all
  using (
    exists (
      select 1 from public.profiles p
      where p.id = auth.uid() and coalesce(p.is_admin, false) = true
    )
  )
  with check (
    exists (
      select 1 from public.profiles p
      where p.id = auth.uid() and coalesce(p.is_admin, false) = true
    )
  );

insert into public.platform_settings (key, value, type, category) values
  ('site.title', '"ValueWeave"'::jsonb, 'text', 'Branding'),
  ('site.description', '"India''s collaboration and opportunity discovery platform for builders, local businesses, and district-first entrepreneurship."'::jsonb, 'textarea', 'SEO'),
  ('site.tagline', '"Where ambition finds its team."'::jsonb, 'text', 'Branding'),
  ('homepage.hero.heading', '"Where Ambition Finds Its Team."'::jsonb, 'text', 'Homepage'),
  ('homepage.hero.subheading', '"ValueWeave connects India''s youth, students, and skilled builders to discover collaborators, form startup teams, and create real economic opportunities — from tier-2 towns to global ambitions."'::jsonb, 'textarea', 'Homepage'),
  ('homepage.cta.primary.label', '"Discover Yourself"'::jsonb, 'text', 'Buttons'),
  ('homepage.cta.secondary.label', '"Explore Ideas"'::jsonb, 'text', 'Buttons'),
  ('homepage.cta.tertiary.label', '"Find Collaborators"'::jsonb, 'text', 'Buttons'),
  ('homepage.video.url', '"https://youtu.be/hRhhYQLPJ7Q?si=ZPAl8q878ZuNFZkY"'::jsonb, 'url', 'Homepage'),
  ('footer.text', '"Where ambition finds its team. Find what to build and who to build it with — from your district."'::jsonb, 'textarea', 'Footer'),
  ('footer.contact_email', '"valueweave.team@gmail.com"'::jsonb, 'email', 'Footer'),
  ('contact.email', '"valueweave.team@gmail.com"'::jsonb, 'email', 'Platform'),
  ('announcement.enabled', 'false'::jsonb, 'boolean', 'Platform'),
  ('announcement.text', '""'::jsonb, 'textarea', 'Platform'),
  ('maintenance.enabled', 'false'::jsonb, 'boolean', 'Platform'),
  ('maintenance.text', '"ValueWeave is undergoing maintenance. Some features may be temporarily unavailable."'::jsonb, 'textarea', 'Platform'),
  ('theme.primary_color', '"#f59e0b"'::jsonb, 'color', 'Branding'),
  ('theme.secondary_color', '"#14b8a6"'::jsonb, 'color', 'Branding'),
  ('theme.accent_color', '"#facc15"'::jsonb, 'color', 'Branding'),
  ('social.youtube', '""'::jsonb, 'url', 'Footer'),
  ('social.instagram', '""'::jsonb, 'url', 'Footer'),
  ('social.x', '""'::jsonb, 'url', 'Footer'),
  ('navigation.research.enabled', 'true'::jsonb, 'boolean', 'Navigation'),
  ('navigation.districts.enabled', 'true'::jsonb, 'boolean', 'Navigation'),
  ('navigation.radar.enabled', 'true'::jsonb, 'boolean', 'Navigation'),
  ('navigation.collaborators.enabled', 'true'::jsonb, 'boolean', 'Navigation'),
  ('navigation.questions.enabled', 'true'::jsonb, 'boolean', 'Navigation'),
  ('navigation.discover.enabled', 'true'::jsonb, 'boolean', 'Navigation')
on conflict (key) do nothing;

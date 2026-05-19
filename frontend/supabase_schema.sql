-- ValueWeave Supabase Schema
-- Run this once in Supabase SQL Editor.

-- ─── PROFILES ───────────────────────────────────────────────
create table if not exists public.profiles (
  id uuid primary key references auth.users on delete cascade,
  email text,
  name text,
  picture text,
  city text,
  bio text,
  skills text[] default '{}',
  interests text[] default '{}',
  looking_for text,
  profile_complete boolean default false,
  created_at timestamptz default now()
);

alter table public.profiles enable row level security;

drop policy if exists "Profiles are viewable by everyone" on public.profiles;
create policy "Profiles are viewable by everyone"
  on public.profiles for select using (true);

drop policy if exists "Users can insert own profile" on public.profiles;
create policy "Users can insert own profile"
  on public.profiles for insert with check (auth.uid() = id);

drop policy if exists "Users can update own profile" on public.profiles;
create policy "Users can update own profile"
  on public.profiles for update using (auth.uid() = id);

-- Auto-create profile on signup
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, email, name, picture)
  values (
    new.id,
    new.email,
    coalesce(new.raw_user_meta_data->>'full_name', new.raw_user_meta_data->>'name', split_part(new.email, '@', 1)),
    new.raw_user_meta_data->>'avatar_url'
  )
  on conflict (id) do nothing;
  return new;
end; $$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- ─── OPPORTUNITIES ──────────────────────────────────────────
create table if not exists public.opportunities (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references public.profiles(id) on delete cascade,
  title text not null,
  description text not null,
  category text not null,
  skills_needed text[] default '{}',
  location text not null,
  collaboration_type text not null,
  commitment text not null,
  created_at timestamptz default now()
);

create index if not exists opportunities_owner_idx on public.opportunities(owner_id);
create index if not exists opportunities_category_idx on public.opportunities(category);
create index if not exists opportunities_created_idx on public.opportunities(created_at desc);

alter table public.opportunities enable row level security;

drop policy if exists "Opportunities are viewable by everyone" on public.opportunities;
create policy "Opportunities are viewable by everyone"
  on public.opportunities for select using (true);

drop policy if exists "Authenticated users can insert opportunities" on public.opportunities;
create policy "Authenticated users can insert opportunities"
  on public.opportunities for insert
  with check (auth.uid() = owner_id);

drop policy if exists "Owners can update own opportunities" on public.opportunities;
create policy "Owners can update own opportunities"
  on public.opportunities for update using (auth.uid() = owner_id);

drop policy if exists "Owners can delete own opportunities" on public.opportunities;
create policy "Owners can delete own opportunities"
  on public.opportunities for delete using (auth.uid() = owner_id);

-- ─── CONNECTIONS ────────────────────────────────────────────
create table if not exists public.connections (
  id uuid primary key default gen_random_uuid(),
  opportunity_id uuid not null references public.opportunities(id) on delete cascade,
  from_user_id uuid not null references public.profiles(id) on delete cascade,
  to_user_id uuid not null references public.profiles(id) on delete cascade,
  message text not null,
  status text not null default 'pending' check (status in ('pending','accepted','rejected')),
  created_at timestamptz default now(),
  unique (opportunity_id, from_user_id)
);

create index if not exists connections_to_idx on public.connections(to_user_id);
create index if not exists connections_from_idx on public.connections(from_user_id);

alter table public.connections enable row level security;

drop policy if exists "Users can see their connections" on public.connections;
create policy "Users can see their connections"
  on public.connections for select
  using (auth.uid() = from_user_id or auth.uid() = to_user_id);

drop policy if exists "Users can create outgoing connections" on public.connections;
create policy "Users can create outgoing connections"
  on public.connections for insert
  with check (auth.uid() = from_user_id);

drop policy if exists "Recipients can update status" on public.connections;
create policy "Recipients can update status"
  on public.connections for update
  using (auth.uid() = to_user_id);

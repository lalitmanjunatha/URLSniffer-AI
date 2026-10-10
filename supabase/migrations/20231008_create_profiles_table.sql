-- Create profiles table
create table if not exists public.profiles (
  id uuid references auth.users on delete cascade not null primary key,
  email text not null,
  full_name text,
  avatar_url text,
  role text not null default 'user' check (role in ('user', 'admin')),
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable Row Level Security
alter table public.profiles enable row level security;

-- Create policies
create policy "Profiles are viewable by own user"
  on public.profiles for select
  using (auth.uid() = id);

create policy "Profiles are updatable by own user"
  on public.profiles for update
  using (auth.uid() = id)
  with check (auth.uid() = id and role = 'user'); -- Only allow updating own profile, but not role

create policy "Profiles are insertable by own user"
  on public.profiles for insert
  with check (auth.uid() = id);

-- Create trigger to update updated_at column
create trigger update_profiles_updated_at
before update on public.profiles
for each row
execute procedure moddatetime (updated_at);

-- Create a function to create a profile on new user signup
-- This is optional; you can also handle it in the frontend or via a database webhook.
-- For simplicity, we'll create a trigger function that inserts a profile when a new user signs up.
-- However, note that the auth.users table does not have triggers.
-- Instead, we can rely on the frontend to create the profile after signup, or use a Supabase Function.

-- Alternative: create a database function that can be called via an auth webhook.
-- Since we are not setting up webhooks here, we will note that the frontend should create the profile.

-- For now, we'll just create the table and policies.
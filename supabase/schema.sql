-- Supabase project: japan-trip-2026 (ref mepfsxfbpfnnudvlijgs, ap-southeast-1)
-- Applied as migrations "trip_schema" and "move_member_check_private". Kept here for reference.

-- Who may use the trip app (matched on the signed-in, email-confirmed address)
create table public.trip_members (
  email text primary key,
  added_at timestamptz not null default now()
);
alter table public.trip_members enable row level security;

create schema if not exists private;
revoke all on schema private from public, anon;
grant usage on schema private to authenticated;

create or replace function private.is_trip_member()
returns boolean language sql stable security definer set search_path = '' as $$
  select exists (
    select 1 from public.trip_members m
    where lower(m.email) = lower(coalesce(auth.jwt() ->> 'email', ''))
  );
$$;
revoke execute on function private.is_trip_member() from public, anon;
grant execute on function private.is_trip_member() to authenticated;

create policy "members can see the member list" on public.trip_members
  for select to authenticated using (private.is_trip_member());

-- App documents: base/itinerary, days/<date>, settings/main, pretrip/main
create table public.trip_docs (
  path text primary key check (path ~ '^[a-z]+/[A-Za-z0-9_.:-]+$'),
  data jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now(),
  updated_by uuid default auth.uid()
);
alter table public.trip_docs enable row level security;
create policy "members read docs"   on public.trip_docs for select to authenticated using (private.is_trip_member());
create policy "members insert docs" on public.trip_docs for insert to authenticated with check (private.is_trip_member());
create policy "members update docs" on public.trip_docs for update to authenticated using (private.is_trip_member()) with check (private.is_trip_member());
create policy "members delete docs" on public.trip_docs for delete to authenticated using (private.is_trip_member());

create or replace function public.trip_docs_touch()
returns trigger language plpgsql set search_path = '' as $$
begin new.updated_at := now(); new.updated_by := auth.uid(); return new; end; $$;
create trigger trip_docs_touch before insert or update on public.trip_docs
  for each row execute function public.trip_docs_touch();

alter publication supabase_realtime add table public.trip_docs;

-- Private bucket for trip photos, videos and note pictures (20 MB per file)
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('trip-media', 'trip-media', false, 20971520, array['image/*','video/*']);
create policy "members read media"   on storage.objects for select to authenticated using (bucket_id = 'trip-media' and private.is_trip_member());
create policy "members upload media" on storage.objects for insert to authenticated with check (bucket_id = 'trip-media' and private.is_trip_member());
create policy "members update media" on storage.objects for update to authenticated using (bucket_id = 'trip-media' and private.is_trip_member());
create policy "members delete media" on storage.objects for delete to authenticated using (bucket_id = 'trip-media' and private.is_trip_member());

-- Add someone:    insert into public.trip_members (email) values ('name@example.com');
-- Remove someone: delete from public.trip_members where email = 'name@example.com';

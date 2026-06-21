-- GCC-SWSS schema: accounts, saved projects/boreholes/scenarios, results, leads.
-- Row-Level Security ensures each user sees only their own data. The FastAPI
-- service uses the service-role key (bypasses RLS) and scopes by user id from
-- the validated JWT; the browser uses the anon key and is constrained by RLS.

create extension if not exists "pgcrypto";

-- ----------------------------------------------------------------------------
-- profiles: 1:1 with auth.users
-- ----------------------------------------------------------------------------
create table if not exists public.profiles (
  id          uuid primary key references auth.users(id) on delete cascade,
  full_name   text,
  organisation text,
  created_at  timestamptz not null default now()
);

-- ----------------------------------------------------------------------------
-- projects -> boreholes -> scenarios -> sim_results
-- ----------------------------------------------------------------------------
create table if not exists public.projects (
  id          uuid primary key default gen_random_uuid(),
  owner       uuid not null references auth.users(id) on delete cascade,
  name        text not null,
  climate_station text not null default 'dubai_coastal',
  created_at  timestamptz not null default now()
);

create table if not exists public.boreholes (
  id          uuid primary key default gen_random_uuid(),
  project_id  uuid not null references public.projects(id) on delete cascade,
  owner       uuid not null references auth.users(id) on delete cascade,
  label       text not null,
  sand        numeric not null,
  silt        numeric not null,
  clay        numeric not null,
  bulk_density numeric not null,
  organic_matter numeric default 0.5,
  ec          numeric,
  sar         numeric,
  root_zone_depth_m numeric not null default 0.5,
  created_at  timestamptz not null default now()
);

create table if not exists public.scenarios (
  id          uuid primary key default gen_random_uuid(),
  project_id  uuid not null references public.projects(id) on delete cascade,
  owner       uuid not null references auth.users(id) on delete cascade,
  name        text not null,
  -- full ProjectInput payload sent to /simulate (source of truth, reproducible)
  payload     jsonb not null,
  created_at  timestamptz not null default now()
);

create table if not exists public.sim_results (
  id          uuid primary key default gen_random_uuid(),
  scenario_id uuid not null references public.scenarios(id) on delete cascade,
  owner       uuid not null references auth.users(id) on delete cascade,
  -- archived SimResult JSON (forensic requirement: reproducible from this record)
  result      jsonb not null,
  engine_version text,
  created_at  timestamptz not null default now()
);

-- ----------------------------------------------------------------------------
-- leads: durable marketing capture (no auth; insert-only from the public site)
-- ----------------------------------------------------------------------------
create table if not exists public.leads (
  id          uuid primary key default gen_random_uuid(),
  name        text not null,
  email       text not null,
  organisation text,
  message     text,
  source      text default 'website',
  created_at  timestamptz not null default now()
);

-- ----------------------------------------------------------------------------
-- Row-Level Security
-- ----------------------------------------------------------------------------
alter table public.profiles    enable row level security;
alter table public.projects    enable row level security;
alter table public.boreholes   enable row level security;
alter table public.scenarios   enable row level security;
alter table public.sim_results enable row level security;
alter table public.leads       enable row level security;

-- profiles: owner can read/update own row
create policy "profiles self" on public.profiles
  for all using (auth.uid() = id) with check (auth.uid() = id);

-- owned tables: full CRUD restricted to the owner
do $$
declare t text;
begin
  foreach t in array array['projects','boreholes','scenarios','sim_results'] loop
    execute format($f$
      create policy "%1$s owner" on public.%1$s
        for all using (auth.uid() = owner) with check (auth.uid() = owner);
    $f$, t);
  end loop;
end $$;

-- leads: anonymous visitors may INSERT only; nobody can read via the anon key
create policy "leads insert" on public.leads
  for insert with check (true);

create index if not exists idx_projects_owner    on public.projects(owner);
create index if not exists idx_boreholes_project on public.boreholes(project_id);
create index if not exists idx_scenarios_project on public.scenarios(project_id);
create index if not exists idx_results_scenario  on public.sim_results(scenario_id);

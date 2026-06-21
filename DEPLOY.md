# Deploying GCC-SWSS

Your GoDaddy plan is domain/shared hosting, which cannot run the Next.js or
FastAPI servers. So: **GoDaddy provides the domain only**, and the app runs on
Vercel (web) + Render (API) + Supabase (database). All have free tiers.

Deploy in this order. Each step gives you a URL the next step needs.

```
Supabase (DB)  ->  Render (API)  ->  Vercel (web)  ->  GoDaddy (DNS)
```

---

## 1. Supabase — database + auth

1. Create a project at https://supabase.com (free tier).
2. Open **SQL Editor**, paste the contents of `supabase/migrations/20260621000000_init.sql`, run it.
3. From **Project Settings → API**, copy:
   - `Project URL`            → `SUPABASE_URL`
   - `service_role` secret    → `SUPABASE_SERVICE_KEY`  (server-only, never in the browser)
   - `anon` public key        → `NEXT_PUBLIC_SUPABASE_ANON_KEY`
4. From **Project Settings → API → JWT Settings**, copy the `JWT Secret` → `SUPABASE_JWT_SECRET`.

> You can skip Supabase at first — the API runs without it (leads fall back to a
> file, auth is disabled). Add it when you want accounts and saved projects.

## 2. Render — the FastAPI engine API

1. At https://render.com → **New → Blueprint**, connect the GitHub repo
   `garyduwyanemorgan/GCC-SWSS`. Render reads `render.yaml` and creates the
   `gcc-swss-api` web service (Docker).
2. Set environment variables on the service (placeholders in `render.yaml`):
   - `SWSS_CORS_ORIGINS` = `https://YOUR-VERCEL-DOMAIN` (fill in after step 3; can be edited later)
   - `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_JWT_SECRET` (from step 1, optional)
3. Deploy. When live, note the URL, e.g. `https://gcc-swss-api.onrender.com`.
   Verify: open `https://gcc-swss-api.onrender.com/health` → `{"status":"ok",...}`.

> Free tier sleeps after ~15 min idle; the first request then takes ~50s to wake.
> Switch `plan: free` → `plan: starter` in `render.yaml` to keep it always-on.

## 3. Vercel — the Next.js web app

1. At https://vercel.com → **Add New → Project**, import `garyduwyanemorgan/GCC-SWSS`.
2. **Important — set Root Directory to `web`** (the app is in a monorepo). Vercel
   auto-detects Next.js.
3. Add environment variables:
   - `NEXT_PUBLIC_API_URL` = the Render URL from step 2 (e.g. `https://gcc-swss-api.onrender.com`)
   - `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY` (optional, step 1)
4. Deploy. You get `https://gcc-swss-xxxx.vercel.app`.
5. Go back to **Render** and set `SWSS_CORS_ORIGINS` to this Vercel URL, then redeploy
   the API (so the browser is allowed to call it).

## 4. GoDaddy — point your domain at Vercel

In **Vercel → Project → Settings → Domains**, add your domain (e.g. `gcc-swss.com`).
Vercel shows the DNS records to create. Then in **GoDaddy → My Products → DNS**:

| Type  | Name  | Value                         | Purpose                  |
|-------|-------|-------------------------------|--------------------------|
| A     | `@`   | `76.76.21.21`                 | apex → Vercel            |
| CNAME | `www` | `cname.vercel-dns.com`        | www → Vercel             |
| CNAME | `api` | `gcc-swss-api.onrender.com`   | api subdomain → Render   |

(Use whatever values Vercel/Render display for your accounts — the above are the
common Vercel/Render targets.) If you add the `api` subdomain, set
`NEXT_PUBLIC_API_URL=https://api.yourdomain.com` in Vercel and add it to the
Render `SWSS_CORS_ORIGINS`. DNS can take 10 min–48 h to propagate.

---

## After it's live

- Every `git push` to `main` auto-redeploys both Vercel and Render.
- Smoke test: open your domain → **Simulator → Run water balance** → confirm the
  flux-attribution chart and scenario table render.
- If the dropdowns are empty, it's CORS: make sure `SWSS_CORS_ORIGINS` on Render
  exactly matches the domain in the browser address bar (scheme + host, no trailing slash).

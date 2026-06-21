# GCC Soil Water Security Simulator (SWSS)

A hydrogeological decision-support SaaS that evaluates whether soil amendments
actually reduce irrigation demand under GCC conditions — by running a complete
daily water balance and **attributing every flux**, not by reporting a retention
curve.

> **Retention curves tell us how water is stored. Water balances tell us whether
> water is saved. Until the fluxes are measured, claims of water security remain
> hypotheses rather than demonstrated outcomes.**

## Architecture

```
web/      Next.js (App Router) dashboard + marketing/lead capture   → Vercel
api/      FastAPI service wrapping the engine                        → Render
engine/   swss — deterministic scientific core (Python, tested)      ← the moat
supabase/ Postgres schema + RLS (accounts, projects, leads)         → Supabase
docs/spec original specification documents (provenance)
```

The engine is built and tested first because the scientific credibility lives
there. The API, web app and database are wrappers around it. The AI
interpretation layer is **rule-based and reproducible** (no LLM in the decision
path) — a forensic/legal requirement.

## Run it locally

**1. Engine + API**
```bash
cd engine && python -m venv .venv && .venv/Scripts/activate
pip install -e .[ptf] && pip install -r ../api/requirements.txt
cd ../api && uvicorn app.main:app --reload      # http://localhost:8000/health
```

**2. Web**
```bash
cd web && cp .env.local.example .env.local       # NEXT_PUBLIC_API_URL=http://localhost:8000
npm install && npm run dev                        # http://localhost:3000
```

Open the simulator, configure a soil + amendments, and run the water balance.

## Verify

```bash
cd engine && pytest -q && mypy swss               # 22 tests, clean types
```

The golden test (`tests/test_pipeline.py`) asserts the platform's thesis: an
amendment can raise available-water storage while the irrigation requirement does
**not** fall proportionally — proving retention ≠ saving.

## Documentation

- [docs/EXECUTIVE_SUMMARY.md](docs/EXECUTIVE_SUMMARY.md) — 2-page non-technical overview for decision-makers.
- [docs/SCIENTIFIC_BASIS.md](docs/SCIENTIFIC_BASIS.md) — full defensibility document: every equation, citation, assumption, limitation, and the validation gap. Built to be interrogated.
- [docs/WORKED_EXAMPLE.md](docs/WORKED_EXAMPLE.md) — one result traced end-to-end with real engine numbers and hand-checked equations.
- [DEPLOY.md](DEPLOY.md) — Supabase → Render → Vercel → GoDaddy deployment.

## Phasing

- **Phase 1 (done):** engine — all six layers, flux attribution, Monte Carlo, WSI, economics, PDF.
- **Phase 2 (done):** FastAPI API (`/simulate`, `/report`, `/libraries`, `/leads`, `/health`).
- **Phase 3 (done):** Next.js dashboard + marketing/lead capture.
- **Phase 4:** wire Supabase (Auth + Postgres) using `supabase/migrations/20260621000000_init.sql`.
- **Phase 5 (future):** AI-vision lab-PDF parser, "explain this result" assistant, salinity module.

© GDM Environmental Consultants & Studies CO. L.L.C. — Lead concept: Gary Morgan.

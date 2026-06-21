"""GCC-SWSS engine API.

Thin async wrapper over the deterministic `swss` engine. The science lives in the
engine; this layer adds transport, validation, CORS, auth and persistence.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import leads, libraries, simulate
from app.settings import settings
from swss import __version__ as engine_version

app = FastAPI(
    title="GCC Soil Water Security Simulator API",
    version="0.1.0",
    description="Where did the water go? Deterministic soil-water-balance engine.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(simulate.router)
app.include_router(libraries.router)
app.include_router(leads.router)


@app.get("/health", tags=["meta"])
def health() -> dict[str, object]:
    from swss.soil.rosetta_ptf import rosetta_available

    return {
        "status": "ok",
        "engine_version": engine_version,
        "rosetta_available": rosetta_available(),
        "auth_enabled": settings.supabase_jwt_secret is not None,
    }

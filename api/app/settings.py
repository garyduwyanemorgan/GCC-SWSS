"""Runtime configuration via environment variables (12-factor)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field


def _origins() -> list[str]:
    raw = os.getenv("SWSS_CORS_ORIGINS", "http://localhost:3000")
    return [o.strip() for o in raw.split(",") if o.strip()]


@dataclass(frozen=True)
class Settings:
    cors_origins: list[str] = field(default_factory=_origins)
    # Supabase (Phase 4). When unset, auth is disabled and leads fall back to file.
    supabase_url: str | None = os.getenv("SUPABASE_URL")
    supabase_service_key: str | None = os.getenv("SUPABASE_SERVICE_KEY")
    supabase_jwt_secret: str | None = os.getenv("SUPABASE_JWT_SECRET")
    # Local fallback store for leads when Supabase is not configured.
    leads_file: str = os.getenv("SWSS_LEADS_FILE", "leads.jsonl")
    max_monte_carlo: int = int(os.getenv("SWSS_MAX_MC", "2000"))


settings = Settings()

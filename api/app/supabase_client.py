"""Lazy Supabase client (Phase 4).

Returns None when Supabase is not configured so the API runs fully without it
(engine + simulate + file-based leads). When SUPABASE_URL/SERVICE_KEY are set,
persistence and auth activate.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any

from app.settings import settings


@lru_cache(maxsize=1)
def get_client() -> Any | None:
    if not (settings.supabase_url and settings.supabase_service_key):
        return None
    from supabase import create_client  # imported lazily

    return create_client(settings.supabase_url, settings.supabase_service_key)

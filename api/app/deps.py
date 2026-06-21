"""Auth dependency.

When SUPABASE_JWT_SECRET is configured, validates the Supabase-issued JWT and
returns the user id. Otherwise authentication is disabled (anonymous access) so
the engine API is usable locally and in CI without Supabase.
"""
from __future__ import annotations

from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.settings import settings

_bearer = HTTPBearer(auto_error=False)


def current_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> Optional[str]:
    """Return the authenticated user id, or None when auth is disabled."""
    if not settings.supabase_jwt_secret:
        return None  # auth disabled
    if creds is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    try:
        payload = jwt.decode(
            creds.credentials,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except jwt.PyJWTError as exc:  # pragma: no cover - exercised in Phase 4
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    return str(payload.get("sub"))

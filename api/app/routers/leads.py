"""Lead capture for the marketing site.

Durable storage in Supabase when configured; otherwise appended to a local JSONL
file so no lead is lost during development. (Phase 4 makes Supabase the default.)
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field

from app.settings import settings
from app.supabase_client import get_client

router = APIRouter(tags=["leads"])


class Lead(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    organisation: str | None = Field(default=None, max_length=200)
    message: str | None = Field(default=None, max_length=2000)
    source: str = "website"


@router.post("/leads", status_code=201)
def capture_lead(lead: Lead) -> dict[str, str]:
    record = {**lead.model_dump(), "created_at": datetime.now(timezone.utc).isoformat()}
    client = get_client()
    if client is not None:
        try:
            client.table("leads").insert(record).execute()
            return {"status": "stored", "backend": "supabase"}
        except Exception as exc:  # pragma: no cover - network path
            raise HTTPException(status_code=502, detail="Lead store failed") from exc
    # Fallback: append to local JSONL.
    path = Path(settings.leads_file)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")
    return {"status": "stored", "backend": "file"}

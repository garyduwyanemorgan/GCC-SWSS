"""Read-only library endpoints (soil / amendment / crop) for UI dropdowns."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from swss.amendments.engine import list_amendments
from swss.plants.crop_coefficients import list_crops
from swss.soil.library import list_soils

router = APIRouter(prefix="/libraries", tags=["libraries"])

_GETTERS = {
    "soil": list_soils,
    "amendment": list_amendments,
    "crop": list_crops,
}


@router.get("/{kind}")
def get_library(kind: str) -> list[dict]:
    if kind not in _GETTERS:
        raise HTTPException(status_code=404, detail=f"Unknown library '{kind}'.")
    return _GETTERS[kind]()

"""Crop/vegetation library and potential water demand.

Uses a representative mid-season single crop coefficient (Kc) for established
GCC landscape vegetation. Crop evapotranspiration is split into potential
transpiration and potential soil evaporation via a category canopy fraction so
the water balance can later attribute fluxes correctly (transpiration is the
'useful' flux; soil evaporation is mostly loss).
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from swss._data import load_yaml

_LIBRARY_FILE = "crop_library.yaml"

# Fraction of crop ET that is transpiration (vs bare-soil evaporation) by category.
_CANOPY_FRACTION = {
    "turf": 0.92,
    "trees": 0.70,
    "shrubs": 0.65,
    "native": 0.60,
    "crops": 0.80,
}


class CropParams(BaseModel):
    id: str
    name: str
    category: str
    kc: float
    root_depth_m: float
    depletion_frac: float
    canopy_fraction: float


def list_crops() -> list[dict[str, Any]]:
    return load_yaml(_LIBRARY_FILE)["crops"]


def get_crop(crop_id: str) -> CropParams:
    for c in list_crops():
        if c["id"] == crop_id:
            return CropParams(
                id=c["id"],
                name=c["name"],
                category=c["category"],
                kc=c["kc_mid"],
                root_depth_m=c["root_depth_m"],
                depletion_frac=c["depletion_frac"],
                canopy_fraction=_CANOPY_FRACTION.get(c["category"], 0.75),
            )
    raise KeyError(f"Unknown crop id '{crop_id}'. Available: {[c['id'] for c in list_crops()]}")


def potential_demand(et0_mm: float, crop: CropParams) -> tuple[float, float]:
    """Return (potential_transpiration_mm, potential_soil_evaporation_mm) for a day."""
    etc = crop.kc * et0_mm
    tp = crop.canopy_fraction * etc
    ep = etc - tp
    return tp, ep

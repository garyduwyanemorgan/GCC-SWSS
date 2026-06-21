"""GCC reference soil library + the Layer-1 characterisation entry point."""
from __future__ import annotations

from typing import Any

from swss._data import load_yaml
from swss.schemas import HydraulicProperties, SoilInput, VanGenuchten
from swss.soil import rosetta_ptf
from swss.soil import vg as _vg
from swss.soil.awc import available_water_capacity

_LIBRARY_FILE = "soil_library.yaml"


def list_soils() -> list[dict[str, Any]]:
    return load_yaml(_LIBRARY_FILE)["soils"]


def get_soil(soil_id: str) -> dict[str, Any]:
    for entry in list_soils():
        if entry["id"] == soil_id:
            return entry
    raise KeyError(f"Unknown soil id '{soil_id}'. Available: {[s['id'] for s in list_soils()]}")


def hydraulics_from_library_entry(entry: dict[str, Any]) -> HydraulicProperties:
    """Build HydraulicProperties from a literature library entry (confidence 2)."""
    vg = VanGenuchten(**entry["vg"])
    notes = [f"Literature values for '{entry['name']}'."]
    if entry.get("requires_site_calibration"):
        notes.append("Requires site calibration - replace with Rosetta/borehole data when available.")
    return HydraulicProperties(
        vg=vg,
        theta_fc=_vg.theta_field_capacity(vg),
        theta_pwp=_vg.theta_wilting_point(vg),
        awc=available_water_capacity(vg),
        confidence_level=2,
        method="soil_library (literature)",
        notes=notes,
    )


def characterise(soil: SoilInput) -> HydraulicProperties:
    """Layer 1: turn a soil description into hydraulic properties via Rosetta.

    Rosetta is the authoritative path. The caller is responsible for catching the
    RuntimeError and falling back to a library entry if it chooses.
    """
    return rosetta_ptf.estimate_hydraulics(soil)

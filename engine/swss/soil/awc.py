"""Available Water Capacity from a van Genuchten curve.

AWC = theta(field capacity) - theta(permanent wilting point).
This is the plant-available fraction; multiply by root-zone depth for a depth (mm).
"""
from __future__ import annotations

from swss.schemas import VanGenuchten
from swss.soil import vg as _vg


def available_water_capacity(vg: VanGenuchten) -> float:
    """AWC as a volumetric fraction (cm3/cm3)."""
    return max(0.0, _vg.theta_field_capacity(vg) - _vg.theta_wilting_point(vg))


def awc_depth_mm(vg: VanGenuchten, root_zone_depth_m: float) -> float:
    """Plant-available water held in the root zone, expressed as a depth (mm)."""
    return available_water_capacity(vg) * root_zone_depth_m * 1000.0

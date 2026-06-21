"""FAO-56 water-stress coefficient (Ks).

Transpiration proceeds at the potential rate until root-zone depletion exceeds
the Readily Available Water (RAW = p * TAW); beyond that it declines linearly to
zero at the wilting point. This is the mechanism by which 'more stored water'
may - or may not - translate into reduced stress and reduced irrigation.
"""
from __future__ import annotations


def readily_available_water(taw_mm: float, depletion_frac: float) -> float:
    """RAW = p * TAW."""
    return depletion_frac * taw_mm


def stress_coefficient(depletion_mm: float, taw_mm: float, depletion_frac: float) -> float:
    """Ks in [0, 1] from current root-zone depletion (FAO-56 eq. 84)."""
    if taw_mm <= 0.0:
        return 0.0
    raw = readily_available_water(taw_mm, depletion_frac)
    if depletion_mm <= raw:
        return 1.0
    ks = (taw_mm - depletion_mm) / (taw_mm - raw) if taw_mm > raw else 0.0
    return max(0.0, min(1.0, ks))

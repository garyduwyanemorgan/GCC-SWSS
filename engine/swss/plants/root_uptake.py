"""Actual transpiration (root uptake) and actual soil evaporation for a day.

Root uptake is potential transpiration reduced by water stress. Soil evaporation
is reduced by surface dryness (proxied by relative root-zone wetness) - this is
the term that quietly consumes 'extra retained water' in hot arid soils.
"""
from __future__ import annotations

from swss.plants.stress import stress_coefficient


def actual_fluxes(
    tp_pot_mm: float,
    ep_pot_mm: float,
    depletion_mm: float,
    taw_mm: float,
    depletion_frac: float,
) -> tuple[float, float, float]:
    """Return (transpiration_mm, evaporation_mm, stress_coefficient) for the day.

    transpiration = Ks * potential_transpiration
    evaporation   = relative_wetness * potential_soil_evaporation
    """
    ks = stress_coefficient(depletion_mm, taw_mm, depletion_frac)
    transpiration = ks * tp_pot_mm

    rel_wetness = 1.0 - (depletion_mm / taw_mm if taw_mm > 0 else 1.0)
    rel_wetness = max(0.0, min(1.0, rel_wetness))
    evaporation = rel_wetness * ep_pot_mm
    return transpiration, evaporation, ks

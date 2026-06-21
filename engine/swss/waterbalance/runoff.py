"""Infiltration-excess (Hortonian) runoff.

Rainfall exceeding the soil's infiltration capacity (~ saturated conductivity)
becomes runoff. For high-Ks GCC sands this is essentially zero; for surface-
sealing biopolymers (which cut Ks) it can become significant.
"""
from __future__ import annotations


def partition_rainfall(rain_mm: float, ks_cm_day: float) -> tuple[float, float]:
    """Return (infiltration_mm, runoff_mm) for a day's rainfall."""
    infil_capacity_mm = ks_cm_day * 10.0  # cm/day -> mm/day
    runoff = max(0.0, rain_mm - infil_capacity_mm)
    return rain_mm - runoff, runoff

"""Deep drainage below the root zone.

Free-drainage assumption: water held above field capacity drains below the root
zone within the day. This is appropriate for the high-conductivity sandy soils
that dominate the GCC, and it is exactly the flux an amendment must REDUCE (by
raising field capacity) for retained water to become a genuine saving.
"""
from __future__ import annotations


def free_drainage(excess_above_fc_mm: float) -> float:
    return max(0.0, excess_above_fc_mm)

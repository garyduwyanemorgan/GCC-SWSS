"""Root-zone storage capacities derived from the (possibly amended) VG curve."""
from __future__ import annotations

from swss.schemas import HydraulicProperties


def total_available_water_mm(h: HydraulicProperties, root_depth_m: float) -> float:
    """TAW = (theta_fc - theta_pwp) * Zr, as a depth in mm."""
    return max(0.0, (h.theta_fc - h.theta_pwp)) * root_depth_m * 1000.0


def saturation_excess_mm(h: HydraulicProperties, root_depth_m: float) -> float:
    """Transient water held between field capacity and saturation (drains fast)."""
    return max(0.0, (h.vg.theta_s - h.theta_fc)) * root_depth_m * 1000.0

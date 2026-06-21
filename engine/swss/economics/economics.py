"""Economic appraisal of an amendment vs baseline.

Savings derive ONLY from a reduction in the irrigation REQUIREMENT (the modelled
flux), never from a retention figure - so the economics inherit the engine's
scientific discipline. A negative saving (amendment increases irrigation, e.g. by
prolonging evaporation) is reported honestly.
"""
from __future__ import annotations

from typing import Optional

from swss.schemas import EconomicsInput, EconomicsResult


def appraise(
    baseline_irrigation_mm: float,
    scenario_irrigation_mm: float,
    econ: EconomicsInput,
) -> EconomicsResult:
    saved_mm = baseline_irrigation_mm - scenario_irrigation_mm
    saved_m3 = saved_mm / 1000.0 * econ.area_m2
    annual_saving = saved_m3 * econ.water_cost_per_m3
    total_cost = econ.amendment_cost + econ.application_cost

    payback = total_cost / annual_saving if annual_saving > 0 else None
    cost_per_m3 = (
        total_cost / (saved_m3 * econ.horizon_years)
        if saved_m3 > 0 and econ.horizon_years > 0
        else None
    )

    r = econ.discount_rate
    npv = -total_cost + sum(
        annual_saving / (1.0 + r) ** yr for yr in range(1, econ.horizon_years + 1)
    )
    roi: Optional[float] = None
    if total_cost > 0:
        roi = 100.0 * (annual_saving * econ.horizon_years - total_cost) / total_cost

    return EconomicsResult(
        annual_water_saved_m3=saved_m3,
        annual_saving_currency=annual_saving,
        payback_years=payback,
        cost_per_m3_saved=cost_per_m3,
        npv=npv,
        roi_pct=roi,
    )

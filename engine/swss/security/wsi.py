"""Layer 6 - Water Security Engine.

Translates hydraulic behaviour into management metrics and the composite Water
Security Index (0-100). Irrigation- and drainage-reduction components are scored
RELATIVE TO BASELINE, so an amendment only scores on them if it demonstrably
reduces those fluxes - consistent with the platform's core scientific rule.

    WSI = 0.25*StorageReliability + 0.25*IrrigationReduction
        + 0.20*DrainageReduction + 0.15*SalinityResistance + 0.15*PlantPerformance
"""
from __future__ import annotations

from typing import Optional

from swss.schemas import WaterSecurityResult
from swss.waterbalance.water_balance import WaterBalanceOutput

_WEIGHTS = {
    "storage_reliability": 0.25,
    "irrigation_reduction": 0.25,
    "drainage_reduction": 0.20,
    "salinity_resistance": 0.15,
    "plant_performance": 0.15,
}


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _relative_reduction(baseline: float, value: float) -> float:
    if baseline <= 0.0:
        return 0.0
    return _clamp01((baseline - value) / baseline)


def salinity_resistance(ec_ds_m: Optional[float]) -> float:
    """Heuristic 0-1 resistance score; EC ~0 -> 1.0, EC >= 8 dS/m -> 0.0."""
    if ec_ds_m is None:
        return 0.6  # unknown -> mildly favourable default for GCC context
    return _clamp01(1.0 - ec_ds_m / 8.0)


def assess(
    balance: WaterBalanceOutput,
    ec_ds_m: Optional[float],
    baseline: Optional[WaterBalanceOutput] = None,
) -> WaterSecurityResult:
    t = balance.totals
    base = baseline.totals if baseline else None

    storage_reliability = _clamp01(balance.reliability)
    irrigation_reduction = _relative_reduction(base.irrigation_mm, t.irrigation_mm) if base else 0.0
    drainage_reduction = _relative_reduction(base.drainage_mm, t.drainage_mm) if base else 0.0
    sal = salinity_resistance(ec_ds_m)
    plant_performance = _clamp01(balance.reliability)  # non-stressed fraction as yield proxy

    components = {
        "storage_reliability": storage_reliability,
        "irrigation_reduction": irrigation_reduction,
        "drainage_reduction": drainage_reduction,
        "salinity_resistance": sal,
        "plant_performance": plant_performance,
    }
    wsi = 100.0 * sum(_WEIGHTS[k] * v for k, v in components.items())

    applied = t.precip_mm + t.irrigation_mm
    productivity = t.transpiration_mm / applied if applied > 0 else 0.0

    return WaterSecurityResult(
        annual_irrigation_mm=t.irrigation_mm,
        annual_et_mm=t.et_mm,
        drainage_loss_mm=t.drainage_mm,
        water_productivity=productivity,
        root_zone_reliability=storage_reliability,
        wsi=wsi,
        wsi_components=components,
    )

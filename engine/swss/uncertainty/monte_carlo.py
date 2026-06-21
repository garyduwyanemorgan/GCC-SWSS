"""Monte Carlo uncertainty propagation.

Samples each amendment multiplier from a triangular(min, likely, max) distribution,
re-runs the full water balance, and reports P10/P50/P90 bands for the metrics that
matter (irrigation requirement, drainage, AWC, irrigation saving). This enforces
the rule that NO deterministic water-saving claim is permitted.
"""
from __future__ import annotations

import numpy as np

from swss.amendments.engine import apply_amendment, get_amendment
from swss.plants.crop_coefficients import CropParams
from swss.schemas import (
    AmendmentInput,
    DailyWeather,
    HydraulicProperties,
    SoilTexture,
    UncertaintyBand,
)
from swss.waterbalance.water_balance import simulate

_VG_EFFECT_KEYS = ("theta_s", "theta_r", "alpha", "n")


def _sample_multipliers(
    spec_effects: dict, texture: SoilTexture, rng: np.random.Generator
) -> dict[str, float]:
    """Draw one realisation of multipliers from triangular distributions."""
    out: dict[str, float] = {}
    for key in _VG_EFFECT_KEYS:
        if key in spec_effects:
            e = spec_effects[key]
            out[key] = float(rng.triangular(e["min"], e["likely"], e["max"]))
    # Resolve a single texture-appropriate Ks multiplier.
    ks_key = "ks" if "ks" in spec_effects else ("ks_sandy" if texture.is_sandy else "ks_clayey")
    if ks_key in spec_effects:
        e = spec_effects[ks_key]
        out["ks"] = float(rng.triangular(e["min"], e["likely"], e["max"]))
    if "bulk_density" in spec_effects:
        e = spec_effects["bulk_density"]
        out["bulk_density"] = float(rng.triangular(e["min"], e["likely"], e["max"]))
    return out


def run(
    baseline: HydraulicProperties,
    texture: SoilTexture,
    amendment_id: str,
    weather: list[DailyWeather],
    crop: CropParams,
    area_m2: float,
    baseline_irrigation_mm: float,
    n: int = 1000,
    seed: int | None = 42,
) -> list[UncertaintyBand]:
    spec = get_amendment(amendment_id)
    effects = spec.get("hydraulic_effects", {})
    rng = np.random.default_rng(seed)

    irr = np.empty(n)
    drain = np.empty(n)
    awc = np.empty(n)
    saving = np.empty(n)

    for i in range(n):
        mult = _sample_multipliers(effects, texture, rng)
        modified, _ = apply_amendment(
            baseline,
            AmendmentInput(amendment_id="custom", custom_multipliers=mult),
            texture,
        )
        wb = simulate(modified, weather, crop)
        irr[i] = wb.totals.irrigation_mm
        drain[i] = wb.totals.drainage_mm
        awc[i] = modified.awc
        saving[i] = (
            100.0 * (baseline_irrigation_mm - wb.totals.irrigation_mm) / baseline_irrigation_mm
            if baseline_irrigation_mm > 0
            else 0.0
        )

    def band(metric: str, arr: np.ndarray) -> UncertaintyBand:
        p10, p50, p90 = np.percentile(arr, [10, 50, 90])
        return UncertaintyBand(metric=metric, p10=float(p10), p50=float(p50), p90=float(p90))

    return [
        band("annual_irrigation_mm", irr),
        band("drainage_mm", drain),
        band("awc", awc),
        band("irrigation_saving_pct", saving),
    ]

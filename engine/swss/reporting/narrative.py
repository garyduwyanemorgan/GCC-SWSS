"""Deterministic, rule-based narrative generation (the AI Interpretation Layer).

No LLM: every sentence is derived from the numerical flux ledger so the output is
fully reproducible - a forensic/legal requirement. This is where the platform's
core message is operationalised: it states the storage gain AND what actually
happened to that water, refusing to equate retention with saving.
"""
from __future__ import annotations

from swss.schemas import Confidence, ScenarioResult

_EVIDENCE_PHRASE = {
    Confidence.HIGH: "supported by a strong, peer-reviewed evidence base",
    Confidence.MEDIUM: "supported by a moderate evidence base",
    Confidence.LOW: "supported by limited peer-reviewed hydraulic data",
    Confidence.USER_DEFINED: "based on user-supplied parameters (not independently validated)",
}


def _pct(numer: float, denom: float) -> float:
    return 100.0 * numer / denom if denom != 0 else 0.0


def scenario_sentence(baseline: ScenarioResult, scn: ScenarioResult) -> str:
    b, s = baseline, scn
    awc_gain = _pct(s.hydraulics.awc - b.hydraulics.awc, b.hydraulics.awc)
    irr_reduction = _pct(b.balance.irrigation_mm - s.balance.irrigation_mm, b.balance.irrigation_mm)

    d_evap = s.balance.evaporation_mm - b.balance.evaporation_mm
    d_drain = s.balance.drainage_mm - b.balance.drainage_mm
    d_transp = s.balance.transpiration_mm - b.balance.transpiration_mm
    base_stressed = b.security.root_zone_reliability < 0.95
    drainage_small = b.balance.drainage_mm < 0.05 * max(1.0, b.balance.irrigation_mm)

    head = (
        f"{s.name} changed available water storage by {awc_gain:+.0f}% and the modelled "
        f"annual irrigation requirement by {-irr_reduction:+.0f}%"
    )

    # Diagnose the regime that produced this result.
    if awc_gain <= 0.5:
        why = "the amendment did not materially increase plant-available storage in this soil"
    elif base_stressed and d_transp > 0.02 * max(1.0, b.balance.transpiration_mm):
        why = (
            "the unamended soil was chronically water-stressed, so the additional storage was spent "
            "on higher transpiration (relieved plant stress) rather than reduced water use - a plant-"
            "performance gain, not a water saving. A like-for-like, non-stressed comparison is required"
        )
    elif irr_reduction >= 0.5 * awc_gain and irr_reduction > 1.0:
        why = (
            "the additional stored water displaced losses (mainly deep drainage and captured rainfall), "
            "translating part of the storage gain into a genuine irrigation saving"
        )
    elif not base_stressed and drainage_small:
        why = (
            "the unamended soil already met full plant water demand without stress, so the extra storage "
            "capacity went largely unused; in this climate irrigation is governed by evapotranspiration "
            "demand, not by storage"
        )
    else:
        losses = {
            "soil evaporation": max(0.0, d_evap),
            "deep drainage (delayed rather than reduced)": max(0.0, d_drain),
            "additional transpiration": max(0.0, d_transp),
        }
        dominant = max(losses, key=lambda k: losses[k])
        why = (
            f"most of the additional stored water was ultimately lost to {dominant}"
            if losses[dominant] > 0.0
            else "the extra retained water did not translate proportionally into reduced irrigation"
        )

    evidence = _EVIDENCE_PHRASE.get(s.confidence, "")
    return f"{head}, because {why}. This result is {evidence}."


def headline(baseline: ScenarioResult, scenarios: list[ScenarioResult]) -> list[str]:
    lines = [
        "Retention curves tell us how water is stored; water balances tell us whether "
        "water is saved. The figures below are modelled fluxes, not storage assertions.",
    ]
    for s in scenarios:
        lines.append(scenario_sentence(baseline, s))
    return lines


def assumptions() -> list[str]:
    return [
        "Single-layer root-zone water balance at daily resolution.",
        "Free-drainage lower boundary (appropriate for high-conductivity GCC sands).",
        "Demand-scheduled irrigation: refill to field capacity at the readily-available "
        "water threshold; reported irrigation is therefore a modelled requirement.",
        "Reference ET0 by FAO-56 Penman-Monteith; crop ET via single Kc.",
        "Amendment effects applied as multiplicative ranges; AWC recomputed from the "
        "modified van Genuchten curve (no independent AWC assertion).",
    ]


def limitations() -> list[str]:
    return [
        "Lateral flow, capillary rise from a water table, and macropore bypass are not modelled.",
        "Salinity affects the Water Security Index heuristically only; osmotic effects on "
        "root uptake are a future module.",
        "Amendment longevity is not modelled (e.g. polymer degradation, biochar ageing).",
        "Parameters are estimated by pedotransfer functions unless field-calibrated; "
        "confidence levels reflect this.",
    ]

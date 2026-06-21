"""Layer 4 - Amendment Response Engine.

Applies an amendment's (min/likely/max) MULTIPLIERS to the baseline van Genuchten
parameters, then RECOMPUTES available water from the modified curve rather than
trusting a separate AWC multiplier - this keeps storage physically consistent and
avoids asserting a water-saving outcome the physics has not produced.
"""
from __future__ import annotations

from typing import Any

from swss._data import load_yaml
from swss.schemas import (
    AmendmentInput,
    Bound,
    Confidence,
    HydraulicProperties,
    SoilTexture,
    VanGenuchten,
)
from swss.soil import vg as _vg
from swss.soil.awc import available_water_capacity

_LIBRARY_FILE = "amendment_library.yaml"
_VG_KEYS = ("theta_s", "theta_r", "alpha", "n")


def list_amendments() -> list[dict[str, Any]]:
    return load_yaml(_LIBRARY_FILE)["amendments"]


def get_amendment(amendment_id: str) -> dict[str, Any]:
    for a in list_amendments():
        if a["id"] == amendment_id:
            return a
    raise KeyError(
        f"Unknown amendment id '{amendment_id}'. Available: "
        f"{[a['id'] for a in list_amendments()]}"
    )


def _multiplier(effect: dict[str, dict[str, float]] | None, key: str, bound: Bound) -> float:
    if not effect or key not in effect:
        return 1.0
    return float(effect[key][bound.value])


def _ks_multiplier(effect: dict[str, Any], bound: Bound, texture: SoilTexture) -> float:
    """Texture-specific Ks effect: ks_sandy / ks_clayey, else generic ks, else 1."""
    if "ks" in effect:
        return _multiplier(effect, "ks", bound)
    key = "ks_sandy" if texture.is_sandy else "ks_clayey"
    if key in effect:
        return _multiplier(effect, key, bound)
    return 1.0


def apply_amendment(
    baseline: HydraulicProperties,
    amendment: AmendmentInput,
    texture: SoilTexture,
) -> tuple[HydraulicProperties, Confidence]:
    """Return modified hydraulics and the amendment's evidence confidence."""
    spec = get_amendment(amendment.amendment_id)
    confidence = Confidence(spec.get("confidence", "USER_DEFINED"))

    if amendment.amendment_id == "custom":
        effect: dict[str, Any] = {
            k: {b.value: v for b in Bound} for k, v in amendment.custom_multipliers.items()
        }
    else:
        effect = spec.get("hydraulic_effects", {})

    b = amendment.bound
    base = baseline.vg
    modified = VanGenuchten(
        theta_r=base.theta_r * _multiplier(effect, "theta_r", b),
        theta_s=min(0.99, base.theta_s * _multiplier(effect, "theta_s", b)),
        alpha=base.alpha * _multiplier(effect, "alpha", b),
        n=max(1.001, base.n * _multiplier(effect, "n", b)),
        ks=base.ks * _ks_multiplier(effect, b, texture),
    )
    # theta_r must stay below theta_s.
    if modified.theta_r >= modified.theta_s:
        modified = modified.model_copy(update={"theta_r": 0.5 * modified.theta_s})

    notes = list(baseline.notes)
    notes.append(
        f"Modified by {spec.get('name', amendment.amendment_id)} "
        f"({confidence.value} evidence, {b.value} bound). AWC recomputed from modified curve."
    )
    if spec.get("warning"):
        notes.append(f"Warning: {spec['warning']}.")

    return (
        HydraulicProperties(
            vg=modified,
            theta_fc=_vg.theta_field_capacity(modified),
            theta_pwp=_vg.theta_wilting_point(modified),
            awc=available_water_capacity(modified),
            # Amendment uncertainty caps reported confidence for LOW-evidence products.
            confidence_level=_cap_confidence(baseline.confidence_level, confidence),
            method=f"{baseline.method} + amendment multipliers",
            notes=notes,
        ),
        confidence,
    )


def _cap_confidence(level: int, evidence: Confidence) -> int:
    caps = {Confidence.HIGH: 4, Confidence.MEDIUM: 3, Confidence.LOW: 2, Confidence.USER_DEFINED: 2}
    return max(1, min(level, caps.get(evidence, 2)))

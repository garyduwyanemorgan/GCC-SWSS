"""Amendment engine applies library multipliers correctly."""
from __future__ import annotations

from swss.amendments.engine import apply_amendment, list_amendments
from swss.schemas import (
    AmendmentInput,
    Bound,
    Confidence,
    HydraulicProperties,
    SoilTexture,
    VanGenuchten,
)
from swss.soil import vg as v

BASE_VG = VanGenuchten(theta_r=0.05, theta_s=0.40, alpha=0.10, n=2.0, ks=100.0)
BASE = HydraulicProperties(
    vg=BASE_VG,
    theta_fc=v.theta_field_capacity(BASE_VG),
    theta_pwp=v.theta_wilting_point(BASE_VG),
    awc=0.1,
    confidence_level=3,
    method="test",
)
SANDY = SoilTexture(sand=90, silt=6, clay=4)


def test_biochar_max_bound_matches_library():
    mod, conf = apply_amendment(BASE, AmendmentInput(amendment_id="biochar", bound=Bound.MAX), SANDY)
    assert conf == Confidence.HIGH
    # library biochar theta_s max multiplier = 1.15
    assert abs(mod.vg.theta_s - BASE_VG.theta_s * 1.15) < 1e-9
    # sandy Ks uses ks_sandy max = 1.20
    assert abs(mod.vg.ks - BASE_VG.ks * 1.20) < 1e-9


def test_likely_bound_is_central():
    lo, _ = apply_amendment(BASE, AmendmentInput(amendment_id="compost", bound=Bound.MIN), SANDY)
    mid, _ = apply_amendment(BASE, AmendmentInput(amendment_id="compost", bound=Bound.LIKELY), SANDY)
    hi, _ = apply_amendment(BASE, AmendmentInput(amendment_id="compost", bound=Bound.MAX), SANDY)
    assert lo.vg.theta_r <= mid.vg.theta_r <= hi.vg.theta_r


def test_theta_r_below_theta_s_invariant():
    for spec in list_amendments():
        if spec["id"] == "custom":
            continue
        mod, _ = apply_amendment(BASE, AmendmentInput(amendment_id=spec["id"], bound=Bound.MAX), SANDY)
        assert mod.vg.theta_r < mod.vg.theta_s


def test_evidence_confidence_caps_level():
    # LOW-evidence amendment cannot report confidence level above 2
    mod, conf = apply_amendment(BASE, AmendmentInput(amendment_id="lnc"), SANDY)
    assert conf == Confidence.LOW
    assert mod.confidence_level <= 2

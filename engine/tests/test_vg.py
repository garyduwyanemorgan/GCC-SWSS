"""Van Genuchten retention & conductivity correctness."""
from __future__ import annotations

import numpy as np

from swss.schemas import VanGenuchten
from swss.soil import vg as v
from swss.soil.awc import available_water_capacity

SAND = VanGenuchten(theta_r=0.045, theta_s=0.36, alpha=0.145, n=2.68, ks=712.0)


def test_theta_bounded_and_monotonic():
    h = np.linspace(0, 15000, 400)
    theta = np.asarray(v.theta_from_h(h, SAND))
    assert np.all(theta <= SAND.theta_s + 1e-9)
    assert np.all(theta >= SAND.theta_r - 1e-9)
    # retention is monotonically non-increasing with suction
    assert np.all(np.diff(theta) <= 1e-9)


def test_saturation_endpoints():
    assert v.theta_from_h(0.0, SAND) == SAND.theta_s
    assert v.effective_saturation(0.0, SAND) == 1.0


def test_h_theta_roundtrip():
    for target in (0.10, 0.15, 0.25):
        h = v.h_from_theta(target, SAND)
        assert abs(v.theta_from_h(h, SAND) - target) < 1e-6


def test_fc_greater_than_pwp():
    assert v.theta_field_capacity(SAND) > v.theta_wilting_point(SAND)
    assert available_water_capacity(SAND) >= 0.0


def test_conductivity_bounds():
    assert abs(v.conductivity_from_se(1.0, SAND) - SAND.ks) < 1e-6
    assert v.conductivity_from_se(0.0, SAND) == 0.0

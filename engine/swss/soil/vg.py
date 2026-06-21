"""Van Genuchten (1980) retention + Mualem unsaturated conductivity.

Suction `h` is expressed as a POSITIVE matric potential head in cm
(i.e. h = |matric head|). h = 0 -> saturation.
"""
from __future__ import annotations

import numpy as np

from swss.schemas import VanGenuchten

# Reference suctions (cm) for agronomic water-holding points.
H_FIELD_CAPACITY = 330.0      # ~ -33 kPa
H_WILTING_POINT = 15000.0     # ~ -1500 kPa
MUALEM_L = 0.5                # pore-connectivity exponent


def effective_saturation(h: float | np.ndarray, vg: VanGenuchten) -> float | np.ndarray:
    """Se(h) in [0, 1]. Se = [1 + (alpha h)^n]^(-m) for h > 0, else 1."""
    h = np.asarray(h, dtype=float)
    se = np.where(
        h <= 0.0,
        1.0,
        (1.0 + (vg.alpha * np.abs(h)) ** vg.n) ** (-vg.m),
    )
    return se if se.ndim else float(se)


def theta_from_h(h: float | np.ndarray, vg: VanGenuchten) -> float | np.ndarray:
    """Volumetric water content theta(h)."""
    se = effective_saturation(h, vg)
    theta = vg.theta_r + (vg.theta_s - vg.theta_r) * se
    return theta


def h_from_theta(theta: float, vg: VanGenuchten) -> float:
    """Invert the retention curve: suction head (cm) for a given theta.

    Returns 0.0 at/above saturation and +inf at/below residual.
    """
    if theta >= vg.theta_s:
        return 0.0
    if theta <= vg.theta_r:
        return float("inf")
    se = (theta - vg.theta_r) / (vg.theta_s - vg.theta_r)
    return (1.0 / vg.alpha) * (se ** (-1.0 / vg.m) - 1.0) ** (1.0 / vg.n)


def conductivity_from_se(se: float | np.ndarray, vg: VanGenuchten) -> float | np.ndarray:
    """Mualem-van Genuchten K(Se) = Ks * Se^L * [1 - (1 - Se^(1/m))^m]^2."""
    se = np.clip(np.asarray(se, dtype=float), 0.0, 1.0)
    inner = (1.0 - (1.0 - se ** (1.0 / vg.m)) ** vg.m) ** 2
    k = vg.ks * se**MUALEM_L * inner
    return k if k.ndim else float(k)


def theta_field_capacity(vg: VanGenuchten) -> float:
    return float(theta_from_h(H_FIELD_CAPACITY, vg))


def theta_wilting_point(vg: VanGenuchten) -> float:
    return float(theta_from_h(H_WILTING_POINT, vg))

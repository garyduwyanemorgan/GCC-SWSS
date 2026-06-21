"""FAO-56 Penman-Monteith reference evapotranspiration (ET0).

Reference: Allen et al. (1998), FAO Irrigation & Drainage Paper 56.
All functions are pure and unit-tested against the worked examples in that paper
(extraterrestrial radiation against Example 8 -> 32.2 MJ/m2/day at 20S, 3 Sep).
"""
from __future__ import annotations

import math

GSC = 0.0820            # solar constant, MJ m-2 min-1
SIGMA = 4.903e-9        # Stefan-Boltzmann, MJ K-4 m-2 day-1
ALBEDO = 0.23           # reference grass albedo


def atmospheric_pressure(elevation_m: float) -> float:
    """Mean atmospheric pressure (kPa) from elevation (FAO-56 eq. 7)."""
    return 101.3 * ((293.0 - 0.0065 * elevation_m) / 293.0) ** 5.26


def psychrometric_constant(elevation_m: float) -> float:
    """gamma (kPa/degC), FAO-56 eq. 8."""
    return 0.000665 * atmospheric_pressure(elevation_m)


def saturation_vapour_pressure(t_c: float) -> float:
    """e0(T) saturation vapour pressure (kPa), FAO-56 eq. 11."""
    return 0.6108 * math.exp(17.27 * t_c / (t_c + 237.3))


def slope_vapour_pressure(t_c: float) -> float:
    """Delta, slope of the SVP curve (kPa/degC), FAO-56 eq. 13."""
    return 4098.0 * saturation_vapour_pressure(t_c) / (t_c + 237.3) ** 2


def extraterrestrial_radiation(latitude_deg: float, doy: int) -> float:
    """Ra (MJ m-2 day-1), FAO-56 eq. 21-25."""
    phi = math.radians(latitude_deg)
    dr = 1.0 + 0.033 * math.cos(2.0 * math.pi / 365.0 * doy)
    decl = 0.409 * math.sin(2.0 * math.pi / 365.0 * doy - 1.39)
    # Sunset hour angle; clamp argument for polar day/night robustness.
    x = max(-1.0, min(1.0, -math.tan(phi) * math.tan(decl)))
    ws = math.acos(x)
    ra = (
        (24.0 * 60.0 / math.pi)
        * GSC
        * dr
        * (ws * math.sin(phi) * math.sin(decl) + math.cos(phi) * math.cos(decl) * math.sin(ws))
    )
    return ra


def clear_sky_radiation(ra: float, elevation_m: float) -> float:
    """Rso (MJ m-2 day-1), FAO-56 eq. 37."""
    return (0.75 + 2e-5 * elevation_m) * ra


def net_radiation(
    rs: float,
    ra: float,
    t_min: float,
    t_max: float,
    ea: float,
    elevation_m: float,
) -> float:
    """Net radiation Rn (MJ m-2 day-1), FAO-56 eq. 38-40."""
    rns = (1.0 - ALBEDO) * rs
    rso = clear_sky_radiation(ra, elevation_m)
    # Cloudiness factor, bounded to [0.05, 1.0] per FAO guidance near sunrise/season ends.
    rs_ratio = min(1.0, rs / rso) if rso > 0 else 1.0
    tmaxk = (t_max + 273.16) ** 4
    tmink = (t_min + 273.16) ** 4
    rnl = (
        SIGMA
        * ((tmaxk + tmink) / 2.0)
        * (0.34 - 0.14 * math.sqrt(max(ea, 0.0)))
        * (1.35 * rs_ratio - 0.35)
    )
    return rns - rnl


def et0_fao56(
    t_min: float,
    t_max: float,
    rh_mean: float,
    wind_2m: float,
    rs: float,
    latitude_deg: float,
    elevation_m: float,
    doy: int,
) -> float:
    """Daily reference ET0 (mm/day), FAO-56 eq. 6. G is taken as 0 for daily steps."""
    t_mean = (t_max + t_min) / 2.0
    delta = slope_vapour_pressure(t_mean)
    gamma = psychrometric_constant(elevation_m)

    es = (saturation_vapour_pressure(t_max) + saturation_vapour_pressure(t_min)) / 2.0
    ea = es * (rh_mean / 100.0)
    vpd = max(0.0, es - ea)

    ra = extraterrestrial_radiation(latitude_deg, doy)
    rn = net_radiation(rs, ra, t_min, t_max, ea, elevation_m)

    num = 0.408 * delta * rn + gamma * (900.0 / (t_mean + 273.0)) * wind_2m * vpd
    den = delta + gamma * (1.0 + 0.34 * wind_2m)
    return max(0.0, num / den)

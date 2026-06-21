"""FAO-56 climate engine validation."""
from __future__ import annotations

from swss.climate import penman_monteith as pm
from swss.climate.weather import build_year
from swss.schemas import ClimateInput


def test_extraterrestrial_radiation_fao56_example8():
    """FAO-56 Example 8: 20 deg S, 3 Sep -> Ra = 32.2 MJ/m2/day."""
    ra = pm.extraterrestrial_radiation(latitude_deg=-20.0, doy=246)
    assert abs(ra - 32.2) < 0.2


def test_et0_in_gcc_range():
    """Daily ET0 for the reference Dubai year stays within 2-16 mm/day."""
    series = build_year(ClimateInput(station_id="dubai_coastal"))
    et0 = [d.et0_mm for d in series]
    assert len(series) == 365
    assert all(e is not None and 2.0 <= e <= 16.0 for e in et0)
    # summer (Jun-Aug, doy ~152-243) should exceed winter mean
    summer = sum(series[i].et0_mm for i in range(151, 243)) / 92
    winter = sum(series[i].et0_mm for i in range(0, 59)) / 59
    assert summer > winter


def test_vapour_pressure_increases_with_temperature():
    assert pm.saturation_vapour_pressure(40) > pm.saturation_vapour_pressure(20)

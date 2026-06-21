"""Daily water balance closes and the flux ledger is consistent."""
from __future__ import annotations

from swss.climate.weather import build_year
from swss.flux.water_fate import attribute
from swss.plants.crop_coefficients import get_crop
from swss.schemas import ClimateInput, HydraulicProperties, VanGenuchten
from swss.soil import vg as v
from swss.waterbalance.water_balance import simulate

VGP = VanGenuchten(theta_r=0.06, theta_s=0.40, alpha=0.075, n=1.9, ks=106.0)
HYD = HydraulicProperties(
    vg=VGP,
    theta_fc=v.theta_field_capacity(VGP),
    theta_pwp=v.theta_wilting_point(VGP),
    awc=v.theta_field_capacity(VGP) - v.theta_wilting_point(VGP),
    confidence_level=2,
    method="test",
)


def _run():
    weather = build_year(ClimateInput())
    crop = get_crop("turf_warm")
    return simulate(HYD, weather, crop)


def test_balance_closes():
    wb = _run()
    assert abs(wb.totals.closure_error_mm) < 1e-6


def test_all_fluxes_non_negative():
    wb = _run()
    t = wb.totals
    for val in (t.precip_mm, t.irrigation_mm, t.et_mm, t.drainage_mm, t.runoff_mm):
        assert val >= -1e-9


def test_flux_ledger_sums_to_input():
    wb = _run()
    led = attribute(wb.totals, area_m2=10000.0)
    fate = (
        led.to_storage_mm
        + led.to_transpiration_mm
        + led.to_evaporation_mm
        + led.to_drainage_mm
        + led.to_runoff_mm
    )
    assert abs(fate - led.total_input_mm) < 1e-6

"""Monte Carlo uncertainty bands are ordered and reproducible."""
from __future__ import annotations

from swss.climate.weather import build_year
from swss.plants.crop_coefficients import get_crop
from swss.schemas import ClimateInput, SoilInput, SoilTexture
from swss.soil.library import characterise
from swss.uncertainty import monte_carlo
from swss.waterbalance.water_balance import simulate

SOIL = SoilInput(texture=SoilTexture(sand=65, silt=25, clay=10), bulk_density=1.48, root_zone_depth_m=0.5)


def _bands(seed=42, n=200):
    base = characterise(SOIL)
    weather = build_year(ClimateInput())
    crop = get_crop("turf_warm")
    base_wb = simulate(base, weather, crop)
    return monte_carlo.run(
        base, SOIL.texture, "biochar", weather, crop, 10000.0,
        base_wb.totals.irrigation_mm, n=n, seed=seed,
    )


def test_percentiles_ordered():
    for band in _bands():
        assert band.p10 <= band.p50 <= band.p90


def test_reproducible_with_seed():
    a = _bands(seed=7, n=100)
    b = _bands(seed=7, n=100)
    assert [x.p50 for x in a] == [x.p50 for x in b]

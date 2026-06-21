"""Golden end-to-end case: the platform proves retention != water saving.

On a realistic GCC landscape soil (sandy loam, turf) both baseline and amended
runs are non-stressed (equal plant performance), the amendment raises available
water storage, yet the irrigation requirement does NOT fall proportionally -
because in this climate the balance is governed by evapotranspiration demand.
"""
from __future__ import annotations

from swss import run_investigation
from swss.reporting import report
from swss.schemas import (
    AmendmentInput,
    EconomicsInput,
    PlantInput,
    ProjectInput,
    SoilInput,
    SoilTexture,
)


def _project(**kw):
    return ProjectInput(
        project_name="Golden GCC Case",
        soil=SoilInput(texture=SoilTexture(sand=65, silt=25, clay=10), bulk_density=1.48,
                       ec=2.0, root_zone_depth_m=0.5),
        plant=PlantInput(crop_id="turf_warm"),
        amendments=[AmendmentInput(amendment_id="biochar")],
        economics=EconomicsInput(area_m2=10000, water_cost_per_m3=2.0, amendment_cost=12000),
        **kw,
    )


def test_pipeline_closes_and_runs():
    r = run_investigation(_project())
    assert abs(r.baseline.balance.closure_error_mm) < 1e-6
    assert all(abs(s.balance.closure_error_mm) < 1e-6 for s in r.scenarios)


def test_storage_gain_does_not_equal_water_saving():
    r = run_investigation(_project())
    cmp = r.comparisons[0]
    # storage capacity rises meaningfully ...
    assert cmp.awc_change_pct > 5.0
    # ... but irrigation does NOT fall proportionally (the whole thesis).
    irrigation_reduction = -cmp.irrigation_change_pct
    assert irrigation_reduction < 0.5 * cmp.awc_change_pct


def test_equal_plant_performance():
    r = run_investigation(_project())
    b, s = r.baseline.balance, r.scenarios[0].balance
    # non-stressed both ways -> transpiration essentially equal
    assert abs(s.transpiration_mm - b.transpiration_mm) < 0.02 * b.transpiration_mm
    assert r.baseline.security.root_zone_reliability > 0.99


def test_narrative_present_and_honest():
    r = run_investigation(_project())
    assert any("water balances tell us whether water is saved" in n for n in r.narrative)
    assert len(r.narrative) >= 2


def test_pdf_report_written(tmp_path):
    r = run_investigation(_project())
    out = report.build_pdf(r, tmp_path / "report.pdf")
    assert out.exists() and out.stat().st_size > 1000

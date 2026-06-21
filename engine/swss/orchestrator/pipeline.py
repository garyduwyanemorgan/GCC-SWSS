"""Simulation Orchestrator - chains Layers 1-6 + flux + uncertainty + economics.

Single entry point `run_investigation(project) -> SimResult`, consumed by the API,
dashboard and report writer. Runs a baseline plus one scenario per selected
amendment, always comparing fluxes (not just storage) against the baseline.
"""
from __future__ import annotations

from statistics import mean

from swss.amendments.engine import apply_amendment
from swss.economics.economics import appraise
from swss.flux.water_fate import attribute
from swss.climate.weather import build_year
from swss.plants.crop_coefficients import get_crop
from swss.reporting import narrative
from swss.schemas import (
    Bound,
    Confidence,
    ProjectInput,
    ScenarioComparison,
    ScenarioResult,
    SimResult,
)
from swss.security.wsi import assess
from swss.soil.library import characterise
from swss.uncertainty import monte_carlo
from swss.waterbalance.water_balance import WaterBalanceOutput, simulate


def _pct(numer: float, denom: float) -> float:
    return 100.0 * numer / denom if denom != 0 else 0.0


def _mean_storage(wb: WaterBalanceOutput) -> float:
    return mean(wb.storage) if wb.storage else 0.0


def run_investigation(project: ProjectInput) -> SimResult:
    weather = build_year(project.climate)
    crop = get_crop(project.plant.crop_id)
    area = project.economics.area_m2 if project.economics else 10000.0

    # Layer 1-6 for the baseline (no amendment)
    base_hydraulics = characterise(project.soil)
    base_wb = simulate(base_hydraulics, weather, crop)
    baseline = ScenarioResult(
        name="Baseline (unamended)",
        amendment_id=None,
        confidence=Confidence.HIGH,
        bound=project.amendments[0].bound if project.amendments else Bound.LIKELY,
        hydraulics=base_hydraulics,
        balance=base_wb.totals,
        flux=attribute(base_wb.totals, area),
        security=assess(base_wb, project.soil.ec, baseline=None),
    )

    scenarios: list[ScenarioResult] = []
    comparisons: list[ScenarioComparison] = []

    for amd in project.amendments:
        hydraulics, conf = apply_amendment(base_hydraulics, amd, project.soil.texture)
        wb = simulate(hydraulics, weather, crop)
        econ = (
            appraise(base_wb.totals.irrigation_mm, wb.totals.irrigation_mm, project.economics)
            if project.economics
            else None
        )
        security = assess(wb, project.soil.ec, baseline=base_wb)

        result = ScenarioResult(
            name=amd.amendment_id.replace("_", " ").title(),
            amendment_id=amd.amendment_id,
            confidence=conf,
            bound=amd.bound,
            hydraulics=hydraulics,
            balance=wb.totals,
            flux=attribute(wb.totals, area),
            security=security,
            economics=econ,
        )
        scenarios.append(result)

        bands = (
            monte_carlo.run(
                base_hydraulics,
                project.soil.texture,
                amd.amendment_id,
                weather,
                crop,
                area,
                base_wb.totals.irrigation_mm,
                n=project.n_realisations,
                seed=project.seed,
            )
            if project.monte_carlo and amd.amendment_id != "custom"
            else []
        )

        comparisons.append(
            ScenarioComparison(
                name=result.name,
                amendment_id=amd.amendment_id,
                confidence=conf,
                awc_change_pct=_pct(hydraulics.awc - base_hydraulics.awc, base_hydraulics.awc),
                storage_change_pct=_pct(_mean_storage(wb) - _mean_storage(base_wb), _mean_storage(base_wb)),
                irrigation_change_pct=_pct(
                    wb.totals.irrigation_mm - base_wb.totals.irrigation_mm, base_wb.totals.irrigation_mm
                ),
                drainage_change_pct=_pct(
                    wb.totals.drainage_mm - base_wb.totals.drainage_mm, base_wb.totals.drainage_mm
                ),
                et_change_pct=_pct(wb.totals.et_mm - base_wb.totals.et_mm, base_wb.totals.et_mm),
                wsi=security.wsi,
                bands=bands,
            )
        )

    return SimResult(
        project_name=project.project_name,
        baseline=baseline,
        scenarios=scenarios,
        comparisons=comparisons,
        narrative=narrative.headline(baseline, scenarios),
        assumptions=narrative.assumptions(),
        limitations=narrative.limitations(),
    )

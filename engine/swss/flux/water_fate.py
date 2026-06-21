"""Flux Attribution Engine - the platform's signature feature.

Answers "where did the water go?" rather than "storage increased X%". Of every
unit of water added (rain + irrigation), it reports how much ended up in storage,
transpiration (the useful flux), soil evaporation, deep drainage and runoff -
in both mm and m3. By construction the ledger sums to total input, so a headline
storage gain cannot hide an offsetting loss to evaporation or drainage.
"""
from __future__ import annotations

from swss.schemas import FluxLedger, WaterBalanceTotals


def attribute(totals: WaterBalanceTotals, area_m2: float) -> FluxLedger:
    total_input = totals.precip_mm + totals.irrigation_mm
    return FluxLedger(
        area_m2=area_m2,
        total_input_mm=total_input,
        to_storage_mm=totals.delta_storage_mm,
        to_transpiration_mm=totals.transpiration_mm,
        to_evaporation_mm=totals.evaporation_mm,
        to_drainage_mm=totals.drainage_mm,
        to_runoff_mm=totals.runoff_mm,
    )


def ledger_rows(ledger: FluxLedger) -> list[tuple[str, float, float, float]]:
    """Return (label, mm, m3, percent_of_input) rows for reporting/dashboards."""
    inp = ledger.total_input_mm or 1.0
    items = [
        ("Transpiration (plant uptake)", ledger.to_transpiration_mm),
        ("Soil evaporation", ledger.to_evaporation_mm),
        ("Deep drainage", ledger.to_drainage_mm),
        ("Runoff", ledger.to_runoff_mm),
        ("Change in storage", ledger.to_storage_mm),
    ]
    return [(label, mm, ledger.as_volume_m3(mm), 100.0 * mm / inp) for label, mm in items]

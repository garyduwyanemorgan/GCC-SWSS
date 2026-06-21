"""Scientific PDF report generation (ReportLab).

Renders a SimResult into the forensic report structure: Executive Summary,
Assumptions, Water Balance, Flux Analysis ('where did the water go?'), Water
Security, Economics and Limitations.
"""
from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from swss.flux.water_fate import ledger_rows
from swss.schemas import ScenarioResult, SimResult

_STYLES = getSampleStyleSheet()


def _table(data: list[list[str]]) -> Table:
    t = Table(data, hAlign="LEFT")
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b4f6c")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef5f8")]),
            ]
        )
    )
    return t


def _flux_table(scn: ScenarioResult) -> Table:
    rows = [["Fate", "mm/yr", "m3/yr", "% of input"]]
    for label, mm_, m3, pct in ledger_rows(scn.flux):
        rows.append([label, f"{mm_:.0f}", f"{m3:.0f}", f"{pct:.0f}%"])
    return _table(rows)


def build_pdf(result: SimResult, path: str | Path) -> Path:
    path = Path(path)
    doc = SimpleDocTemplate(str(path), pagesize=A4, title=result.project_name)
    story: list = []
    h1, h2, body = _STYLES["Heading1"], _STYLES["Heading2"], _STYLES["BodyText"]

    story.append(Paragraph("GCC Soil Water Security Simulator", h1))
    story.append(Paragraph(result.project_name, h2))
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph("Executive Summary", h2))
    for line in result.narrative:
        story.append(Paragraph(line, body))
        story.append(Spacer(1, 2 * mm))

    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("Scientific Assumptions", h2))
    for a in result.assumptions:
        story.append(Paragraph(f"&bull; {a}", body))

    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("Water Balance (mm/yr)", h2))
    wb_rows = [["Scenario", "Rain", "Irrig.", "ET", "Drainage", "Runoff", "dStorage", "Closure"]]
    for scn in [result.baseline, *result.scenarios]:
        b = scn.balance
        wb_rows.append(
            [
                scn.name,
                f"{b.precip_mm:.0f}",
                f"{b.irrigation_mm:.0f}",
                f"{b.et_mm:.0f}",
                f"{b.drainage_mm:.0f}",
                f"{b.runoff_mm:.0f}",
                f"{b.delta_storage_mm:.0f}",
                f"{b.closure_error_mm:.2f}",
            ]
        )
    story.append(_table(wb_rows))

    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("Flux Analysis - Where Did the Water Go?", h2))
    for scn in [result.baseline, *result.scenarios]:
        story.append(Paragraph(scn.name, body))
        story.append(_flux_table(scn))
        story.append(Spacer(1, 3 * mm))

    story.append(Paragraph("Water Security & Economics", h2))
    ws_rows = [["Scenario", "WSI", "Irrig (mm)", "Drainage (mm)", "Payback (yr)", "NPV"]]
    for scn in [result.baseline, *result.scenarios]:
        econ = scn.economics
        ws_rows.append(
            [
                scn.name,
                f"{scn.security.wsi:.0f}",
                f"{scn.security.annual_irrigation_mm:.0f}",
                f"{scn.security.drainage_loss_mm:.0f}",
                f"{econ.payback_years:.1f}" if econ and econ.payback_years else "-",
                f"{econ.npv:.0f}" if econ else "-",
            ]
        )
    story.append(_table(ws_rows))

    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("Limitations", h2))
    for lim in result.limitations:
        story.append(Paragraph(f"&bull; {lim}", body))

    doc.build(story)
    return path

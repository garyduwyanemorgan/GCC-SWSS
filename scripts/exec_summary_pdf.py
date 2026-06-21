"""Generate a branded, client-facing Executive Summary PDF.

Uses the same ReportLab toolkit the engine uses for simulation reports, so the
handout matches the platform's look. Run with the engine venv (reportlab installed):

    engine/.venv/Scripts/python.exe scripts/exec_summary_pdf.py

Writes docs/GCC-SWSS_Executive_Summary.pdf.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

INK = colors.HexColor("#0b2f3a")
ACCENT = colors.HexColor("#0b7a8c")
ACCENT_LIGHT = colors.HexColor("#e7f2f4")
GOOD = colors.HexColor("#2f8f5b")
WARN = colors.HexColor("#b8791f")
BAD = colors.HexColor("#b5462f")
MUTED = colors.HexColor("#5a6b72")

ORG = "GDM Environmental Consultants & Studies CO. L.L.C."
OUT = Path(__file__).resolve().parent.parent / "docs" / "GCC-SWSS_Executive_Summary.pdf"


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "h1": ParagraphStyle("h1", parent=base["Heading1"], textColor=INK, fontSize=20, spaceAfter=2),
        "sub": ParagraphStyle("sub", parent=base["Normal"], textColor=MUTED, fontSize=10, spaceAfter=10),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], textColor=ACCENT, fontSize=13, spaceBefore=10, spaceAfter=4),
        "body": ParagraphStyle("body", parent=base["BodyText"], textColor=INK, fontSize=10, leading=14, spaceAfter=6),
        "thesis": ParagraphStyle("thesis", parent=base["BodyText"], textColor=INK, fontSize=11.5,
                                 leading=16, leftIndent=8, rightIndent=8, spaceBefore=4, spaceAfter=4,
                                 fontName="Helvetica-Oblique"),
        "cell": ParagraphStyle("cell", parent=base["BodyText"], textColor=INK, fontSize=9.5, leading=12),
        "cellw": ParagraphStyle("cellw", parent=base["BodyText"], textColor=colors.white, fontSize=9.5,
                                leading=12, fontName="Helvetica-Bold"),
        "foot": ParagraphStyle("foot", parent=base["Normal"], textColor=MUTED, fontSize=8, alignment=TA_CENTER),
    }


def _header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    # top accent band
    canvas.setFillColor(INK)
    canvas.rect(0, h - 26 * mm, w, 26 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 15)
    canvas.drawString(20 * mm, h - 14 * mm, "GCC Soil Water Security Simulator")
    canvas.setFillColor(ACCENT_LIGHT)
    canvas.setFont("Helvetica", 9)
    canvas.drawString(20 * mm, h - 20 * mm, "Executive Summary — where did the water go?")
    canvas.setFillColor(ACCENT)
    canvas.rect(0, h - 27.5 * mm, w, 1.5 * mm, fill=1, stroke=0)
    # footer
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(20 * mm, 10 * mm, ORG)
    canvas.drawRightString(w - 20 * mm, 10 * mm, f"Generated {date.today().isoformat()}  ·  Page {doc.page}")
    canvas.restoreState()


def _callout(text: str, st) -> Table:
    p = Paragraph(text, st["thesis"])
    t = Table([[p]], colWidths=[165 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), ACCENT_LIGHT),
        ("LINEBEFORE", (0, 0), (0, -1), 3, ACCENT),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    return t


def _table(rows, st, widths, header_bg=ACCENT, badge_col=None):
    data = []
    for r, row in enumerate(rows):
        styled = []
        for c, val in enumerate(row):
            style = st["cellw"] if r == 0 else st["cell"]
            styled.append(Paragraph(str(val), style))
        data.append(styled)
    t = Table(data, colWidths=widths, hAlign="LEFT")
    ts = [
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cdd8db")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ACCENT_LIGHT]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
    ]
    if badge_col is not None:
        colormap = {"High": GOOD, "Medium": WARN, "Low": BAD}
        for r in range(1, len(rows)):
            label = rows[r][badge_col]
            if label in colormap:
                ts.append(("TEXTCOLOR", (badge_col, r), (badge_col, r), colormap[label]))
    t.setStyle(TableStyle(ts))
    return t


def build() -> Path:
    st = _styles()
    doc = BaseDocTemplate(str(OUT), pagesize=A4, topMargin=32 * mm, bottomMargin=16 * mm,
                          leftMargin=20 * mm, rightMargin=20 * mm, title="GCC-SWSS Executive Summary",
                          author=ORG)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=_header_footer)])

    s: list = []
    s.append(_callout(
        "Retention curves tell us how water is <b>stored</b>. Water balances tell us whether "
        "water is <b>saved</b>. Until the fluxes are measured, water-security claims are "
        "hypotheses, not outcomes.", st))
    s.append(Spacer(1, 6))

    s.append(Paragraph("The problem", st["h2"]))
    s.append(Paragraph(
        "Soil amendments are sold on one claim: they make soil hold more water — and from that, "
        "vendors leap to &ldquo;reduced irrigation&rdquo; and &ldquo;water security.&rdquo; That leap is not "
        "scientifically valid. <b>Holding more water is not the same as using less water.</b> A soil "
        "can store more and still lose it to evaporation, drainage, or extra plant uptake, leaving "
        "the irrigation bill unchanged. In the Gulf, where evaporative demand is extreme, this gap "
        "is the rule, not the exception.", st["body"]))

    s.append(Paragraph("What this platform does differently", st["h2"]))
    s.append(Paragraph(
        "Instead of stopping at &ldquo;how much can the soil hold?&rdquo;, GCC-SWSS runs a complete daily "
        "water balance over a full year and tracks every millimetre of rain and irrigation to its "
        "fate: plant uptake (useful), evaporation, drainage, runoff, or storage. It does this for an "
        "unamended baseline <b>and</b> each amendment, comparing them at <b>equal plant health</b> — a "
        "fair comparison, not &ldquo;healthy plant vs stressed plant.&rdquo;", st["body"]))

    s.append(Paragraph("A typical finding (real model output)", st["h2"]))
    s.append(Paragraph(
        "For a Dubai-climate landscape (sandy loam, warm-season turf), adding biochar:", st["body"]))
    s.append(_table([
        ["What the vendor measures", "What actually happens to the water budget"],
        ["Available water storage <b>+13%</b>", "Annual irrigation requirement <b>&minus;0.2%</b>"],
    ], st, [82 * mm, 83 * mm]))
    s.append(Spacer(1, 4))
    s.append(Paragraph(
        "Why almost no saving despite a real +13% storage gain? Because roughly <b>94% of all applied "
        "water</b> leaves as plant transpiration regardless of the amendment, and the soil was already "
        "meeting the plant&rsquo;s needs. The extra storage capacity goes largely unused. The platform "
        "reports this honestly instead of converting the 13% into a marketing claim.", st["body"]))

    s.append(Paragraph("Strength of evidence, made explicit", st["h2"]))
    s.append(_table([
        ["Amendment", "Evidence for water effects"],
        ["Biochar, Compost", "High"],
        ["Biosolids, Engineered biochar, Polymer", "Medium"],
        ["Lignite nanocarbon (LNC), Dust-suppression biopolymer", "Low"],
    ], st, [110 * mm, 55 * mm], badge_col=1))

    s.append(Paragraph("What it can &mdash; and cannot &mdash; say", st["h2"]))
    s.append(Paragraph(
        "<b>It can:</b> screen amendments and climates quickly; show where water goes; compare options "
        "on irrigation, drainage, water security, payback and ROI; and put honest uncertainty on every "
        "number. <b>It cannot (yet):</b> replace field measurement. The physics is verified and "
        "internally consistent &mdash; the water balance conserves mass exactly and the climate maths match "
        "the FAO international reference &mdash; but it has not yet been calibrated against a specific Gulf "
        "site. For a site-specific guarantee, the model is calibrated against field data (the planned "
        "next phase). Stating this plainly is what makes the tool credible rather than another "
        "marketing instrument.", st["body"]))

    s.append(Paragraph("Bottom line", st["h2"]))
    s.append(_callout(
        "GCC-SWSS replaces an unprovable marketing claim (&ldquo;holds more water&rdquo;) with a defensible "
        "engineering question (&ldquo;how much irrigation will I actually avoid, and what happens to the "
        "rest?&rdquo;). In the Gulf, the honest answer is often &ldquo;less than you were told&rdquo; &mdash; and knowing "
        "that before you buy is exactly the point.", st))

    doc.build(s)
    return OUT


if __name__ == "__main__":
    path = build()
    print(f"wrote {path}  ({path.stat().st_size} bytes)")

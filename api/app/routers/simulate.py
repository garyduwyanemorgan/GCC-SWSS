"""Simulation + report endpoints."""
from __future__ import annotations

import io
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.deps import current_user
from app.settings import settings
from swss import ProjectInput, SimResult, run_investigation
from swss.reporting.report import build_pdf

router = APIRouter(tags=["simulation"])


def _guard(project: ProjectInput) -> None:
    if project.monte_carlo and project.n_realisations > settings.max_monte_carlo:
        raise HTTPException(
            status_code=422,
            detail=f"n_realisations exceeds limit ({settings.max_monte_carlo}).",
        )


@router.post("/simulate", response_model=SimResult)
def simulate(project: ProjectInput, user: Optional[str] = Depends(current_user)) -> SimResult:
    _guard(project)
    try:
        return run_investigation(project)
    except RuntimeError as exc:  # e.g. rosetta-soil not installed
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/report")
def report(project: ProjectInput, user: Optional[str] = Depends(current_user)) -> StreamingResponse:
    _guard(project)
    result = run_investigation(project)
    with tempfile.TemporaryDirectory() as tmp:
        pdf_path = build_pdf(result, Path(tmp) / "swss_report.pdf")
        data = pdf_path.read_bytes()
    return StreamingResponse(
        io.BytesIO(data),
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="swss_report.pdf"'},
    )

"""GCC Soil Water Security Simulator (SWSS) - deterministic scientific engine.

Public entry point::

    from swss import run_investigation
    result = run_investigation(project_input)
"""
from __future__ import annotations

from swss.orchestrator.pipeline import run_investigation
from swss.schemas import ProjectInput, SimResult

__version__ = "0.1.0"
__all__ = ["run_investigation", "ProjectInput", "SimResult", "__version__"]

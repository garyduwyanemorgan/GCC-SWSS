"""Deterministic 3-point (min/likely/max) scenario helpers."""
from __future__ import annotations

from swss.schemas import Bound

THREE_POINT: tuple[Bound, Bound, Bound] = (Bound.MIN, Bound.LIKELY, Bound.MAX)

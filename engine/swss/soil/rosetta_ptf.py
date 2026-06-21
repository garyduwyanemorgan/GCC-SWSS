"""Rosetta pedotransfer wrapper.

Maps basic soil texture/bulk-density (optionally measured retention points) to
van Genuchten parameters using the peer-reviewed `rosetta-soil` package
(Zhang & Schaap). The package is an OPTIONAL dependency: if it is not installed
we raise a clear, actionable error rather than silently guessing.

With the default ('arith') estimate the returned columns are LINEAR:
    [theta_r, theta_s, alpha(1/cm), n, Ksat(cm/day), K0, Lpar]
so no back-transformation is applied. The model's prediction spread (stdev) is
translated into a 1-4 confidence level for the report's uncertainty layer.
"""
from __future__ import annotations

from swss.schemas import HydraulicProperties, SoilInput, VanGenuchten
from swss.soil import vg as _vg
from swss.soil.awc import available_water_capacity

_INSTALL_HINT = (
    "The 'rosetta-soil' package is required for pedotransfer estimation but is not "
    "installed. Install it with:  pip install rosetta-soil  (or `pip install "
    "swss[ptf]`). Alternatively pass soil parameters via the soil library."
)


def rosetta_available() -> bool:
    try:
        import rosetta  # noqa: F401

        return True
    except ImportError:
        return False


def _confidence_level(n_inputs: int, mean: list[float], stdev: list[float]) -> int:
    """Heuristic 1-4 confidence from model-class richness and relative spread.

    More measured inputs -> higher model class -> more confidence. A wide relative
    prediction spread (std/mean) in alpha/n/Ksat lowers confidence.
    """
    base = {3: 1, 4: 2, 5: 3, 6: 3}.get(n_inputs, 1)
    rel = []
    for i in (2, 3, 4):  # alpha, n, ksat
        if i < len(mean) and mean[i] not in (0.0, None):
            rel.append(abs(stdev[i] / mean[i]))
    spread = sum(rel) / len(rel) if rel else 1.0
    if spread > 0.5:
        base -= 1
    return max(1, min(4, base))


def estimate_hydraulics(soil: SoilInput) -> HydraulicProperties:
    """Estimate VG parameters + AWC for a soil using Rosetta. Raises if unavailable."""
    if not rosetta_available():
        raise RuntimeError(_INSTALL_HINT)

    from rosetta import rosetta  # type: ignore

    # Build the input vector in Rosetta's expected order, using as many measured
    # columns as are available (texture, then BD, then th33, then th1500).
    row: list[float] = [soil.texture.sand, soil.texture.silt, soil.texture.clay]
    row.append(soil.bulk_density)
    if soil.theta_33 is not None:
        row.append(soil.theta_33)
        if soil.theta_1500 is not None:
            row.append(soil.theta_1500)
    n_inputs = len(row)

    mean, stdev, _codes = rosetta(3, [row])
    m = [float(x) for x in mean[0]]
    s = [float(x) for x in stdev[0]]

    # Default 'arith' estimate -> columns are linear: tr, ts, alpha, n, Ksat, ...
    vg = VanGenuchten(
        theta_r=max(0.0, m[0]),
        theta_s=m[1],
        alpha=m[2],
        n=max(1.001, m[3]),
        ks=max(1e-3, m[4]),
    )
    level = _confidence_level(n_inputs, m, s)
    awc = available_water_capacity(vg)
    notes = [
        f"Van Genuchten parameters estimated by Rosetta (model class {n_inputs - 2}).",
        "No field calibration applied." if soil.theta_33 is None else
        "Constrained by measured retention point(s).",
    ]
    if awc < 0.02:
        notes.append("Very low AWC - storage-limited coarse soil typical of GCC sands.")

    return HydraulicProperties(
        vg=vg,
        theta_fc=_vg.theta_field_capacity(vg),
        theta_pwp=_vg.theta_wilting_point(vg),
        awc=awc,
        confidence_level=level,
        method="rosetta-soil pedotransfer",
        notes=notes,
    )

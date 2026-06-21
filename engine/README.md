# swss — GCC Soil Water Security Simulator engine

Deterministic, reproducible scientific core. No web concerns, no LLM in the
decision path.

> Retention curves tell us how water is stored. Water balances tell us whether
> water is saved.

## Layers

| Layer | Module | What it does |
|------|--------|--------------|
| 1 Soil hydraulics | `swss/soil` | Rosetta PTF → van Genuchten θr,θs,α,n,Ks; AWC |
| 2 Climate | `swss/climate` | FAO-56 Penman-Monteith ET0 from station normals |
| 3 Plants | `swss/plants` | Kc, FAO-56 water stress, T/E partition |
| 4 Amendments | `swss/amendments` | min/likely/max multipliers → modified curve |
| 5 Water balance | `swss/waterbalance` | daily ΔS = P + I − ET − D − R |
| — Flux attribution | `swss/flux` | "where did the water go?" ledger (mm & m³) |
| 6 Water security | `swss/security` | WSI 0–100, reliability, productivity |
| — Uncertainty | `swss/uncertainty` | 3-point + Monte Carlo P10/P50/P90 |
| — Economics | `swss/economics` | payback, NPV, ROI, $/m³ saved |
| — Reporting | `swss/reporting` | rule-based narrative + PDF |

## Quick start

```bash
python -m venv .venv && .venv/Scripts/activate     # Windows
pip install -e .[ptf,dev]                          # ptf = rosetta-soil
pytest -q                                          # 22 tests
mypy swss
```

```python
from swss import run_investigation, ProjectInput
from swss.schemas import SoilInput, SoilTexture, AmendmentInput

result = run_investigation(ProjectInput(
    soil=SoilInput(texture=SoilTexture(sand=65, silt=25, clay=10),
                   bulk_density=1.48, ec=2.0, root_zone_depth_m=0.5),
    amendments=[AmendmentInput(amendment_id="biochar")],
))
print(result.narrative)
```

The engine answers *what happened to the water?*, not *how much can the soil hold?*

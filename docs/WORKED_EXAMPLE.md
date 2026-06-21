# GCC-SWSS — Worked Example (one result traced end-to-end)

*Companion to `SCIENTIFIC_BASIS.md`. Every number below is real engine output, and
the hand-calculations reproduce the engine to the digits shown. You can regenerate
all of it (see §8). This file exists so a reviewer can follow a single result from
raw soil inputs to the final irrigation figure through every equation.*

**The case.** A Dubai-climate amenity landscape:
- Soil: sandy loam — 65% sand, 25% silt, 10% clay; bulk density 1.48 g/cm³; EC 2.0 dS/m
- Vegetation: warm-season turf (bermuda/paspalum)
- Climate: Dubai-coastal reference year
- Amendment tested: biochar (likely bound)

**The headline result we will derive:** biochar raises available water storage by
**+12.6%**, yet the modelled annual irrigation requirement changes by **−0.2%**
(essentially nil). This worked example shows *why*, step by step.

---

## Step 1 — Soil texture → van Genuchten parameters (Rosetta)

Texture + bulk density `[65, 25, 10, 1.48]` go into the Rosetta pedotransfer model.
Output (van Genuchten parameters):

| θr | θs | α (1/cm) | n | Ks (cm/day) | Confidence |
|----|----|----------|---|-------------|-----------|
| 0.0647 | 0.3783 | 0.01552 | 1.4853 | 42.88 | Level 2 (texture+BD, no measured retention) |

Confidence is **Level 2** because we supplied texture and bulk density but no
measured retention points — exactly the honest cap described in the basis document.

---

## Step 2 — van Genuchten curve → field capacity, wilting point, AWC

The van Genuchten retention equation (with m = 1 − 1/n = 1 − 1/1.4853 = **0.3267**):

```
Se(h) = [1 + (α·h)^n]^(−m)
θ(h)  = θr + (θs − θr)·Se(h)
```

**Field capacity** at h = 330 cm (−33 kPa):
```
(α·h)   = 0.01552 × 330         = 5.122
(α·h)^n = 5.122^1.4853          = 11.32
Se      = (1 + 11.32)^(−0.3267) = 0.4403
θ_FC    = 0.0647 + (0.3783−0.0647)×0.4403 = 0.2028
```

**Wilting point** at h = 15 000 cm (−1500 kPa):
```
(α·h)   = 0.01552 × 15000        = 232.8
(α·h)^n = 232.8^1.4853           = 3275
Se      = (1 + 3275)^(−0.3267)   = 0.07105
θ_PWP   = 0.0647 + (0.3136)×0.07105 = 0.0870
```

**Available Water Capacity:**
```
AWC = θ_FC − θ_PWP = 0.2028 − 0.0870 = 0.1158 cm³/cm³
```

These three hand-computed numbers (0.2028, 0.0870, 0.1158) match the engine
**exactly**. This is the storage property — and on its own it tells us nothing yet
about water saving.

---

## Step 3 — One day of reference evapotranspiration (FAO-56)

Take a representative mid-July day (day-of-year 196) at the Dubai reference station
(lat 25.25°, elev 5 m). Inputs from the climate normals:
Tmin = 30°C, Tmax = 42°C, RH = 56%, u2 = 3.4 m/s, Rs = 25.5 MJ/m²/day.

**Vapour pressures:**
```
e°(42) = 0.6108·exp(17.27·42/(42+237.3)) = 8.197 kPa
e°(30) = 0.6108·exp(17.27·30/(30+237.3)) = 4.243 kPa
es = (8.197 + 4.243)/2 = 6.221 kPa
ea = es · RH/100 = 6.221 × 0.56 = 3.484 kPa
```

**Radiation chain** (FAO-56 Eq. 21–40):
```
Extraterrestrial   Ra  = 40.07 MJ/m²/day   (from latitude + day-of-year)
Net radiation      Rn  = 16.83 MJ/m²/day   (shortwave minus longwave)
```

**Penman-Monteith assembly** (T = 36°C → slope Δ = 0.326 kPa/°C; γ = 0.0673 kPa/°C):
```
        0.408·Δ·Rn + γ·(900/(T+273))·u2·(es−ea)
ET0 = ─────────────────────────────────────────
              Δ + γ·(1 + 0.34·u2)

      0.408·0.326·16.83 + 0.0673·(900/309)·3.4·(6.221−3.484)
    = ──────────────────────────────────────────────────────
              0.326 + 0.0673·(1 + 0.34·3.4)

      2.239 + 1.824
    = ───────────── = 8.62 mm/day
         0.4711
```

A July day demands **8.62 mm** of reference evapotranspiration — that is the engine
of the whole budget. (The astronomical/radiation chain is pinned to FAO-56
Example 8, Ra = 32.2 at 20°S, 3 Sep; see basis document §4.2.)

---

## Step 4 — Crop water demand and the root-zone reservoir

Warm-season turf: Kc = 0.85, rooting depth Zr = 0.40 m, depletion fraction p = 0.50,
canopy fraction = 0.92.

```
Crop ET (this day)        ETc = Kc·ET0 = 0.85 × 8.62 = 7.33 mm
Potential transpiration   Tp  = 0.92 × 7.33 = 6.74 mm   (the useful flux)
Potential soil evaporation Ep = 0.08 × 7.33 = 0.59 mm   (mostly loss)
```

The reservoir the plant draws from (note: governed by the **crop** rooting depth):
```
TAW = AWC × Zr × 1000 = 0.1158 × 0.40 × 1000 = 46.3 mm   (total available water)
RAW = p × TAW         = 0.50 × 46.3            = 23.2 mm   (readily available)
```

Irrigation triggers when depletion reaches RAW (23.2 mm) and refills to field
capacity, keeping the plant non-stressed.

---

## Step 5 — The amendment (biochar) modifies the curve

Biochar's "likely" multipliers are applied to the baseline van Genuchten parameters,
and **AWC is recomputed from the modified curve** (never asserted separately):

| Parameter | Baseline | × biochar | Amended |
|-----------|----------|-----------|---------|
| θr | 0.0647 | ×1.10 | 0.0712 |
| θs | 0.3783 | ×1.08 | 0.4085 |
| α | 0.01552 | ×0.90 | 0.01397 |
| n | 1.4853 | ×1.00 | 1.4853 |
| Ks | 42.88 | ×1.10 (sandy) | 47.17 |
| **AWC** | 0.1158 | *recomputed* | **0.1304** |

```
AWC change = (0.1304 − 0.1158)/0.1158 = +12.6%
```

So the storage property genuinely improves by **+12.6%**. A retention-only study
would stop here and claim a water saving. We do not.

---

## Step 6 — The full-year water balance (where the water actually goes)

Running the daily balance `ΔS = P + I − ET − D − R` over all 365 days, for the
**baseline**, gives these annual totals (mm):

| P (rain) | I (irrigation) | ET | …transpiration | …evaporation | D (drainage) | R (runoff) | ΔS |
|----------|----------------|----|----------------|--------------|--------------|-----------|----|
| 93.000 | 1744.631 | 1847.942 | 1731.674 | 116.268 | 6.558 | 0.000 | −16.869 |

**Mass conservation check** (the integrity guarantee):
```
inputs − outputs − ΔS
= (93.000 + 1744.631) − (1847.942 + 6.558 + 0.000) − (−16.869)
= 1837.631 − 1854.500 + 16.869
= 0.000   (engine closure error: −4.2 × 10⁻¹³ mm)
```
Water is neither created nor destroyed. Every result rests on this.

Now the **biochar** run, same climate, same plant:

| Metric | Baseline | Biochar | Change |
|--------|----------|---------|--------|
| Available water storage (AWC) | 0.1158 | 0.1304 | **+12.6%** |
| Annual irrigation requirement | 1744.6 mm | 1741.6 mm | **−0.2%** |
| Annual ET | 1847.9 mm | ~1850 mm | ~0 |
| Deep drainage | 6.6 mm | ~10 mm | small |
| Plant performance (non-stressed days) | 100% | 100% | equal |

---

## Step 7 — The conclusion the model forces you to see

The Flux Attribution Engine partitions the baseline's 1837.6 mm of applied water:

| Fate | mm/yr | m³/yr (per ha) | % of input |
|------|-------|----------------|-----------|
| Transpiration (plant uptake — useful) | 1732 | 17 317 | **94%** |
| Soil evaporation (loss) | 116 | 1 163 | 6% |
| Deep drainage (loss) | 7 | 66 | 0% |
| Runoff (loss) | 0 | 0 | 0% |
| Change in storage | −17 | −169 | −1% |

**Why +12.6% storage produced −0.2% irrigation:** 94% of all water applied is
transpired by the turf to meet an extreme evaporative demand (≈1850 mm/yr ET).
Deep drainage — the only loss an amendment could meaningfully recover here — is just
**7 mm/yr**, because the baseline sandy loam already retains the scarce rainfall.
There is almost nothing for the extra storage capacity to save. The amendment's
+12.6% storage is real but **largely unused**: the plant's demand, not the soil's
storage, governs the irrigation bill in this climate.

This is the platform's entire thesis, demonstrated on one case with conserved mass
and cited physics:

> **The soil can hold 12.6% more water, but you will not irrigate 12.6% less —
> because the water was never going to be saved there in the first place.**

A different soil (e.g. a leaky pure sand with high drainage) or a leaching-driven
regime would show a different, larger saving — and the same engine would quantify
it. The point is that the answer is *computed from the fluxes*, not assumed from the
retention curve.

---

## Step 8 — Reproduce every number yourself

```bash
cd engine
python -m venv .venv && .venv/Scripts/activate     # Windows
pip install -e .[ptf]
python - <<'PY'
from swss import run_investigation, ProjectInput
from swss.schemas import SoilInput, SoilTexture, AmendmentInput, PlantInput
r = run_investigation(ProjectInput(
    soil=SoilInput(texture=SoilTexture(sand=65, silt=25, clay=10),
                   bulk_density=1.48, ec=2.0, root_zone_depth_m=0.5),
    plant=PlantInput(crop_id="turf_warm"),
    amendments=[AmendmentInput(amendment_id="biochar")],
))
b, s = r.baseline, r.scenarios[0]
print("baseline AWC", round(b.hydraulics.awc, 4), "irrigation", round(b.balance.irrigation_mm))
print("biochar  AWC", round(s.hydraulics.awc, 4), "irrigation", round(s.balance.irrigation_mm))
print("closure", b.balance.closure_error_mm)
for line in r.narrative: print("-", line)
PY
```

The numbers in this document are the output of exactly that engine
(`engine/swss`, v0.1.0), and the golden test `engine/tests/test_pipeline.py`
asserts the central finding (storage gain ≫ irrigation reduction) automatically.

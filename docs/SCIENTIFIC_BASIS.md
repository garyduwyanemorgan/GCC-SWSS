# GCC-SWSS — Scientific Basis & Defensibility Document

**Purpose.** This document explains *every* scientific decision inside the GCC Soil
Water Security Simulator (SWSS) engine so that each number it produces can be
defended, challenged, and traced back to a governing equation, a cited source, or
an explicitly-stated assumption. It is written to be self-contained: you can load
it into a Claude chat (or hand it to a reviewer) and interrogate any detail.

**How to use it.** Each engine output maps to a section here. Section 16
(Traceability) links every result to the exact code file and the test that
checks it. Section 15 (Anticipated Challenges) pre-answers the hard questions a
hydrologist, agronomist, or opposing expert will ask.

**The single most important thing to understand first:** this platform is
deliberately conservative. It is built to *avoid* overclaiming. Its core position
is that increased water *retention* is not the same as water *saving*, and it will
frequently report that an amendment produces little or no irrigation saving in GCC
conditions. That is not a weakness of the model — it is the finding, and it is the
scientifically defensible position.

---

## 1. Scientific philosophy — what the platform does and does not claim

### 1.1 The thesis
> Retention curves tell us how water is *stored*. Water balances tell us whether
> water is *saved*. Until the fluxes are measured, claims of water security remain
> hypotheses rather than demonstrated outcomes.

A soil water-retention curve (θ–h relationship) is a **storage** property: it says
how much water the soil holds at a given matric potential. It says nothing about
what *happens* to that water over time. Whether water is "saved" is a property of
the complete water **balance**:

```
ΔS = P + I − ET − D − R
```

where ΔS = change in root-zone storage, P = precipitation, I = irrigation,
ET = evapotranspiration, D = deep drainage, R = runoff (all as depths, mm).

An amendment can raise storage (ΔS capacity) yet produce **no** reduction in
irrigation if the extra stored water is simply transpired, evaporated, or
eventually drained. The platform's job is to compute the *fluxes*, not assert the
*outcome*.

### 1.2 What the platform claims
- A physically-consistent, mass-conserving daily water balance for a single
  root-zone reservoir under GCC climate forcing.
- An attribution of where applied water goes (the Flux Attribution Engine).
- A *comparison* of amendment vs unamended baseline **at equal plant performance**.
- Uncertainty on every headline number (3-point and Monte Carlo).

### 1.3 What the platform explicitly does NOT claim
- It does **not** claim to replace field measurement (lysimeters, sap flow, eddy
  covariance, neutron probes). It is a screening and decision-support model.
- It does **not** assert that more retention = more saving. It tests it.
- It does **not** model depth-resolved unsaturated flow (no full Richards-equation
  solver — see §7.1 and §14).
- It does **not** model solute transport / osmotic stress (salinity is heuristic
  only — see §10.4 and §14).
- It does **not** make deterministic single-value claims; every result carries a
  confidence level and/or uncertainty band.

### 1.4 The "Rules" enforced in code
1. A retention curve alone cannot demonstrate water savings.
2. Additional storage does not automatically reduce irrigation demand.
3. Water savings exist only if ET, drainage, runoff, or irrigation requirement
   falls **without reducing plant performance**.
4. All outputs include uncertainty.
5. No deterministic claims are permitted.

These are not slogans — §15.1 shows how the model *structurally* enforces Rule 3
by comparing scenarios only at equal (non-stressed) plant performance.

---

## 2. System overview & data flow

```
Soil texture/BD ─▶ [L1 Rosetta PTF] ─▶ van Genuchten θr,θs,α,n,Ks ─▶ AWC, FC, PWP
Climate normals ─▶ [L2 FAO-56 PM]  ─▶ daily ET0
Crop selection  ─▶ [L3 Kc, stress] ─▶ potential T, potential E, stress thresholds
Amendment       ─▶ [L4 multipliers]─▶ modified θr,θs,α,n,Ks ─▶ modified AWC/FC/PWP
                         │
                         ▼
          [L5 daily water balance: ΔS = P + I − ET − D − R]
                         │
        ┌────────────────┼─────────────────┐
        ▼                ▼                  ▼
  [Flux Attribution] [L6 Water Security] [Economics]
        │
        ▼
 [Uncertainty: 3-point + Monte Carlo]  ─▶ [rule-based narrative + PDF]
```

The model runs at **daily resolution for one representative year (365 days)** for a
baseline (no amendment) and for each selected amendment, then compares them.

---

## 3. Layer 1 — Soil hydraulic characterisation

### 3.1 The van Genuchten (1980) retention model
Water content as a function of suction head `h` (positive cm; h = 0 at saturation):

```
Se(h) = [ 1 + (α·|h|)^n ]^(−m),     m = 1 − 1/n          (van Genuchten 1980)
θ(h)  = θr + (θs − θr)·Se(h)
```

- θr = residual water content (cm³/cm³)
- θs = saturated water content (≈ porosity)
- α  = inverse air-entry scale (1/cm)
- n  = pore-size distribution shape (dimensionless, > 1)
- m  = 1 − 1/n is the **Mualem constraint** (we do not fit m independently)

The inverse, suction for a given θ, is solved analytically:
```
h(θ) = (1/α)·( Se^(−1/m) − 1 )^(1/n),   Se = (θ − θr)/(θs − θr)
```

**Code:** `engine/swss/soil/vg.py`. **Test:** `test_vg.py` checks θ is bounded in
[θr, θs], monotonically non-increasing with suction, exact at saturation, and that
h(θ)→θ(h) round-trips to 1e-6.

### 3.2 Mualem (1976) unsaturated hydraulic conductivity
```
K(Se) = Ks · Se^L · [ 1 − (1 − Se^(1/m))^m ]²,    L = 0.5     (Mualem 1976)
```
L = 0.5 is Mualem's pore-connectivity value, standard in the VG–Mualem model. K is
exact (= Ks) at saturation and 0 at residual. **Note:** the current daily balance
(§7) uses Ks for the infiltration-capacity / drainage logic; the full K(θ) curve is
implemented and available but the bucket scheme does not integrate Richards' flux
(see §14, limitation L1).

### 3.3 Field capacity, wilting point, available water
- Field capacity: θ_FC = θ(h = 330 cm) ≈ −33 kPa (−1/3 bar).
- Permanent wilting point: θ_PWP = θ(h = 15 000 cm) ≈ −1500 kPa (−15 bar).
- **Available Water Capacity:** AWC = θ_FC − θ_PWP (cm³/cm³).
- Root-zone available depth: AWC × Zr × 1000 (mm), Zr = rooting depth (m).

These are the standard agronomic definitions (FAO-56 §; Allen et al. 1998). −33 kPa
for field capacity is conventional for medium soils; some authors use −10 kPa for
sands. We use −33 kPa uniformly and disclose it (a reviewer may argue −10 kPa for
pure sand — see §15.4). **Code:** `vg.py` constants `H_FIELD_CAPACITY`,
`H_WILTING_POINT`; `soil/awc.py`.

### 3.4 Pedotransfer: Rosetta (Zhang & Schaap 2017)
We do not invent van Genuchten parameters. Texture (sand/silt/clay %), bulk
density, and optionally measured retention points (θ at −33 and −1500 kPa) are
passed to the peer-reviewed **Rosetta** pedotransfer model (`rosetta-soil` v0.3.2,
Zhang & Schaap 2017, *J. Hydrology*; the neural-network successor to Schaap et al.
2001). It returns θr, θs, α, n, Ks.

- The **model class** rises with input richness: 3 inputs (texture only) → 4
  (+BD) → 5 (+θ33) → 6 (+θ33,θ1500). More inputs = more constrained = higher
  confidence.
- With the default `arith` estimate the package returns **linear** parameter
  values (not log10) — the wrapper uses them directly.
- The model also returns a prediction standard deviation per parameter, which we
  collapse into a **confidence level 1–4** (input richness, reduced if the relative
  spread of α/n/Ks is wide). Level 4 is reserved for field-calibrated inputs.

**Code:** `soil/rosetta_ptf.py`. If `rosetta-soil` is not installed the engine
raises a clear, actionable error (it never silently guesses). A literature soil
library (`soil/library.py`, confidence level 2) is the documented fallback.

**Defensibility:** Rosetta is the most widely used and cited PTF in vadose-zone
hydrology; using it (rather than ad-hoc values) is the standard defensible choice
when site retention curves are unavailable. Its limitation is that it is trained on
mostly temperate soils — GCC calcareous/sabkha materials are out-of-sample, which
is exactly why every library soil is flagged `requires_site_calibration` and the
confidence level is capped without measured points (§15.6).

---

## 4. Layer 2 — Climate engine (FAO-56 Penman-Monteith)

### 4.1 Reference evapotranspiration
Daily reference ET0 (grass reference, mm/day) by the FAO-56 Penman-Monteith
equation (Allen, Pereira, Raes, Smith 1998, *FAO Irrigation & Drainage Paper 56*,
Eq. 6):

```
        0.408·Δ·(Rn − G) + γ·(900/(T+273))·u2·(es − ea)
ET0 = ─────────────────────────────────────────────────
                Δ + γ·(1 + 0.34·u2)
```

| Term | Meaning | FAO-56 eq. | Code |
|------|---------|-----------|------|
| T | mean daily air temp = (Tmax+Tmin)/2 (°C) | — | penman_monteith.py |
| u2 | wind speed at 2 m (m/s) | — | input |
| Δ | slope of saturation vapour-pressure curve (kPa/°C) | 13 | `slope_vapour_pressure` |
| γ | psychrometric constant (kPa/°C) | 8 | `psychrometric_constant` |
| P | atmospheric pressure from elevation (kPa) | 7 | `atmospheric_pressure` |
| es | saturation vapour pressure = (e°(Tmax)+e°(Tmin))/2 | 11,12 | `saturation_vapour_pressure` |
| ea | actual vapour pressure | — | from RH (see 4.3) |
| Rn | net radiation (MJ/m²/day) | 38–40 | `net_radiation` |
| G | soil heat flux, taken = 0 for daily step | 42 | — |

### 4.2 The radiation chain (fully implemented, not approximated)
- Extraterrestrial radiation Ra (Eq. 21–25) from latitude φ, day-of-year, inverse
  Earth–Sun distance dr, solar declination δ, sunset hour angle ωs.
- Clear-sky radiation Rso = (0.75 + 2e-5·z)·Ra (Eq. 37).
- Net shortwave Rns = (1 − α)·Rs, albedo α = 0.23 (Eq. 38).
- Net longwave Rnl (Eq. 39): Stefan-Boltzmann with humidity and cloudiness terms,
  σ = 4.903e-9 MJ K⁻⁴ m⁻² day⁻¹.
- Rn = Rns − Rnl (Eq. 40).

**Validation anchor:** `extraterrestrial_radiation(−20°, DOY 246)` returns
**32.2 MJ/m²/day**, matching FAO-56 **Example 8** exactly (test asserts ±0.2).
This pins the entire astronomical/radiation chain to the reference text.
**Code:** `climate/penman_monteith.py`. **Test:** `test_climate.py`.

### 4.3 The one approximation to disclose
Actual vapour pressure is computed as `ea = es · RH_mean/100`. The most rigorous
FAO-56 form uses RHmax with e°(Tmin) and RHmin with e°(Tmax); we use mean RH
because the GCC climate normals provide mean RH only. The effect is a small bias in
the vapour-pressure deficit. This is a known, bounded simplification (§15.3), and
the framework accepts station data with full RHmax/RHmin when available.

### 4.4 Synthetic weather year
When no station time series is supplied, a deterministic 365-day series is built
from monthly normals (a Dubai-coastal reference is shipped: T, RH, wind, solar
radiation, rainfall). ET0 is **computed**, not stored, so the calculation stays
auditable. Rainfall (sparse in the GCC) is concentrated into two events/month to
preserve realistic wetting/drying cycles rather than smearing it (which would
understate drainage and runoff). **Code:** `climate/weather.py`.
**GCC sanity range:** the test asserts daily ET0 ∈ [2, 16] mm/day with summer > winter.

---

## 5. Layer 3 — Vegetation response

### 5.1 Crop coefficient and ET partition
Crop evapotranspiration under standard (non-stressed) conditions:
```
ETc = Kc · ET0                                   (FAO-56 single crop coefficient)
```
We use a representative **mid-season Kc** for established GCC landscape vegetation
(turf, date palm, trees, shrubs, native xeric, vegetable). ETc is split into
**potential transpiration** and **potential soil evaporation** using a per-category
**canopy fraction** fc:
```
Tp = fc · ETc        Ep = (1 − fc) · ETc
```
(turf fc≈0.92 → mostly transpiration; trees/shrubs lower → more bare-soil
evaporation). This is a pragmatic partition, *not* the full FAO-56 dual crop
coefficient (Kcb + Ke) — disclosed as limitation L4. **Code:** `plants/crop_coefficients.py`.

### 5.2 Water-stress coefficient (FAO-56 Eq. 84)
Transpiration proceeds at potential until root-zone depletion Dr exceeds the
**Readily Available Water**; then it declines linearly to zero at wilting:
```
RAW = p · TAW
Ks  = (TAW − Dr) / (TAW − RAW)   for Dr > RAW,   else Ks = 1     (FAO-56 Eq. 84)
```
- TAW = total available water in the root zone (mm) = AWC × Zr × 1000
- p = depletion fraction (crop-specific; turf ≈ 0.4–0.5, date palm ≈ 0.65, native ≈ 0.75)
- Actual transpiration Ta = Ks · Tp.

**Code:** `plants/stress.py`, `plants/root_uptake.py`. This Ks is *the* mechanism by
which "more stored water" may or may not reduce stress — and therefore whether it
changes water use (§15.1).

### 5.3 Soil evaporation
Actual soil evaporation is reduced by surface dryness, proxied by relative
root-zone wetness: `Ea = (1 − Dr/TAW) · Ep`. This is a single-store proxy, not the
two-stage Ritchie (1972) energy/falling-rate model (limitation L5). It is
deliberately simple and is the term that quietly consumes "extra retained water" in
hot arid soils — which the Flux Attribution Engine then makes visible.

---

## 6. Layer 4 — Amendment response

### 6.1 Multiplicative effect model
Each amendment modifies the **baseline** van Genuchten parameters by **multipliers**
drawn from a (min, likely, max) range:
```
θs_amended = θs_baseline × m(θs)     (and likewise θr, α, n, Ks)
```
Ranges are stored in `engine/swss/data/amendment_library.yaml` (cleaned, valid-YAML
version of the project's authored library). Ks multipliers are **texture-specific**
(separate sandy vs clayey factors) because amendment effects on conductivity differ
sharply by matrix. **Code:** `amendments/engine.py`.

### 6.2 The critical modelling choice — AWC is RECOMPUTED, not asserted
After applying the multipliers, available water is **recomputed from the modified
retention curve** (θ_FC and θ_PWP re-derived from the new θr,θs,α,n). The library
*also* contains an AWC multiplier, but we deliberately **do not** apply it on top —
that would double-count and let the model assert a storage benefit the physics has
not produced. This is central to defensibility: the storage change is an *emergent*
property of the modified curve, consistent with §1.

### 6.3 Strength of evidence (carried into every report)
Each amendment carries a confidence rating that propagates to the output and caps
the reported confidence level:

| Amendment | Hydraulic evidence | Confidence cap |
|-----------|-------------------|----------------|
| Biochar | High (largest peer-reviewed base; strongest in coarse soils) | 4 |
| Compost | High | 4 |
| Biosolids | Medium | 3 |
| Engineered biochar | Medium | 3 |
| Water-absorbing polymer | Medium (degrades over time) | 3 |
| Lignite nanocarbon (LNC) | Low (limited peer-reviewed hydraulic data) | 2 |
| Dust-suppression biopolymer | Low (may reduce infiltration) | 2 |

The literature genuinely supports biochar/compost effects on hydraulic properties
far more strongly than LNC or dust-suppression products, and the platform says so.
Warnings (e.g. "polymer performance degrades over time", "biopolymer may reduce
infiltration") are surfaced in the narrative. **Limitation L7:** amendment
*longevity* is not time-integrated — results represent the amended state, not its
decay.

---

## 7. Layer 5 — Daily water balance

### 7.1 The model
A **single-layer root-zone reservoir** ("bucket") integrated daily. **Storage is the
state variable**, tracked as depletion Dr below field capacity; P, I, ET, drainage,
runoff are accounting fluxes. This is the FAO-56 soil-water-balance approach (Allen
et al. 1998, Ch. 8), not a depth-resolved Richards solver (limitation L1). For the
high-conductivity sandy soils that dominate the GCC, a single well-mixed root-zone
store is a reasonable and widely-used screening approximation.

### 7.2 Daily sequence (order matters and is explicit)
For each day:
1. **Rainfall partition** → infiltration vs infiltration-excess runoff:
   `R = max(0, P − Ks_mm)`, where Ks_mm = Ks(cm/day)×10. For GCC sands Ks is
   hundreds–thousands of mm/day, so R ≈ 0 unless a surface-sealing biopolymer cuts
   Ks. (Hortonian/infiltration-excess runoff; **code:** `waterbalance/runoff.py`.)
2. **Infiltration into the store**; any water above field capacity becomes **deep
   drainage** the same day (free-drainage lower boundary, appropriate for sands;
   **code:** `waterbalance/drainage.py`, limitation L2).
3. **Demand-scheduled irrigation:** if depletion ≥ RAW, irrigate exactly enough to
   refill to field capacity. Irrigation is therefore an **output (a requirement)**,
   computed by the model — this is the number that actually decides water saving.
4. **Evapotranspiration:** Ta and Ea from §5, limited so total ET cannot exceed
   water available above wilting point.
5. **Update storage**, record all fluxes.

**Code:** `waterbalance/water_balance.py`.

### 7.3 Mass conservation (the integrity check)
Every run computes a **closure error**:
```
closure = (ΣP + ΣI) − (ΣET + ΣD + ΣR) − ΔS_total
```
It is asserted to be **< 1e-6 mm** in tests on every scenario. If the balance did
not close, the simulation would be physically invalid; this guard is what lets you
state the results conserve mass exactly. **Test:** `test_water_balance.py::test_balance_closes`.

### 7.4 Why irrigation is scheduled to avoid stress (equal-performance comparison)
Irrigation refills before the plant is stressed, so in soils where TAW exceeds the
daily ET demand the plant transpires at its potential rate in **both** baseline and
amended runs. That makes the comparison apples-to-apples: equal yield/performance,
and any difference in irrigation comes from drainage and rainfall-capture, not from
one scenario quietly under-watering the plant. This *is* Rule 3 enforced
structurally (§15.1).

---

## 8. Flux Attribution Engine (the signature feature)

Of the total water applied over the year (ΣP + ΣI), the engine reports the fate:
```
total input = to_storage + to_transpiration + to_evaporation + to_drainage + to_runoff
```
in both **mm and m³** (m³ = mm/1000 × area). Because the ledger is constructed from
the closed balance, it **sums to total input by construction** — a headline storage
gain therefore *cannot* hide an offsetting loss to evaporation or drainage; the
ledger forces it into view. (ΔStorage may be negative, meaning storage acted as a
source; this is reported honestly.) **Code:** `flux/water_fate.py`.
**Test:** `test_water_balance.py::test_flux_ledger_sums_to_input`.

This operationalises the thesis: it turns "+22% storage" into
"…of which X% went to transpiration, Y% to evaporation, Z% to drainage, so
irrigation fell only N%."

---

## 9. Layer 6 — Water Security Index

A composite 0–100 score:
```
WSI = 0.25·StorageReliability + 0.25·IrrigationReduction
    + 0.20·DrainageReduction  + 0.15·SalinityResistance
    + 0.15·PlantPerformance
```
- **StorageReliability** = fraction of days the root zone was non-stressed (Ks ≥ ~1).
- **IrrigationReduction** = relative reduction in annual irrigation **vs baseline**
  (0 for the baseline itself).
- **DrainageReduction** = relative reduction in deep drainage vs baseline.
- **SalinityResistance** = heuristic from soil EC (1.0 at EC≈0, 0.0 at EC≥8 dS/m;
  0.6 if unknown). **Heuristic only** — see L6.
- **PlantPerformance** = non-stressed-day fraction (yield proxy).

The weights are a **transparent management-priority choice, not a measured law** —
they are disclosed and editable. The two "reduction" components are scored *only*
relative to baseline, so an amendment cannot score on them unless it demonstrably
reduces those fluxes. **Code:** `security/wsi.py`. A reviewer may legitimately
contest the weights (§15.7); they are configuration, and the underlying fluxes
(which are physical) are reported separately and unweighted.

---

## 10. Uncertainty

### 10.1 Three-point (deterministic) scenarios
Every amendment can be run at its **min / likely / max** multiplier bound, giving a
conservative–central–optimistic envelope.

### 10.2 Monte Carlo
1,000 (configurable) realisations sample each amendment multiplier from a
**triangular(min, likely, max)** distribution, re-run the full water balance, and
report **P10 / P50 / P90** for irrigation requirement, drainage, AWC, and
irrigation-saving %. Triangular is chosen because the library specifies exactly
three points (min/likely/max) and the triangular is the standard maximum-information
distribution for that case. Seeded for reproducibility (forensic requirement).
**Code:** `uncertainty/monte_carlo.py`. **Test:** `test_monte_carlo.py` asserts
P10 ≤ P50 ≤ P90 and seed-reproducibility.

### 10.3 Confidence levels
Every hydraulic property carries a 1–4 confidence level (§3.4) reflecting how it was
derived (pedotransfer vs measured vs calibrated). No result is presented as a bare
deterministic value.

### 10.4 What uncertainty is NOT captured
Parameter correlation in sampling is not modelled (multipliers sampled
independently); climate inter-annual variability is not propagated (single
representative year); Rosetta's own parameter covariance is summarised, not fully
propagated. These are honest scope limits (L8).

---

## 11. Economics

Savings derive **only** from a reduction in the modelled irrigation requirement
(never from a retention figure):
```
water_saved_m3 = (I_baseline − I_amended)/1000 × area
annual_saving  = water_saved_m3 × water_cost_per_m3
payback        = total_amendment_cost / annual_saving        (if saving > 0)
NPV            = −cost + Σ_{t=1..H} saving/(1+r)^t
ROI%           = 100·(saving·H − cost)/cost
```
A **negative** saving (amendment increases irrigation, e.g. by prolonging
evaporation) is reported honestly — payback/ROI return null rather than a
misleading number. **Code:** `economics/economics.py`.

---

## 12. Parameter provenance

| Library | What it holds | Source / status |
|---------|---------------|-----------------|
| `soil_library.yaml` | VG params for GCC Sand, Calcareous Sand, Sabkha, Sandy Loam, Urban Fill | **Literature/typical**, every entry flagged `requires_site_calibration`. Production path is Rosetta on borehole data. |
| `crop_library.yaml` | Kc, rooting depth, depletion fraction p | FAO-56 typical values for the crop categories. |
| `amendment_library.yaml` | min/likely/max multipliers + evidence rating | Authored from the amendment literature; biochar/compost High, LNC/biopolymer Low. |
| `climate_library.yaml` | Monthly normals (Dubai-coastal reference) | Representative coastal-Gulf normals; replace with station data for a real site. |

**Honesty statement:** the shipped soil and climate libraries are *defaults for
demonstration and screening*. For a defensible site result you supply (a) borehole
texture + bulk density (ideally + measured θ33/θ1500) for Rosetta, and (b) local
station weather. The engine confidence level reflects which you used.

---

## 13. Verification performed — and what is NOT validated

### 13.1 Performed (automated, 22 tests, mypy-clean)
- **Retention curve**: bounded, monotonic, exact at saturation, invertible (1e-6).
- **Conductivity**: K = Ks at saturation, 0 at residual.
- **FAO-56 radiation**: Ra = 32.2 MJ/m²/day vs FAO-56 Example 8 (±0.2).
- **ET0 regime**: daily ET0 ∈ [2,16] mm/day, summer > winter (GCC sanity).
- **Mass conservation**: balance closes < 1e-6 mm every run.
- **Flux ledger**: sums to total input < 1e-6 mm.
- **Amendment multipliers**: reproduce library min/likely/max exactly; θr < θs invariant; evidence caps confidence.
- **Monte Carlo**: P10 ≤ P50 ≤ P90; reproducible under seed.
- **Golden case**: amendment raises AWC > 5% while irrigation falls < half that —
  i.e. retention ≠ proportional saving; transpiration equal (equal performance);
  reliability > 0.99.

### 13.2 NOT yet validated (state this plainly to reviewers)
- **No calibration/validation against field data** (lysimeter ET, neutron-probe
  storage, sap-flow transpiration, drainage lysimeters, or measured irrigation
  records). The model is internally consistent and theory-faithful, but its
  *accuracy* against a specific GCC site is unquantified until calibrated.
- No multi-year or extreme-event validation.
- Rosetta is applied to GCC calcareous/sabkha soils that are out of its training
  distribution.

**This is the single most important caveat.** The correct claim is: *"a
physically-consistent, theory-faithful screening model whose structural logic is
verified, pending field calibration for site-specific accuracy."* Anyone who needs
a hard numeric guarantee for a specific site needs the calibration step (PEST++/pyEMU
against field observations — the intended Phase-5 workflow).

---

## 14. Assumptions & limitations (each with its defense)

| # | Assumption / limitation | Why it is acceptable | When it could mislead |
|---|--------------------------|----------------------|-----------------------|
| L1 | Single-layer bucket, not depth-resolved Richards | Standard FAO-56 screening method; root zone well-mixed; high-K sands homogenise fast | Layered profiles, perched water, strong capillary gradients |
| L2 | Free-drainage lower boundary | Correct for high-conductivity GCC sands; conservative | Fine soils, shallow water table, capillary rise |
| L3 | Daily timestep | Standard for water-balance screening | Sub-daily irrigation on very low-storage sand → apparent chronic stress (see §15.5) |
| L4 | Single mid-season Kc, simple T/E split | Adequate for established perennial landscape | Annual crops with strong growth-stage Kc curves |
| L5 | Evaporation as wetness-proxy, not two-stage Ritchie | Simple, transparent, captures the key loss | Frequent light wetting where stage-1 evaporation dominates |
| L6 | Salinity is a heuristic EC score | Honest placeholder; flagged future module | Saline soils where osmotic stress materially cuts uptake |
| L7 | Amendment longevity not time-integrated | Reports the amended state; ranges bracket effect | Multi-year claims (polymer decay, biochar ageing) |
| L8 | Independent multiplier sampling, single climate year | Reasonable first-order uncertainty | Strongly correlated parameters; inter-annual climate risk |
| L9 | Mean-RH vapour pressure (§4.3) | Small bounded VPD bias; data-limited | Sites with large diurnal humidity swings & full RH data |
| L10 | Library soils/climate are defaults | Clearly flagged; replaced by site data | Using defaults as if site-specific |

None of these undermine the **core message** (retention ≠ saving), because that
conclusion is driven by mass conservation and the dominance of evaporative demand —
both robust to these simplifications.

---

## 15. Anticipated challenges & how to answer them

**15.1 "You're just assuming amendments don't help."**
No — the model *computes* it. The water balance closes exactly; irrigation is an
emergent requirement scheduled to keep the plant non-stressed in both scenarios.
If an amendment reduces drainage or captures more rainfall, irrigation falls and the
model shows it. The finding that savings are often small is a *consequence* of
ET dominating the GCC balance, not an input.

**15.2 "Your AWC increase doesn't match the storage benefit the vendor claims."**
We recompute AWC from the modified van Genuchten curve and refuse to apply a
separate AWC multiplier on top (§6.2). Vendor "storage" claims are usually retention
figures; we report storage *and* its fate. Ask the vendor for the flux data.

**15.3 "Your ET0 is wrong because you used mean RH."**
The radiation/astronomical chain is pinned to FAO-56 Example 8 (Ra = 32.2). The only
approximation is ea from mean RH (§4.3), a small VPD effect; supply RHmax/RHmin and
the engine uses the rigorous form.

**15.4 "Field capacity at −33 kPa is wrong for pure sand."**
Defensible point. −33 kPa is the conventional value; −10 kPa is sometimes used for
sands. It is a single disclosed constant (`H_FIELD_CAPACITY`) and can be set per
soil. It shifts absolute AWC but not the *comparative* conclusion.

**15.5 "Turf on pure sand shows chronic stress / weird irrigation."**
Correct and physical: pure dune sand holds almost no plant-available water
(AWC ≈ 0.003), so daily irrigation cannot prevent within-day stress — real golf
courses irrigate sub-daily, which a daily model cannot resolve (L3). Use a realistic
landscape soil (sandy loam) or sub-daily forcing for those cases; the model is
behaving correctly given the input.

**15.6 "Rosetta wasn't trained on Gulf soils."**
True, and disclosed (§13.2). That is why every default soil is flagged for site
calibration and confidence is capped without measured retention points. Provide
measured θ33/θ1500 to raise the model class and confidence.

**15.7 "Your WSI weights are arbitrary."**
They are an explicit, editable management-priority choice (§9), not a physical law.
The physical fluxes are reported separately and unweighted; the WSI is a convenience
summary, and reviewers can re-weight it.

**15.8 "Where's the validation?"**
Stated plainly (§13.2): structural logic is verified; site accuracy requires
calibration against field observations. We do not claim otherwise. That honesty is
the platform's strongest defensive position.

---

## 16. Traceability — output → equation → code → test

| Output | Governing basis | Code | Test |
|--------|-----------------|------|------|
| θr,θs,α,n,Ks | Rosetta PTF | `soil/rosetta_ptf.py` | (smoke via pipeline) |
| θ(h), AWC, FC, PWP | van Genuchten 1980 | `soil/vg.py`, `soil/awc.py` | `test_vg.py` |
| K(θ) | Mualem 1976 | `soil/vg.py` | `test_vg.py` |
| ET0 | FAO-56 Eq. 6 + radiation chain | `climate/penman_monteith.py` | `test_climate.py` |
| Daily weather/ET0 series | FAO-56 from normals | `climate/weather.py` | `test_climate.py` |
| Kc, T/E split | FAO-56 single Kc | `plants/crop_coefficients.py` | (pipeline) |
| Stress Ks | FAO-56 Eq. 84 | `plants/stress.py` | (pipeline) |
| Amended θr,θs,α,n,Ks | multiplicative library | `amendments/engine.py` | `test_amendments.py` |
| Daily ΔS, irrigation, drainage, runoff | bucket balance | `waterbalance/water_balance.py` | `test_water_balance.py` |
| Mass closure | ΣP+ΣI−ΣET−ΣD−ΣR−ΔS≈0 | `waterbalance/water_balance.py` | `test_water_balance.py` |
| Flux ledger (mm, m³) | closed-balance attribution | `flux/water_fate.py` | `test_water_balance.py` |
| WSI + components | weighted composite | `security/wsi.py` | (pipeline) |
| P10/P50/P90 | triangular Monte Carlo | `uncertainty/monte_carlo.py` | `test_monte_carlo.py` |
| payback/NPV/ROI | discounted cash flow | `economics/economics.py` | (pipeline) |
| narrative | rule-based from fluxes | `reporting/narrative.py` | `test_pipeline.py` |
| retention ≠ saving | golden end-to-end | (orchestrator) | `test_pipeline.py` |

Run it yourself: `cd engine && .venv/Scripts/python.exe -m pytest -q` (22 tests) and
`mypy swss` (clean).

---

## 17. References

- Allen, R.G., Pereira, L.S., Raes, D., Smith, M. (1998). *Crop evapotranspiration —
  Guidelines for computing crop water requirements.* FAO Irrigation & Drainage Paper 56.
- van Genuchten, M.Th. (1980). A closed-form equation for predicting the hydraulic
  conductivity of unsaturated soils. *Soil Sci. Soc. Am. J.* 44(5), 892–898.
- Mualem, Y. (1976). A new model for predicting the hydraulic conductivity of
  unsaturated porous media. *Water Resources Research* 12(3), 513–522.
- Zhang, Y., Schaap, M.G. (2017). Weighted recalibration of the Rosetta pedotransfer
  model (Rosetta3). *Journal of Hydrology* 547, 39–53. (and Schaap, Leij, van
  Genuchten 2001, the original Rosetta.)
- Ritchie, J.T. (1972). Model for predicting evaporation from a row crop with
  incomplete cover. *Water Resources Research* 8(5), 1204–1213.
- Carsel, R.F., Parrish, R.S. (1988). Developing joint probability distributions of
  soil water retention characteristics. *Water Resources Research* 24(5), 755–769.

---

*Scope note:* this document describes the engine as implemented at the time of
writing (engine v0.1.0). The salinity/solute-transport module and PEST++/pyEMU field
calibration are designed but not yet built; treat any salinity-dependent number as a
heuristic until that module lands.

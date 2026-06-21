# GCC-SWSS — Executive Summary

*A two-page, non-technical overview for decision-makers. The full scientific
justification is in `SCIENTIFIC_BASIS.md`; a number-by-number worked example is in
`WORKED_EXAMPLE.md`.*

---

## The problem

Soil amendments (biochar, compost, polymers, and others) are almost always sold on
a single claim: **they make soil hold more water.** From that, vendors leap to
"reduced irrigation" and "improved water security."

That leap is not scientifically valid. **Holding more water is not the same as
using less water.** A soil can store more and still lose it all to evaporation,
drainage, or extra plant uptake — leaving the irrigation bill unchanged. In the
Gulf, where evaporative demand is extreme, this gap is the rule, not the exception.

## What this platform does differently

Instead of stopping at "how much water can the soil hold?", GCC-SWSS answers the
question that actually matters for a water budget:

> **Where did the water go?**

It runs a complete daily water balance over a full year and tracks every millimetre
of rain and irrigation to its fate: plant uptake (useful), soil evaporation (loss),
deep drainage (loss), runoff (loss), or storage. It does this for an unamended
baseline **and** for each amendment, then compares them — *at equal plant health*,
so it is a fair comparison and not "healthy plant vs stressed plant."

The guiding principle, enforced in the software:

> Retention curves tell us how water is **stored**. Water balances tell us whether
> water is **saved**. Until the fluxes are measured, water-security claims are
> hypotheses, not outcomes.

## A typical finding (real model output)

For a Dubai-climate landscape (sandy loam, warm-season turf), adding biochar:

| What the vendor measures | What actually happens to the water budget |
|--------------------------|-------------------------------------------|
| Available water storage **+13%** | Annual irrigation requirement **−0.2%** |

Why almost no saving despite a real +13% storage gain? Because in this climate the
water budget is dominated by evaporative demand — roughly **94%** of all applied
water leaves as plant transpiration regardless of the amendment, and the soil was
already meeting the plant's needs. The extra storage capacity simply goes largely
unused. The platform reports this honestly instead of converting the 13% storage
number into a marketing claim.

This is the platform's core value: it tells you **when an amendment will help, when
it won't, and why** — before you spend on it.

## Strength of evidence, made explicit

Not all amendments are backed equally. Every result is tagged with the strength of
the underlying science:

| Amendment | Evidence for water effects |
|-----------|----------------------------|
| Biochar, Compost | **High** |
| Biosolids, Engineered biochar, Polymer | **Medium** |
| Lignite nanocarbon (LNC), Dust-suppression biopolymer | **Low** |

The platform will not present a Low-evidence product with the same confidence as
biochar, and it surfaces product-specific warnings (e.g. polymers degrade over
time; some biopolymers reduce infiltration).

## What it can and cannot say

**It can:** screen amendments and climates quickly; show where water goes; compare
options on irrigation, drainage, water security, payback and ROI; and put honest
uncertainty (best/likely/worst and statistical ranges) on every number.

**It cannot (yet):** replace field measurement. Its physics is verified and
internally consistent — the water balance conserves mass exactly and the climate
calculations match the international FAO reference standard — but it has **not yet
been calibrated against a specific Gulf site's field data.** For a defensible
site-specific guarantee, the model is calibrated against measurements (the planned
next phase). We state this plainly; it is what makes the tool credible rather than
another marketing instrument.

## Why this is defensible under scrutiny

- Every calculation traces to a published, peer-reviewed equation (FAO-56 for
  evapotranspiration; van Genuchten and Mualem for soil physics; Rosetta for soil
  parameters).
- The water balance **conserves mass exactly** — water is never created or lost in
  the accounting.
- The model is deliberately **conservative**: it refuses to convert a storage
  increase into a water saving unless the fluxes prove it.
- Nothing is hidden: assumptions, limitations, and the validation gap are written
  down (see `SCIENTIFIC_BASIS.md`).

## Bottom line

GCC-SWSS is a decision-support tool that replaces an unprovable marketing claim
("holds more water") with a defensible engineering question ("how much irrigation
will I actually avoid, and what happens to the rest?"). In the Gulf, the honest
answer is often "less than you were told" — and knowing that before you buy is
exactly the point.

---

*Intended users: municipalities, landscape and irrigation consultants,
environmental regulators, golf courses, parks departments, and developers.*

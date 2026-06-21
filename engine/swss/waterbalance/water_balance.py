"""Layer 5 - daily soil-water balance: dS = P + I - ET - D - R.

Single-layer root-zone reservoir. Storage is the STATE variable (tracked as
depletion below field capacity); P, I, ET, drainage and runoff are accounting
FLUXES. Irrigation is demand-scheduled (refill to field capacity once depletion
reaches the readily-available threshold), so annual irrigation is an OUTPUT - the
number that actually decides whether an amendment saves water.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from swss.plants.crop_coefficients import CropParams, potential_demand
from swss.plants.root_uptake import actual_fluxes
from swss.schemas import DailyWeather, HydraulicProperties, WaterBalanceTotals
from swss.waterbalance.drainage import free_drainage
from swss.waterbalance.runoff import partition_rainfall
from swss.waterbalance.storage import total_available_water_mm


@dataclass
class WaterBalanceOutput:
    totals: WaterBalanceTotals
    reliability: float                      # fraction of days without water stress
    taw_mm: float
    # daily series (mm), length = days, for the flux engine and charts
    transpiration: list[float] = field(default_factory=list)
    evaporation: list[float] = field(default_factory=list)
    drainage: list[float] = field(default_factory=list)
    runoff: list[float] = field(default_factory=list)
    irrigation: list[float] = field(default_factory=list)
    rainfall: list[float] = field(default_factory=list)
    storage: list[float] = field(default_factory=list)  # water above PWP, mm


def simulate(
    hydraulics: HydraulicProperties,
    weather: list[DailyWeather],
    crop: CropParams,
) -> WaterBalanceOutput:
    taw = total_available_water_mm(hydraulics, crop.root_depth_m)
    ks_cm_day = hydraulics.vg.ks
    p = crop.depletion_frac
    raw = p * taw

    depletion = 0.0  # start at field capacity (well-watered)
    initial_storage = taw - depletion

    out = WaterBalanceOutput(
        totals=WaterBalanceTotals(
            precip_mm=0, irrigation_mm=0, et_mm=0, transpiration_mm=0, evaporation_mm=0,
            drainage_mm=0, runoff_mm=0, delta_storage_mm=0, days=len(weather), closure_error_mm=0,
        ),
        reliability=0.0,
        taw_mm=taw,
    )
    sum_p = sum_i = sum_t = sum_e = sum_dr = sum_r = 0.0
    stress_free = 0

    for w in weather:
        et0 = w.et0_mm or 0.0
        infil, runoff = partition_rainfall(w.rainfall_mm, ks_cm_day)

        # 1. rainfall into the store; anything above field capacity drains
        depletion -= infil
        drain = free_drainage(-depletion) if depletion < 0 else 0.0
        depletion = max(0.0, depletion)

        # 2. demand-scheduled irrigation: refill to field capacity at RAW threshold
        irrig = depletion if (taw > 0 and depletion >= raw) else 0.0
        depletion -= irrig

        # 3. evapotranspiration limited by water above wilting point
        tp_pot, ep_pot = potential_demand(et0, crop)
        ta, ea, ks_stress = actual_fluxes(tp_pot, ep_pot, depletion, taw, p)
        et_avail = max(0.0, taw - depletion)
        if (ta + ea) > et_avail and (ta + ea) > 0:
            scale = et_avail / (ta + ea)
            ta *= scale
            ea *= scale
        depletion = min(taw, depletion + ta + ea)

        # accumulate
        sum_p += w.rainfall_mm
        sum_i += irrig
        sum_t += ta
        sum_e += ea
        sum_dr += drain
        sum_r += runoff
        if ks_stress >= 0.999:
            stress_free += 1

        out.transpiration.append(ta)
        out.evaporation.append(ea)
        out.drainage.append(drain)
        out.runoff.append(runoff)
        out.irrigation.append(irrig)
        out.rainfall.append(w.rainfall_mm)
        out.storage.append(taw - depletion)

    final_storage = taw - depletion
    delta_storage = final_storage - initial_storage
    et_total = sum_t + sum_e
    closure = (sum_p + sum_i) - (et_total + sum_dr + sum_r) - delta_storage

    out.totals = WaterBalanceTotals(
        precip_mm=sum_p,
        irrigation_mm=sum_i,
        et_mm=et_total,
        transpiration_mm=sum_t,
        evaporation_mm=sum_e,
        drainage_mm=sum_dr,
        runoff_mm=sum_r,
        delta_storage_mm=delta_storage,
        days=len(weather),
        closure_error_mm=closure,
    )
    out.reliability = stress_free / len(weather) if weather else 0.0
    return out

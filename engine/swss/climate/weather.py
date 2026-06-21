"""Build a deterministic daily weather year from monthly climate normals.

The Gulf rainfall regime is episodic, so monthly totals are concentrated into a
few discrete wetting events rather than smeared evenly - this is what drives the
wetting/drying cycles the water balance must resolve.
"""
from __future__ import annotations

from typing import Any

from swss._data import load_yaml
from swss.climate.penman_monteith import et0_fao56
from swss.schemas import ClimateInput, DailyWeather

_LIBRARY_FILE = "climate_library.yaml"
_DAYS_IN_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]  # non-leap, 365 days
# Day-of-month indices that receive rainfall (two events/month), share of monthly total.
_RAIN_EVENTS = {10: 0.5, 20: 0.5}


def get_station(station_id: str) -> dict[str, Any]:
    for st in load_yaml(_LIBRARY_FILE)["stations"]:
        if st["id"] == station_id:
            return st
    raise KeyError(f"Unknown climate station '{station_id}'.")


def _month_of_doy(doy: int) -> tuple[int, int]:
    """Return (month 1-12, day-of-month 1-..) for a non-leap day-of-year."""
    d = doy
    for i, n in enumerate(_DAYS_IN_MONTH, start=1):
        if d <= n:
            return i, d
        d -= n
    return 12, 31


def build_year(climate: ClimateInput) -> list[DailyWeather]:
    """Return 365 DailyWeather records with ET0 computed for each day."""
    station = get_station(climate.station_id or "dubai_coastal")
    lat = climate.latitude_deg if climate.latitude_deg is not None else station["latitude_deg"]
    elev = climate.elevation_m if climate.elevation_m is not None else station["elevation_m"]
    months = {m["month"]: m for m in station["months"]}

    series: list[DailyWeather] = []
    for doy in range(1, 366):
        month, dom = _month_of_doy(doy)
        mrec = months[month]
        rain = mrec["rainfall_mm"] * _RAIN_EVENTS.get(dom, 0.0)
        et0 = et0_fao56(
            t_min=mrec["t_min"],
            t_max=mrec["t_max"],
            rh_mean=mrec["rh_mean"],
            wind_2m=mrec["wind_2m"],
            rs=mrec["rs"],
            latitude_deg=lat,
            elevation_m=elev,
            doy=doy,
        )
        series.append(
            DailyWeather(
                doy=doy,
                t_min=mrec["t_min"],
                t_max=mrec["t_max"],
                rh_mean=mrec["rh_mean"],
                wind_2m=mrec["wind_2m"],
                rs=mrec["rs"],
                rainfall_mm=rain,
                et0_mm=et0,
            )
        )
    return series

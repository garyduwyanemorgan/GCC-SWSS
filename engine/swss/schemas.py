"""Pydantic I/O models shared across every SWSS layer and the API.

These are the data contract. Engine layers consume and produce these types so the
orchestrator, API and report writer all speak the same language.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, computed_field


# --------------------------------------------------------------------------- #
# Enumerations
# --------------------------------------------------------------------------- #
class Bound(str, Enum):
    """The three deterministic points used everywhere uncertainty is expressed."""

    MIN = "min"
    LIKELY = "likely"
    MAX = "max"


class Confidence(str, Enum):
    """Strength-of-evidence ranking carried from the amendment library to reports."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    USER_DEFINED = "USER_DEFINED"


# Pedotransfer/parameter confidence level, 1 (poor) .. 4 (field-calibrated).
ConfidenceLevel = int


# --------------------------------------------------------------------------- #
# Layer 1 - soil hydraulics
# --------------------------------------------------------------------------- #
class VanGenuchten(BaseModel):
    """Van Genuchten-Mualem retention parameters. alpha in 1/cm, ks in cm/day."""

    theta_r: float = Field(ge=0.0, lt=1.0)
    theta_s: float = Field(gt=0.0, le=1.0)
    alpha: float = Field(gt=0.0)
    n: float = Field(gt=1.0)
    ks: float = Field(gt=0.0)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def m(self) -> float:
        """Mualem constraint m = 1 - 1/n."""
        return 1.0 - 1.0 / self.n


class SoilTexture(BaseModel):
    sand: float = Field(ge=0.0, le=100.0)
    silt: float = Field(ge=0.0, le=100.0)
    clay: float = Field(ge=0.0, le=100.0)

    @property
    def is_sandy(self) -> bool:
        """USDA-ish coarse-texture flag used to pick texture-specific Ks effects."""
        return self.sand >= 70.0


class SoilInput(BaseModel):
    """Raw site/borehole soil description (the user's Layer-1 input)."""

    texture: SoilTexture
    bulk_density: float = Field(gt=0.5, lt=2.2, description="g/cm3")
    organic_matter: float = Field(default=0.5, ge=0.0, description="mass %")
    gravel_fraction: float = Field(default=0.0, ge=0.0, lt=1.0, description="volume fraction")
    ec: Optional[float] = Field(default=None, description="electrical conductivity dS/m")
    sar: Optional[float] = Field(default=None, description="sodium adsorption ratio")
    root_zone_depth_m: float = Field(default=0.5, gt=0.0)
    # Optional measured retention points improve the Rosetta model class.
    theta_33: Optional[float] = Field(default=None, description="water content at -33 kPa")
    theta_1500: Optional[float] = Field(default=None, description="water content at -1500 kPa")


class HydraulicProperties(BaseModel):
    """Layer-1 output: VG params + plant-available water + provenance/confidence."""

    vg: VanGenuchten
    theta_fc: float = Field(description="field capacity water content (h=-330 cm)")
    theta_pwp: float = Field(description="permanent wilting point (h=-15000 cm)")
    awc: float = Field(description="available water capacity, cm3/cm3")
    confidence_level: ConfidenceLevel = Field(ge=1, le=4)
    method: str = Field(description="how parameters were derived")
    notes: list[str] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Layer 2 - climate
# --------------------------------------------------------------------------- #
class ClimateInput(BaseModel):
    """Either a named station id (resolved from the library) or explicit location."""

    station_id: Optional[str] = "dubai_coastal"
    latitude_deg: Optional[float] = None
    elevation_m: Optional[float] = None


class DailyWeather(BaseModel):
    doy: int = Field(ge=1, le=366)
    t_min: float
    t_max: float
    rh_mean: float
    wind_2m: float
    rs: float = Field(description="solar radiation MJ/m2/day")
    rainfall_mm: float = Field(ge=0.0)
    et0_mm: Optional[float] = None


# --------------------------------------------------------------------------- #
# Layer 3 - plants
# --------------------------------------------------------------------------- #
class PlantInput(BaseModel):
    crop_id: str = "turf_warm"


# --------------------------------------------------------------------------- #
# Layer 4 - amendments
# --------------------------------------------------------------------------- #
class AmendmentInput(BaseModel):
    """Selects a library amendment (or 'custom') at a given uncertainty bound."""

    amendment_id: str
    bound: Bound = Bound.LIKELY
    # For id == 'custom', explicit multipliers may be supplied.
    custom_multipliers: dict[str, float] = Field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Layer 5 - water balance & flux
# --------------------------------------------------------------------------- #
class WaterBalanceTotals(BaseModel):
    """Annualised water balance, all depths in mm/year unless noted."""

    precip_mm: float
    irrigation_mm: float
    et_mm: float
    transpiration_mm: float
    evaporation_mm: float
    drainage_mm: float
    runoff_mm: float
    delta_storage_mm: float
    days: int
    closure_error_mm: float = Field(description="inputs - outputs - dStorage; ~0 if closed")


class FluxLedger(BaseModel):
    """Flux Attribution Engine output - 'where did the water go?' in mm and m3."""

    area_m2: float
    total_input_mm: float
    to_storage_mm: float
    to_transpiration_mm: float
    to_evaporation_mm: float
    to_drainage_mm: float
    to_runoff_mm: float

    def as_volume_m3(self, depth_mm: float) -> float:
        return depth_mm / 1000.0 * self.area_m2


# --------------------------------------------------------------------------- #
# Layer 6 - water security
# --------------------------------------------------------------------------- #
class WaterSecurityResult(BaseModel):
    annual_irrigation_mm: float
    annual_et_mm: float
    drainage_loss_mm: float
    water_productivity: float = Field(description="transpiration / total water applied")
    root_zone_reliability: float = Field(ge=0.0, le=1.0, description="fraction of days non-stressed")
    wsi: float = Field(ge=0.0, le=100.0, description="Water Security Index 0-100")
    wsi_components: dict[str, float] = Field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Economics
# --------------------------------------------------------------------------- #
class EconomicsInput(BaseModel):
    area_m2: float = 10000.0
    water_cost_per_m3: float = 2.0
    amendment_cost: float = 0.0
    application_cost: float = 0.0
    discount_rate: float = 0.08
    horizon_years: int = 10


class EconomicsResult(BaseModel):
    annual_water_saved_m3: float
    annual_saving_currency: float
    payback_years: Optional[float]
    cost_per_m3_saved: Optional[float]
    npv: float
    roi_pct: Optional[float]


# --------------------------------------------------------------------------- #
# Scenario + simulation result
# --------------------------------------------------------------------------- #
class ScenarioResult(BaseModel):
    """Result for one scenario (baseline or a single amendment) at one bound."""

    name: str
    amendment_id: Optional[str]
    confidence: Confidence
    bound: Bound
    hydraulics: HydraulicProperties
    balance: WaterBalanceTotals
    flux: FluxLedger
    security: WaterSecurityResult
    economics: Optional[EconomicsResult] = None


class UncertaintyBand(BaseModel):
    """P10/P50/P90 of a single metric across Monte Carlo realisations."""

    metric: str
    p10: float
    p50: float
    p90: float


class ScenarioComparison(BaseModel):
    """Baseline vs amendment with derived savings figures - feeds the dashboard."""

    name: str
    amendment_id: Optional[str]
    confidence: Confidence
    awc_change_pct: float
    storage_change_pct: float
    irrigation_change_pct: float
    drainage_change_pct: float
    et_change_pct: float
    wsi: float
    bands: list[UncertaintyBand] = Field(default_factory=list)


class SimResult(BaseModel):
    """Top-level orchestrator output consumed by the API, dashboard and reports."""

    project_name: str
    baseline: ScenarioResult
    scenarios: list[ScenarioResult] = Field(default_factory=list)
    comparisons: list[ScenarioComparison] = Field(default_factory=list)
    narrative: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class ProjectInput(BaseModel):
    """Everything needed to run a full investigation."""

    project_name: str = "Untitled GCC-SWSS Project"
    soil: SoilInput
    climate: ClimateInput = Field(default_factory=ClimateInput)
    plant: PlantInput = Field(default_factory=PlantInput)
    amendments: list[AmendmentInput] = Field(default_factory=list)
    economics: Optional[EconomicsInput] = None
    monte_carlo: bool = False
    n_realisations: int = 1000
    seed: Optional[int] = 42

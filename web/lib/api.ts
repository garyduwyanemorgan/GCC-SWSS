// Typed client for the GCC-SWSS engine API.
import { supabase } from "./supabase";

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function getToken(): Promise<string | null> {
  if (!supabase) return null;
  const { data } = await supabase.auth.getSession();
  return data.session?.access_token ?? null;
}

export interface SoilTexture { sand: number; silt: number; clay: number; }

export interface ProjectInput {
  project_name: string;
  soil: {
    texture: SoilTexture;
    bulk_density: number;
    organic_matter?: number;
    ec?: number | null;
    root_zone_depth_m: number;
  };
  climate: { station_id: string };
  plant: { crop_id: string };
  amendments: { amendment_id: string; bound?: "min" | "likely" | "max" }[];
  economics?: {
    area_m2: number;
    water_cost_per_m3: number;
    amendment_cost: number;
    application_cost: number;
  } | null;
  monte_carlo?: boolean;
  n_realisations?: number;
}

export interface FluxLedger {
  area_m2: number;
  total_input_mm: number;
  to_storage_mm: number;
  to_transpiration_mm: number;
  to_evaporation_mm: number;
  to_drainage_mm: number;
  to_runoff_mm: number;
}

export interface WaterBalanceTotals {
  precip_mm: number; irrigation_mm: number; et_mm: number;
  transpiration_mm: number; evaporation_mm: number;
  drainage_mm: number; runoff_mm: number; delta_storage_mm: number;
  days: number; closure_error_mm: number;
}

export interface ScenarioResult {
  name: string;
  amendment_id: string | null;
  confidence: "HIGH" | "MEDIUM" | "LOW" | "USER_DEFINED";
  hydraulics: { awc: number; confidence_level: number; method: string };
  balance: WaterBalanceTotals;
  flux: FluxLedger;
  security: {
    wsi: number; annual_irrigation_mm: number; drainage_loss_mm: number;
    water_productivity: number; root_zone_reliability: number;
    wsi_components: Record<string, number>;
  };
  economics?: {
    annual_water_saved_m3: number; annual_saving_currency: number;
    payback_years: number | null; npv: number; roi_pct: number | null;
  } | null;
}

export interface ScenarioComparison {
  name: string;
  amendment_id: string | null;
  confidence: ScenarioResult["confidence"];
  awc_change_pct: number;
  storage_change_pct: number;
  irrigation_change_pct: number;
  drainage_change_pct: number;
  et_change_pct: number;
  wsi: number;
  bands: { metric: string; p10: number; p50: number; p90: number }[];
}

export interface SimResult {
  project_name: string;
  baseline: ScenarioResult;
  scenarios: ScenarioResult[];
  comparisons: ScenarioComparison[];
  narrative: string[];
  assumptions: string[];
  limitations: string[];
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const token = await getToken();
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail ?? `Request failed (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export const simulate = (p: ProjectInput) => post<SimResult>("/simulate", p);

export async function getLibrary(kind: "soil" | "amendment" | "crop") {
  const res = await fetch(`${API_URL}/libraries/${kind}`);
  if (!res.ok) throw new Error(`Failed to load ${kind} library`);
  return res.json();
}

export async function submitLead(lead: {
  name: string; email: string; organisation?: string; message?: string;
}) {
  return post<{ status: string }>("/leads", { ...lead, source: "website" });
}

export function reportUrl() {
  return `${API_URL}/report`;
}

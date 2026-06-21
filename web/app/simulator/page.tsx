"use client";
import { useEffect, useState } from "react";
import {
  API_URL, getLibrary, ProjectInput, reportUrl, simulate, SimResult,
} from "@/lib/api";
import FluxAttribution from "@/components/FluxAttribution";
import ScenarioTable from "@/components/ScenarioTable";

const DEFAULT_AMENDMENTS = ["biochar", "compost", "polymer", "lnc"];

const initialProject = (): ProjectInput => ({
  project_name: "GCC landscape trial",
  soil: {
    texture: { sand: 65, silt: 25, clay: 10 },
    bulk_density: 1.48,
    organic_matter: 1.0,
    ec: 2.0,
    root_zone_depth_m: 0.5,
  },
  climate: { station_id: "dubai_coastal" },
  plant: { crop_id: "turf_warm" },
  amendments: [{ amendment_id: "biochar" }, { amendment_id: "compost" }],
  economics: { area_m2: 10000, water_cost_per_m3: 2.0, amendment_cost: 12000, application_cost: 3000 },
  monte_carlo: false,
  n_realisations: 500,
});

export default function Simulator() {
  const [p, setP] = useState<ProjectInput>(initialProject);
  const [crops, setCrops] = useState<{ id: string; name: string }[]>([]);
  const [amendments, setAmendments] = useState<{ id: string; name: string; confidence: string }[]>([]);
  const [result, setResult] = useState<SimResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    getLibrary("crop").then(setCrops).catch(() => {});
    getLibrary("amendment").then(setAmendments).catch(() => {});
  }, []);

  function setSoil(patch: Partial<ProjectInput["soil"]>) {
    setP((prev) => ({ ...prev, soil: { ...prev.soil, ...patch } }));
  }
  function toggleAmendment(id: string) {
    setP((prev) => {
      const has = prev.amendments.some((a) => a.amendment_id === id);
      return {
        ...prev,
        amendments: has
          ? prev.amendments.filter((a) => a.amendment_id !== id)
          : [...prev.amendments, { amendment_id: id }],
      };
    });
  }

  async function run() {
    setBusy(true); setErr(null);
    try {
      setResult(await simulate(p));
    } catch (e: any) {
      setErr(e.message ?? "Simulation failed");
    } finally {
      setBusy(false);
    }
  }

  async function downloadPdf() {
    const res = await fetch(reportUrl(), {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(p),
    });
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "swss_report.pdf"; a.click();
    URL.revokeObjectURL(url);
  }

  const selected = (id: string) => p.amendments.some((a) => a.amendment_id === id);

  return (
    <div className="container grid cols-2">
      {/* ---------------- inputs ---------------- */}
      <div className="panel" style={{ alignSelf: "start" }}>
        <h3>Inputs</h3>
        <label>Project name</label>
        <input value={p.project_name} onChange={(e) => setP({ ...p, project_name: e.target.value })} />

        <label>Soil texture (sand / silt / clay %)</label>
        <div className="row">
          <input type="number" value={p.soil.texture.sand}
            onChange={(e) => setSoil({ texture: { ...p.soil.texture, sand: +e.target.value } })} />
          <input type="number" value={p.soil.texture.silt}
            onChange={(e) => setSoil({ texture: { ...p.soil.texture, silt: +e.target.value } })} />
          <input type="number" value={p.soil.texture.clay}
            onChange={(e) => setSoil({ texture: { ...p.soil.texture, clay: +e.target.value } })} />
        </div>

        <div className="row">
          <div>
            <label>Bulk density (g/cm³)</label>
            <input type="number" step="0.01" value={p.soil.bulk_density}
              onChange={(e) => setSoil({ bulk_density: +e.target.value })} />
          </div>
          <div>
            <label>EC (dS/m)</label>
            <input type="number" step="0.1" value={p.soil.ec ?? 0}
              onChange={(e) => setSoil({ ec: +e.target.value })} />
          </div>
          <div>
            <label>Root depth (m)</label>
            <input type="number" step="0.1" value={p.soil.root_zone_depth_m}
              onChange={(e) => setSoil({ root_zone_depth_m: +e.target.value })} />
          </div>
        </div>

        <label>Vegetation</label>
        <select value={p.plant.crop_id} onChange={(e) => setP({ ...p, plant: { crop_id: e.target.value } })}>
          {crops.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>

        <label>Amendments to compare</label>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 4 }}>
          {(amendments.length ? amendments : DEFAULT_AMENDMENTS.map((id) => ({ id, name: id, confidence: "" })))
            .filter((a) => a.id !== "custom")
            .map((a) => (
              <button key={a.id} type="button" className="ghost"
                onClick={() => toggleAmendment(a.id)}
                style={{ borderColor: selected(a.id) ? "var(--accent)" : "var(--line)",
                  color: selected(a.id) ? "var(--accent)" : "var(--ink)" }}>
                {a.name}
              </button>
            ))}
        </div>

        <label style={{ marginTop: 12 }}>
          <input type="checkbox" style={{ width: "auto", marginRight: 8 }}
            checked={!!p.monte_carlo}
            onChange={(e) => setP({ ...p, monte_carlo: e.target.checked })} />
          Monte-Carlo uncertainty (P10/P50/P90)
        </label>

        <button className="primary" onClick={run} disabled={busy || p.amendments.length === 0}>
          {busy ? "Simulating…" : "Run water balance"}
        </button>
        {err && <p className="err">{err}</p>}
        <p className="muted" style={{ fontSize: 12, marginTop: 10 }}>Engine: {API_URL}</p>
      </div>

      {/* ---------------- results ---------------- */}
      <div className="grid" style={{ gap: 16 }}>
        {!result ? (
          <div className="panel"><p className="muted">
            Configure a scenario and run the water balance. Results show where the
            water actually goes — not just how much the soil can hold.
          </p></div>
        ) : (
          <>
            <div className="panel grid cols-3">
              <div className="kpi">
                <span className="v">{result.baseline.security.annual_irrigation_mm.toFixed(0)}</span>
                <span className="l">Baseline irrigation mm/yr</span>
              </div>
              <div className="kpi">
                <span className="v">{result.baseline.balance.et_mm.toFixed(0)}</span>
                <span className="l">Annual ET mm/yr</span>
              </div>
              <div className="kpi">
                <span className="v">{Math.abs(result.baseline.balance.closure_error_mm) < 0.01 ? "✓" : "!"}</span>
                <span className="l">Balance closure</span>
              </div>
            </div>

            <div className="panel">
              <h3>Interpretation</h3>
              {result.narrative.map((n, i) => (
                <p key={i} className={i === 0 ? "muted" : "narrative"}>{n}</p>
              ))}
            </div>

            <div className="panel">
              <h3>Flux Attribution — where did the water go?</h3>
              <FluxAttribution scenarios={[result.baseline, ...result.scenarios]} />
            </div>

            <div className="panel">
              <h3>Scenario comparison</h3>
              <ScenarioTable baseline={result.baseline} scenarios={result.scenarios}
                comparisons={result.comparisons} />
              <button className="ghost" style={{ marginTop: 14 }} onClick={downloadPdf}>
                Download PDF report
              </button>
            </div>

            {result.comparisons.some((c) => c.bands.length > 0) && (
              <div className="panel">
                <h3>Uncertainty (P10 / P50 / P90)</h3>
                {result.comparisons.map((c) =>
                  c.bands.length ? (
                    <div key={c.name} style={{ marginBottom: 10 }}>
                      <strong>{c.name}</strong>
                      <table>
                        <thead><tr><th>Metric</th><th>P10</th><th>P50</th><th>P90</th></tr></thead>
                        <tbody>
                          {c.bands.map((b) => (
                            <tr key={b.metric}>
                              <td>{b.metric}</td>
                              <td>{b.p10.toFixed(1)}</td>
                              <td>{b.p50.toFixed(1)}</td>
                              <td>{b.p90.toFixed(1)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : null
                )}
              </div>
            )}

            <div className="panel">
              <h3>Assumptions &amp; limitations</h3>
              <ul className="muted" style={{ fontSize: 13, marginTop: 0 }}>
                {result.assumptions.map((a, i) => <li key={`a${i}`}>{a}</li>)}
                {result.limitations.map((l, i) => <li key={`l${i}`} style={{ color: "var(--warn)" }}>{l}</li>)}
              </ul>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

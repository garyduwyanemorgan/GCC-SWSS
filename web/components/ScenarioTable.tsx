"use client";
import type { ScenarioComparison, ScenarioResult } from "@/lib/api";

const pct = (v: number) => `${v >= 0 ? "+" : ""}${v.toFixed(0)}%`;
const cls = (v: number, goodIfNegative = false) =>
  goodIfNegative ? (v < 0 ? "pos" : v > 0 ? "neg" : "") : v > 0 ? "pos" : v < 0 ? "neg" : "";

export default function ScenarioTable({
  baseline, scenarios, comparisons,
}: {
  baseline: ScenarioResult;
  scenarios: ScenarioResult[];
  comparisons: ScenarioComparison[];
}) {
  const cmpFor = (id: string | null) => comparisons.find((c) => c.amendment_id === id);
  return (
    <table>
      <thead>
        <tr>
          <th>Scenario</th>
          <th>Evidence</th>
          <th>AWC Δ</th>
          <th>Irrigation</th>
          <th>Irrig. Δ</th>
          <th>Drainage Δ</th>
          <th>ET Δ</th>
          <th>WSI</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>{baseline.name}</td>
          <td><span className="badge USER_DEFINED">baseline</span></td>
          <td className="muted">—</td>
          <td>{baseline.balance.irrigation_mm.toFixed(0)} mm</td>
          <td className="muted">—</td>
          <td className="muted">—</td>
          <td className="muted">—</td>
          <td>{baseline.security.wsi.toFixed(0)}</td>
        </tr>
        {scenarios.map((s) => {
          const c = cmpFor(s.amendment_id);
          if (!c) return null;
          return (
            <tr key={s.name}>
              <td>{s.name}</td>
              <td><span className={`badge ${s.confidence}`}>{s.confidence}</span></td>
              <td className={cls(c.awc_change_pct)}>{pct(c.awc_change_pct)}</td>
              <td>{s.balance.irrigation_mm.toFixed(0)} mm</td>
              <td className={cls(c.irrigation_change_pct, true)}>{pct(c.irrigation_change_pct)}</td>
              <td className={cls(c.drainage_change_pct, true)}>{pct(c.drainage_change_pct)}</td>
              <td className={cls(c.et_change_pct, true)}>{pct(c.et_change_pct)}</td>
              <td>{c.wsi.toFixed(0)}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

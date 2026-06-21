"use client";
import type { ScenarioResult } from "@/lib/api";

// "Where did the water go?" — a stacked bar per scenario showing the fate of
// every mm of applied water (transpiration / evaporation / drainage / runoff /
// storage). Storage can be negative (a source), shown clamped at zero with a note.

const SEGMENTS = [
  { key: "to_transpiration_mm", label: "Transpiration", color: "var(--transp)" },
  { key: "to_evaporation_mm", label: "Soil evaporation", color: "var(--evap)" },
  { key: "to_drainage_mm", label: "Deep drainage", color: "var(--drain)" },
  { key: "to_runoff_mm", label: "Runoff", color: "var(--runoff)" },
  { key: "to_storage_mm", label: "Δ storage", color: "var(--store)" },
] as const;

export default function FluxAttribution({ scenarios }: { scenarios: ScenarioResult[] }) {
  const maxInput = Math.max(...scenarios.map((s) => s.flux.total_input_mm), 1);
  const W = 720, rowH = 46, labelW = 150, barW = W - labelW - 70;

  return (
    <div>
      <svg viewBox={`0 0 ${W} ${scenarios.length * rowH + 10}`} width="100%" role="img"
        aria-label="Flux attribution by scenario">
        {scenarios.map((s, i) => {
          const y = i * rowH + 8;
          let x = labelW;
          const total = s.flux.total_input_mm || 1;
          return (
            <g key={s.name}>
              <text x={0} y={y + 20} fill="var(--ink)" fontSize={13}>{s.name}</text>
              {SEGMENTS.map((seg) => {
                const mm = Math.max(0, (s.flux as any)[seg.key] as number);
                const w = (mm / maxInput) * barW;
                const rect = (
                  <rect key={seg.key} x={x} y={y} width={Math.max(0, w)} height={26}
                    fill={seg.color} opacity={0.9}>
                    <title>{`${seg.label}: ${mm.toFixed(0)} mm (${((mm / total) * 100).toFixed(0)}%)`}</title>
                  </rect>
                );
                x += w;
                return rect;
              })}
              <text x={x + 8} y={y + 18} fill="var(--muted)" fontSize={12}>
                {s.flux.total_input_mm.toFixed(0)} mm in
              </text>
            </g>
          );
        })}
      </svg>
      <div className="legend" style={{ marginTop: 10 }}>
        {SEGMENTS.map((s) => (
          <span key={s.key}>
            <i className="dot" style={{ background: s.color }} /> {s.label}
          </span>
        ))}
      </div>
    </div>
  );
}

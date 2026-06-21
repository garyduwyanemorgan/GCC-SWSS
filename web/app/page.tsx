"use client";
import Link from "next/link";
import { useState } from "react";
import { submitLead } from "@/lib/api";

const EVIDENCE = [
  ["Biochar", "High"],
  ["Compost", "High"],
  ["Biosolids", "Medium"],
  ["Engineered Biochar", "Medium"],
  ["Polymer", "Medium"],
  ["LNC", "Low"],
  ["Dust-Suppression Biopolymer", "Low"],
] as const;

export default function Home() {
  const [lead, setLead] = useState({ name: "", email: "", organisation: "", message: "" });
  const [state, setState] = useState<"idle" | "sending" | "done" | "error">("idle");

  async function send(e: React.FormEvent) {
    e.preventDefault();
    setState("sending");
    try {
      await submitLead(lead);
      setState("done");
    } catch {
      setState("error");
    }
  }

  return (
    <main>
      <section className="hero">
        <h1>Where did the water go?</h1>
        <p className="lead">
          A hydrogeological decision-support platform that evaluates whether soil
          amendments actually reduce irrigation demand under GCC conditions — by
          running a complete daily water balance, not a retention curve.
        </p>
        <p className="thesis">
          “Retention curves tell us how water is stored. Water balances tell us
          whether water is saved. Until the fluxes are measured, claims of water
          security remain hypotheses.”
        </p>
        <Link href="/simulator">
          <button className="ghost">Open the simulator →</button>
        </Link>
      </section>

      <div className="container grid cols-3">
        <div className="panel">
          <h3>Flux Attribution Engine</h3>
          <p className="muted">
            Of every cubic metre applied, the engine reports how much became plant
            transpiration, soil evaporation, deep drainage, runoff or storage — so a
            headline storage gain can never hide an offsetting loss.
          </p>
        </div>
        <div className="panel">
          <h3>Uncertainty by default</h3>
          <p className="muted">
            Amendment effects are min/likely/max ranges propagated through 1,000
            Monte-Carlo runs to P10/P50/P90 bands. No deterministic water-saving
            claims are permitted.
          </p>
        </div>
        <div className="panel">
          <h3>Strength of evidence</h3>
          <table>
            <tbody>
              {EVIDENCE.map(([name, level]) => (
                <tr key={name}>
                  <td>{name}</td>
                  <td>
                    <span className={`badge ${level === "High" ? "HIGH" : level === "Medium" ? "MEDIUM" : "LOW"}`}>
                      {level}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="container grid cols-2">
        <div className="panel">
          <h3>Request access</h3>
          {state === "done" ? (
            <p className="ok">Thank you — we will be in touch shortly.</p>
          ) : (
            <form onSubmit={send}>
              <label>Name</label>
              <input required value={lead.name} onChange={(e) => setLead({ ...lead, name: e.target.value })} />
              <label>Email</label>
              <input required type="email" value={lead.email} onChange={(e) => setLead({ ...lead, email: e.target.value })} />
              <label>Organisation</label>
              <input value={lead.organisation} onChange={(e) => setLead({ ...lead, organisation: e.target.value })} />
              <label>How would you use the platform?</label>
              <input value={lead.message} onChange={(e) => setLead({ ...lead, message: e.target.value })} />
              <button className="primary" disabled={state === "sending"}>
                {state === "sending" ? "Sending…" : "Request access"}
              </button>
              {state === "error" && <p className="err">Something went wrong. Please try again.</p>}
            </form>
          )}
        </div>
        <div className="panel">
          <h3>Built for the GCC</h3>
          <p className="muted">
            Extreme evaporative demand (ET₀ 5–15 mm/day), sandy low-storage soils,
            high salinity and near-total irrigation dependency. In this regime,
            increased water retention does not automatically translate into reduced
            irrigation demand — the platform is designed to prove, or disprove, that
            link at the system scale.
          </p>
          <p className="muted">
            Intended users: municipalities, landscape consultants, irrigation
            engineers, environmental regulators, golf courses and parks departments.
          </p>
        </div>
      </div>
      <div style={{ height: 40 }} />
    </main>
  );
}

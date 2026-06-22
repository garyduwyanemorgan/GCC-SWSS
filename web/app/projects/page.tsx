"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import { listScenarios, deleteScenario, type SavedScenario } from "@/lib/db";
import { supabase } from "@/lib/supabase";

function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

export default function ProjectsPage() {
  const { session, loading } = useAuth();
  const router = useRouter();
  const [scenarios, setScenarios] = useState<SavedScenario[]>([]);
  const [fetching, setFetching] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    if (loading) return;
    if (!session) { router.push("/auth"); return; }
    listScenarios()
      .then(setScenarios)
      .catch((e) => setErr(e.message))
      .finally(() => setFetching(false));
  }, [session, loading]);

  async function remove(id: string) {
    if (!confirm("Delete this scenario and its results?")) return;
    await deleteScenario(id);
    setScenarios((prev) => prev.filter((s) => s.id !== id));
  }

  if (!supabase) {
    return (
      <main className="container" style={{ paddingTop: 40 }}>
        <div className="panel">
          <p className="muted">
            Supabase is not configured. Saved projects require{" "}
            <code>NEXT_PUBLIC_SUPABASE_URL</code> and{" "}
            <code>NEXT_PUBLIC_SUPABASE_ANON_KEY</code>.
          </p>
        </div>
      </main>
    );
  }

  if (loading || fetching) {
    return (
      <main className="container" style={{ paddingTop: 40 }}>
        <p className="muted">Loading…</p>
      </main>
    );
  }

  // Group scenarios by project
  const byProject: Record<string, { name: string; rows: SavedScenario[] }> = {};
  for (const s of scenarios) {
    if (!byProject[s.project_id]) {
      byProject[s.project_id] = { name: s.project_name, rows: [] };
    }
    byProject[s.project_id].rows.push(s);
  }

  return (
    <main className="container" style={{ paddingTop: 32 }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 24,
        }}
      >
        <h2 style={{ margin: 0 }}>My Projects</h2>
        <Link href="/simulator">
          <button className="primary" style={{ width: "auto", marginTop: 0 }}>
            New simulation
          </button>
        </Link>
      </div>

      {err && <p className="err">{err}</p>}

      {scenarios.length === 0 ? (
        <div className="panel">
          <p className="muted">
            No saved scenarios yet. Run a simulation and use the{" "}
            <em>Save to My Projects</em> button to archive results.
          </p>
        </div>
      ) : (
        Object.values(byProject).map((proj) => (
          <div key={proj.name} style={{ marginBottom: 28 }}>
            <h3
              style={{
                fontSize: 13,
                textTransform: "uppercase",
                letterSpacing: ".5px",
                color: "var(--muted)",
                margin: "0 0 10px",
              }}
            >
              {proj.name}
            </h3>
            <div className="grid">
              {proj.rows.map((s) => {
                const amendList = (s.payload.amendments ?? [])
                  .map((a) => a.amendment_id)
                  .join(", ");
                return (
                  <div
                    key={s.id}
                    className="panel"
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      padding: "14px 18px",
                    }}
                  >
                    <div>
                      <strong style={{ fontSize: 14 }}>{s.name}</strong>
                      <p
                        className="muted"
                        style={{ fontSize: 12, margin: "4px 0 0" }}
                      >
                        {fmtDate(s.created_at)} · {amendList || "baseline only"}
                      </p>
                    </div>
                    <div style={{ display: "flex", gap: 8 }}>
                      <button
                        className="ghost"
                        style={{ padding: "6px 14px", fontSize: 13 }}
                        onClick={() =>
                          router.push(`/simulator?scenario=${s.id}`)
                        }
                      >
                        Open
                      </button>
                      <button
                        className="ghost"
                        style={{
                          padding: "6px 14px",
                          fontSize: 13,
                          color: "var(--bad)",
                          borderColor: "var(--bad)",
                        }}
                        onClick={() => remove(s.id)}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))
      )}
    </main>
  );
}

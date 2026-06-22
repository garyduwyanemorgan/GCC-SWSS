import { supabase } from "./supabase";
import type { ProjectInput, SimResult } from "./api";

export interface SavedScenario {
  id: string;
  project_id: string;
  name: string;
  payload: ProjectInput;
  created_at: string;
  project_name: string;
}

export async function saveScenario(
  projectName: string,
  scenarioName: string,
  payload: ProjectInput,
  result: SimResult,
): Promise<{ scenarioId: string }> {
  if (!supabase) throw new Error("Supabase not configured");
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) throw new Error("Not signed in");
  const uid = session.user.id;

  // Find or create project by name
  let projectId: string;
  const { data: existing } = await supabase
    .from("projects")
    .select("id")
    .eq("owner", uid)
    .eq("name", projectName)
    .maybeSingle();

  if (existing) {
    projectId = existing.id;
  } else {
    const { data: created, error } = await supabase
      .from("projects")
      .insert({ owner: uid, name: projectName, climate_station: payload.climate.station_id })
      .select("id")
      .single();
    if (error) throw error;
    projectId = created.id;
  }

  // Insert scenario with the full payload (forensic requirement: reproducible)
  const { data: scenario, error: sErr } = await supabase
    .from("scenarios")
    .insert({ project_id: projectId, owner: uid, name: scenarioName, payload })
    .select("id")
    .single();
  if (sErr) throw sErr;

  // Archive the SimResult JSON
  const { error: rErr } = await supabase
    .from("sim_results")
    .insert({ scenario_id: scenario.id, owner: uid, result });
  if (rErr) throw rErr;

  return { scenarioId: scenario.id };
}

export async function listScenarios(): Promise<SavedScenario[]> {
  if (!supabase) return [];
  const { data, error } = await supabase
    .from("scenarios")
    .select("id, project_id, name, payload, created_at, projects(name)")
    .order("created_at", { ascending: false })
    .limit(100);
  if (error) throw error;
  return (data ?? []).map((r: any) => ({
    id: r.id,
    project_id: r.project_id,
    name: r.name,
    payload: r.payload as ProjectInput,
    created_at: r.created_at,
    project_name: r.projects?.name ?? "Unknown project",
  }));
}

export async function loadScenario(id: string): Promise<SavedScenario | null> {
  if (!supabase) return null;
  const { data, error } = await supabase
    .from("scenarios")
    .select("id, project_id, name, payload, created_at, projects(name)")
    .eq("id", id)
    .single();
  if (error) return null;
  return {
    id: data.id,
    project_id: data.project_id,
    name: data.name,
    payload: data.payload as ProjectInput,
    created_at: data.created_at,
    project_name: (data as any).projects?.name ?? "",
  };
}

export async function deleteScenario(id: string): Promise<void> {
  if (!supabase) return;
  await supabase.from("scenarios").delete().eq("id", id);
}

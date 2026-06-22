"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";

export default function AuthPage() {
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [org, setOrg] = useState("");
  const [state, setState] = useState<"idle" | "loading" | "done" | "error">("idle");
  const [msg, setMsg] = useState("");
  const router = useRouter();

  if (!supabase) {
    return (
      <main>
        <div className="container" style={{ maxWidth: 480, paddingTop: 60 }}>
          <div className="panel">
            <p className="muted">
              Authentication is not configured. Set{" "}
              <code>NEXT_PUBLIC_SUPABASE_URL</code> and{" "}
              <code>NEXT_PUBLIC_SUPABASE_ANON_KEY</code> in your environment.
            </p>
          </div>
        </div>
      </main>
    );
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setState("loading");
    setMsg("");
    try {
      if (mode === "signin") {
        const { error } = await supabase!.auth.signInWithPassword({ email, password });
        if (error) throw error;
        router.push("/projects");
        return;
      } else {
        const { error } = await supabase!.auth.signUp({
          email,
          password,
          options: { data: { full_name: name, organisation: org } },
        });
        if (error) throw error;
        setState("done");
        setMsg("Check your email to confirm your account, then sign in.");
        return;
      }
    } catch (err: any) {
      setState("error");
      setMsg(err.message ?? "Something went wrong.");
    }
  }

  if (state === "done") {
    return (
      <main>
        <div className="container" style={{ maxWidth: 480, paddingTop: 60 }}>
          <div className="panel">
            <h3>Account created</h3>
            <p className="ok">{msg}</p>
            <button className="ghost" style={{ marginTop: 12 }} onClick={() => { setState("idle"); setMode("signin"); }}>
              Back to sign in
            </button>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main>
      <div className="container" style={{ maxWidth: 480, paddingTop: 60 }}>
        <div className="panel">
          <div className="row" style={{ marginBottom: 20 }}>
            <button
              className={mode === "signin" ? "primary" : "ghost"}
              style={{ marginTop: 0 }}
              onClick={() => setMode("signin")}
            >
              Sign in
            </button>
            <button
              className={mode === "signup" ? "primary" : "ghost"}
              style={{ marginTop: 0 }}
              onClick={() => setMode("signup")}
            >
              Create account
            </button>
          </div>

          <form onSubmit={submit}>
            {mode === "signup" && (
              <>
                <label>Full name</label>
                <input value={name} onChange={(e) => setName(e.target.value)} required />
                <label>Organisation</label>
                <input value={org} onChange={(e) => setOrg(e.target.value)} />
              </>
            )}
            <label>Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
            />
            <button className="primary" disabled={state === "loading"}>
              {state === "loading"
                ? "…"
                : mode === "signin"
                ? "Sign in"
                : "Create account"}
            </button>
            {state === "error" && <p className="err">{msg}</p>}
          </form>
        </div>
      </div>
    </main>
  );
}

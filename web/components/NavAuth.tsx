"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "./AuthProvider";
import { supabase } from "@/lib/supabase";

export default function NavAuth() {
  const { session, loading } = useAuth();
  const router = useRouter();

  // Hide auth controls when Supabase is not configured or still hydrating
  if (!supabase || loading) return null;

  if (session) {
    return (
      <>
        <Link href="/projects">My Projects</Link>
        <button
          className="ghost"
          style={{ padding: "4px 12px", fontSize: 14 }}
          onClick={async () => {
            await supabase!.auth.signOut();
            router.push("/");
          }}
        >
          Sign out
        </button>
      </>
    );
  }

  return <Link href="/auth">Sign in</Link>;
}

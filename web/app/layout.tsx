import "./globals.css";
import type { Metadata } from "next";
import Link from "next/link";
import { AuthProvider } from "@/components/AuthProvider";
import NavAuth from "@/components/NavAuth";

export const metadata: Metadata = {
  title: "GCC Soil Water Security Simulator",
  description:
    "Retention curves tell us how water is stored. Water balances tell us whether water is saved.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <nav className="nav">
            <div className="brand">
              GCC&nbsp;SWSS <small>· Soil Water Security Simulator</small>
            </div>
            <div style={{ display: "flex", gap: 18, alignItems: "center" }}>
              <Link href="/">Overview</Link>
              <Link href="/simulator">Simulator</Link>
              <NavAuth />
            </div>
          </nav>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}

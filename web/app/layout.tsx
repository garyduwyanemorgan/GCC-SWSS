import "./globals.css";
import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "GCC Soil Water Security Simulator",
  description:
    "Retention curves tell us how water is stored. Water balances tell us whether water is saved.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <nav className="nav">
          <div className="brand">
            GCC&nbsp;SWSS <small>· Soil Water Security Simulator</small>
          </div>
          <div style={{ display: "flex", gap: 18 }}>
            <Link href="/">Overview</Link>
            <Link href="/simulator">Simulator</Link>
          </div>
        </nav>
        {children}
      </body>
    </html>
  );
}

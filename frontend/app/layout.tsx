import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";
import { Toaster } from "react-hot-toast";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "NEXUS OS — Autonomous Software Engineering Operating System",
  description:
    "Enterprise-grade AI-native engineering workforce. Autonomously designs, builds, tests, deploys, monitors, and improves software systems.",
  keywords: ["autonomous engineering", "AI software", "multi-agent", "code generation"],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans antialiased bg-nexus-void text-nexus-text`}>
        <Providers>
          {children}
          <Toaster
            position="bottom-right"
            toastOptions={{
              style: {
                background: "rgba(15,15,25,0.95)",
                border: "1px solid rgba(99,102,241,0.3)",
                color: "#e2e8f0",
                backdropFilter: "blur(12px)",
              },
            }}
          />
        </Providers>
      </body>
    </html>
  );
}

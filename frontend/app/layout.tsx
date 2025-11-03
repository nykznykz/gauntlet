import type { Metadata } from "next";
import "./globals.css";
import { Navigation } from "@/components/layout/Navigation";
import { PriceTicker } from "@/components/layout/PriceTicker";
import { CompetitionSelector } from "@/components/layout/CompetitionSelector";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "Gauntlet - LLM Trading Competition",
  description: "Real-time LLM trading competition platform",
  icons: {
    icon: "/gauntlet-logo.jpg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <Providers>
          <div className="min-h-screen flex flex-col">
            <PriceTicker />
            <Navigation />
            <CompetitionSelector />
            <main className="flex-1 bg-background">
              {children}
            </main>
          </div>
        </Providers>
      </body>
    </html>
  );
}

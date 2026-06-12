"use client";

import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Sidebar } from "@/components/layout/sidebar";
import { TopBar } from "@/components/layout/topbar";
import { useAstraStore } from "@/lib/store";
import { cn } from "@/lib/utils";
import "@/app/globals.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30000,
      retry: 1,
    },
  },
});

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <title>ASTRA-X | Autonomous Defence Readiness Intelligence</title>
        <meta
          name="description"
          content="Multi-agent ML-driven logistics readiness and asset governance platform"
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🛡️</text></svg>" />
      </head>
      <body className="min-h-screen overflow-x-hidden">
        <QueryClientProvider client={queryClient}>
          <AppShell>{children}</AppShell>
        </QueryClientProvider>
      </body>
    </html>
  );
}

function AppShell({ children }: { children: React.ReactNode }) {
  const sidebarOpen = useAstraStore((s) => s.sidebarOpen);

  return (
    <div className="flex min-h-screen relative">
      <Sidebar />
      <main
        className={cn(
          "flex-1 transition-all duration-300",
          sidebarOpen ? "ml-64" : "ml-20",
          "mt-16 p-6"
        )}
      >
        <TopBar />
        <div className="relative z-10 animate-fade-in-up">{children}</div>
      </main>
    </div>
  );
}

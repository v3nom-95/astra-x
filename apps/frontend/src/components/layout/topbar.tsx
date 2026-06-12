"use client";

import React from "react";
import { usePathname } from "next/navigation";
import { useHealth } from "@/lib/hooks";
import { useAstraStore } from "@/lib/store";
import { Badge } from "@/components/ui/badge";
import { Activity, Wifi, WifiOff } from "lucide-react";
import { cn } from "@/lib/utils";

const pageTitles: Record<string, string> = {
  "/": "Operations Dashboard",
  "/upload": "Data Upload",
  "/assets": "Asset Inventory",
  "/agents": "Agent Pipeline",
  "/readiness": "Readiness Analysis",
  "/audit": "Audit Trail",
};

export function TopBar() {
  const pathname = usePathname();
  const { sidebarOpen } = useAstraStore();
  const { data: health, isError } = useHealth();

  const title = pageTitles[pathname] || "ASTRA-X";

  return (
    <header
      className={cn(
        "fixed top-0 right-0 z-30 h-16 border-b border-border/30",
        "bg-background/80 backdrop-blur-xl",
        "flex items-center justify-between px-6",
        "transition-all duration-300",
        sidebarOpen ? "left-64" : "left-20"
      )}
    >
      {/* Page Title */}
      <div>
        <h2 className="text-lg font-semibold tracking-tight">{title}</h2>
        <p className="text-xs text-muted-foreground font-mono">
          {new Date().toLocaleDateString("en-US", {
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric",
          })}
        </p>
      </div>

      {/* Status Indicators */}
      <div className="flex items-center gap-4">
        {/* ML Models Status */}
        {health && (
          <div className="flex items-center gap-2">
            {Object.entries(health.ml_models).map(([model, status]) => (
              <Badge
                key={model}
                variant={status === "ready" ? "success" : "warning"}
                className="text-[10px] uppercase tracking-wider"
              >
                {model}
              </Badge>
            ))}
          </div>
        )}

        {/* Connection Status */}
        <div className="flex items-center gap-2 pl-4 border-l border-border/30">
          {isError ? (
            <>
              <WifiOff className="w-4 h-4 text-cyber-red" />
              <span className="text-xs text-cyber-red font-mono">Offline</span>
            </>
          ) : (
            <>
              <Wifi className="w-4 h-4 text-cyber-green" />
              <span className="text-xs text-cyber-green font-mono">Connected</span>
            </>
          )}
        </div>

        {/* System Activity */}
        <div className="flex items-center gap-1.5 pl-4 border-l border-border/30">
          <Activity className="w-4 h-4 text-cyber-cyan animate-pulse" />
          <span className="text-xs text-muted-foreground font-mono">
            {health?.environment || "dev"}
          </span>
        </div>
      </div>
    </header>
  );
}

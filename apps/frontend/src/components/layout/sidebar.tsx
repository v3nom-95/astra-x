"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Upload,
  Box,
  Bot,
  Shield,
  FileText,
  Activity,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { useAstraStore } from "@/lib/store";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/upload", label: "Upload", icon: Upload },
  { href: "/assets", label: "Assets", icon: Box },
  { href: "/agents", label: "Agents", icon: Bot },
  { href: "/readiness", label: "Readiness", icon: Activity },
  { href: "/audit", label: "Audit", icon: FileText },
];

export function Sidebar() {
  const pathname = usePathname();
  const { sidebarOpen, toggleSidebar } = useAstraStore();

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 z-40 h-screen transition-all duration-300 ease-in-out",
        "bg-gradient-to-b from-[#0a0e17] to-[#0d1321]",
        "border-r border-cyber-cyan/10",
        sidebarOpen ? "w-64" : "w-20"
      )}
    >
      {/* Logo */}
      <div className="flex items-center h-16 px-4 border-b border-border/30">
        <div className="flex items-center gap-3">
          <div className="relative w-10 h-10 flex items-center justify-center">
            <div className="absolute inset-0 bg-gradient-to-br from-cyber-cyan to-cyber-purple rounded-lg opacity-20 animate-pulse-glow" />
            <Shield className="w-6 h-6 text-cyber-cyan relative z-10" />
          </div>
          {sidebarOpen && (
            <div className="animate-fade-in-up">
              <h1 className="text-lg font-bold tracking-wider glow-cyan">
                ASTRA-X
              </h1>
              <p className="text-[10px] text-muted-foreground tracking-widest uppercase">
                Defence Readiness
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex flex-col gap-1 p-3 mt-4">
        {navItems.map((item) => {
          const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group",
                isActive
                  ? "bg-primary/10 text-primary border border-primary/20 shadow-lg shadow-primary/5"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
              )}
            >
              <item.icon
                className={cn(
                  "w-5 h-5 flex-shrink-0 transition-colors",
                  isActive ? "text-cyber-cyan" : "group-hover:text-cyber-cyan/70"
                )}
              />
              {sidebarOpen && (
                <span className="text-sm font-medium">{item.label}</span>
              )}
              {isActive && (
                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-cyber-cyan animate-pulse-glow" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Collapse Toggle */}
      <button
        onClick={toggleSidebar}
        className="absolute bottom-4 right-0 translate-x-1/2 z-50 w-6 h-6 rounded-full bg-card border border-border/50 flex items-center justify-center hover:border-primary/50 transition-colors"
      >
        {sidebarOpen ? (
          <ChevronLeft className="w-3 h-3 text-muted-foreground" />
        ) : (
          <ChevronRight className="w-3 h-3 text-muted-foreground" />
        )}
      </button>

      {/* Status Footer */}
      {sidebarOpen && (
        <div className="absolute bottom-12 left-0 right-0 px-4">
          <div className="glass-card rounded-lg p-3">
            <div className="flex items-center gap-2 mb-2">
              <div className="status-dot status-dot-active" />
              <span className="text-xs text-muted-foreground">System Online</span>
            </div>
            <p className="text-[10px] text-muted-foreground/60 font-mono">
              v1.0.0 • Terminal3 Active
            </p>
          </div>
        </div>
      )}
    </aside>
  );
}

"use client";

import React from "react";
import { useDashboard } from "@/lib/hooks";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Activity,
  Shield,
  Package,
  Wrench,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Bot,
  TrendingUp,
  FileText,
} from "lucide-react";
import { cn } from "@/lib/utils";

export default function DashboardPage() {
  const { data, isLoading, isError } = useDashboard();

  if (isLoading) {
    return <DashboardSkeleton />;
  }

  if (isError || !data) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Card className="max-w-md w-full">
          <CardContent className="p-8 text-center">
            <AlertTriangle className="w-12 h-12 text-cyber-amber mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Connection Issue</h3>
            <p className="text-muted-foreground text-sm">
              Unable to reach ASTRA-X backend. Ensure the API server is running.
            </p>
            <p className="text-xs text-muted-foreground/60 mt-2 font-mono">
              Expected at: {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const { readiness, recent_actions, recent_authorizations, recent_audit, asset_summary } = data;

  return (
    <div className="space-y-6">
      {/* ── Readiness Score Hero ────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Overall Score */}
        <Card className="lg:col-span-1 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-cyber-cyan/10 to-transparent rounded-bl-full" />
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyber-cyan" />
              Overall Readiness
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-end gap-2">
              <span className={cn(
                "text-5xl font-bold font-mono tracking-tighter",
                readiness.overall >= 70 ? "text-cyber-green glow-green" :
                readiness.overall >= 40 ? "text-cyber-amber glow-amber" :
                "text-cyber-red glow-red"
              )}>
                {readiness.overall.toFixed(0)}
              </span>
              <span className="text-lg text-muted-foreground mb-1">%</span>
            </div>
            <Progress value={readiness.overall} className="mt-3" />
            <p className="text-xs text-muted-foreground mt-2">
              {readiness.assets_needing_attention} assets need attention
            </p>
          </CardContent>
        </Card>

        {/* Inventory Health */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground flex items-center gap-2">
              <Package className="w-4 h-4 text-cyber-blue" />
              Inventory Health
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold font-mono text-cyber-cyan">
              {readiness.inventory_health.toFixed(0)}%
            </div>
            <Progress
              value={readiness.inventory_health}
              className="mt-3"
              indicatorClassName="bg-gradient-to-r from-cyan-500 to-blue-500"
            />
            <p className="text-xs text-muted-foreground mt-2">
              Supply chain status
            </p>
          </CardContent>
        </Card>

        {/* Maintenance Health */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground flex items-center gap-2">
              <Wrench className="w-4 h-4 text-cyber-amber" />
              Maintenance Health
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold font-mono text-cyber-amber">
              {readiness.maintenance_health.toFixed(0)}%
            </div>
            <Progress
              value={readiness.maintenance_health}
              className="mt-3"
              indicatorClassName="bg-gradient-to-r from-amber-500 to-orange-500"
            />
            <p className="text-xs text-muted-foreground mt-2">
              Equipment reliability
            </p>
          </CardContent>
        </Card>

        {/* Risk Health */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground flex items-center gap-2">
              <Shield className="w-4 h-4 text-cyber-green" />
              Risk Health
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold font-mono text-cyber-green">
              {readiness.risk_health.toFixed(0)}%
            </div>
            <Progress
              value={readiness.risk_health}
              className="mt-3"
              indicatorClassName="bg-gradient-to-r from-green-500 to-emerald-500"
            />
            <p className="text-xs text-muted-foreground mt-2">
              Operational safety
            </p>
          </CardContent>
        </Card>
      </div>

      {/* ── Stats Row ──────────────────────────────────── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MiniStat label="Total Assets" value={readiness.total_assets} icon={<Package className="w-4 h-4" />} color="cyan" />
        <MiniStat label="Active" value={readiness.active_assets} icon={<CheckCircle className="w-4 h-4" />} color="green" />
        <MiniStat label="Need Attention" value={readiness.assets_needing_attention} icon={<AlertTriangle className="w-4 h-4" />} color="amber" />
        <MiniStat label="Asset Types" value={Object.keys(asset_summary).length} icon={<TrendingUp className="w-4 h-4" />} color="purple" />
      </div>

      {/* ── Activity Feeds ─────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Agent Actions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Bot className="w-5 h-5 text-cyber-cyan" />
              Agent Actions
            </CardTitle>
          </CardHeader>
          <CardContent>
            {recent_actions.length === 0 ? (
              <EmptyState message="No agent actions yet. Upload data and run the pipeline." />
            ) : (
              <div className="space-y-3 max-h-[300px] overflow-y-auto pr-2">
                {recent_actions.slice(0, 8).map((action, i) => (
                  <div key={i} className="flex items-start gap-3 p-2 rounded-lg hover:bg-muted/30 transition-colors">
                    <div className={cn(
                      "w-2 h-2 rounded-full mt-2 flex-shrink-0",
                      action.action.includes("freeze") || action.action.includes("schedule") ? "bg-cyber-red" :
                      action.action.includes("restock") ? "bg-cyber-amber" : "bg-cyber-green"
                    )} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium truncate">{action.asset_id}</span>
                        <Badge variant={
                          action.action.includes("freeze") ? "danger" :
                          action.action.includes("schedule") ? "warning" :
                          action.action.includes("restock") ? "info" : "success"
                        } className="text-[10px]">
                          {action.action}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground truncate mt-0.5">
                        {action.reason}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Authorization Timeline */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Shield className="w-5 h-5 text-cyber-green" />
              Authorization Timeline
            </CardTitle>
          </CardHeader>
          <CardContent>
            {recent_authorizations.length === 0 ? (
              <EmptyState message="No authorization events yet." />
            ) : (
              <div className="space-y-3 max-h-[300px] overflow-y-auto pr-2">
                {recent_authorizations.slice(0, 8).map((auth, i) => (
                  <div key={i} className="flex items-start gap-3 p-2 rounded-lg hover:bg-muted/30 transition-colors">
                    {auth.authorized ? (
                      <CheckCircle className="w-4 h-4 text-cyber-green mt-0.5 flex-shrink-0" />
                    ) : (
                      <XCircle className="w-4 h-4 text-cyber-red mt-0.5 flex-shrink-0" />
                    )}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">{auth.asset_id}</span>
                        <Badge variant={auth.authorized ? "success" : "danger"} className="text-[10px]">
                          {auth.authorized ? "AUTHORIZED" : "DENIED"}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {auth.action} • {auth.policy_applied}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* ── Audit Feed ─────────────────────────────────── */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <FileText className="w-5 h-5 text-cyber-purple" />
            Audit Feed
          </CardTitle>
        </CardHeader>
        <CardContent>
          {recent_audit.length === 0 ? (
            <EmptyState message="No audit entries yet. Run the agent pipeline to generate audit data." />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {recent_audit.slice(0, 6).map((entry, i) => (
                <div key={i} className="glass-card rounded-lg p-3 border border-border/30">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-mono text-muted-foreground">{entry.asset_id}</span>
                    <Badge
                      variant={
                        entry.severity === "CRITICAL" ? "danger" :
                        entry.severity === "WARNING" ? "warning" : "info"
                      }
                      className="text-[10px]"
                    >
                      {entry.severity}
                    </Badge>
                  </div>
                  <p className="text-sm font-medium">{entry.action}</p>
                  <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{entry.reason}</p>
                  <div className="flex items-center gap-1 mt-2">
                    {entry.authorized ? (
                      <CheckCircle className="w-3 h-3 text-cyber-green" />
                    ) : (
                      <XCircle className="w-3 h-3 text-cyber-red" />
                    )}
                    <span className="text-[10px] text-muted-foreground">
                      {entry.agent_name}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// ── Sub-components ────────────────────────────────

function MiniStat({ label, value, icon, color }: {
  label: string; value: number; icon: React.ReactNode; color: string;
}) {
  const colorMap: Record<string, string> = {
    cyan: "text-cyber-cyan",
    green: "text-cyber-green",
    amber: "text-cyber-amber",
    red: "text-cyber-red",
    purple: "text-cyber-purple",
    blue: "text-cyber-blue",
  };

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-muted-foreground">{label}</p>
            <p className={cn("text-2xl font-bold font-mono", colorMap[color] || "text-foreground")}>
              {value}
            </p>
          </div>
          <div className={cn("p-2 rounded-lg bg-muted/50", colorMap[color] || "")}>
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-8 text-center">
      <div className="w-12 h-12 rounded-full bg-muted/50 flex items-center justify-center mb-3">
        <Activity className="w-6 h-6 text-muted-foreground" />
      </div>
      <p className="text-sm text-muted-foreground">{message}</p>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i}>
            <CardContent className="p-6">
              <div className="h-4 bg-muted/50 rounded w-24 mb-4 animate-pulse" />
              <div className="h-10 bg-muted/50 rounded w-20 animate-pulse" />
              <div className="h-3 bg-muted/50 rounded w-full mt-4 animate-pulse" />
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}


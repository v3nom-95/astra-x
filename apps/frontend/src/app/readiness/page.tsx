"use client";

import React from "react";
import { useDashboard, usePredict } from "@/lib/hooks";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import {
  Activity,
  Package,
  Wrench,
  Shield,
  Loader2,
  Play,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";

export default function ReadinessPage() {
  const { data: dashboard, isLoading } = useDashboard();
  const predict = usePredict();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const readiness = dashboard?.readiness;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Readiness Analysis</h1>
          <p className="text-muted-foreground mt-1">
            Operational readiness scores and predictions
          </p>
        </div>
        <Button
          variant="outline"
          onClick={() => predict.mutate(undefined)}
          disabled={predict.isPending}
        >
          {predict.isPending ? (
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
          ) : (
            <Play className="w-4 h-4 mr-2" />
          )}
          Refresh Predictions
        </Button>
      </div>

      {/* ── Overall Readiness ──────────────────────────── */}
      {readiness && (
        <>
          <Card className="relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-cyber-cyan/5 via-transparent to-cyber-purple/5" />
            <CardContent className="p-8 relative z-10">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground uppercase tracking-wider">
                    Overall Readiness Score
                  </p>
                  <div className="flex items-end gap-3 mt-2">
                    <span className={cn(
                      "text-7xl font-bold font-mono tracking-tighter",
                      readiness.overall >= 70 ? "text-cyber-green glow-green" :
                      readiness.overall >= 40 ? "text-cyber-amber glow-amber" :
                      "text-cyber-red glow-red"
                    )}>
                      {readiness.overall.toFixed(0)}
                    </span>
                    <span className="text-2xl text-muted-foreground mb-3">/ 100</span>
                  </div>
                  <Progress value={readiness.overall} className="mt-4 max-w-sm h-2" />
                </div>
                <div className="text-right space-y-3">
                  <div className="flex items-center gap-2 justify-end">
                    <span className="text-sm text-muted-foreground">Total Assets</span>
                    <span className="text-lg font-bold font-mono">{readiness.total_assets}</span>
                  </div>
                  <div className="flex items-center gap-2 justify-end">
                    <span className="text-sm text-muted-foreground">Active</span>
                    <span className="text-lg font-bold font-mono text-cyber-green">{readiness.active_assets}</span>
                  </div>
                  <div className="flex items-center gap-2 justify-end">
                    <span className="text-sm text-muted-foreground">Attention Needed</span>
                    <span className="text-lg font-bold font-mono text-cyber-amber">{readiness.assets_needing_attention}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* ── Health Breakdown ───────────────────────── */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <HealthCard
              title="Inventory Health"
              score={readiness.inventory_health}
              icon={<Package className="w-6 h-6" />}
              color="cyan"
              description="Supply chain readiness based on days-remaining forecasts"
              metrics={[
                { label: "Supply Status", value: readiness.inventory_health >= 70 ? "Adequate" : "Low" },
              ]}
            />
            <HealthCard
              title="Maintenance Health"
              score={readiness.maintenance_health}
              icon={<Wrench className="w-6 h-6" />}
              color="amber"
              description="Equipment reliability based on failure probability analysis"
              metrics={[
                { label: "Reliability", value: readiness.maintenance_health >= 70 ? "Good" : "At Risk" },
              ]}
            />
            <HealthCard
              title="Risk Health"
              score={readiness.risk_health}
              icon={<Shield className="w-6 h-6" />}
              color="green"
              description="Operational safety based on anomaly detection"
              metrics={[
                { label: "Safety Level", value: readiness.risk_health >= 70 ? "Secure" : "Elevated" },
              ]}
            />
          </div>

          {/* ── Asset Distribution ─────────────────────── */}
          {dashboard?.asset_summary && Object.keys(dashboard.asset_summary).length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-cyber-cyan" />
                  Asset Distribution
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {Object.entries(dashboard.asset_summary).map(([type, count]) => (
                    <div key={type} className="glass-card rounded-lg p-4 text-center">
                      <p className="text-xs text-muted-foreground uppercase tracking-wider">{type}</p>
                      <p className="text-2xl font-bold font-mono text-cyber-cyan mt-1">{count}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}

      {/* ── Prediction Results ─────────────────────────── */}
      {predict.data && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Latest Prediction Results</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="text-center">
                <p className="text-xs text-muted-foreground">Processed</p>
                <p className="text-xl font-bold font-mono">{predict.data.total_assets}</p>
              </div>
              <div className="text-center">
                <p className="text-xs text-muted-foreground">High Risk</p>
                <p className="text-xl font-bold font-mono text-cyber-red">{predict.data.high_risk_count}</p>
              </div>
              <div className="text-center">
                <p className="text-xs text-muted-foreground">Need Service</p>
                <p className="text-xl font-bold font-mono text-cyber-amber">{predict.data.needs_service_count}</p>
              </div>
              <div className="text-center">
                <p className="text-xs text-muted-foreground">Need Restock</p>
                <p className="text-xl font-bold font-mono text-cyber-cyan">{predict.data.needs_restock_count}</p>
              </div>
            </div>

            <div className="space-y-2">
              {predict.data.predictions.slice(0, 10).map((pred) => (
                <div key={pred.asset_id} className="flex items-center gap-3 p-3 rounded-lg bg-muted/20 border border-border/20">
                  <span className="text-sm font-mono font-semibold text-cyber-cyan w-24">{pred.asset_id}</span>
                  {pred.inventory && (
                    <Badge variant={pred.inventory.needs_restock ? "warning" : "success"} className="text-[10px]">
                      {pred.inventory.days_remaining.toFixed(0)}d remaining
                    </Badge>
                  )}
                  {pred.maintenance && (
                    <Badge variant={pred.maintenance.needs_service ? "danger" : "success"} className="text-[10px]">
                      {(pred.maintenance.failure_probability * 100).toFixed(0)}% failure
                    </Badge>
                  )}
                  {pred.risk && (
                    <Badge
                      variant={
                        pred.risk.risk === "HIGH" ? "danger" :
                        pred.risk.risk === "MEDIUM" ? "warning" : "success"
                      }
                      className="text-[10px]"
                    >
                      {pred.risk.risk} risk
                    </Badge>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function HealthCard({
  title, score, icon, color, description, metrics,
}: {
  title: string; score: number; icon: React.ReactNode; color: string;
  description: string; metrics: { label: string; value: string }[];
}) {
  const colorMap: Record<string, { text: string; bg: string; glow: string; gradient: string }> = {
    cyan: { text: "text-cyber-cyan", bg: "bg-cyber-cyan/10", glow: "glow-cyan", gradient: "from-cyan-500 to-blue-500" },
    amber: { text: "text-cyber-amber", bg: "bg-cyber-amber/10", glow: "glow-amber", gradient: "from-amber-500 to-orange-500" },
    green: { text: "text-cyber-green", bg: "bg-cyber-green/10", glow: "glow-green", gradient: "from-green-500 to-emerald-500" },
    red: { text: "text-cyber-red", bg: "bg-cyber-red/10", glow: "glow-red", gradient: "from-red-500 to-rose-500" },
  };
  const c = colorMap[color] || colorMap.cyan;

  return (
    <Card className="relative overflow-hidden">
      <div className={cn("absolute top-0 right-0 w-24 h-24 rounded-bl-full", c.bg)} />
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <div className={cn("p-2 rounded-lg", c.bg, c.text)}>{icon}</div>
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-end gap-2 mb-3">
          <span className={cn("text-4xl font-bold font-mono", c.text, c.glow)}>
            {score.toFixed(0)}
          </span>
          <span className="text-lg text-muted-foreground mb-1">%</span>
        </div>
        <Progress
          value={score}
          className="h-2"
          indicatorClassName={cn("bg-gradient-to-r", c.gradient)}
        />
        <p className="text-xs text-muted-foreground mt-3">{description}</p>
        <div className="mt-3 space-y-1">
          {metrics.map((m, i) => (
            <div key={i} className="flex justify-between text-xs">
              <span className="text-muted-foreground">{m.label}</span>
              <span className="font-medium">{m.value}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

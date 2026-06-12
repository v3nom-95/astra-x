"use client";

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useRunPipeline } from "@/lib/hooks";
import { useAstraStore } from "@/lib/store";
import {
  Bot,
  Play,
  Loader2,
  Package,
  Wrench,
  AlertTriangle,
  Shield,
  ChevronRight,
  CheckCircle,
  XCircle,
  Zap,
  ArrowDown,
} from "lucide-react";
import { cn } from "@/lib/utils";

const PIPELINE_STEPS = [
  { name: "ML Prediction", icon: Zap, description: "Run inventory, maintenance, and risk models" },
  { name: "Inventory Agent", icon: Package, description: "Analyze supply levels and restock needs" },
  { name: "Maintenance Agent", icon: Wrench, description: "Evaluate equipment failure probability" },
  { name: "Risk Agent", icon: AlertTriangle, description: "Detect anomalous operational patterns" },
  { name: "Command Agent", icon: Bot, description: "Coordinate and prioritize all decisions" },
  { name: "Terminal3 Auth", icon: Shield, description: "Authorize protected actions via policies" },
  { name: "Audit Agent", icon: CheckCircle, description: "Generate audit trail for all decisions" },
];

export default function AgentsPage() {
  const runPipeline = useRunPipeline();
  const lastRun = useAstraStore((s) => s.lastPipelineRun);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Agent Pipeline</h1>
          <p className="text-muted-foreground mt-1">
            LangGraph-orchestrated multi-agent workflow
          </p>
        </div>
        <Button
          variant="cyber"
          onClick={() => runPipeline.mutate(undefined)}
          disabled={runPipeline.isPending}
        >
          {runPipeline.isPending ? (
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
          ) : (
            <Play className="w-4 h-4 mr-2" />
          )}
          Run Pipeline
        </Button>
      </div>

      {/* ── Pipeline Visualization ─────────────────────── */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Bot className="w-5 h-5 text-cyber-cyan" />
            Pipeline Flow
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center gap-1">
            {PIPELINE_STEPS.map((step, i) => (
              <React.Fragment key={step.name}>
                <div className={cn(
                  "w-full max-w-md glass-card rounded-lg p-4 flex items-center gap-4 transition-all duration-300",
                  "hover:border-cyber-cyan/30 hover:shadow-lg hover:shadow-cyber-cyan/5",
                  lastRun ? "border-cyber-green/20" : "border-border/30"
                )}>
                  <div className={cn(
                    "w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0",
                    lastRun ? "bg-cyber-green/10" : "bg-muted/50"
                  )}>
                    <step.icon className={cn(
                      "w-5 h-5",
                      lastRun ? "text-cyber-green" : "text-muted-foreground"
                    )} />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-semibold">{step.name}</p>
                    <p className="text-xs text-muted-foreground">{step.description}</p>
                  </div>
                  {lastRun && <CheckCircle className="w-4 h-4 text-cyber-green" />}
                </div>
                {i < PIPELINE_STEPS.length - 1 && (
                  <ArrowDown className="w-4 h-4 text-muted-foreground/40 my-1" />
                )}
              </React.Fragment>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* ── Agent Decisions Timeline ───────────────────── */}
      {lastRun && lastRun.decisions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Agent Decisions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="relative">
              {/* Timeline line */}
              <div className="absolute left-[19px] top-0 bottom-0 w-px bg-border/50" />

              <div className="space-y-4">
                {lastRun.decisions.map((decision, i) => (
                  <div key={i} className="flex gap-4 relative">
                    <div className={cn(
                      "w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 z-10 border-2",
                      decision.action.includes("freeze") ? "bg-cyber-red/10 border-cyber-red/30" :
                      decision.action.includes("schedule") ? "bg-cyber-amber/10 border-cyber-amber/30" :
                      decision.action.includes("restock") ? "bg-cyber-cyan/10 border-cyber-cyan/30" :
                      "bg-cyber-green/10 border-cyber-green/30"
                    )}>
                      {decision.action.includes("freeze") ? <AlertTriangle className="w-4 h-4 text-cyber-red" /> :
                       decision.action.includes("schedule") ? <Wrench className="w-4 h-4 text-cyber-amber" /> :
                       decision.action.includes("restock") ? <Package className="w-4 h-4 text-cyber-cyan" /> :
                       <CheckCircle className="w-4 h-4 text-cyber-green" />}
                    </div>
                    <div className="flex-1 glass-card rounded-lg p-4 border border-border/20">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-mono font-semibold text-cyber-cyan">
                          {decision.asset_id}
                        </span>
                        <Badge
                          variant={
                            decision.action.includes("freeze") ? "danger" :
                            decision.action.includes("schedule") ? "warning" :
                            decision.action.includes("restock") ? "info" : "success"
                          }
                        >
                          {decision.action}
                        </Badge>
                        <span className="text-xs text-muted-foreground ml-auto font-mono">
                          {(decision.confidence * 100).toFixed(0)}% confidence
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground">{decision.reason}</p>
                      <p className="text-[10px] text-muted-foreground/50 mt-1">Agent: {decision.agent_name}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* ── Authorization Results ──────────────────────── */}
      {lastRun && lastRun.authorizations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Shield className="w-5 h-5 text-cyber-green" />
              Terminal3 Authorization Results
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {lastRun.authorizations.map((auth, i) => (
                <div key={i} className="glass-card rounded-lg p-4 border border-border/20">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-mono font-semibold">{auth.asset_id}</span>
                    {auth.authorization.authorized ? (
                      <Badge variant="success" className="flex items-center gap-1">
                        <CheckCircle className="w-3 h-3" /> AUTHORIZED
                      </Badge>
                    ) : (
                      <Badge variant="danger" className="flex items-center gap-1">
                        <XCircle className="w-3 h-3" /> DENIED
                      </Badge>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground">{auth.audit.action}</p>
                  <p className="text-[10px] text-muted-foreground/60 mt-1">
                    Policy: {auth.authorization.policy_applied}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

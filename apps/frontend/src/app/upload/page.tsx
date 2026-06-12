"use client";

import React, { useState, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { useUpload, useRunPipeline } from "@/lib/hooks";
import { useAstraStore } from "@/lib/store";
import {
  Upload,
  FileUp,
  Play,
  CheckCircle,
  AlertTriangle,
  Loader2,
  FileText,
  Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string[][]>([]);
  const [dragActive, setDragActive] = useState(false);

  const upload = useUpload();
  const runPipeline = useRunPipeline();
  const lastUpload = useAstraStore((s) => s.lastUpload);
  const lastPipelineRun = useAstraStore((s) => s.lastPipelineRun);

  const handleFile = useCallback((f: File) => {
    setFile(f);
    if (f.name.match(/\.(xlsx|xls)$/i)) {
      setPreview([]);
      return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      const lines = text.split("\n").filter(Boolean);
      const parsed = lines.map((line) => line.split(",").map((s) => s.trim()));
      setPreview(parsed.slice(0, 11)); // Header + 10 rows
    };
    reader.readAsText(f);
  }, []);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    const f = e.dataTransfer.files[0];
    if (f && f.name.match(/\.(csv|xlsx|xls)$/i)) handleFile(f);
  }, [handleFile]);

  const onFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) handleFile(f);
  }, [handleFile]);

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Data Upload</h1>
        <p className="text-muted-foreground mt-1">
          Upload operational datasets to train ML models and run the agent pipeline
        </p>
      </div>

      {/* ── Upload Zone ────────────────────────────────── */}
      <Card>
        <CardContent className="p-8">
          <div
            onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
            onDragLeave={() => setDragActive(false)}
            onDrop={onDrop}
            className={cn(
              "relative border-2 border-dashed rounded-xl p-12 text-center transition-all duration-300 cursor-pointer",
              dragActive
                ? "border-cyber-cyan bg-cyber-cyan/5 shadow-lg shadow-cyber-cyan/10"
                : "border-border/50 hover:border-primary/30 hover:bg-muted/20"
            )}
            onClick={() => document.getElementById("csv-input")?.click()}
          >
            <input
              id="csv-input"
              type="file"
              accept=".csv, .xlsx, .xls"
              onChange={onFileSelect}
              className="hidden"
            />
            <div className="flex flex-col items-center gap-4">
              <div className={cn(
                "w-16 h-16 rounded-2xl flex items-center justify-center transition-colors",
                dragActive ? "bg-cyber-cyan/20" : "bg-muted/50"
              )}>
                <FileUp className={cn("w-8 h-8", dragActive ? "text-cyber-cyan" : "text-muted-foreground")} />
              </div>
              <div>
                <p className="text-lg font-medium">
                  {file ? file.name : "Drop your CSV file here"}
                </p>
                <p className="text-sm text-muted-foreground mt-1">
                  or click to browse • Accepts .csv and .xlsx files
                </p>
              </div>
              {file && (
                <div className="flex gap-2 mt-2">
                  <Badge variant="info">
                    <FileText className="w-3 h-3 mr-1" />
                    {(file.size / 1024).toFixed(1)} KB
                  </Badge>
                  {file.name.match(/\.(xlsx|xls)$/i) && (
                    <Badge variant="secondary" className="border-cyber-cyan/30 text-cyber-cyan text-xs">
                      Excel File (Preview not shown, ready to upload)
                    </Badge>
                  )}
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ── Preview ────────────────────────────────────── */}
      {preview.length > 0 && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-base">Data Preview</CardTitle>
            <Badge variant="secondary">{preview.length - 1} rows shown</Badge>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    {preview[0]?.map((header, i) => (
                      <TableHead key={i} className="text-xs uppercase tracking-wider text-cyber-cyan">
                        {header}
                      </TableHead>
                    ))}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {preview.slice(1).map((row, i) => (
                    <TableRow key={i}>
                      {row.map((cell, j) => (
                        <TableCell key={j}>{cell}</TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* ── Action Buttons ─────────────────────────────── */}
      {file && (
        <div className="flex flex-wrap gap-4">
          <Button
            variant="cyber"
            size="lg"
            onClick={() => upload.mutate(file)}
            disabled={upload.isPending}
          >
            {upload.isPending ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Upload className="w-4 h-4 mr-2" />
            )}
            Upload & Train Models
          </Button>

          {lastUpload && (
            <Button
              variant="outline"
              size="lg"
              onClick={() => runPipeline.mutate(undefined)}
              disabled={runPipeline.isPending}
            >
              {runPipeline.isPending ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Play className="w-4 h-4 mr-2" />
              )}
              Run Agent Pipeline
            </Button>
          )}
        </div>
      )}

      {/* ── Upload Result ──────────────────────────────── */}
      {lastUpload && (
        <Card className={cn(lastUpload.assets_loaded === 0 ? "border-cyber-red/20" : "border-cyber-green/20")}>
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              {lastUpload.assets_loaded === 0 ? (
                <AlertTriangle className="w-6 h-6 text-cyber-red flex-shrink-0 mt-0.5" />
              ) : (
                <CheckCircle className="w-6 h-6 text-cyber-green flex-shrink-0 mt-0.5" />
              )}
              <div>
                <h3 className={cn("font-semibold", lastUpload.assets_loaded === 0 ? "text-cyber-red" : "text-cyber-green")}>
                  {lastUpload.message}
                </h3>
                <div className="flex gap-4 mt-2">
                  <Badge variant={lastUpload.assets_loaded === 0 ? "danger" : "success"}>
                    {lastUpload.assets_loaded} assets loaded
                  </Badge>
                  {lastUpload.batch_id && (
                    <Badge variant="secondary">Batch: {lastUpload.batch_id}</Badge>
                  )}
                </div>
                {lastUpload.validation_errors.length > 0 && (
                  <div className="mt-3">
                    {lastUpload.validation_errors.map((err, i) => (
                      <p key={i} className="text-xs text-cyber-amber flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3" /> {err}
                      </p>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* ── Pipeline Result ────────────────────────────── */}
      {lastPipelineRun && (
        <Card className="border-cyber-cyan/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Zap className="w-5 h-5 text-cyber-cyan" />
              Pipeline Results
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard label="Assets Processed" value={lastPipelineRun.summary.total_assets} />
              <StatCard label="Actions Taken" value={lastPipelineRun.summary.total_actions} color="cyan" />
              <StatCard label="Authorized" value={lastPipelineRun.summary.authorized_count} color="green" />
              <StatCard label="High Risk" value={lastPipelineRun.summary.high_risk_count} color="red" />
            </div>

            {/* Decision List */}
            <div className="mt-6 space-y-2">
              <h4 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">Decisions</h4>
              {lastPipelineRun.decisions.map((d, i) => (
                <div key={i} className="flex items-center gap-3 p-3 rounded-lg bg-muted/20 border border-border/20">
                  <Badge
                    variant={
                      d.action.includes("freeze") ? "danger" :
                      d.action.includes("schedule") ? "warning" :
                      d.action.includes("restock") ? "info" : "success"
                    }
                  >
                    {d.action}
                  </Badge>
                  <span className="text-sm font-mono">{d.asset_id}</span>
                  <span className="text-xs text-muted-foreground flex-1 truncate">{d.reason}</span>
                  <span className="text-xs font-mono text-muted-foreground">
                    {(d.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function StatCard({ label, value, color }: { label: string; value: number; color?: string }) {
  const colorClass = color === "cyan" ? "text-cyber-cyan" :
    color === "green" ? "text-cyber-green" :
    color === "red" ? "text-cyber-red" :
    color === "amber" ? "text-cyber-amber" : "text-foreground";

  return (
    <div className="glass-card rounded-lg p-4 text-center">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className={cn("text-2xl font-bold font-mono mt-1", colorClass)}>{value}</p>
    </div>
  );
}

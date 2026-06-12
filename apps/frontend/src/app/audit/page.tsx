"use client";

import React, { useState } from "react";
import { useAudit } from "@/lib/hooks";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import {
  FileText,
  ChevronLeft,
  ChevronRight,
  CheckCircle,
  XCircle,
  Loader2,
  Filter,
  AlertTriangle,
  Info,
  AlertOctagon,
} from "lucide-react";
import { cn, formatDate } from "@/lib/utils";

const SEVERITY_FILTERS = ["ALL", "CRITICAL", "WARNING", "INFO"];

export default function AuditPage() {
  const [page, setPage] = useState(1);
  const [severityFilter, setSeverityFilter] = useState("ALL");

  const { data, isLoading } = useAudit(
    page,
    severityFilter === "ALL" ? undefined : { severity: severityFilter }
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Audit Trail</h1>
        <p className="text-muted-foreground mt-1">
          Complete decision history with authorization verification
        </p>
      </div>

      {/* ── Severity Filter ────────────────────────────── */}
      <div className="flex items-center gap-3">
        <Filter className="w-4 h-4 text-muted-foreground" />
        <div className="flex gap-2">
          {SEVERITY_FILTERS.map((sev) => (
            <Button
              key={sev}
              variant={severityFilter === sev ? "default" : "outline"}
              size="sm"
              onClick={() => { setSeverityFilter(sev); setPage(1); }}
              className="text-xs"
            >
              {sev === "CRITICAL" && <AlertOctagon className="w-3 h-3 mr-1 text-cyber-red" />}
              {sev === "WARNING" && <AlertTriangle className="w-3 h-3 mr-1 text-cyber-amber" />}
              {sev === "INFO" && <Info className="w-3 h-3 mr-1 text-cyber-cyan" />}
              {sev}
            </Button>
          ))}
        </div>
        {data && (
          <span className="text-xs text-muted-foreground ml-auto font-mono">
            {data.total} entries
          </span>
        )}
      </div>

      {/* ── Audit Table ────────────────────────────────── */}
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
            </div>
          ) : !data || data.entries.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12">
              <FileText className="w-12 h-12 text-muted-foreground/50 mb-3" />
              <p className="text-muted-foreground">No audit entries found.</p>
              <p className="text-xs text-muted-foreground/60 mt-1">
                Run the agent pipeline to generate audit data.
              </p>
            </div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-12">Status</TableHead>
                    <TableHead>Asset</TableHead>
                    <TableHead>Action</TableHead>
                    <TableHead>Agent</TableHead>
                    <TableHead>Severity</TableHead>
                    <TableHead>Reason</TableHead>
                    <TableHead>Time</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.entries.map((entry) => (
                    <TableRow key={entry.id}>
                      <TableCell>
                        {entry.authorized ? (
                          <CheckCircle className="w-4 h-4 text-cyber-green" />
                        ) : (
                          <XCircle className="w-4 h-4 text-cyber-red" />
                        )}
                      </TableCell>
                      <TableCell className="font-semibold text-cyber-cyan">
                        {entry.asset_id}
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            entry.action.includes("freeze") ? "danger" :
                            entry.action.includes("schedule") ? "warning" :
                            entry.action.includes("restock") ? "info" : "success"
                          }
                          className="text-[10px]"
                        >
                          {entry.action}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground">
                        {entry.agent_name}
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            entry.severity === "CRITICAL" ? "danger" :
                            entry.severity === "WARNING" ? "warning" : "info"
                          }
                          className="text-[10px]"
                        >
                          {entry.severity}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground max-w-[300px] truncate">
                        {entry.reason}
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground whitespace-nowrap">
                        {entry.created_at ? formatDate(entry.created_at) : "—"}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {/* Pagination */}
              <div className="flex items-center justify-between px-4 py-3 border-t border-border/30">
                <p className="text-xs text-muted-foreground">
                  Page {data.page} • Showing {data.entries.length} of {data.total}
                </p>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(Math.max(1, page - 1))}
                    disabled={page <= 1}
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(page + 1)}
                    disabled={data.entries.length < data.page_size}
                  >
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

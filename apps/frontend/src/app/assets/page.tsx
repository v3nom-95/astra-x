"use client";

import React, { useState } from "react";
import { useAssets } from "@/lib/hooks";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { Box, Filter, Loader2, Thermometer, Wrench, TrendingDown } from "lucide-react";
import { cn } from "@/lib/utils";

const ASSET_TYPES = ["ALL", "TRUCK", "DRONE", "GENERATOR", "RADIO", "VEHICLE", "MEDEVAC", "FORKLIFT", "TRAILER"];

export default function AssetsPage() {
  const [typeFilter, setTypeFilter] = useState<string>("ALL");
  const { data: assets, isLoading } = useAssets(
    typeFilter === "ALL" ? undefined : { type: typeFilter }
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Asset Inventory</h1>
          <p className="text-muted-foreground mt-1">
            Operational assets tracked by ASTRA-X
          </p>
        </div>
        <Badge variant="info" className="text-sm">
          {assets?.length || 0} assets
        </Badge>
      </div>

      {/* ── Type Filter ────────────────────────────────── */}
      <div className="flex flex-wrap gap-2">
        {ASSET_TYPES.map((type) => (
          <Button
            key={type}
            variant={typeFilter === type ? "default" : "outline"}
            size="sm"
            onClick={() => setTypeFilter(type)}
            className="text-xs"
          >
            {type}
          </Button>
        ))}
      </div>

      {/* ── Asset Table ────────────────────────────────── */}
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
            </div>
          ) : !assets || assets.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12">
              <Box className="w-12 h-12 text-muted-foreground/50 mb-3" />
              <p className="text-muted-foreground">No assets found. Upload a CSV to get started.</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Asset ID</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Inventory</TableHead>
                  <TableHead className="text-right">Usage Rate</TableHead>
                  <TableHead className="text-right">Service Days</TableHead>
                  <TableHead className="text-right">Temperature</TableHead>
                  <TableHead className="text-right">Repairs</TableHead>
                  <TableHead>Location</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {assets.map((asset) => (
                  <TableRow key={asset.asset_id}>
                    <TableCell className="font-semibold text-cyber-cyan">{asset.asset_id}</TableCell>
                    <TableCell>
                      <Badge variant="secondary" className="text-[10px]">{asset.type}</Badge>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          asset.status === "ACTIVE" ? "success" :
                          asset.status === "MAINTENANCE" ? "warning" :
                          "secondary"
                        }
                        className="text-[10px]"
                      >
                        <span className={cn(
                          "w-1.5 h-1.5 rounded-full mr-1 inline-block",
                          asset.status === "ACTIVE" ? "bg-cyber-green" :
                          asset.status === "MAINTENANCE" ? "bg-cyber-amber" : "bg-muted-foreground"
                        )} />
                        {asset.status}
                      </Badge>
                    </TableCell>
                    <TableCell className={cn(
                      "text-right",
                      asset.inventory < 20 ? "text-cyber-red font-semibold" : ""
                    )}>
                      {asset.inventory}
                      {asset.inventory < 20 && <TrendingDown className="w-3 h-3 inline ml-1 text-cyber-red" />}
                    </TableCell>
                    <TableCell className={cn(
                      "text-right",
                      asset.usage_rate > 50 ? "text-cyber-amber" : ""
                    )}>
                      {asset.usage_rate}
                    </TableCell>
                    <TableCell className={cn(
                      "text-right",
                      asset.service_days > 150 ? "text-cyber-amber" : ""
                    )}>
                      {asset.service_days}d
                    </TableCell>
                    <TableCell className={cn(
                      "text-right",
                      asset.temperature > 70 ? "text-cyber-red" : ""
                    )}>
                      {asset.temperature}°
                      {asset.temperature > 70 && <Thermometer className="w-3 h-3 inline ml-1 text-cyber-red" />}
                    </TableCell>
                    <TableCell className={cn(
                      "text-right",
                      asset.repairs > 4 ? "text-cyber-red" : ""
                    )}>
                      {asset.repairs}
                      {asset.repairs > 4 && <Wrench className="w-3 h-3 inline ml-1 text-cyber-amber" />}
                    </TableCell>
                    <TableCell className="text-muted-foreground text-xs">{asset.location}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

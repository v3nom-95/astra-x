/**
 * ASTRA-X React Query hooks for data fetching.
 */
"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAstraStore } from "@/lib/store";

export function useDashboard() {
  const setDashboard = useAstraStore((s) => s.setDashboard);
  return useQuery({
    queryKey: ["dashboard"],
    queryFn: async () => {
      const data = await api.dashboard();
      setDashboard(data);
      return data;
    },
    refetchInterval: 30000, // Refresh every 30s
  });
}

export function useAssets(filters?: { status?: string; type?: string }) {
  return useQuery({
    queryKey: ["assets", filters],
    queryFn: () => api.getAssets(filters),
  });
}

export function useAudit(page = 1, filters?: { asset_id?: string; severity?: string }) {
  return useQuery({
    queryKey: ["audit", page, filters],
    queryFn: () => api.getAudit(page, 50, filters),
  });
}

export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: api.health,
    refetchInterval: 60000,
  });
}

export function useUpload() {
  const queryClient = useQueryClient();
  const setLastUpload = useAstraStore((s) => s.setLastUpload);

  return useMutation({
    mutationFn: api.uploadCSV,
    onSuccess: (data) => {
      setLastUpload(data);
      queryClient.invalidateQueries({ queryKey: ["assets"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useRunPipeline() {
  const queryClient = useQueryClient();
  const setLastPipelineRun = useAstraStore((s) => s.setLastPipelineRun);

  return useMutation({
    mutationFn: (assetIds?: string[]) => api.runAgents(assetIds),
    onSuccess: (data) => {
      setLastPipelineRun(data);
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["audit"] });
      queryClient.invalidateQueries({ queryKey: ["assets"] });
    },
  });
}

export function usePredict() {
  return useMutation({
    mutationFn: (assetIds?: string[]) => api.predict(assetIds),
  });
}

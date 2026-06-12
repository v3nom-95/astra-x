/**
 * ASTRA-X API Client.
 * Centralized HTTP client for all backend communication.
 */
import type {
  Asset,
  DashboardResponse,
  BatchPredictionResponse,
  AgentRunResponse,
  AuditResponse,
  UploadResponse,
  HealthResponse,
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const error = await res.text();
    throw new Error(`API Error ${res.status}: ${error}`);
  }

  return res.json();
}

export const api = {
  // Health
  health: () => request<HealthResponse>("/health"),

  // Dashboard
  dashboard: () => request<DashboardResponse>("/dashboard"),

  // Assets
  getAssets: (filters?: { status?: string; type?: string }) => {
    const params = new URLSearchParams();
    if (filters?.status) params.set("status", filters.status);
    if (filters?.type) params.set("asset_type", filters.type);
    const qs = params.toString();
    return request<Asset[]>(`/assets${qs ? `?${qs}` : ""}`);
  },

  // Upload
  uploadCSV: async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append("file", file);
    const url = `${API_BASE}/upload`;
    const res = await fetch(url, { method: "POST", body: formData });
    if (!res.ok) throw new Error(`Upload failed: ${res.statusText}`);
    return res.json();
  },

  // Predictions
  predict: (assetIds?: string[]) =>
    request<BatchPredictionResponse>("/predict", {
      method: "POST",
      body: JSON.stringify(assetIds || null),
    }),

  // Agent Pipeline
  runAgents: (assetIds?: string[]) =>
    request<AgentRunResponse>("/agent/run", {
      method: "POST",
      body: JSON.stringify({ asset_ids: assetIds || null }),
    }),

  // Audit
  getAudit: (page = 1, pageSize = 50, filters?: { asset_id?: string; severity?: string }) => {
    const params = new URLSearchParams({
      page: String(page),
      page_size: String(pageSize),
    });
    if (filters?.asset_id) params.set("asset_id", filters.asset_id);
    if (filters?.severity) params.set("severity", filters.severity);
    return request<AuditResponse>(`/audit?${params}`);
  },
};

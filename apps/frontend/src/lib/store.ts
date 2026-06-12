/**
 * ASTRA-X Zustand Store.
 * Global state management for the application.
 */
import { create } from "zustand";
import type {
  DashboardResponse,
  AgentRunResponse,
  UploadResponse,
} from "@/types";

interface AstraStore {
  // Dashboard state
  dashboard: DashboardResponse | null;
  setDashboard: (data: DashboardResponse) => void;

  // Pipeline results
  lastPipelineRun: AgentRunResponse | null;
  setLastPipelineRun: (data: AgentRunResponse) => void;

  // Upload state
  lastUpload: UploadResponse | null;
  setLastUpload: (data: UploadResponse) => void;

  // UI state
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  isLoading: boolean;
  setLoading: (loading: boolean) => void;

  // Active analysis
  activeAssetId: string | null;
  setActiveAssetId: (id: string | null) => void;
}

export const useAstraStore = create<AstraStore>((set) => ({
  // Dashboard
  dashboard: null,
  setDashboard: (data) => set({ dashboard: data }),

  // Pipeline
  lastPipelineRun: null,
  setLastPipelineRun: (data) => set({ lastPipelineRun: data }),

  // Upload
  lastUpload: null,
  setLastUpload: (data) => set({ lastUpload: data }),

  // UI
  sidebarOpen: true,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  isLoading: false,
  setLoading: (loading) => set({ isLoading: loading }),

  // Active
  activeAssetId: null,
  setActiveAssetId: (id) => set({ activeAssetId: id }),
}));

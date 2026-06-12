/**
 * ASTRA-X TypeScript type definitions.
 */

export interface Asset {
  id: number;
  asset_id: string;
  type: string;
  inventory: number;
  usage_rate: number;
  service_days: number;
  temperature: number;
  repairs: number;
  location: string;
  status: string;
  created_at: string;
}

export interface InventoryPrediction {
  asset_id: string;
  days_remaining: number;
  needs_restock: boolean;
}

export interface MaintenancePrediction {
  asset_id: string;
  failure_probability: number;
  needs_service: boolean;
}

export interface RiskPrediction {
  asset_id: string;
  risk: "HIGH" | "MEDIUM" | "LOW";
  anomaly_score: number;
}

export interface PredictionResponse {
  asset_id: string;
  inventory: InventoryPrediction | null;
  maintenance: MaintenancePrediction | null;
  risk: RiskPrediction | null;
}

export interface BatchPredictionResponse {
  batch_id: string;
  predictions: PredictionResponse[];
  total_assets: number;
  high_risk_count: number;
  needs_service_count: number;
  needs_restock_count: number;
}

export interface AgentDecision {
  agent_name: string;
  asset_id: string;
  action: string;
  reason: string;
  confidence: number;
}

export interface AgentRunResponse {
  batch_id: string;
  decisions: AgentDecision[];
  authorizations: AuthorizationResult[];
  audit_entries: AuditEntry[];
  summary: PipelineSummary;
}

export interface AuthorizationResult {
  asset_id: string;
  request_id: string;
  authorization: {
    authorized: boolean;
    policy_applied: string;
    execution_id: string;
    reason: string;
  };
  execution: {
    result: string;
    timestamp: string;
  };
  audit: {
    execution_id: string;
    agent_name: string;
    action: string;
    asset_id: string;
    authorized: boolean;
    policy_applied: string;
    result: string;
    timestamp: string;
  };
}

export interface AuditEntry {
  id?: number;
  agent_name: string;
  action: string;
  asset_id: string;
  authorized: boolean;
  reason: string;
  details?: string;
  severity: string;
  created_at: string;
}

export interface AuditResponse {
  entries: AuditEntry[];
  total: number;
  page: number;
  page_size: number;
}

export interface ReadinessScore {
  overall: number;
  inventory_health: number;
  maintenance_health: number;
  risk_health: number;
  total_assets: number;
  active_assets: number;
  assets_needing_attention: number;
}

export interface DashboardResponse {
  readiness: ReadinessScore;
  recent_predictions: PredictionResponse[];
  recent_actions: AgentAction[];
  recent_authorizations: AuthorizationLogEntry[];
  recent_audit: AuditEntry[];
  asset_summary: Record<string, number>;
}

export interface AgentAction {
  id: number;
  agent_name: string;
  asset_id: string;
  action: string;
  reason: string;
  status: string;
  created_at: string;
}

export interface AuthorizationLogEntry {
  id: number;
  agent_name: string;
  action: string;
  asset_id: string;
  authorized: boolean;
  policy_applied: string;
  reason: string;
  created_at: string;
}

export interface PipelineSummary {
  batch_id: string;
  total_assets: number;
  high_risk_count: number;
  needs_service_count: number;
  needs_restock_count: number;
  total_actions: number;
  authorized_count: number;
  rejected_count: number;
  timestamp: string;
}

export interface UploadResponse {
  message: string;
  assets_loaded: number;
  batch_id: string;
  validation_errors: string[];
}

export interface HealthResponse {
  status: string;
  environment: string;
  database: string;
  ml_models: Record<string, string>;
  version: string;
}

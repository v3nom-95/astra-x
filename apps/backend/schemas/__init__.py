"""
ASTRA-X Pydantic Schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


# ── Asset Schemas ──────────────────────────────────

class AssetBase(BaseModel):
    asset_id: str
    type: str
    inventory: int
    usage_rate: float
    service_days: int
    temperature: float
    repairs: int
    location: str = "UNKNOWN"
    status: str = "ACTIVE"


class AssetResponse(AssetBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Prediction Schemas ─────────────────────────────

class InventoryPredictionInput(BaseModel):
    asset_id: str
    inventory: float
    usage_rate: float


class InventoryPredictionResult(BaseModel):
    asset_id: str
    days_remaining: float
    needs_restock: bool


class MaintenancePredictionInput(BaseModel):
    asset_id: str
    temperature: float
    service_days: int
    repairs: int


class MaintenancePredictionResult(BaseModel):
    asset_id: str
    failure_probability: float
    needs_service: bool


class RiskPredictionInput(BaseModel):
    asset_id: str
    usage_rate: float
    service_days: int
    repairs: int


class RiskPredictionResult(BaseModel):
    asset_id: str
    risk: str  # HIGH, MEDIUM, LOW
    anomaly_score: float


class PredictionResponse(BaseModel):
    asset_id: str
    inventory: Optional[InventoryPredictionResult] = None
    maintenance: Optional[MaintenancePredictionResult] = None
    risk: Optional[RiskPredictionResult] = None


class BatchPredictionResponse(BaseModel):
    batch_id: str
    predictions: List[PredictionResponse]
    total_assets: int
    high_risk_count: int
    needs_service_count: int
    needs_restock_count: int


# ── Agent Schemas ──────────────────────────────────

class AgentDecision(BaseModel):
    agent_name: str
    asset_id: str
    action: str
    reason: str
    confidence: float = 1.0


class AgentRunRequest(BaseModel):
    batch_id: Optional[str] = None
    asset_ids: Optional[List[str]] = None


class AgentRunResponse(BaseModel):
    batch_id: str
    decisions: List[AgentDecision]
    authorizations: List[dict]
    audit_entries: List[dict]
    summary: dict


# ── Authorization Schemas ──────────────────────────

class AuthorizationRequest(BaseModel):
    agent_name: str
    action: str
    asset_id: str
    reason: str


class AuthorizationResponse(BaseModel):
    authorized: bool
    policy_applied: str
    execution_id: str
    reason: str


# ── Dashboard Schemas ──────────────────────────────

class ReadinessScore(BaseModel):
    overall: float
    inventory_health: float
    maintenance_health: float
    risk_health: float
    total_assets: int
    active_assets: int
    assets_needing_attention: int


class DashboardResponse(BaseModel):
    readiness: ReadinessScore
    recent_predictions: List[PredictionResponse]
    recent_actions: List[dict]
    recent_authorizations: List[dict]
    recent_audit: List[dict]
    asset_summary: dict


# ── Audit Schemas ──────────────────────────────────

class AuditEntry(BaseModel):
    id: int
    agent_name: str
    action: str
    asset_id: str
    authorized: bool
    reason: str
    details: Optional[str] = None
    severity: str = "INFO"
    created_at: datetime

    class Config:
        from_attributes = True


class AuditResponse(BaseModel):
    entries: List[AuditEntry]
    total: int
    page: int
    page_size: int


# ── Upload Schemas ─────────────────────────────────

class UploadResponse(BaseModel):
    message: str
    assets_loaded: int
    batch_id: str
    validation_errors: List[str] = []


# ── Health Schema ──────────────────────────────────

class HealthResponse(BaseModel):
    status: str = "healthy"
    environment: str
    database: str
    ml_models: dict
    version: str = "1.0.0"

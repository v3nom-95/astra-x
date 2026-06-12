"""
Dashboard API — Aggregated readiness intelligence for the frontend.
"""
import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from db.engine import get_db
from models import Asset, Prediction, AgentAction, AuthorizationLog, AuditLog
from schemas import DashboardResponse, ReadinessScore, PredictionResponse

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(db: Session = Depends(get_db)):
    """
    Get aggregated dashboard data including readiness scores,
    recent predictions, actions, and audit feed.
    """
    # Asset counts
    total_assets = db.query(Asset).count()
    active_assets = db.query(Asset).filter(Asset.status == "ACTIVE").count()

    # Recent predictions (last batch)
    latest_predictions = (
        db.query(Prediction)
        .order_by(desc(Prediction.created_at))
        .limit(100)
        .all()
    )

    # Calculate readiness scores from recent predictions
    inv_scores = []
    maint_scores = []
    risk_scores = []
    assets_needing_attention = 0

    # Group by asset
    asset_preds: dict[str, dict] = {}
    for pred in latest_predictions:
        if pred.asset_id not in asset_preds:
            asset_preds[pred.asset_id] = {}
        try:
            result = json.loads(pred.result) if pred.result else {}
        except json.JSONDecodeError:
            result = {}
        asset_preds[pred.asset_id][pred.prediction_type] = result

    for asset_id, preds in asset_preds.items():
        inv = preds.get("inventory", {})
        maint = preds.get("maintenance", {})
        risk = preds.get("risk", {})

        # Inventory health: higher days_remaining = better
        dr = inv.get("days_remaining", 50)
        inv_health = min(dr / 50, 1.0)  # Normalize to 0-1
        inv_scores.append(inv_health)

        # Maintenance health: lower failure_prob = better
        fp = maint.get("failure_probability", 0.0)
        maint_health = 1.0 - fp
        maint_scores.append(maint_health)

        # Risk health: LOW=1.0, MEDIUM=0.5, HIGH=0.0
        risk_level = risk.get("risk", "LOW")
        risk_health = {"LOW": 1.0, "MEDIUM": 0.5, "HIGH": 0.0}.get(risk_level, 0.5)
        risk_scores.append(risk_health)

        # Count attention needed
        if inv.get("needs_restock") or maint.get("needs_service") or risk_level == "HIGH":
            assets_needing_attention += 1

    # Calculate averages
    inv_avg = sum(inv_scores) / len(inv_scores) if inv_scores else 1.0
    maint_avg = sum(maint_scores) / len(maint_scores) if maint_scores else 1.0
    risk_avg = sum(risk_scores) / len(risk_scores) if risk_scores else 1.0
    overall = (inv_avg * 0.3 + maint_avg * 0.4 + risk_avg * 0.3)

    readiness = ReadinessScore(
        overall=round(overall * 100, 1),
        inventory_health=round(inv_avg * 100, 1),
        maintenance_health=round(maint_avg * 100, 1),
        risk_health=round(risk_avg * 100, 1),
        total_assets=total_assets,
        active_assets=active_assets,
        assets_needing_attention=assets_needing_attention,
    )

    # Recent actions
    recent_actions = (
        db.query(AgentAction)
        .order_by(desc(AgentAction.created_at))
        .limit(20)
        .all()
    )
    actions_data = [
        {
            "id": a.id,
            "agent_name": a.agent_name,
            "asset_id": a.asset_id,
            "action": a.action,
            "reason": a.reason,
            "status": a.status,
            "created_at": a.created_at.isoformat() if a.created_at else "",
        }
        for a in recent_actions
    ]

    # Recent authorizations
    recent_auths = (
        db.query(AuthorizationLog)
        .order_by(desc(AuthorizationLog.created_at))
        .limit(20)
        .all()
    )
    auths_data = [
        {
            "id": a.id,
            "agent_name": a.agent_name,
            "action": a.action,
            "asset_id": a.asset_id,
            "authorized": a.authorized,
            "policy_applied": a.policy_applied,
            "reason": a.reason,
            "created_at": a.created_at.isoformat() if a.created_at else "",
        }
        for a in recent_auths
    ]

    # Recent audit entries
    recent_audit = (
        db.query(AuditLog)
        .order_by(desc(AuditLog.created_at))
        .limit(20)
        .all()
    )
    audit_data = [
        {
            "id": a.id,
            "agent_name": a.agent_name,
            "action": a.action,
            "asset_id": a.asset_id,
            "authorized": a.authorized,
            "reason": a.reason,
            "severity": a.severity,
            "created_at": a.created_at.isoformat() if a.created_at else "",
        }
        for a in recent_audit
    ]

    # Asset summary by type
    asset_types = db.query(Asset.type, func.count(Asset.id)).group_by(Asset.type).all()
    asset_summary = {t: c for t, c in asset_types}

    # Build prediction response objects
    pred_responses = []
    for asset_id, preds in list(asset_preds.items())[:10]:
        pred_responses.append(PredictionResponse(
            asset_id=asset_id,
            inventory=None,
            maintenance=None,
            risk=None,
        ))

    return DashboardResponse(
        readiness=readiness,
        recent_predictions=pred_responses,
        recent_actions=actions_data,
        recent_authorizations=auths_data,
        recent_audit=audit_data,
        asset_summary=asset_summary,
    )

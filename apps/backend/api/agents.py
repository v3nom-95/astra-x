"""
Agent API — Run the full agent pipeline via LangGraph.
"""
import uuid
import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.engine import get_db
from models import Asset, AgentAction, AuthorizationLog, AuditLog
from schemas import AgentRunRequest, AgentRunResponse, AgentDecision
from services.agents.workflow import run_pipeline

router = APIRouter(tags=["Agents"])


@router.post("/agent/run", response_model=AgentRunResponse)
async def run_agents(request: AgentRunRequest, db: Session = Depends(get_db)):
    """
    Run the complete agent pipeline:
    Predict → Agents → Authorize → Audit

    Processes all assets (or filtered by asset_ids) through the LangGraph workflow.
    """
    # Fetch assets
    query = db.query(Asset)
    if request.asset_ids:
        query = query.filter(Asset.asset_id.in_(request.asset_ids))
    assets = query.all()

    if not assets:
        return AgentRunResponse(
            batch_id="empty",
            decisions=[],
            authorizations=[],
            audit_entries=[],
            summary={"error": "No assets found"},
        )

    # Convert to dicts for pipeline
    asset_dicts = [
        {
            "asset_id": a.asset_id,
            "type": a.type,
            "inventory": a.inventory,
            "usage_rate": a.usage_rate,
            "service_days": a.service_days,
            "temperature": a.temperature,
            "repairs": a.repairs,
            "location": a.location,
            "status": a.status,
        }
        for a in assets
    ]

    batch_id = request.batch_id or str(uuid.uuid4())[:8]

    # Run LangGraph pipeline
    result = run_pipeline(asset_dicts, batch_id)

    # Persist decisions to DB
    for action in result.get("final_actions", []):
        db_action = AgentAction(
            agent_name=action["agent_name"],
            asset_id=action["asset_id"],
            action=action["action"],
            reason=action.get("reason", ""),
            input_predictions=json.dumps(action.get("input_data", {})),
            status="executed",
            batch_id=batch_id,
        )
        db.add(db_action)

    # Persist authorizations to DB
    for auth in result.get("authorizations", []):
        auth_data = auth.get("authorization", {})
        db_auth = AuthorizationLog(
            agent_name="command_agent",
            action=auth.get("audit", {}).get("action", ""),
            asset_id=auth.get("asset_id", ""),
            authorized=auth_data.get("authorized", False),
            policy_applied=auth_data.get("policy_applied", ""),
            reason=auth_data.get("reason", ""),
            execution_id=auth_data.get("execution_id", ""),
            batch_id=batch_id,
        )
        db.add(db_auth)

    # Persist audit entries to DB
    for entry in result.get("audit_entries", []):
        db_audit = AuditLog(
            agent_name=entry.get("agent_name", ""),
            action=entry.get("action", ""),
            asset_id=entry.get("asset_id", ""),
            authorized=entry.get("authorized", False),
            reason=entry.get("reason", ""),
            details=json.dumps(entry.get("details", {})),
            severity=entry.get("severity", "INFO"),
            batch_id=batch_id,
        )
        db.add(db_audit)

    db.commit()

    # Build response
    decisions = [
        AgentDecision(
            agent_name=a["agent_name"],
            asset_id=a["asset_id"],
            action=a["action"],
            reason=a.get("reason", ""),
            confidence=a.get("confidence", 0.9),
        )
        for a in result.get("final_actions", [])
    ]

    return AgentRunResponse(
        batch_id=batch_id,
        decisions=decisions,
        authorizations=result.get("authorizations", []),
        audit_entries=result.get("audit_entries", []),
        summary=result.get("summary", {}),
    )

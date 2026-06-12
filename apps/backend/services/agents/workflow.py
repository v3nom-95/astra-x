"""
LangGraph Workflow — Orchestrates the complete ASTRA-X agent pipeline.

Flow:
  Dataset → ML Prediction → Inventory Agent → Maintenance Agent →
  Risk Agent → Command Agent → Terminal3 Authorization → Audit Agent → Dashboard
"""
import uuid
import json
import logging
from typing import TypedDict, Any
from datetime import datetime

from langgraph.graph import StateGraph, END

from services.agents import inventory_agent, maintenance_agent, risk_agent, command_agent, audit_agent
from services.ml.model_manager import ModelManager
from services.authorization.terminal3_client import Terminal3Client

logger = logging.getLogger(__name__)


class WorkflowState(TypedDict, total=False):
    """State passed through the LangGraph workflow."""
    batch_id: str
    assets: list[dict]
    predictions: list[dict]
    decisions: list[dict]
    final_actions: list[dict]
    authorizations: list[dict]
    audit_entries: list[dict]
    summary: dict
    errors: list[str]


def predict_node(state: WorkflowState) -> WorkflowState:
    """Run ML predictions for all assets."""
    assets = state.get("assets", [])
    model_manager = ModelManager.get_instance()
    predictions = []
    errors = state.get("errors", [])

    for asset in assets:
        try:
            pred = model_manager.predict_all(asset)
            predictions.append(pred)
        except Exception as e:
            errors.append(f"Prediction failed for {asset.get('asset_id')}: {str(e)}")
            logger.error(f"Prediction error for {asset.get('asset_id')}: {e}")

    state["predictions"] = predictions
    state["errors"] = errors
    logger.info(f"Predictions complete: {len(predictions)} assets processed")
    return state


def inventory_node(state: WorkflowState) -> WorkflowState:
    """Run inventory agent."""
    return inventory_agent.run(state)


def maintenance_node(state: WorkflowState) -> WorkflowState:
    """Run maintenance agent."""
    return maintenance_agent.run(state)


def risk_node(state: WorkflowState) -> WorkflowState:
    """Run risk agent."""
    return risk_agent.run(state)


def command_node(state: WorkflowState) -> WorkflowState:
    """Run command agent to coordinate decisions."""
    return command_agent.run(state)


def authorize_node(state: WorkflowState) -> WorkflowState:
    """Run Terminal3 authorization for all final actions using a persistent HTTP session."""
    terminal3 = Terminal3Client.get_instance()
    authorizations = []
    final_actions = state.get("final_actions", [])

    logger.info(f"Authorizing {len(final_actions)} actions via Terminal3 (batched)...")

    # Use a single persistent httpx.Client for all requests to avoid
    # connection overhead per asset (was the #1 bottleneck).
    import httpx
    with httpx.Client(base_url=terminal3.base_url, headers=terminal3.headers, timeout=10.0) as client:
        for action in final_actions:
            try:
                # 1. Auth check
                auth_resp = client.post("/auth/check", json={
                    "request_id": f"req-{uuid.uuid4().hex[:8]}",
                    "agent_name": action["agent_name"],
                    "action": action["action"],
                    "asset_id": action["asset_id"],
                    "context": action.get("input_data", {}),
                })
                auth_data = auth_resp.json()

                exec_id = auth_data.get("execution_id", f"exec-{uuid.uuid4().hex[:8]}")

                # 2. Log execution
                client.post("/executions/log", json={
                    "execution_id": exec_id,
                    "agent_name": action["agent_name"],
                    "action": action["action"],
                    "asset_id": action["asset_id"],
                    "authorized": auth_data.get("authorized", False),
                    "result": "executed" if auth_data.get("authorized") else "blocked",
                })

                authorizations.append({
                    "asset_id": action["asset_id"],
                    "request_id": f"req-{uuid.uuid4().hex[:8]}",
                    "authorization": {
                        "authorized": auth_data.get("authorized", False),
                        "policy_applied": auth_data.get("policy_applied", ""),
                        "execution_id": exec_id,
                        "reason": auth_data.get("reason", ""),
                    },
                    "execution": {
                        "result": "executed" if auth_data.get("authorized") else "blocked",
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    "audit": {
                        "execution_id": exec_id,
                        "agent_name": action["agent_name"],
                        "action": action["action"],
                        "asset_id": action["asset_id"],
                        "authorized": auth_data.get("authorized", False),
                        "policy_applied": auth_data.get("policy_applied", ""),
                        "result": "executed" if auth_data.get("authorized") else "blocked",
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                })
            except Exception as e:
                logger.error(f"Authorization error for {action['asset_id']}: {e}")
                authorizations.append({
                    "asset_id": action["asset_id"],
                    "authorization": {"authorized": False, "reason": str(e)},
                    "audit": {"action": action["action"], "asset_id": action["asset_id"], "authorized": False},
                    "execution": {"result": "blocked", "timestamp": datetime.utcnow().isoformat()},
                })

    state["authorizations"] = authorizations
    logger.info(f"Authorization complete: {len(authorizations)} actions processed")
    return state


def audit_node(state: WorkflowState) -> WorkflowState:
    """Run audit agent."""
    return audit_agent.run(state)


def summary_node(state: WorkflowState) -> WorkflowState:
    """Generate workflow summary."""
    predictions = state.get("predictions", [])
    final_actions = state.get("final_actions", [])
    authorizations = state.get("authorizations", [])

    high_risk = sum(1 for p in predictions if p.get("risk", {}).get("risk") == "HIGH")
    needs_service = sum(1 for p in predictions if p.get("maintenance", {}).get("needs_service", False))
    needs_restock = sum(1 for p in predictions if p.get("inventory", {}).get("needs_restock", False))
    authorized_count = sum(1 for a in authorizations if a.get("authorization", {}).get("authorized", False))

    state["summary"] = {
        "batch_id": state.get("batch_id", ""),
        "total_assets": len(predictions),
        "high_risk_count": high_risk,
        "needs_service_count": needs_service,
        "needs_restock_count": needs_restock,
        "total_actions": len(final_actions),
        "authorized_count": authorized_count,
        "rejected_count": len(authorizations) - authorized_count,
        "timestamp": datetime.utcnow().isoformat(),
    }
    return state


def build_workflow() -> StateGraph:
    """Build the LangGraph workflow for ASTRA-X agent pipeline."""
    workflow = StateGraph(WorkflowState)

    # Add nodes
    workflow.add_node("predict", predict_node)
    workflow.add_node("inventory_agent", inventory_node)
    workflow.add_node("maintenance_agent", maintenance_node)
    workflow.add_node("risk_agent", risk_node)
    workflow.add_node("command_agent", command_node)
    workflow.add_node("authorize", authorize_node)
    workflow.add_node("audit_agent", audit_node)
    workflow.add_node("generate_summary", summary_node)

    # Define edges (sequential pipeline)
    workflow.set_entry_point("predict")
    workflow.add_edge("predict", "inventory_agent")
    workflow.add_edge("inventory_agent", "maintenance_agent")
    workflow.add_edge("maintenance_agent", "risk_agent")
    workflow.add_edge("risk_agent", "command_agent")
    workflow.add_edge("command_agent", "authorize")
    workflow.add_edge("authorize", "audit_agent")
    workflow.add_edge("audit_agent", "generate_summary")
    workflow.add_edge("generate_summary", END)

    return workflow


# Compile the workflow
_workflow = build_workflow()
compiled_workflow = _workflow.compile()


def run_pipeline(assets: list[dict], batch_id: str | None = None) -> dict:
    """
    Execute the complete ASTRA-X agent pipeline.

    Args:
        assets: List of asset dictionaries with required fields.
        batch_id: Optional batch identifier.

    Returns:
        Complete workflow state with predictions, decisions, authorizations, and audit.
    """
    if batch_id is None:
        batch_id = str(uuid.uuid4())[:8]

    initial_state: WorkflowState = {
        "batch_id": batch_id,
        "assets": assets,
        "predictions": [],
        "decisions": [],
        "final_actions": [],
        "authorizations": [],
        "audit_entries": [],
        "summary": {},
        "errors": [],
    }

    logger.info(f"Starting pipeline batch={batch_id} with {len(assets)} assets")
    result = compiled_workflow.invoke(initial_state)
    logger.info(f"Pipeline complete batch={batch_id}: {result.get('summary', {})}")

    return result

"""
Audit Agent — Generates structured audit records for all decisions and actions.
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

AGENT_NAME = "audit_agent"


def run(state: dict) -> dict:
    """
    Generate structured audit records for all agent decisions and authorizations.
    Each record captures: who, what, why, authorized status, and context.
    """
    final_actions = state.get("final_actions", [])
    authorizations = state.get("authorizations", [])
    audit_entries = state.get("audit_entries", [])

    # Create authorization lookup by asset_id
    auth_lookup: dict[str, dict] = {}
    for auth in authorizations:
        auth_lookup[auth.get("asset_id", "")] = auth

    for action in final_actions:
        asset_id = action["asset_id"]
        auth_info = auth_lookup.get(asset_id, {})
        auth_data = auth_info.get("authorization", {})

        severity = "INFO"
        if action["action"] in ("freeze_operation", "pause_operation"):
            severity = "CRITICAL"
        elif action["action"] == "schedule_service":
            severity = "WARNING"

        entry = {
            "agent_name": action.get("agent_name", AGENT_NAME),
            "action": action["action"],
            "asset_id": asset_id,
            "authorized": auth_data.get("authorized", False),
            "reason": action.get("reason", ""),
            "severity": severity,
            "details": {
                "policy_applied": auth_data.get("policy_applied", ""),
                "execution_id": auth_data.get("execution_id", ""),
                "authorization_reason": auth_data.get("reason", ""),
                "confidence": action.get("confidence", 0.0),
                "sub_decisions": [
                    {
                        "agent": d["agent_name"],
                        "action": d["action"],
                        "reason": d["reason"],
                    }
                    for d in action.get("sub_decisions", [])
                ],
                "timestamp": datetime.utcnow().isoformat(),
            },
        }
        audit_entries.append(entry)
        logger.info(
            f"[{AGENT_NAME}] Audit: {asset_id} | {action['action']} | "
            f"authorized={auth_data.get('authorized', False)}"
        )

    state["audit_entries"] = audit_entries
    return state

"""
Maintenance Agent — Analyzes maintenance predictions and decides service actions.
"""
import logging

logger = logging.getLogger(__name__)

AGENT_NAME = "maintenance_agent"


def run(state: dict) -> dict:
    """
    Process maintenance predictions and generate service decisions.

    Rules:
    - failure_probability > 0.80 → schedule_service
    - failure_probability <= 0.80 → continue_operation
    """
    predictions = state.get("predictions", [])
    decisions = state.get("decisions", [])

    for pred in predictions:
        asset_id = pred.get("asset_id", "UNKNOWN")
        maint_pred = pred.get("maintenance", {})

        if "error" in maint_pred:
            continue

        failure_prob = maint_pred.get("failure_probability", 0.0)
        needs_service = maint_pred.get("needs_service", False)

        if needs_service or failure_prob > 0.80:
            action = "schedule_service"
            reason = f"High failure probability: {failure_prob:.0%} (threshold: 80%)"
            severity = "CRITICAL" if failure_prob > 0.90 else "WARNING"
        else:
            action = "continue_operation"
            reason = f"Failure probability acceptable: {failure_prob:.0%}"
            severity = "INFO"

        decision = {
            "agent_name": AGENT_NAME,
            "asset_id": asset_id,
            "action": action,
            "reason": reason,
            "confidence": min(failure_prob + 0.1, 1.0) if needs_service else 0.8,
            "severity": severity,
            "input_data": {
                "failure_probability": failure_prob,
                "needs_service": needs_service,
            },
        }
        decisions.append(decision)
        logger.info(f"[{AGENT_NAME}] {asset_id}: {action} — {reason}")

    state["decisions"] = decisions
    return state

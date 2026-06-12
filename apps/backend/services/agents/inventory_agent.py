"""
Inventory Agent — Analyzes inventory predictions and decides restock actions.
"""
import logging

logger = logging.getLogger(__name__)

AGENT_NAME = "inventory_agent"


def run(state: dict) -> dict:
    """
    Process inventory predictions and generate restock decisions.

    Rules:
    - days_remaining < 20 → approve_restock
    - days_remaining >= 20 → delay_restock
    """
    predictions = state.get("predictions", [])
    decisions = state.get("decisions", [])

    for pred in predictions:
        asset_id = pred.get("asset_id", "UNKNOWN")
        inv_pred = pred.get("inventory", {})

        if "error" in inv_pred:
            continue

        days_remaining = inv_pred.get("days_remaining", 999)
        needs_restock = inv_pred.get("needs_restock", False)

        if needs_restock or days_remaining < 20:
            action = "approve_restock"
            reason = f"Inventory critically low: {days_remaining:.1f} days remaining (threshold: 20)"
        else:
            action = "delay_restock"
            reason = f"Inventory adequate: {days_remaining:.1f} days remaining"

        decision = {
            "agent_name": AGENT_NAME,
            "asset_id": asset_id,
            "action": action,
            "reason": reason,
            "confidence": 0.95 if needs_restock else 0.85,
            "input_data": {
                "days_remaining": days_remaining,
                "needs_restock": needs_restock,
            },
        }
        decisions.append(decision)
        logger.info(f"[{AGENT_NAME}] {asset_id}: {action} — {reason}")

    state["decisions"] = decisions
    return state

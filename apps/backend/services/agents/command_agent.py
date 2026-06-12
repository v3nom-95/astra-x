"""
Command Agent — Coordinates all agent decisions with priority-based rules.
Safety > Maintenance > Logistics.
"""
import logging

logger = logging.getLogger(__name__)

AGENT_NAME = "command_agent"


def run(state: dict) -> dict:
    """
    Coordinate all agent decisions into a final action plan.
    Applies priority rules and resolves conflicts between agent decisions.

    Priority order:
    1. Safety: freeze_operation (highest)
    2. Maintenance: schedule_service
    3. Logistics: approve_restock (lowest)
    """
    decisions = state.get("decisions", [])
    final_actions = state.get("final_actions", [])

    # Group decisions by asset
    asset_decisions: dict[str, list[dict]] = {}
    for decision in decisions:
        asset_id = decision["asset_id"]
        if asset_id not in asset_decisions:
            asset_decisions[asset_id] = []
        asset_decisions[asset_id].append(decision)

    # Priority mapping
    ACTION_PRIORITY = {
        "freeze_operation": 100,
        "pause_operation": 90,
        "schedule_service": 70,
        "approve_restock": 50,
        "approve_dispatch": 40,
        "monitor": 20,
        "delay_restock": 10,
        "continue_operation": 5,
    }

    for asset_id, asset_decs in asset_decisions.items():
        # Sort by priority (highest first)
        sorted_decs = sorted(
            asset_decs,
            key=lambda d: ACTION_PRIORITY.get(d["action"], 0),
            reverse=True,
        )

        # Primary action is highest priority
        primary = sorted_decs[0]

        # Build coordinated action
        all_actions = [d["action"] for d in sorted_decs]
        all_reasons = [f"[{d['agent_name']}] {d['reason']}" for d in sorted_decs]

        coordinated = {
            "agent_name": AGENT_NAME,
            "asset_id": asset_id,
            "action": primary["action"],
            "reason": f"Command decision: {primary['action']} | Coordinated from: {', '.join(all_actions)}",
            "confidence": primary.get("confidence", 0.9),
            "severity": primary.get("severity", "INFO"),
            "sub_decisions": sorted_decs,
            "all_reasons": all_reasons,
            "input_data": {
                "primary_action": primary["action"],
                "all_actions": all_actions,
                "decision_count": len(sorted_decs),
            },
        }
        final_actions.append(coordinated)
        logger.info(
            f"[{AGENT_NAME}] {asset_id}: PRIMARY={primary['action']} "
            f"(from {len(sorted_decs)} agent decisions)"
        )

    state["final_actions"] = final_actions
    return state

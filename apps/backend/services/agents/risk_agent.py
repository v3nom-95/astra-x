"""
Risk Agent — Analyzes risk predictions and decides operational freezes.
"""
import logging

logger = logging.getLogger(__name__)

AGENT_NAME = "risk_agent"


def run(state: dict) -> dict:
    """
    Process risk predictions and generate operational decisions.

    Rules:
    - risk == HIGH → freeze_operation
    - risk == MEDIUM → monitor
    - risk == LOW → (no action needed)
    """
    predictions = state.get("predictions", [])
    decisions = state.get("decisions", [])

    for pred in predictions:
        asset_id = pred.get("asset_id", "UNKNOWN")
        risk_pred = pred.get("risk", {})

        if "error" in risk_pred:
            continue

        risk = risk_pred.get("risk", "LOW")
        anomaly_score = risk_pred.get("anomaly_score", 0.0)

        if risk == "HIGH":
            action = "freeze_operation"
            reason = f"HIGH risk detected — anomaly score: {anomaly_score:.3f}"
            severity = "CRITICAL"
        elif risk == "MEDIUM":
            action = "monitor"
            reason = f"MEDIUM risk — anomaly score: {anomaly_score:.3f}, monitoring recommended"
            severity = "WARNING"
        else:
            action = "monitor"
            reason = f"LOW risk — anomaly score: {anomaly_score:.3f}, normal operations"
            severity = "INFO"

        decision = {
            "agent_name": AGENT_NAME,
            "asset_id": asset_id,
            "action": action,
            "reason": reason,
            "confidence": 0.90 if risk == "HIGH" else 0.75,
            "severity": severity,
            "input_data": {
                "risk": risk,
                "anomaly_score": anomaly_score,
            },
        }
        decisions.append(decision)
        logger.info(f"[{AGENT_NAME}] {asset_id}: {action} — {reason}")

    state["decisions"] = decisions
    return state

"""
Authorization Policies for ASTRA-X.
Defines what actions each agent role is permitted to perform.
"""
from dataclasses import dataclass


@dataclass
class Policy:
    """Authorization policy definition."""
    name: str
    description: str
    allowed_actions: list[str]
    required_role: str
    auto_approve: bool = True  # In MVP, most policies auto-approve if conditions met
    max_risk_level: str = "HIGH"  # Maximum risk level this policy can handle


# ── Policy Registry ─────────────────────────────────

POLICIES: dict[str, Policy] = {
    "inventory_management": Policy(
        name="inventory_management",
        description="Controls inventory restock and delay decisions",
        allowed_actions=["approve_restock", "delay_restock", "approve_dispatch"],
        required_role="inventory_agent",
        auto_approve=True,
    ),
    "maintenance_operations": Policy(
        name="maintenance_operations",
        description="Controls maintenance scheduling decisions",
        allowed_actions=["schedule_service", "continue_operation"],
        required_role="maintenance_agent",
        auto_approve=True,
    ),
    "risk_control": Policy(
        name="risk_control",
        description="Controls risk-related operational freezes",
        allowed_actions=["freeze_operation", "monitor", "pause_operation"],
        required_role="risk_agent",
        auto_approve=True,
        max_risk_level="HIGH",
    ),
    "command_override": Policy(
        name="command_override",
        description="Command agent can override and coordinate all actions",
        allowed_actions=[
            "approve_restock", "delay_restock", "schedule_service",
            "continue_operation", "freeze_operation", "monitor",
            "pause_operation", "approve_dispatch",
        ],
        required_role="command_agent",
        auto_approve=True,
    ),
}

# ── Protected Actions ────────────────────────────────

PROTECTED_ACTIONS = [
    "schedule_service",
    "approve_restock",
    "pause_operation",
    "approve_dispatch",
    "freeze_operation",
]


def get_policy_for_action(action: str, agent_role: str) -> Policy | None:
    """Find the matching policy for a given action and agent role."""
    for policy in POLICIES.values():
        if action in policy.allowed_actions:
            if policy.required_role == agent_role or agent_role == "command_agent":
                return policy
    return None


def is_protected_action(action: str) -> bool:
    """Check if an action requires authorization."""
    return action in PROTECTED_ACTIONS

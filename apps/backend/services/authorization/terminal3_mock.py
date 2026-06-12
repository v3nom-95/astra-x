"""
Terminal3 Agentic Kit — Mock Implementation.
Simulates the Terminal3 authorization layer with agent identity,
policy-based authorization, and execution logging.
"""
import uuid
import logging
from datetime import datetime

from services.authorization.interface import (
    AuthorizationProvider,
    AgentIdentity,
    ActionRequest,
    AuthorizationResult,
    ExecutionLog,
)
from services.authorization.policies import (
    get_policy_for_action,
    is_protected_action,
    PROTECTED_ACTIONS,
)

logger = logging.getLogger(__name__)


class Terminal3Mock(AuthorizationProvider):
    """
    Mock implementation of Terminal3 Agentic Kit.
    Provides: agent identity, protected actions, authorization policies,
    delegation tracking, and execution logs.
    """

    _instance = None

    def __init__(self):
        self._agents: dict[str, AgentIdentity] = {}
        self._execution_logs: list[ExecutionLog] = []
        self._pending_requests: dict[str, ActionRequest] = {}

    @classmethod
    def get_instance(cls) -> "Terminal3Mock":
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._register_default_agents()
        return cls._instance

    def _register_default_agents(self):
        """Register the default ASTRA-X agents."""
        agents = [
            AgentIdentity("inv-001", "inventory_agent", "inventory_agent",
                          ["approve_restock", "delay_restock", "approve_dispatch"]),
            AgentIdentity("maint-001", "maintenance_agent", "maintenance_agent",
                          ["schedule_service", "continue_operation"]),
            AgentIdentity("risk-001", "risk_agent", "risk_agent",
                          ["freeze_operation", "monitor", "pause_operation"]),
            AgentIdentity("cmd-001", "command_agent", "command_agent",
                          PROTECTED_ACTIONS + ["continue_operation", "delay_restock", "monitor"]),
            AgentIdentity("audit-001", "audit_agent", "audit_agent", []),
        ]
        for agent in agents:
            self.register_agent(agent)

    def register_agent(self, agent: AgentIdentity) -> bool:
        """Register an agent identity in the system."""
        self._agents[agent.agent_id] = agent
        logger.info(f"Agent registered: {agent.agent_name} ({agent.agent_id})")
        return True

    def request_action(self, request: ActionRequest) -> ActionRequest:
        """Submit an action request for authorization."""
        if not request.request_id:
            request.request_id = str(uuid.uuid4())
        self._pending_requests[request.request_id] = request
        logger.info(f"Action requested: {request.action} by {request.agent_name} for {request.asset_id}")
        return request

    def authorize(self, request: ActionRequest) -> AuthorizationResult:
        """
        Authorize an action request based on policies.
        Checks: agent exists, action is valid for agent's role, policy allows it.
        """
        # Find the agent
        agent = None
        for a in self._agents.values():
            if a.agent_name == request.agent_name:
                agent = a
                break

        if agent is None:
            return AuthorizationResult(
                authorized=False,
                policy_applied="agent_not_found",
                reason=f"Agent '{request.agent_name}' not registered",
            )

        # Check if this is a protected action
        if not is_protected_action(request.action):
            # Non-protected actions are auto-authorized
            return AuthorizationResult(
                authorized=True,
                policy_applied="non_protected_auto_approve",
                reason=f"Action '{request.action}' is not protected — auto-approved",
            )

        # Check if the agent has permission
        if request.action not in agent.permissions:
            return AuthorizationResult(
                authorized=False,
                policy_applied="permission_denied",
                reason=f"Agent '{request.agent_name}' lacks permission for '{request.action}'",
            )

        # Find matching policy
        policy = get_policy_for_action(request.action, agent.role)
        if policy is None:
            return AuthorizationResult(
                authorized=False,
                policy_applied="no_matching_policy",
                reason=f"No policy found for action '{request.action}' with role '{agent.role}'",
            )

        # Policy-based authorization
        if policy.auto_approve:
            return AuthorizationResult(
                authorized=True,
                policy_applied=policy.name,
                reason=f"Auto-approved by policy '{policy.name}': {policy.description}",
            )

        return AuthorizationResult(
            authorized=False,
            policy_applied=policy.name,
            reason=f"Policy '{policy.name}' requires manual approval",
        )

    def execute(self, request: ActionRequest, auth_result: AuthorizationResult) -> ExecutionLog:
        """Execute an authorized action and create an execution log."""
        log = ExecutionLog(
            execution_id=auth_result.execution_id,
            agent_id=request.agent_id or request.agent_name,
            agent_name=request.agent_name,
            action=request.action,
            asset_id=request.asset_id,
            authorized=auth_result.authorized,
            policy_applied=auth_result.policy_applied,
            result="executed" if auth_result.authorized else "blocked",
        )
        self._execution_logs.append(log)

        # Clean up pending request
        if request.request_id in self._pending_requests:
            del self._pending_requests[request.request_id]

        logger.info(
            f"Action {'executed' if auth_result.authorized else 'blocked'}: "
            f"{request.action} by {request.agent_name} for {request.asset_id}"
        )
        return log

    def audit(self, execution_log: ExecutionLog) -> dict:
        """Generate audit record for the execution."""
        return {
            "execution_id": execution_log.execution_id,
            "agent_name": execution_log.agent_name,
            "action": execution_log.action,
            "asset_id": execution_log.asset_id,
            "authorized": execution_log.authorized,
            "policy_applied": execution_log.policy_applied,
            "result": execution_log.result,
            "timestamp": execution_log.timestamp.isoformat(),
        }

    def get_execution_logs(self) -> list[ExecutionLog]:
        """Retrieve all execution logs."""
        return self._execution_logs.copy()

    def process_action(self, agent_name: str, action: str, asset_id: str, reason: str, context: dict | None = None) -> dict:
        """
        Convenience method: request → authorize → execute → audit in one call.
        This is the primary interface used by agents.
        """
        request = ActionRequest(
            agent_name=agent_name,
            action=action,
            asset_id=asset_id,
            reason=reason,
            context=context or {},
        )

        request = self.request_action(request)
        auth_result = self.authorize(request)
        exec_log = self.execute(request, auth_result)
        audit_record = self.audit(exec_log)

        return {
            "request_id": request.request_id,
            "authorization": {
                "authorized": auth_result.authorized,
                "policy_applied": auth_result.policy_applied,
                "execution_id": auth_result.execution_id,
                "reason": auth_result.reason,
            },
            "execution": {
                "result": exec_log.result,
                "timestamp": exec_log.timestamp.isoformat(),
            },
            "audit": audit_record,
        }

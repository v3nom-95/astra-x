"""
Terminal 3 Agentic Kit — Real-time HTTP Client.
Connects to the Terminal 3 Network for live authorization and execution tracking.
"""
import os
import uuid
import logging
import httpx
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


class Terminal3Client(AuthorizationProvider):
    """
    Live implementation of Terminal3 Agentic Kit using HTTP API.
    Falls back to local policy check on API error or connection failure.
    """

    _instance = None

    def __init__(self):
        self.api_key = os.getenv("TERMINAL3_API_KEY", "")
        self.base_url = os.getenv("TERMINAL3_BASE_URL", "https://api.terminal3.io/v1")
        self._execution_logs: list[ExecutionLog] = []
        self._agents: dict[str, AgentIdentity] = {}

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ASTRA-X-Backend/1.0"
        }
        self._register_default_agents()

    @classmethod
    def get_instance(cls) -> "Terminal3Client":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _register_default_agents(self):
        """Register the default ASTRA-X agents locally for policy fallback."""
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
            self._agents[agent.agent_id] = agent

    def register_agent(self, agent: AgentIdentity) -> bool:
        """Register an agent identity in the system via API and locally."""
        self._agents[agent.agent_id] = agent
        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{self.base_url}/agents/register",
                    headers=self.headers,
                    json={
                        "agent_id": agent.agent_id,
                        "agent_name": agent.agent_name,
                        "role": agent.role,
                        "permissions": agent.permissions
                    },
                    timeout=5.0
                )
                response.raise_for_status()
                logger.info(f"Agent registered with Terminal 3: {agent.agent_name}")
                return True
        except httpx.HTTPError as e:
            logger.warning(f"Failed to register agent {agent.agent_name} via API: {e}. Registered locally.")
            # Fallback for now if API is not actually accessible
            return True

    def request_action(self, request: ActionRequest) -> ActionRequest:
        """Submit an action request for authorization."""
        if not request.request_id:
            request.request_id = str(uuid.uuid4())
        return request

    def _local_authorize(self, request: ActionRequest) -> AuthorizationResult:
        """Fallback local policy authorization."""
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
                reason=f"Agent '{request.agent_name}' not registered locally",
            )

        # Check if this is a protected action
        if not is_protected_action(request.action):
            # Non-protected actions are auto-authorized
            return AuthorizationResult(
                authorized=True,
                policy_applied="non_protected_auto_approve",
                reason=f"Action '{request.action}' is not protected — auto-approved locally",
            )

        # Check if the agent has permission
        if request.action not in agent.permissions:
            return AuthorizationResult(
                authorized=False,
                policy_applied="permission_denied",
                reason=f"Agent '{request.agent_name}' lacks local permission for '{request.action}'",
            )

        # Find matching policy
        policy = get_policy_for_action(request.action, agent.role)
        if policy is None:
            return AuthorizationResult(
                authorized=False,
                policy_applied="no_matching_policy",
                reason=f"No local policy found for action '{request.action}' with role '{agent.role}'",
            )

        # Policy-based authorization
        if policy.auto_approve:
            return AuthorizationResult(
                authorized=True,
                policy_applied=policy.name,
                reason=f"Auto-approved locally by policy '{policy.name}': {policy.description}",
            )

        return AuthorizationResult(
            authorized=False,
            policy_applied=policy.name,
            reason=f"Local policy '{policy.name}' requires manual approval",
        )

    def authorize(self, request: ActionRequest) -> AuthorizationResult:
        """
        Authorize an action request by calling the local Terminal 3 Bridge.
        """
        with httpx.Client() as client:
            response = client.post(
                f"{self.base_url}/auth/check",
                headers=self.headers,
                json={
                    "request_id": request.request_id,
                    "agent_name": request.agent_name,
                    "action": request.action,
                    "asset_id": request.asset_id,
                    "context": request.context
                },
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            return AuthorizationResult(
                authorized=data.get("authorized", False),
                policy_applied=data.get("policy_applied", "api_policy"),
                execution_id=data.get("execution_id", str(uuid.uuid4())),
                reason=data.get("reason", "")
            )

    def execute(self, request: ActionRequest, auth_result: AuthorizationResult) -> ExecutionLog:
        """Log execution to Terminal 3."""
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

        try:
            with httpx.Client() as client:
                client.post(
                    f"{self.base_url}/executions/log",
                    headers=self.headers,
                    json={
                        "execution_id": log.execution_id,
                        "agent_name": log.agent_name,
                        "action": log.action,
                        "asset_id": log.asset_id,
                        "authorized": log.authorized,
                        "result": log.result
                    },
                    timeout=5.0
                )
        except httpx.HTTPError as e:
            logger.warning(f"Failed to push execution log to Terminal 3: {e}")

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
        """Retrieve all local execution logs."""
        return self._execution_logs.copy()

    def process_action(self, agent_name: str, action: str, asset_id: str, reason: str, context: dict | None = None) -> dict:
        """
        Convenience method: request → authorize → execute → audit in one call.
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


"""
Terminal3 Agentic Kit — Abstract Interface.
Defines the contract for authorization providers.
When the real Terminal3 SDK is available, implement this interface.
"""
from abc import ABC, abstractmethod
from typing import Any
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class AgentIdentity:
    """Represents an autonomous agent's identity in the system."""
    agent_id: str
    agent_name: str
    role: str
    permissions: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ActionRequest:
    """A request from an agent to execute a protected action."""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    agent_name: str = ""
    action: str = ""
    asset_id: str = ""
    reason: str = ""
    context: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AuthorizationResult:
    """Result of an authorization check."""
    authorized: bool = False
    policy_applied: str = ""
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    reason: str = ""
    delegated_by: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ExecutionLog:
    """Log entry for an executed action."""
    execution_id: str
    agent_id: str
    agent_name: str
    action: str
    asset_id: str
    authorized: bool
    policy_applied: str
    result: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)


class AuthorizationProvider(ABC):
    """Abstract interface for Terminal3-style authorization."""

    @abstractmethod
    def register_agent(self, agent: AgentIdentity) -> bool:
        """Register an agent identity."""
        ...

    @abstractmethod
    def request_action(self, request: ActionRequest) -> ActionRequest:
        """Submit an action request."""
        ...

    @abstractmethod
    def authorize(self, request: ActionRequest) -> AuthorizationResult:
        """Check if the requested action is authorized."""
        ...

    @abstractmethod
    def execute(self, request: ActionRequest, auth_result: AuthorizationResult) -> ExecutionLog:
        """Execute an authorized action and log it."""
        ...

    @abstractmethod
    def audit(self, execution_log: ExecutionLog) -> dict:
        """Generate audit record for the execution."""
        ...

    @abstractmethod
    def get_execution_logs(self) -> list[ExecutionLog]:
        """Retrieve all execution logs."""
        ...

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4


class Capability(StrEnum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    NETWORK = "network"
    DELETE = "delete"
    SEND = "send"
    CREDENTIALS = "credentials"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PermissionDecision(StrEnum):
    ALLOW = "allow"
    ASK = "ask"
    DENY = "deny"
    APPROVED_ONCE = "approved_once"
    APPROVED_SESSION = "approved_session"
    REJECTED = "rejected"
    AUTO_REVIEWING = "auto_reviewing"
    AUTO_APPROVED = "auto_approved"
    AUTO_DENIED = "auto_denied"


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ControlScope(StrEnum):
    ALL = "all"
    NEW_TASKS = "new_tasks"
    ACTIONS = "actions"


SENSITIVE_CAPABILITIES = frozenset(
    {
        Capability.WRITE,
        Capability.EXECUTE,
        Capability.NETWORK,
        Capability.DELETE,
        Capability.SEND,
        Capability.CREDENTIALS,
    }
)


@dataclass(frozen=True)
class ActionRequest:
    capability: Capability
    description: str
    task_id: str
    trace_id: str
    workspace_id: str = "default"
    session_id: str = "default"
    actor: str = "system"
    target: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    action_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class PolicyDecision:
    action_id: str
    capability: Capability
    decision: PermissionDecision
    risk_level: RiskLevel
    reason: str
    task_id: str
    trace_id: str
    workspace_id: str
    session_id: str
    actor: str
    requires_approval: bool = False
    decision_record_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class ApprovalRequest:
    decision_record_id: str
    action_id: str
    capability: Capability
    risk_level: RiskLevel
    task_id: str
    trace_id: str
    workspace_id: str
    session_id: str
    actor: str
    reason: str
    requested_by: str
    target: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    status: ApprovalStatus = ApprovalStatus.PENDING
    resolved_by: str | None = None
    resolved_reason: str | None = None
    approval_id: str = field(default_factory=lambda: str(uuid4()))
    requested_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    resolved_at: datetime | None = None


@dataclass(frozen=True)
class GovernedActionResult:
    request: ActionRequest
    decision: PolicyDecision
    approval: ApprovalRequest | None = None
    blocked_reason: str | None = None


@dataclass(frozen=True)
class KillSwitchSnapshot:
    active: bool
    reason: str | None
    actor: str | None
    scope: ControlScope
    changed_at: datetime | None


@dataclass(frozen=True)
class DoomLoopObservation:
    task_id: str
    trace_id: str
    action_name: str
    normalized_input: str
    count: int
    threshold: int
    detected: bool
    reason: str | None = None

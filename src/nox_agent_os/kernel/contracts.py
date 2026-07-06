from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

SCHEMA_VERSION = 2


class EventType(StrEnum):
    TASK_CREATED = "task_created"
    TASK_STATUS_CHANGED = "task_status_changed"
    STATE_TRANSITION_DENIED = "state_transition_denied"
    POLICY_DECISION_RECORDED = "policy_decision_recorded"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_RESOLVED = "approval_resolved"
    KILL_SWITCH_CHANGED = "kill_switch_changed"
    KILL_SWITCH_BLOCKED = "kill_switch_blocked"
    DOOM_LOOP_DETECTED = "doom_loop_detected"
    MODEL_ROUTE_SELECTED = "model_route_selected"
    MODEL_INVOCATION_COMPLETED = "model_invocation_completed"


class TaskStatus(StrEnum):
    CREATED = "created"
    CLASSIFIED = "classified"
    PLANNED = "planned"
    POLICY_REVIEW = "policy_review"
    WAITING_APPROVAL = "waiting_approval"
    QUEUED = "queued"
    RUNNING = "running"
    WAITING_MODEL = "waiting_model"
    WAITING_TOOL = "waiting_tool"
    WAITING_SUBAGENT = "waiting_subagent"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    TIMED_OUT = "timed_out"
    KILLED = "killed"
    RECOVERING = "recovering"
    REPLAYING = "replaying"
    ROLLED_BACK = "rolled_back"


class AgentStatus(StrEnum):
    SPAWNING = "spawning"
    ACTIVE = "active"
    IDLE = "idle"
    AWAITING_USER_INPUT = "awaiting_user_input"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    PAUSED = "paused"
    FINISHED = "finished"
    STOPPED = "stopped"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"


class RunMode(StrEnum):
    PLAN = "plan"
    ACT = "act"
    BUILD = "build"
    REVIEW = "review"
    EXPLORE = "explore"
    RESEARCH = "research"
    DEEP_PLANNING = "deep_planning"
    READ_ONLY = "read_only"
    AUTONOMOUS = "autonomous"
    INCIDENT_MODE = "incident_mode"


class RecoveryState(StrEnum):
    CHECKPOINTED = "checkpointed"
    COMPACTING = "compacting"
    COMPACTED = "compacted"
    REWIND_REQUESTED = "rewind_requested"
    RESTORE_FILES = "restore_files"
    RESTORE_CONTEXT = "restore_context"
    RESTORE_ALL = "restore_all"
    REPLAYING = "replaying"


class TerminationReason(StrEnum):
    COMPLETED = "completed"
    USER_STOP = "user_stop"
    MAX_STEPS = "max_steps"
    MAX_TOKENS = "max_tokens"
    MAX_TIME = "max_time"
    POLICY_DENIED = "policy_denied"
    TOOL_ERROR = "tool_error"
    MODEL_ERROR = "model_error"
    RATE_LIMITED = "rate_limited"
    KILL_SWITCH = "kill_switch"
    SHUTDOWN_GRACEFUL = "shutdown_graceful"
    DOOM_LOOP_DETECTED = "doom_loop_detected"


TERMINAL_TASK_STATUSES = frozenset(
    {
        TaskStatus.COMPLETED,
        TaskStatus.CANCELLED,
        TaskStatus.REJECTED,
        TaskStatus.TIMED_OUT,
        TaskStatus.KILLED,
    }
)


@dataclass(frozen=True)
class EventRecord:
    event_type: EventType
    trace_id: str
    task_id: str
    session_id: str
    workspace_id: str
    actor: str
    instance_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    source_module: str = "kernel"
    risk_level: str | None = None
    decision_record_id: str | None = None
    previous_event_id: str | None = None
    schema_version: int = SCHEMA_VERSION
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class TaskState:
    task_id: str
    user_goal: str
    workspace_id: str
    session_id: str
    trace_id: str
    status: TaskStatus
    instance_id: str | None = None
    agent_status: AgentStatus = AgentStatus.IDLE
    run_mode: RunMode = RunMode.PLAN
    recovery_state: RecoveryState | None = None
    termination_reason: TerminationReason | None = None
    current_state: dict[str, Any] = field(default_factory=dict)

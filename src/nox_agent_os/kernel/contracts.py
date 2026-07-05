from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

SCHEMA_VERSION = 1


class EventType(StrEnum):
    TASK_CREATED = "task_created"
    TASK_STATUS_CHANGED = "task_status_changed"
    STATE_TRANSITION_DENIED = "state_transition_denied"


class TaskStatus(StrEnum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    KILLED = "killed"


TERMINAL_TASK_STATUSES = frozenset(
    {
        TaskStatus.COMPLETED,
        TaskStatus.CANCELLED,
        TaskStatus.REJECTED,
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
    current_state: dict[str, Any] = field(default_factory=dict)

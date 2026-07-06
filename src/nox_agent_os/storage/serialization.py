from __future__ import annotations

from datetime import datetime
from typing import Any

from nox_agent_os.kernel.contracts import (
    AgentStatus,
    EventRecord,
    EventType,
    RecoveryState,
    RunMode,
    TaskState,
    TaskStatus,
    TerminationReason,
)
from nox_agent_os.storage.contracts import ConfigEntry, EvidenceRecord


def event_to_record(event: EventRecord) -> dict[str, Any]:
    return {
        "event_id": event.event_id,
        "event_type": event.event_type.value,
        "schema_version": event.schema_version,
        "trace_id": event.trace_id,
        "task_id": event.task_id,
        "session_id": event.session_id,
        "workspace_id": event.workspace_id,
        "instance_id": event.instance_id,
        "actor": event.actor,
        "timestamp": event.timestamp.isoformat(),
        "payload": event.payload,
        "previous_event_id": event.previous_event_id,
        "source_module": event.source_module,
        "risk_level": event.risk_level,
        "decision_record_id": event.decision_record_id,
    }


def event_from_record(data: dict[str, Any]) -> EventRecord:
    return EventRecord(
        event_type=EventType(data["event_type"]),
        trace_id=str(data["trace_id"]),
        task_id=str(data["task_id"]),
        session_id=str(data["session_id"]),
        workspace_id=str(data["workspace_id"]),
        actor=str(data["actor"]),
        instance_id=data.get("instance_id"),
        payload=dict(data.get("payload") or {}),
        source_module=str(data.get("source_module") or "kernel"),
        risk_level=data.get("risk_level"),
        decision_record_id=data.get("decision_record_id"),
        previous_event_id=data.get("previous_event_id"),
        schema_version=int(data.get("schema_version") or 1),
        event_id=str(data["event_id"]),
        timestamp=datetime.fromisoformat(str(data["timestamp"])),
    )


def task_to_record(task: TaskState) -> dict[str, Any]:
    return {
        "task_id": task.task_id,
        "user_goal": task.user_goal,
        "workspace_id": task.workspace_id,
        "instance_id": task.instance_id,
        "session_id": task.session_id,
        "trace_id": task.trace_id,
        "status": task.status.value,
        "agent_status": task.agent_status.value,
        "run_mode": task.run_mode.value,
        "recovery_state": task.recovery_state.value if task.recovery_state else None,
        "termination_reason": (
            task.termination_reason.value if task.termination_reason else None
        ),
        "current_state": task.current_state,
    }


def task_from_record(data: dict[str, Any]) -> TaskState:
    recovery_state = data.get("recovery_state")
    termination_reason = data.get("termination_reason")
    return TaskState(
        task_id=str(data["task_id"]),
        user_goal=str(data["user_goal"]),
        workspace_id=str(data["workspace_id"]),
        session_id=str(data["session_id"]),
        trace_id=str(data["trace_id"]),
        status=TaskStatus(data["status"]),
        instance_id=data.get("instance_id"),
        agent_status=AgentStatus(data.get("agent_status") or AgentStatus.IDLE.value),
        run_mode=RunMode(data.get("run_mode") or RunMode.PLAN.value),
        recovery_state=RecoveryState(recovery_state) if recovery_state else None,
        termination_reason=(
            TerminationReason(termination_reason) if termination_reason else None
        ),
        current_state=dict(data.get("current_state") or {}),
    )


def config_to_record(entry: ConfigEntry) -> dict[str, Any]:
    return {
        "namespace": entry.namespace,
        "key": entry.key,
        "value": entry.value,
        "schema_version": entry.schema_version,
        "updated_at": entry.updated_at.isoformat(),
    }


def config_from_record(data: dict[str, Any]) -> ConfigEntry:
    return ConfigEntry(
        namespace=str(data["namespace"]),
        key=str(data["key"]),
        value=data.get("value"),
        schema_version=int(data.get("schema_version") or 1),
        updated_at=datetime.fromisoformat(str(data["updated_at"])),
    )


def evidence_to_record(evidence: EvidenceRecord) -> dict[str, Any]:
    return {
        "evidence_id": evidence.evidence_id,
        "workspace_id": evidence.workspace_id,
        "source": evidence.source,
        "content_ref": evidence.content_ref,
        "task_id": evidence.task_id,
        "trace_id": evidence.trace_id,
        "metadata": evidence.metadata,
        "schema_version": evidence.schema_version,
        "created_at": evidence.created_at.isoformat(),
    }


def evidence_from_record(data: dict[str, Any]) -> EvidenceRecord:
    return EvidenceRecord(
        workspace_id=str(data["workspace_id"]),
        source=str(data["source"]),
        content_ref=str(data["content_ref"]),
        task_id=data.get("task_id"),
        trace_id=data.get("trace_id"),
        metadata=dict(data.get("metadata") or {}),
        schema_version=int(data.get("schema_version") or 1),
        evidence_id=str(data["evidence_id"]),
        created_at=datetime.fromisoformat(str(data["created_at"])),
    )

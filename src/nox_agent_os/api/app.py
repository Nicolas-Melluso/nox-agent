from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from nox_agent_os import __version__
from nox_agent_os.cli.runtime import CliKernelContext, load_kernel_context
from nox_agent_os.governance import (
    ApprovalAlreadyResolvedError,
    ApprovalNotFoundError,
    Capability,
    ControlScope,
)
from nox_agent_os.kernel import EventRecord, EventStoreError, EventType, TaskStatus
from nox_agent_os.kernel.kernel import KernelControlBlockedError, TaskNotFoundError
from nox_agent_os.workspace import WorkspaceError


class TaskCreateRequest(BaseModel):
    goal: str = Field(min_length=1)


class TaskTransitionRequest(BaseModel):
    status: TaskStatus
    reason: str = Field(min_length=1)


class PolicyCheckRequest(BaseModel):
    task_id: str = Field(min_length=1)
    capability: Capability
    target: str | None = None
    description: str | None = None


class ApprovalResolutionRequest(BaseModel):
    reason: str = "resolved by api"


class KillSwitchOnRequest(BaseModel):
    reason: str = Field(min_length=1)
    scope: ControlScope = ControlScope.ALL


class KillSwitchOffRequest(BaseModel):
    reason: str = "resumed by api"


def create_app(*, workspace_path: Path | None = None) -> FastAPI:
    app = FastAPI(
        title="Nox Local API",
        version=__version__,
        description="Local HTTP adapter for the Nox governed kernel.",
    )

    def context() -> CliKernelContext:
        try:
            return load_kernel_context(workspace_path)
        except WorkspaceError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except EventStoreError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {"status": "ok", "version": __version__}

    @app.get("/status")
    def status() -> dict[str, Any]:
        ctx = context()
        snapshot = ctx.kernel.resource_snapshot()
        return {
            "workspace": str(ctx.workspace.workspace_dir.parent),
            "event_log": str(ctx.workspace.event_log_path),
            "health": snapshot.health,
            "total_events": snapshot.total_events,
            "total_tasks": snapshot.total_tasks,
            "task_status_counts": snapshot.task_status_counts,
            "pending_approvals": snapshot.pending_approvals,
            "kill_switch_active": snapshot.kill_switch_active,
            "kill_switch_scope": snapshot.kill_switch_scope,
            "blocked_tasks": snapshot.blocked_tasks,
            "running_tasks": snapshot.running_tasks,
            "completed_tasks": snapshot.completed_tasks,
            "last_event_id": snapshot.last_event_id,
            "last_event_type": snapshot.last_event_type,
        }

    @app.post("/tasks", status_code=201)
    def create_task(request: TaskCreateRequest) -> dict[str, Any]:
        ctx = context()
        try:
            task = ctx.kernel.create_task(
                request.goal,
                workspace_id=str(ctx.workspace.workspace_dir.parent.resolve()),
                actor="api",
            )
        except KernelControlBlockedError as exc:
            raise HTTPException(status_code=423, detail=str(exc)) from exc

        return task_to_response(task)

    @app.get("/tasks")
    def list_tasks() -> list[dict[str, Any]]:
        ctx = context()
        created_events = ctx.kernel.audit_trail.list_events(event_type=EventType.TASK_CREATED)
        return [
            task_to_response(ctx.kernel.get_task(event.task_id))
            for event in created_events
        ]

    @app.get("/tasks/{task_id}")
    def get_task(task_id: str) -> dict[str, Any]:
        ctx = context()
        try:
            return task_to_response(ctx.kernel.get_task(task_id))
        except TaskNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/tasks/{task_id}/transitions")
    def transition_task(task_id: str, request: TaskTransitionRequest) -> dict[str, Any]:
        ctx = context()
        try:
            task = ctx.kernel.transition_task(
                task_id,
                request.status,
                reason=request.reason,
                actor="api",
            )
        except TaskNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        return task_to_response(task)

    @app.get("/events")
    def list_events(
        limit: int = Query(20, ge=1),
        event_type: EventType | None = Query(None, alias="type"),
    ) -> list[dict[str, Any]]:
        ctx = context()
        events = ctx.kernel.audit_trail.list_events(event_type=event_type)
        return [event_to_response(event) for event in events[-limit:]]

    @app.get("/tasks/{task_id}/events")
    def list_task_events(task_id: str) -> list[dict[str, Any]]:
        ctx = context()
        return [
            event_to_response(event)
            for event in ctx.kernel.audit_trail.list_events(task_id=task_id)
        ]

    @app.post("/policy/check")
    def check_policy(request: PolicyCheckRequest) -> dict[str, Any]:
        ctx = context()
        try:
            result = ctx.kernel.request_capability(
                request.task_id,
                request.capability,
                description=request.description or f"API request {request.capability.value}",
                target=request.target,
                actor="api",
            )
        except TaskNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        return {
            "action_id": result.request.action_id,
            "decision_record_id": result.decision.decision_record_id,
            "decision": result.decision.decision.value,
            "risk_level": result.decision.risk_level.value,
            "reason": result.decision.reason,
            "requires_approval": result.decision.requires_approval,
            "approval": approval_to_response(result.approval)
            if result.approval is not None
            else None,
            "blocked_reason": result.blocked_reason,
        }

    @app.get("/approvals")
    def list_approvals() -> list[dict[str, Any]]:
        ctx = context()
        return [
            approval_to_response(approval)
            for approval in ctx.kernel.approval_queue.list_pending()
        ]

    @app.post("/approvals/{approval_id}/approve")
    def approve_approval(
        approval_id: str,
        request: ApprovalResolutionRequest,
    ) -> dict[str, Any]:
        return resolve_approval(approval_id, approved=True, request=request)

    @app.post("/approvals/{approval_id}/reject")
    def reject_approval(
        approval_id: str,
        request: ApprovalResolutionRequest,
    ) -> dict[str, Any]:
        return resolve_approval(approval_id, approved=False, request=request)

    def resolve_approval(
        approval_id: str,
        *,
        approved: bool,
        request: ApprovalResolutionRequest,
    ) -> dict[str, Any]:
        ctx = context()
        try:
            approval = ctx.kernel.resolve_approval(
                approval_id,
                approved=approved,
                actor="api",
                reason=request.reason,
            )
        except ApprovalNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ApprovalAlreadyResolvedError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

        return approval_to_response(approval)

    @app.get("/kill")
    def get_kill_switch() -> dict[str, Any]:
        snapshot = context().kernel.kill_switch.snapshot()
        return {
            "active": snapshot.active,
            "scope": snapshot.scope.value,
            "reason": snapshot.reason,
            "actor": snapshot.actor,
            "changed_at": snapshot.changed_at.isoformat()
            if snapshot.changed_at is not None
            else None,
        }

    @app.post("/kill/on")
    def activate_kill_switch(request: KillSwitchOnRequest) -> dict[str, Any]:
        snapshot = context().kernel.activate_kill_switch(
            reason=request.reason,
            actor="api",
            scope=request.scope,
        )
        return {
            "active": snapshot.active,
            "scope": snapshot.scope.value,
            "reason": snapshot.reason,
            "actor": snapshot.actor,
            "changed_at": snapshot.changed_at.isoformat()
            if snapshot.changed_at is not None
            else None,
        }

    @app.post("/kill/off")
    def deactivate_kill_switch(request: KillSwitchOffRequest) -> dict[str, Any]:
        snapshot = context().kernel.deactivate_kill_switch(
            reason=request.reason,
            actor="api",
        )
        return {
            "active": snapshot.active,
            "scope": snapshot.scope.value,
            "reason": snapshot.reason,
            "actor": snapshot.actor,
            "changed_at": snapshot.changed_at.isoformat()
            if snapshot.changed_at is not None
            else None,
        }

    return app


def task_to_response(task) -> dict[str, Any]:
    return {
        "task_id": task.task_id,
        "user_goal": task.user_goal,
        "workspace_id": task.workspace_id,
        "session_id": task.session_id,
        "trace_id": task.trace_id,
        "status": task.status.value,
        "agent_status": task.agent_status.value,
        "run_mode": task.run_mode.value,
        "recovery_state": task.recovery_state.value
        if task.recovery_state is not None
        else None,
        "termination_reason": task.termination_reason.value
        if task.termination_reason is not None
        else None,
        "current_state": task.current_state,
    }


def event_to_response(event: EventRecord) -> dict[str, Any]:
    return {
        "event_id": event.event_id,
        "event_type": event.event_type.value,
        "schema_version": event.schema_version,
        "trace_id": event.trace_id,
        "task_id": event.task_id,
        "session_id": event.session_id,
        "workspace_id": event.workspace_id,
        "actor": event.actor,
        "timestamp": event.timestamp.isoformat(),
        "payload": event.payload,
        "previous_event_id": event.previous_event_id,
        "source_module": event.source_module,
        "risk_level": event.risk_level,
        "decision_record_id": event.decision_record_id,
    }


def approval_to_response(approval) -> dict[str, Any]:
    return {
        "approval_id": approval.approval_id,
        "decision_record_id": approval.decision_record_id,
        "action_id": approval.action_id,
        "capability": approval.capability.value,
        "risk_level": approval.risk_level.value,
        "task_id": approval.task_id,
        "trace_id": approval.trace_id,
        "workspace_id": approval.workspace_id,
        "session_id": approval.session_id,
        "actor": approval.actor,
        "reason": approval.reason,
        "requested_by": approval.requested_by,
        "target": approval.target,
        "metadata": approval.metadata,
        "status": approval.status.value,
        "resolved_by": approval.resolved_by,
        "resolved_reason": approval.resolved_reason,
        "requested_at": approval.requested_at.isoformat(),
        "resolved_at": approval.resolved_at.isoformat()
        if approval.resolved_at is not None
        else None,
    }

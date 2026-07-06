from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from nox_agent_os.governance import (
    ApprovalRequest,
    ApprovalStatus,
    Capability,
    ControlScope,
    InMemoryApprovalQueue,
    KillSwitch,
    RiskLevel,
)
from nox_agent_os.kernel import AgentKernel, EventRecord, EventType, JsonlEventStore
from nox_agent_os.modeling import ModelConfigError, ModelWorkspaceConfig, load_model_config
from nox_agent_os.workspace import Workspace, WorkspaceError, find_workspace


@dataclass(frozen=True)
class CliKernelContext:
    workspace: Workspace
    event_store: JsonlEventStore
    model_config: ModelWorkspaceConfig
    kernel: AgentKernel


def load_kernel_context(path: Path | None = None) -> CliKernelContext:
    root = Path.cwd() if path is None else path
    workspace = find_workspace(root)
    if workspace is None:
        raise WorkspaceError("No Nox workspace found. Run: nox init")

    event_store = JsonlEventStore(workspace.event_log_path)
    try:
        model_config = load_model_config(workspace.model_config_path)
    except ModelConfigError as exc:
        raise WorkspaceError(str(exc)) from exc
    approval_queue = InMemoryApprovalQueue()
    kill_switch = KillSwitch()
    events = event_store.list_all()

    _restore_pending_approvals(events, approval_queue)
    _restore_kill_switch(events, kill_switch)

    return CliKernelContext(
        workspace=workspace,
        event_store=event_store,
        model_config=model_config,
        kernel=AgentKernel(
            event_store=event_store,
            approval_queue=approval_queue,
            kill_switch=kill_switch,
        ),
    )


def _restore_pending_approvals(
    events: list[EventRecord],
    approval_queue: InMemoryApprovalQueue,
) -> None:
    pending: dict[str, ApprovalRequest] = {}

    for event in events:
        if event.event_type == EventType.APPROVAL_REQUESTED:
            approval_id = str(event.payload["approval_id"])
            pending[approval_id] = ApprovalRequest(
                decision_record_id=str(event.decision_record_id or ""),
                action_id=str(event.payload.get("action_id") or ""),
                capability=Capability(event.payload["capability"]),
                risk_level=RiskLevel(event.risk_level or RiskLevel.MEDIUM.value),
                task_id=event.task_id,
                trace_id=event.trace_id,
                workspace_id=event.workspace_id,
                instance_id=event.instance_id,
                session_id=event.session_id,
                actor=event.actor,
                reason=str(event.payload.get("reason") or ""),
                requested_by=event.actor,
                target=event.payload.get("target"),
                metadata=dict(event.payload.get("metadata") or {}),
                status=ApprovalStatus.PENDING,
                approval_id=approval_id,
                requested_at=event.timestamp,
            )
            continue

        if event.event_type == EventType.APPROVAL_RESOLVED:
            approval_id = str(event.payload["approval_id"])
            pending.pop(approval_id, None)

    for approval in pending.values():
        approval_queue.restore_pending(approval)


def _restore_kill_switch(events: list[EventRecord], kill_switch: KillSwitch) -> None:
    kill_switch_events = [
        event for event in events if event.event_type == EventType.KILL_SWITCH_CHANGED
    ]
    if not kill_switch_events:
        return

    last_event = kill_switch_events[-1]
    kill_switch.restore(
        active=bool(last_event.payload.get("active")),
        reason=last_event.payload.get("reason"),
        actor=last_event.actor,
        scope=ControlScope(last_event.payload.get("scope") or ControlScope.ALL.value),
        changed_at=last_event.timestamp,
    )

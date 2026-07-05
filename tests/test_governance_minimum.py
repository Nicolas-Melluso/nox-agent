import pytest

from nox_agent_os.governance import (
    ApprovalStatus,
    Capability,
    ControlScope,
    DoomLoopGuard,
    PermissionDecision,
)
from nox_agent_os.kernel import AgentKernel, EventType, KernelControlBlockedError, TaskStatus


def test_read_capability_is_allowed_and_audited() -> None:
    kernel = AgentKernel()
    task = kernel.create_task("inspect local context")

    result = kernel.request_capability(
        task.task_id,
        Capability.READ,
        description="read a project file",
        target="README.md",
    )
    events = kernel.event_store.list_for_task(task.task_id)
    replayed = kernel.get_task(task.task_id)

    assert result.decision.decision == PermissionDecision.ALLOW
    assert result.approval is None
    assert events[-1].event_type == EventType.POLICY_DECISION_RECORDED
    assert replayed.current_state["last_policy_decision"]["decision"] == "allow"
    assert replayed.current_state["last_policy_decision"]["capability"] == "read"


def test_write_capability_requires_approval_and_can_be_resolved() -> None:
    kernel = AgentKernel()
    task = kernel.create_task("change a file")

    result = kernel.request_capability(
        task.task_id,
        Capability.WRITE,
        description="write a file",
        target="src/example.py",
    )

    assert result.decision.decision == PermissionDecision.ASK
    assert result.approval is not None
    assert result.approval.status == ApprovalStatus.PENDING
    assert kernel.approval_queue.list_pending() == [result.approval]

    resolved = kernel.resolve_approval(
        result.approval.approval_id,
        approved=True,
        actor="user",
        reason="safe local edit",
    )
    events = kernel.event_store.list_for_task(task.task_id)
    replayed = kernel.get_task(task.task_id)

    assert resolved.status == ApprovalStatus.APPROVED
    assert events[-1].event_type == EventType.APPROVAL_RESOLVED
    assert replayed.current_state["pending_approval_id"] is None
    assert replayed.current_state["last_approval"]["status"] == "approved"


def test_delete_capability_is_denied_by_default() -> None:
    kernel = AgentKernel()
    task = kernel.create_task("remove dangerous files")

    result = kernel.request_capability(
        task.task_id,
        Capability.DELETE,
        description="delete a directory",
        target="C:/important",
    )

    assert result.decision.decision == PermissionDecision.DENY
    assert result.approval is None
    assert result.decision.risk_level == "critical"


def test_kill_switch_blocks_new_tasks_and_records_event() -> None:
    kernel = AgentKernel()
    kernel.activate_kill_switch(reason="maintenance", actor="user")

    with pytest.raises(KernelControlBlockedError):
        kernel.create_task("should not start")

    events = kernel.event_store.list_all()

    assert events[-1].event_type == EventType.KILL_SWITCH_BLOCKED
    assert events[-1].payload["operation"] == "create_task"


def test_kill_switch_can_block_governed_actions_without_stopping_task_creation() -> None:
    kernel = AgentKernel()
    task = kernel.create_task("inspect but do not act")
    kernel.activate_kill_switch(
        reason="freeze actions",
        actor="user",
        scope=ControlScope.ACTIONS,
    )

    result = kernel.request_capability(
        task.task_id,
        Capability.READ,
        description="read a file",
        target="README.md",
    )

    assert result.decision.decision == PermissionDecision.DENY
    assert result.blocked_reason == "Kill switch blocks governed actions."
    assert any(
        event.event_type == EventType.KILL_SWITCH_BLOCKED
        for event in kernel.event_store.list_for_task(task.task_id)
    )


def test_doom_loop_detection_blocks_repeated_action() -> None:
    kernel = AgentKernel(doom_loop_guard=DoomLoopGuard(threshold=3))
    task = kernel.create_task("avoid repeating the same action")

    for _ in range(2):
        result = kernel.request_capability(
            task.task_id,
            Capability.READ,
            description="read same file",
            target="README.md",
        )
        assert result.decision.decision == PermissionDecision.ALLOW

    blocked = kernel.request_capability(
        task.task_id,
        Capability.READ,
        description="read same file",
        target="README.md",
    )
    replayed = kernel.get_task(task.task_id)
    event_types = [event.event_type for event in kernel.event_store.list_for_task(task.task_id)]

    assert blocked.decision.decision == PermissionDecision.DENY
    assert blocked.blocked_reason is not None
    assert replayed.status == TaskStatus.BLOCKED
    assert EventType.DOOM_LOOP_DETECTED in event_types

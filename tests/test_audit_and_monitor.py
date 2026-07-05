from nox_agent_os.governance import Capability, ControlScope, DoomLoopGuard
from nox_agent_os.kernel import AgentKernel, EventType, TaskStatus


def test_audit_trail_lists_policy_approvals_blocks_and_trace_events() -> None:
    kernel = AgentKernel(doom_loop_guard=DoomLoopGuard(threshold=3))
    task = kernel.create_task("audit governed behavior")

    allowed = kernel.request_capability(
        task.task_id,
        Capability.READ,
        description="read one file",
        target="README.md",
    )
    approval_result = kernel.request_capability(
        task.task_id,
        Capability.WRITE,
        description="write one file",
        target="docs/example.md",
    )
    assert approval_result.approval is not None
    kernel.resolve_approval(
        approval_result.approval.approval_id,
        approved=False,
        actor="user",
        reason="not needed",
    )

    trace_events = kernel.audit_trail.list_for_trace(task.trace_id)
    policy_events = kernel.audit_trail.list_policy_decisions()
    approval_events = kernel.audit_trail.list_approvals()
    summary = kernel.audit_trail.summary()

    assert allowed.decision.decision == "allow"
    assert len(trace_events) == len(kernel.event_store.list_for_task(task.task_id))
    assert len(policy_events) == 2
    assert [event.event_type for event in approval_events] == [
        EventType.APPROVAL_REQUESTED,
        EventType.APPROVAL_RESOLVED,
    ]
    assert summary.total_events == len(trace_events)
    assert summary.policy_decisions == 2
    assert summary.approval_requests == 1
    assert summary.approval_resolutions == 1


def test_audit_trail_reports_block_events() -> None:
    kernel = AgentKernel(doom_loop_guard=DoomLoopGuard(threshold=2))
    task = kernel.create_task("detect repeat")

    kernel.request_capability(
        task.task_id,
        Capability.READ,
        description="read same file",
        target="README.md",
    )
    kernel.request_capability(
        task.task_id,
        Capability.READ,
        description="read same file",
        target="README.md",
    )

    blocks = kernel.audit_trail.list_blocks()
    replayed = kernel.get_task(task.task_id)

    assert replayed.status == TaskStatus.BLOCKED
    assert [event.event_type for event in blocks] == [EventType.DOOM_LOOP_DETECTED]
    assert kernel.audit_trail.summary().doom_loop_events == 1


def test_resource_monitor_reports_kernel_snapshot() -> None:
    kernel = AgentKernel()
    first = kernel.create_task("running task")
    second = kernel.create_task("waiting approval")
    kernel.transition_task(first.task_id, TaskStatus.RUNNING, reason="start")
    kernel.request_capability(
        second.task_id,
        Capability.WRITE,
        description="write one file",
        target="docs/example.md",
    )

    snapshot = kernel.resource_snapshot()

    assert snapshot.health == "ok"
    assert snapshot.total_tasks == 2
    assert snapshot.task_status_counts == {
        TaskStatus.RUNNING.value: 1,
        TaskStatus.CREATED.value: 1,
    }
    assert snapshot.pending_approvals == 1
    assert snapshot.running_tasks == 1
    assert snapshot.last_event_type == EventType.APPROVAL_REQUESTED.value


def test_resource_monitor_reports_kill_switch_health() -> None:
    kernel = AgentKernel()
    kernel.activate_kill_switch(
        reason="freeze actions",
        actor="user",
        scope=ControlScope.ACTIONS,
    )

    snapshot = kernel.resource_snapshot()

    assert snapshot.health == "kill_switch_active"
    assert snapshot.kill_switch_active is True
    assert snapshot.kill_switch_scope == "actions"
    assert snapshot.total_tasks == 0

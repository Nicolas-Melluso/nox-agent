from nox_agent_os.kernel import AgentKernel, EventType, InMemoryEventStore, TaskStatus


def test_create_task_emits_event_contract() -> None:
    kernel = AgentKernel()

    task = kernel.create_task("build the kernel", workspace_id="workspace-a")
    events = kernel.event_store.list_for_task(task.task_id)

    assert task.status == TaskStatus.CREATED
    assert task.trace_id
    assert len(events) == 1
    assert events[0].event_type == EventType.TASK_CREATED
    assert events[0].schema_version == 1
    assert events[0].trace_id == task.trace_id
    assert events[0].workspace_id == "workspace-a"


def test_replay_reconstructs_task_state() -> None:
    store = InMemoryEventStore()
    kernel = AgentKernel(event_store=store)

    created = kernel.create_task("persist through replay")
    reconstructed = kernel.get_task(created.task_id)

    assert reconstructed == created


def test_transition_updates_state_by_replay() -> None:
    kernel = AgentKernel()

    task = kernel.create_task("move state")
    running = kernel.transition_task(task.task_id, TaskStatus.RUNNING, reason="start")

    assert running.status == TaskStatus.RUNNING
    assert running.current_state["last_transition_reason"] == "start"


def test_invalid_terminal_to_running_transition_is_denied() -> None:
    kernel = AgentKernel()

    task = kernel.create_task("do not resurrect")
    kernel.transition_task(task.task_id, TaskStatus.COMPLETED, reason="done")
    after_denied = kernel.transition_task(task.task_id, TaskStatus.RUNNING, reason="restart")
    events = kernel.event_store.list_for_task(task.task_id)

    assert after_denied.status == TaskStatus.COMPLETED
    assert events[-1].event_type == EventType.STATE_TRANSITION_DENIED

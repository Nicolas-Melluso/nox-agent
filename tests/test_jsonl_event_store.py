from nox_agent_os.kernel import AgentKernel, EventType, JsonlEventStore, TaskStatus


def test_jsonl_event_store_persists_events_between_kernels(tmp_path) -> None:
    event_log = tmp_path / ".nox" / "events.jsonl"
    first_kernel = AgentKernel(event_store=JsonlEventStore(event_log))

    created = first_kernel.create_task("persist through jsonl")
    first_kernel.transition_task(created.task_id, TaskStatus.RUNNING, reason="start")

    second_kernel = AgentKernel(event_store=JsonlEventStore(event_log))
    replayed = second_kernel.get_task(created.task_id)
    events = second_kernel.event_store.list_for_task(created.task_id)

    assert replayed.status == TaskStatus.RUNNING
    assert replayed.trace_id == created.trace_id
    assert [event.event_type for event in events] == [
        EventType.TASK_CREATED,
        EventType.TASK_STATUS_CHANGED,
    ]
    assert events[1].previous_event_id == events[0].event_id

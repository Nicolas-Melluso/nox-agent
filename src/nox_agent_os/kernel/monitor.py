from __future__ import annotations

from dataclasses import dataclass

from nox_agent_os.governance import InMemoryApprovalQueue, KillSwitch
from nox_agent_os.kernel.contracts import EventRecord, EventType, TaskStatus
from nox_agent_os.kernel.events import EventStore
from nox_agent_os.kernel.state import StateMachineKernel, StateReplayError


@dataclass(frozen=True)
class KernelResourceSnapshot:
    health: str
    total_events: int
    total_tasks: int
    task_status_counts: dict[str, int]
    pending_approvals: int
    kill_switch_active: bool
    kill_switch_scope: str
    blocked_tasks: int
    running_tasks: int
    completed_tasks: int
    last_event_id: str | None
    last_event_type: str | None


class ResourceMonitor:
    def __init__(
        self,
        *,
        event_store: EventStore,
        state_machine: StateMachineKernel,
        approval_queue: InMemoryApprovalQueue,
        kill_switch: KillSwitch,
    ) -> None:
        self._event_store = event_store
        self._state_machine = state_machine
        self._approval_queue = approval_queue
        self._kill_switch = kill_switch

    def snapshot(self) -> KernelResourceSnapshot:
        events = self._event_store.list_all()
        task_ids = self._task_ids(events)
        task_status_counts: dict[str, int] = {}

        for task_id in task_ids:
            try:
                task = self._state_machine.replay(self._event_store.list_for_task(task_id))
            except StateReplayError:
                continue

            status = task.status.value
            task_status_counts[status] = task_status_counts.get(status, 0) + 1

        kill_switch_snapshot = self._kill_switch.snapshot()
        last_event = events[-1] if events else None
        blocked_tasks = task_status_counts.get(TaskStatus.BLOCKED.value, 0)
        running_tasks = task_status_counts.get(TaskStatus.RUNNING.value, 0)
        completed_tasks = task_status_counts.get(TaskStatus.COMPLETED.value, 0)

        health = "ok"
        if kill_switch_snapshot.active:
            health = "kill_switch_active"
        elif blocked_tasks:
            health = "degraded"

        return KernelResourceSnapshot(
            health=health,
            total_events=len(events),
            total_tasks=len(task_ids),
            task_status_counts=task_status_counts,
            pending_approvals=len(self._approval_queue.list_pending()),
            kill_switch_active=kill_switch_snapshot.active,
            kill_switch_scope=kill_switch_snapshot.scope.value,
            blocked_tasks=blocked_tasks,
            running_tasks=running_tasks,
            completed_tasks=completed_tasks,
            last_event_id=last_event.event_id if last_event is not None else None,
            last_event_type=last_event.event_type.value if last_event is not None else None,
        )

    def _task_ids(self, events: list[EventRecord]) -> list[str]:
        task_ids: list[str] = []
        seen: set[str] = set()

        for event in events:
            if event.event_type != EventType.TASK_CREATED:
                continue
            if event.task_id in seen:
                continue
            seen.add(event.task_id)
            task_ids.append(event.task_id)

        return task_ids

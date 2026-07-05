from __future__ import annotations

from uuid import uuid4

from nox_agent_os.kernel.contracts import EventType, TaskState, TaskStatus
from nox_agent_os.kernel.events import EventBus, InMemoryEventStore
from nox_agent_os.kernel.state import StateMachineKernel


class TaskNotFoundError(RuntimeError):
    pass


class AgentKernel:
    def __init__(
        self,
        *,
        event_store: InMemoryEventStore | None = None,
        state_machine: StateMachineKernel | None = None,
    ) -> None:
        self.event_store = event_store or InMemoryEventStore()
        self.event_bus = EventBus(self.event_store)
        self.state_machine = state_machine or StateMachineKernel()

    def create_task(
        self,
        user_goal: str,
        *,
        workspace_id: str = "default",
        session_id: str | None = None,
        actor: str = "user",
    ) -> TaskState:
        task_id = str(uuid4())
        trace_id = str(uuid4())
        resolved_session_id = session_id or str(uuid4())

        self.event_bus.emit(
            event_type=EventType.TASK_CREATED,
            trace_id=trace_id,
            task_id=task_id,
            session_id=resolved_session_id,
            workspace_id=workspace_id,
            actor=actor,
            payload={"user_goal": user_goal},
        )

        return self.get_task(task_id)

    def get_task(self, task_id: str) -> TaskState:
        events = self.event_store.list_for_task(task_id)
        if not events:
            raise TaskNotFoundError(f"Task not found: {task_id}")
        return self.state_machine.replay(events)

    def transition_task(
        self,
        task_id: str,
        target_status: TaskStatus,
        *,
        reason: str,
        actor: str = "system",
    ) -> TaskState:
        current = self.get_task(task_id)

        if not self.state_machine.can_transition(current.status, target_status):
            self.event_bus.emit(
                event_type=EventType.STATE_TRANSITION_DENIED,
                trace_id=current.trace_id,
                task_id=current.task_id,
                session_id=current.session_id,
                workspace_id=current.workspace_id,
                actor=actor,
                payload={
                    "from": current.status.value,
                    "to": target_status.value,
                    "reason": reason,
                },
            )
            return self.get_task(task_id)

        self.event_bus.emit(
            event_type=EventType.TASK_STATUS_CHANGED,
            trace_id=current.trace_id,
            task_id=current.task_id,
            session_id=current.session_id,
            workspace_id=current.workspace_id,
            actor=actor,
            payload={
                "from": current.status.value,
                "to": target_status.value,
                "reason": reason,
            },
        )
        return self.get_task(task_id)

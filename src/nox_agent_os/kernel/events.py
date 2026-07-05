from __future__ import annotations

from typing import Protocol

from nox_agent_os.kernel.contracts import EventRecord, EventType


class EventStore(Protocol):
    def append(self, event: EventRecord) -> EventRecord:
        ...

    def list_for_task(self, task_id: str) -> list[EventRecord]:
        ...

    def list_all(self) -> list[EventRecord]:
        ...


class InMemoryEventStore:
    def __init__(self) -> None:
        self._events: list[EventRecord] = []

    def append(self, event: EventRecord) -> EventRecord:
        self._events.append(event)
        return event

    def list_for_task(self, task_id: str) -> list[EventRecord]:
        return [event for event in self._events if event.task_id == task_id]

    def list_all(self) -> list[EventRecord]:
        return list(self._events)

    def last_event_id_for_task(self, task_id: str) -> str | None:
        events = self.list_for_task(task_id)
        if not events:
            return None
        return events[-1].event_id


class EventBus:
    def __init__(self, store: InMemoryEventStore) -> None:
        self._store = store

    def emit(
        self,
        *,
        event_type: EventType,
        trace_id: str,
        task_id: str,
        session_id: str,
        workspace_id: str,
        actor: str,
        payload: dict,
        source_module: str = "kernel",
        risk_level: str | None = None,
        decision_record_id: str | None = None,
    ) -> EventRecord:
        event = EventRecord(
            event_type=event_type,
            trace_id=trace_id,
            task_id=task_id,
            session_id=session_id,
            workspace_id=workspace_id,
            actor=actor,
            payload=payload,
            source_module=source_module,
            risk_level=risk_level,
            decision_record_id=decision_record_id,
            previous_event_id=self._store.last_event_id_for_task(task_id),
        )
        return self._store.append(event)

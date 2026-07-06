from __future__ import annotations

from nox_agent_os.kernel.contracts import EventRecord, EventType
from nox_agent_os.storage import (
    EventStore,
    EventStoreError,
    InMemoryEventStore,
    JsonlEventStore,
    SQLiteEventStore,
)


class EventBus:
    def __init__(self, store: EventStore) -> None:
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
        instance_id: str | None = None,
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
            instance_id=instance_id,
            payload=payload,
            source_module=source_module,
            risk_level=risk_level,
            decision_record_id=decision_record_id,
            previous_event_id=self._store.last_event_id_for_task(task_id),
        )
        return self._store.append(event)

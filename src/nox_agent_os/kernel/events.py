from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Protocol

from nox_agent_os.kernel.contracts import EventRecord, EventType


class EventStoreError(RuntimeError):
    pass


class EventStore(Protocol):
    def append(self, event: EventRecord) -> EventRecord:
        ...

    def list_for_task(self, task_id: str) -> list[EventRecord]:
        ...

    def list_all(self) -> list[EventRecord]:
        ...

    def last_event_id_for_task(self, task_id: str) -> str | None:
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


class JsonlEventStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def append(self, event: EventRecord) -> EventRecord:
        self.path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with self.path.open("a", encoding="utf-8") as file:
                file.write(json.dumps(self._to_json(event), sort_keys=True) + "\n")
        except OSError as exc:
            raise EventStoreError(f"Could not append event to {self.path}: {exc}") from exc

        return event

    def list_for_task(self, task_id: str) -> list[EventRecord]:
        return [event for event in self.list_all() if event.task_id == task_id]

    def list_all(self) -> list[EventRecord]:
        if not self.path.exists():
            return []

        events: list[EventRecord] = []
        try:
            lines = self.path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            raise EventStoreError(f"Could not read events from {self.path}: {exc}") from exc

        for line_number, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            try:
                events.append(self._from_json(json.loads(line)))
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                raise EventStoreError(
                    f"Invalid event at {self.path}:{line_number}: {exc}"
                ) from exc

        return events

    def last_event_id_for_task(self, task_id: str) -> str | None:
        events = self.list_for_task(task_id)
        if not events:
            return None
        return events[-1].event_id

    def _to_json(self, event: EventRecord) -> dict:
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

    def _from_json(self, data: dict) -> EventRecord:
        return EventRecord(
            event_type=EventType(data["event_type"]),
            trace_id=str(data["trace_id"]),
            task_id=str(data["task_id"]),
            session_id=str(data["session_id"]),
            workspace_id=str(data["workspace_id"]),
            actor=str(data["actor"]),
            payload=dict(data.get("payload") or {}),
            source_module=str(data.get("source_module") or "kernel"),
            risk_level=data.get("risk_level"),
            decision_record_id=data.get("decision_record_id"),
            previous_event_id=data.get("previous_event_id"),
            schema_version=int(data.get("schema_version") or 1),
            event_id=str(data["event_id"]),
            timestamp=datetime.fromisoformat(str(data["timestamp"])),
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

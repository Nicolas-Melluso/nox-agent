from __future__ import annotations

from typing import Any

from nox_agent_os.kernel.contracts import EventRecord, TaskState
from nox_agent_os.storage.contracts import ConfigEntry, EvidenceRecord


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


class InMemoryTaskStore:
    def __init__(self) -> None:
        self._tasks: dict[str, TaskState] = {}

    def upsert(self, task: TaskState) -> TaskState:
        self._tasks[task.task_id] = task
        return task

    def get(self, task_id: str) -> TaskState | None:
        return self._tasks.get(task_id)

    def list_all(self) -> list[TaskState]:
        return list(self._tasks.values())


class InMemoryConfigStore:
    def __init__(self) -> None:
        self._entries: dict[tuple[str, str], ConfigEntry] = {}

    def set(self, namespace: str, key: str, value: Any) -> ConfigEntry:
        entry = ConfigEntry(namespace=namespace, key=key, value=value)
        self._entries[(namespace, key)] = entry
        return entry

    def get(self, namespace: str, key: str) -> ConfigEntry | None:
        return self._entries.get((namespace, key))

    def list_namespace(self, namespace: str) -> list[ConfigEntry]:
        return [
            entry
            for (entry_namespace, _), entry in self._entries.items()
            if entry_namespace == namespace
        ]


class InMemoryEvidenceStore:
    def __init__(self) -> None:
        self._records: dict[str, EvidenceRecord] = {}

    def append(self, evidence: EvidenceRecord) -> EvidenceRecord:
        self._records[evidence.evidence_id] = evidence
        return evidence

    def get(self, evidence_id: str) -> EvidenceRecord | None:
        return self._records.get(evidence_id)

    def list_for_task(self, task_id: str) -> list[EvidenceRecord]:
        return [
            evidence for evidence in self._records.values() if evidence.task_id == task_id
        ]

    def list_all(self) -> list[EvidenceRecord]:
        return list(self._records.values())

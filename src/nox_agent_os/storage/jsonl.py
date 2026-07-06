from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, TypeVar

from nox_agent_os.kernel.contracts import EventRecord, TaskState
from nox_agent_os.storage.contracts import (
    ConfigEntry,
    ConfigStoreError,
    EventStoreError,
    EvidenceRecord,
    EvidenceStoreError,
    TaskStoreError,
)
from nox_agent_os.storage.serialization import (
    config_from_record,
    config_to_record,
    event_from_record,
    event_to_record,
    evidence_from_record,
    evidence_to_record,
    task_from_record,
    task_to_record,
)

T = TypeVar("T")


def _append_jsonl(path: Path, record: dict[str, Any], error_type: type[Exception]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, sort_keys=True) + "\n")
    except OSError as exc:
        raise error_type(f"Could not append record to {path}: {exc}") from exc


def _read_jsonl(
    path: Path,
    *,
    parser: Callable[[dict[str, Any]], T],
    error_type: type[Exception],
) -> list[T]:
    if not path.exists():
        return []

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise error_type(f"Could not read records from {path}: {exc}") from exc

    records: list[T] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            records.append(parser(json.loads(line)))
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise error_type(f"Invalid record at {path}:{line_number}: {exc}") from exc

    return records


class JsonlEventStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def append(self, event: EventRecord) -> EventRecord:
        _append_jsonl(self.path, event_to_record(event), EventStoreError)
        return event

    def list_for_task(self, task_id: str) -> list[EventRecord]:
        return [event for event in self.list_all() if event.task_id == task_id]

    def list_all(self) -> list[EventRecord]:
        return _read_jsonl(
            self.path,
            parser=event_from_record,
            error_type=EventStoreError,
        )

    def last_event_id_for_task(self, task_id: str) -> str | None:
        events = self.list_for_task(task_id)
        if not events:
            return None
        return events[-1].event_id


class JsonlTaskStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def upsert(self, task: TaskState) -> TaskState:
        _append_jsonl(self.path, task_to_record(task), TaskStoreError)
        return task

    def get(self, task_id: str) -> TaskState | None:
        tasks = [task for task in self.list_all() if task.task_id == task_id]
        if not tasks:
            return None
        return tasks[-1]

    def list_all(self) -> list[TaskState]:
        by_id: dict[str, TaskState] = {}
        for task in _read_jsonl(
            self.path,
            parser=task_from_record,
            error_type=TaskStoreError,
        ):
            by_id[task.task_id] = task
        return list(by_id.values())


class JsonlConfigStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def set(self, namespace: str, key: str, value: Any) -> ConfigEntry:
        entry = ConfigEntry(namespace=namespace, key=key, value=value)
        _append_jsonl(self.path, config_to_record(entry), ConfigStoreError)
        return entry

    def get(self, namespace: str, key: str) -> ConfigEntry | None:
        entries = [
            entry
            for entry in self.list_namespace(namespace)
            if entry.key == key
        ]
        if not entries:
            return None
        return entries[-1]

    def list_namespace(self, namespace: str) -> list[ConfigEntry]:
        by_key: dict[str, ConfigEntry] = {}
        for entry in _read_jsonl(
            self.path,
            parser=config_from_record,
            error_type=ConfigStoreError,
        ):
            if entry.namespace == namespace:
                by_key[entry.key] = entry
        return list(by_key.values())


class JsonlEvidenceStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def append(self, evidence: EvidenceRecord) -> EvidenceRecord:
        _append_jsonl(self.path, evidence_to_record(evidence), EvidenceStoreError)
        return evidence

    def get(self, evidence_id: str) -> EvidenceRecord | None:
        for evidence in self.list_all():
            if evidence.evidence_id == evidence_id:
                return evidence
        return None

    def list_for_task(self, task_id: str) -> list[EvidenceRecord]:
        return [
            evidence for evidence in self.list_all() if evidence.task_id == task_id
        ]

    def list_all(self) -> list[EvidenceRecord]:
        return _read_jsonl(
            self.path,
            parser=evidence_from_record,
            error_type=EvidenceStoreError,
        )

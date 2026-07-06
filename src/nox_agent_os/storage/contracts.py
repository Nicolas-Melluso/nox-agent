from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Protocol
from uuid import uuid4

from nox_agent_os.kernel.contracts import EventRecord, TaskState

STORAGE_SCHEMA_VERSION = 1


class StorageError(RuntimeError):
    pass


class EventStoreError(StorageError):
    pass


class ConfigStoreError(StorageError):
    pass


class TaskStoreError(StorageError):
    pass


class EvidenceStoreError(StorageError):
    pass


@dataclass(frozen=True)
class ConfigEntry:
    namespace: str
    key: str
    value: Any
    schema_version: int = STORAGE_SCHEMA_VERSION
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class EvidenceRecord:
    workspace_id: str
    source: str
    content_ref: str
    task_id: str | None = None
    trace_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    schema_version: int = STORAGE_SCHEMA_VERSION
    evidence_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class EventStore(Protocol):
    def append(self, event: EventRecord) -> EventRecord:
        ...

    def list_for_task(self, task_id: str) -> list[EventRecord]:
        ...

    def list_all(self) -> list[EventRecord]:
        ...

    def last_event_id_for_task(self, task_id: str) -> str | None:
        ...


class TaskStore(Protocol):
    def upsert(self, task: TaskState) -> TaskState:
        ...

    def get(self, task_id: str) -> TaskState | None:
        ...

    def list_all(self) -> list[TaskState]:
        ...


class ConfigStore(Protocol):
    def set(self, namespace: str, key: str, value: Any) -> ConfigEntry:
        ...

    def get(self, namespace: str, key: str) -> ConfigEntry | None:
        ...

    def list_namespace(self, namespace: str) -> list[ConfigEntry]:
        ...


class EvidenceStore(Protocol):
    def append(self, evidence: EvidenceRecord) -> EvidenceRecord:
        ...

    def get(self, evidence_id: str) -> EvidenceRecord | None:
        ...

    def list_for_task(self, task_id: str) -> list[EvidenceRecord]:
        ...

    def list_all(self) -> list[EvidenceRecord]:
        ...

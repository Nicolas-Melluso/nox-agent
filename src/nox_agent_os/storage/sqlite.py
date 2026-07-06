from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from nox_agent_os.kernel.contracts import EventRecord, TaskState
from nox_agent_os.storage.contracts import (
    ConfigEntry,
    ConfigStoreError,
    EventStoreError,
    EvidenceRecord,
    EvidenceStoreError,
    STORAGE_SCHEMA_VERSION,
    TaskStoreError,
)
from nox_agent_os.storage.serialization import (
    event_from_record,
    event_to_record,
    evidence_from_record,
    task_from_record,
    task_to_record,
)


def migrate_sqlite_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with sqlite3.connect(path) as connection:
            connection.row_factory = sqlite3.Row
            connection.executescript(
                """
                PRAGMA foreign_keys = ON;

                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    schema_version INTEGER NOT NULL,
                    trace_id TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    workspace_id TEXT NOT NULL,
                    instance_id TEXT,
                    actor TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    previous_event_id TEXT,
                    source_module TEXT NOT NULL,
                    risk_level TEXT,
                    decision_record_id TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_events_task_id
                    ON events(task_id);

                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    schema_version INTEGER NOT NULL,
                    user_goal TEXT NOT NULL,
                    workspace_id TEXT NOT NULL,
                    instance_id TEXT,
                    session_id TEXT NOT NULL,
                    trace_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    agent_status TEXT NOT NULL,
                    run_mode TEXT NOT NULL,
                    recovery_state TEXT,
                    termination_reason TEXT,
                    current_state_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS config (
                    namespace TEXT NOT NULL,
                    key TEXT NOT NULL,
                    schema_version INTEGER NOT NULL,
                    value_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (namespace, key)
                );

                CREATE TABLE IF NOT EXISTS evidence (
                    evidence_id TEXT PRIMARY KEY,
                    schema_version INTEGER NOT NULL,
                    workspace_id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    content_ref TEXT NOT NULL,
                    task_id TEXT,
                    trace_id TEXT,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_evidence_task_id
                    ON evidence(task_id);
                """
            )
            _add_column_if_missing(connection, "events", "instance_id", "TEXT")
            _add_column_if_missing(connection, "tasks", "instance_id", "TEXT")
            for version in range(1, STORAGE_SCHEMA_VERSION + 1):
                connection.execute(
                    """
                    INSERT OR IGNORE INTO schema_migrations(version, applied_at)
                    VALUES (?, ?)
                    """,
                    (version, datetime.now(UTC).isoformat()),
                )
    except sqlite3.Error as exc:
        raise EventStoreError(f"Could not migrate SQLite storage {path}: {exc}") from exc


class SQLiteEventStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        migrate_sqlite_database(path)

    def append(self, event: EventRecord) -> EventRecord:
        data = event_to_record(event)
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO events (
                        event_id, event_type, schema_version, trace_id, task_id,
                        session_id, workspace_id, instance_id, actor, timestamp, payload_json,
                        previous_event_id, source_module, risk_level,
                        decision_record_id
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        data["event_id"],
                        data["event_type"],
                        data["schema_version"],
                        data["trace_id"],
                        data["task_id"],
                        data["session_id"],
                        data["workspace_id"],
                        data["instance_id"],
                        data["actor"],
                        data["timestamp"],
                        json.dumps(data["payload"], sort_keys=True),
                        data["previous_event_id"],
                        data["source_module"],
                        data["risk_level"],
                        data["decision_record_id"],
                    ),
                )
        except sqlite3.Error as exc:
            raise EventStoreError(f"Could not append event to {self.path}: {exc}") from exc

        return event

    def list_for_task(self, task_id: str) -> list[EventRecord]:
        try:
            with self._connect() as connection:
                rows = connection.execute(
                    "SELECT * FROM events WHERE task_id = ? ORDER BY rowid",
                    (task_id,),
                ).fetchall()
        except sqlite3.Error as exc:
            raise EventStoreError(f"Could not read events from {self.path}: {exc}") from exc

        return [self._row_to_event(row) for row in rows]

    def list_all(self) -> list[EventRecord]:
        try:
            with self._connect() as connection:
                rows = connection.execute("SELECT * FROM events ORDER BY rowid").fetchall()
        except sqlite3.Error as exc:
            raise EventStoreError(f"Could not read events from {self.path}: {exc}") from exc

        return [self._row_to_event(row) for row in rows]

    def last_event_id_for_task(self, task_id: str) -> str | None:
        try:
            with self._connect() as connection:
                row = connection.execute(
                    """
                    SELECT event_id FROM events
                    WHERE task_id = ?
                    ORDER BY rowid DESC
                    LIMIT 1
                    """,
                    (task_id,),
                ).fetchone()
        except sqlite3.Error as exc:
            raise EventStoreError(f"Could not read events from {self.path}: {exc}") from exc

        return str(row["event_id"]) if row else None

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _row_to_event(self, row: sqlite3.Row) -> EventRecord:
        return event_from_record(
            {
                "event_id": row["event_id"],
                "event_type": row["event_type"],
                "schema_version": row["schema_version"],
                "trace_id": row["trace_id"],
                "task_id": row["task_id"],
                "session_id": row["session_id"],
                "workspace_id": row["workspace_id"],
                "instance_id": row["instance_id"],
                "actor": row["actor"],
                "timestamp": row["timestamp"],
                "payload": json.loads(row["payload_json"]),
                "previous_event_id": row["previous_event_id"],
                "source_module": row["source_module"],
                "risk_level": row["risk_level"],
                "decision_record_id": row["decision_record_id"],
            }
        )


class SQLiteTaskStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        migrate_sqlite_database(path)

    def upsert(self, task: TaskState) -> TaskState:
        data = task_to_record(task)
        try:
            with _connect(self.path) as connection:
                connection.execute(
                    """
                    INSERT INTO tasks (
                        task_id, schema_version, user_goal, workspace_id, instance_id,
                        session_id, trace_id, status, agent_status, run_mode,
                        recovery_state, termination_reason, current_state_json,
                        updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(task_id) DO UPDATE SET
                        schema_version = excluded.schema_version,
                        user_goal = excluded.user_goal,
                        workspace_id = excluded.workspace_id,
                        instance_id = excluded.instance_id,
                        session_id = excluded.session_id,
                        trace_id = excluded.trace_id,
                        status = excluded.status,
                        agent_status = excluded.agent_status,
                        run_mode = excluded.run_mode,
                        recovery_state = excluded.recovery_state,
                        termination_reason = excluded.termination_reason,
                        current_state_json = excluded.current_state_json,
                        updated_at = excluded.updated_at
                    """,
                    (
                        data["task_id"],
                        STORAGE_SCHEMA_VERSION,
                        data["user_goal"],
                        data["workspace_id"],
                        data["instance_id"],
                        data["session_id"],
                        data["trace_id"],
                        data["status"],
                        data["agent_status"],
                        data["run_mode"],
                        data["recovery_state"],
                        data["termination_reason"],
                        json.dumps(data["current_state"], sort_keys=True),
                        datetime.now(UTC).isoformat(),
                    ),
                )
        except sqlite3.Error as exc:
            raise TaskStoreError(f"Could not upsert task in {self.path}: {exc}") from exc

        return task

    def get(self, task_id: str) -> TaskState | None:
        try:
            with _connect(self.path) as connection:
                row = connection.execute(
                    "SELECT * FROM tasks WHERE task_id = ?",
                    (task_id,),
                ).fetchone()
        except sqlite3.Error as exc:
            raise TaskStoreError(f"Could not read task from {self.path}: {exc}") from exc

        return _task_from_row(row) if row else None

    def list_all(self) -> list[TaskState]:
        try:
            with _connect(self.path) as connection:
                rows = connection.execute("SELECT * FROM tasks ORDER BY updated_at").fetchall()
        except sqlite3.Error as exc:
            raise TaskStoreError(f"Could not read tasks from {self.path}: {exc}") from exc

        return [_task_from_row(row) for row in rows]


class SQLiteConfigStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        migrate_sqlite_database(path)

    def set(self, namespace: str, key: str, value: Any) -> ConfigEntry:
        entry = ConfigEntry(namespace=namespace, key=key, value=value)
        try:
            with _connect(self.path) as connection:
                connection.execute(
                    """
                    INSERT INTO config (
                        namespace, key, schema_version, value_json, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(namespace, key) DO UPDATE SET
                        schema_version = excluded.schema_version,
                        value_json = excluded.value_json,
                        updated_at = excluded.updated_at
                    """,
                    (
                        namespace,
                        key,
                        entry.schema_version,
                        json.dumps(value, sort_keys=True),
                        entry.updated_at.isoformat(),
                    ),
                )
        except sqlite3.Error as exc:
            raise ConfigStoreError(f"Could not write config to {self.path}: {exc}") from exc

        return entry

    def get(self, namespace: str, key: str) -> ConfigEntry | None:
        try:
            with _connect(self.path) as connection:
                row = connection.execute(
                    "SELECT * FROM config WHERE namespace = ? AND key = ?",
                    (namespace, key),
                ).fetchone()
        except sqlite3.Error as exc:
            raise ConfigStoreError(f"Could not read config from {self.path}: {exc}") from exc

        return _config_from_row(row) if row else None

    def list_namespace(self, namespace: str) -> list[ConfigEntry]:
        try:
            with _connect(self.path) as connection:
                rows = connection.execute(
                    "SELECT * FROM config WHERE namespace = ? ORDER BY key",
                    (namespace,),
                ).fetchall()
        except sqlite3.Error as exc:
            raise ConfigStoreError(f"Could not read config from {self.path}: {exc}") from exc

        return [_config_from_row(row) for row in rows]


class SQLiteEvidenceStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        migrate_sqlite_database(path)

    def append(self, evidence: EvidenceRecord) -> EvidenceRecord:
        try:
            with _connect(self.path) as connection:
                connection.execute(
                    """
                    INSERT INTO evidence (
                        evidence_id, schema_version, workspace_id, source,
                        content_ref, task_id, trace_id, metadata_json, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        evidence.evidence_id,
                        evidence.schema_version,
                        evidence.workspace_id,
                        evidence.source,
                        evidence.content_ref,
                        evidence.task_id,
                        evidence.trace_id,
                        json.dumps(evidence.metadata, sort_keys=True),
                        evidence.created_at.isoformat(),
                    ),
                )
        except sqlite3.Error as exc:
            raise EvidenceStoreError(
                f"Could not append evidence to {self.path}: {exc}"
            ) from exc

        return evidence

    def get(self, evidence_id: str) -> EvidenceRecord | None:
        try:
            with _connect(self.path) as connection:
                row = connection.execute(
                    "SELECT * FROM evidence WHERE evidence_id = ?",
                    (evidence_id,),
                ).fetchone()
        except sqlite3.Error as exc:
            raise EvidenceStoreError(
                f"Could not read evidence from {self.path}: {exc}"
            ) from exc

        return _evidence_from_row(row) if row else None

    def list_for_task(self, task_id: str) -> list[EvidenceRecord]:
        try:
            with _connect(self.path) as connection:
                rows = connection.execute(
                    "SELECT * FROM evidence WHERE task_id = ? ORDER BY created_at",
                    (task_id,),
                ).fetchall()
        except sqlite3.Error as exc:
            raise EvidenceStoreError(
                f"Could not read evidence from {self.path}: {exc}"
            ) from exc

        return [_evidence_from_row(row) for row in rows]

    def list_all(self) -> list[EvidenceRecord]:
        try:
            with _connect(self.path) as connection:
                rows = connection.execute(
                    "SELECT * FROM evidence ORDER BY created_at"
                ).fetchall()
        except sqlite3.Error as exc:
            raise EvidenceStoreError(
                f"Could not read evidence from {self.path}: {exc}"
            ) from exc

        return [_evidence_from_row(row) for row in rows]


def sqlite_schema_versions(path: Path) -> list[int]:
    migrate_sqlite_database(path)
    try:
        with _connect(path) as connection:
            rows = connection.execute(
                "SELECT version FROM schema_migrations ORDER BY version"
            ).fetchall()
    except sqlite3.Error as exc:
        raise EventStoreError(f"Could not read SQLite schema versions {path}: {exc}") from exc

    return [int(row["version"]) for row in rows]


def _connect(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def _add_column_if_missing(
    connection: sqlite3.Connection,
    table: str,
    column: str,
    column_type: str,
) -> None:
    columns = {
        str(row["name"])
        for row in connection.execute(f"PRAGMA table_info({table})").fetchall()
    }
    if column not in columns:
        connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")


def _task_from_row(row: sqlite3.Row) -> TaskState:
    return task_from_record(
        {
            "task_id": row["task_id"],
            "user_goal": row["user_goal"],
            "workspace_id": row["workspace_id"],
            "instance_id": row["instance_id"],
            "session_id": row["session_id"],
            "trace_id": row["trace_id"],
            "status": row["status"],
            "agent_status": row["agent_status"],
            "run_mode": row["run_mode"],
            "recovery_state": row["recovery_state"],
            "termination_reason": row["termination_reason"],
            "current_state": json.loads(row["current_state_json"]),
        }
    )


def _config_from_row(row: sqlite3.Row) -> ConfigEntry:
    return ConfigEntry(
        namespace=row["namespace"],
        key=row["key"],
        value=json.loads(row["value_json"]),
        schema_version=int(row["schema_version"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def _evidence_from_row(row: sqlite3.Row) -> EvidenceRecord:
    return evidence_from_record(
        {
            "evidence_id": row["evidence_id"],
            "schema_version": row["schema_version"],
            "workspace_id": row["workspace_id"],
            "source": row["source"],
            "content_ref": row["content_ref"],
            "task_id": row["task_id"],
            "trace_id": row["trace_id"],
            "metadata": json.loads(row["metadata_json"]),
            "created_at": row["created_at"],
        }
    )

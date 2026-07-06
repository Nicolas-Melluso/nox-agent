import json
from pathlib import Path
from typing import Callable

import pytest
from typer.testing import CliRunner

from nox_agent_os.cli.main import app
from nox_agent_os.kernel import (
    AgentKernel,
    EventType,
    InMemoryEventStore,
    JsonlEventStore,
    SQLiteEventStore,
    TaskStatus,
)
from nox_agent_os.storage import (
    EvidenceRecord,
    InMemoryConfigStore,
    InMemoryEvidenceStore,
    InMemoryTaskStore,
    JsonlConfigStore,
    JsonlEvidenceStore,
    JsonlTaskStore,
    SQLiteConfigStore,
    SQLiteEvidenceStore,
    SQLiteTaskStore,
    backup_file,
    export_events,
    sqlite_schema_versions,
)

runner = CliRunner()


@pytest.mark.parametrize(
    "store_factory",
    [
        pytest.param(lambda path: InMemoryEventStore(), id="memory"),
        pytest.param(lambda path: JsonlEventStore(path / "events.jsonl"), id="jsonl"),
        pytest.param(lambda path: SQLiteEventStore(path / "storage.sqlite3"), id="sqlite"),
    ],
)
def test_event_store_contract_replays_kernel_events(
    tmp_path: Path,
    store_factory: Callable[[Path], object],
) -> None:
    store = store_factory(tmp_path)
    first_kernel = AgentKernel(event_store=store)

    created = first_kernel.create_task(
        "persist through adapter",
        workspace_id="workspace-a",
        instance_id="instance-a",
    )
    first_kernel.transition_task(created.task_id, TaskStatus.RUNNING, reason="start")

    second_kernel = AgentKernel(event_store=store)
    replayed = second_kernel.get_task(created.task_id)
    events = second_kernel.event_store.list_for_task(created.task_id)

    assert replayed.status == TaskStatus.RUNNING
    assert replayed.workspace_id == "workspace-a"
    assert replayed.instance_id == "instance-a"
    assert [event.event_type for event in events] == [
        EventType.TASK_CREATED,
        EventType.TASK_STATUS_CHANGED,
    ]
    assert events[1].previous_event_id == events[0].event_id


@pytest.mark.parametrize(
    "stores_factory",
    [
        pytest.param(
            lambda path: (
                InMemoryTaskStore(),
                InMemoryConfigStore(),
                InMemoryEvidenceStore(),
            ),
            id="memory",
        ),
        pytest.param(
            lambda path: (
                JsonlTaskStore(path / "tasks.jsonl"),
                JsonlConfigStore(path / "config.jsonl"),
                JsonlEvidenceStore(path / "evidence.jsonl"),
            ),
            id="jsonl",
        ),
        pytest.param(
            lambda path: (
                SQLiteTaskStore(path / "storage.sqlite3"),
                SQLiteConfigStore(path / "storage.sqlite3"),
                SQLiteEvidenceStore(path / "storage.sqlite3"),
            ),
            id="sqlite",
        ),
    ],
)
def test_task_config_and_evidence_store_contracts(
    tmp_path: Path,
    stores_factory: Callable[[Path], tuple[object, object, object]],
) -> None:
    task_store, config_store, evidence_store = stores_factory(tmp_path)
    task = AgentKernel().create_task(
        "store task snapshot",
        workspace_id="workspace-a",
        instance_id="instance-a",
    )

    task_store.upsert(task)
    config_store.set("workspace", "storage_backend", "jsonl")
    evidence = evidence_store.append(
        EvidenceRecord(
            workspace_id="workspace-a",
            task_id=task.task_id,
            trace_id=task.trace_id,
            source="file",
            content_ref="README.md",
            metadata={"kind": "read_only"},
        )
    )

    assert task_store.get(task.task_id).user_goal == "store task snapshot"
    assert config_store.get("workspace", "storage_backend").value == "jsonl"
    assert evidence_store.get(evidence.evidence_id).content_ref == "README.md"
    assert evidence_store.list_for_task(task.task_id) == [evidence]


def test_sqlite_storage_records_schema_migration(tmp_path: Path) -> None:
    db_path = tmp_path / "storage.sqlite3"

    SQLiteEventStore(db_path)

    assert sqlite_schema_versions(db_path) == [1, 2]


def test_event_export_and_file_backup(tmp_path: Path) -> None:
    event_log = tmp_path / ".nox" / "events.jsonl"
    store = JsonlEventStore(event_log)
    kernel = AgentKernel(event_store=store)
    task = kernel.create_task("export me")

    backup_path = backup_file(event_log)
    export_path = export_events(store, tmp_path / "export" / "events.json")

    assert backup_path.exists()
    exported = json.loads(export_path.read_text(encoding="utf-8"))
    assert exported["schema_version"] == 1
    assert exported["events"][0]["task_id"] == task.task_id


def test_cli_storage_info_backup_and_export(tmp_path: Path) -> None:
    runner.invoke(app, ["init", str(tmp_path)])
    runner.invoke(app, ["task", "create", "storage cli", "--path", str(tmp_path)])

    info = runner.invoke(app, ["storage", "info", "--path", str(tmp_path)])
    backup = runner.invoke(app, ["storage", "backup", "--path", str(tmp_path)])
    export_path = tmp_path / "events-export.json"
    exported = runner.invoke(
        app,
        [
            "storage",
            "export-events",
            "--path",
            str(tmp_path),
            "--output",
            str(export_path),
        ],
    )

    assert info.exit_code == 0
    assert "Storage backend: jsonl" in info.output
    assert backup.exit_code == 0
    assert (tmp_path / ".nox" / "backups").exists()
    assert exported.exit_code == 0
    assert export_path.exists()

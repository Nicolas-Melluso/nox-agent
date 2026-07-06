from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

from nox_agent_os.storage.contracts import EventStore, StorageError
from nox_agent_os.storage.serialization import event_to_record


def backup_file(source: Path, backup_dir: Path | None = None) -> Path:
    if not source.exists():
        raise StorageError(f"Cannot back up missing file: {source}")

    target_dir = backup_dir or source.parent / "backups"
    target_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    target = target_dir / f"{source.stem}-{timestamp}{source.suffix}"
    shutil.copy2(source, target)
    return target


def export_events(store: EventStore, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "exported_at": datetime.now(UTC).isoformat(),
        "events": [event_to_record(event) for event in store.list_all()],
    }
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return output_path

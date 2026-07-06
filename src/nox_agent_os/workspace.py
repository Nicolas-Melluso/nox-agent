from __future__ import annotations

import json
import sys
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from os import makedirs
from pathlib import Path
from typing import Any
from uuid import uuid4

import nox_agent_os
from nox_agent_os import __version__

WORKSPACE_DIR_NAME = ".nox"
SYSTEM_PROMPT_NAME = "system.prompt.md"
EVENT_LOG_NAME = "events.jsonl"
IDENTITY_NAME = "identity.json"
IDENTITY_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class WorkspaceIdentity:
    workspace_id: str
    instance_id: str
    created_at: str
    updated_at: str
    nox_version: str
    last_known_workspace_root_path: Path
    engine: "EngineReference"
    schema_version: int = IDENTITY_SCHEMA_VERSION


@dataclass(frozen=True)
class WorkspaceInitResult:
    workspace_dir: Path
    system_prompt_path: Path
    identity_path: Path
    identity: WorkspaceIdentity
    created: bool


@dataclass(frozen=True)
class Workspace:
    workspace_dir: Path
    system_prompt_path: Path
    identity_path: Path
    identity: WorkspaceIdentity

    @property
    def event_log_path(self) -> Path:
        return self.workspace_dir / EVENT_LOG_NAME

    @property
    def workspace_root_path(self) -> Path:
        return self.workspace_dir.parent

    @property
    def workspace_id(self) -> str:
        return self.identity.workspace_id

    @property
    def instance_id(self) -> str:
        return self.identity.instance_id


class WorkspaceError(RuntimeError):
    pass


@dataclass(frozen=True)
class EngineReference:
    mode: str
    package: str
    import_name: str
    version: str
    install_root_path: Path
    package_path: Path
    executable_path: Path


def get_engine_reference() -> EngineReference:
    frozen = bool(getattr(sys, "frozen", False))
    package_file = Path(nox_agent_os.__file__ or "").resolve()
    executable_path = Path(sys.executable if frozen else sys.argv[0]).resolve()
    install_root_path = executable_path.parent if frozen else package_file.parent

    return EngineReference(
        mode="frozen-exe" if frozen else "python-package",
        package="nox-agent-os",
        import_name="nox_agent_os",
        version=__version__,
        install_root_path=install_root_path,
        package_path=package_file.parent,
        executable_path=executable_path,
    )


def _frontmatter_string(value: object) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


def _engine_to_dict(engine: EngineReference) -> dict[str, str]:
    return {
        "mode": engine.mode,
        "package": engine.package,
        "import_name": engine.import_name,
        "version": engine.version,
        "install_root_path": str(engine.install_root_path),
        "package_path": str(engine.package_path),
        "executable_path": str(engine.executable_path),
    }


def _engine_from_dict(data: dict[str, Any]) -> EngineReference:
    return EngineReference(
        mode=str(data["mode"]),
        package=str(data["package"]),
        import_name=str(data["import_name"]),
        version=str(data["version"]),
        install_root_path=Path(str(data["install_root_path"])),
        package_path=Path(str(data["package_path"])),
        executable_path=Path(str(data["executable_path"])),
    )


def _identity_to_dict(identity: WorkspaceIdentity) -> dict[str, Any]:
    return {
        "schema_version": identity.schema_version,
        "workspace_id": identity.workspace_id,
        "instance_id": identity.instance_id,
        "created_at": identity.created_at,
        "updated_at": identity.updated_at,
        "nox_version": identity.nox_version,
        "last_known_workspace_root_path": str(identity.last_known_workspace_root_path),
        "engine": _engine_to_dict(identity.engine),
    }


def _identity_from_dict(data: dict[str, Any]) -> WorkspaceIdentity:
    return WorkspaceIdentity(
        schema_version=int(data.get("schema_version") or IDENTITY_SCHEMA_VERSION),
        workspace_id=str(data["workspace_id"]),
        instance_id=str(data["instance_id"]),
        created_at=str(data["created_at"]),
        updated_at=str(data["updated_at"]),
        nox_version=str(data["nox_version"]),
        last_known_workspace_root_path=Path(str(data["last_known_workspace_root_path"])),
        engine=_engine_from_dict(dict(data["engine"])),
    )


def _read_identity(path: Path) -> WorkspaceIdentity:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise TypeError("identity must be a JSON object")
        return _identity_from_dict(data)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise WorkspaceError(f"Invalid workspace identity: {path}. {exc}") from exc


def _write_identity(path: Path, identity: WorkspaceIdentity) -> None:
    try:
        path.write_text(
            json.dumps(_identity_to_dict(identity), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        raise WorkspaceError(f"Could not write workspace identity: {path}. {exc}") from exc


def ensure_workspace_identity(
    workspace_dir: Path,
    workspace_root_path: Path,
    *,
    refresh: bool = False,
) -> WorkspaceIdentity:
    identity_path = workspace_dir / IDENTITY_NAME
    now = _utc_now()

    if identity_path.exists():
        current = _read_identity(identity_path)
        if not refresh:
            return current
        identity = WorkspaceIdentity(
            schema_version=IDENTITY_SCHEMA_VERSION,
            workspace_id=current.workspace_id,
            instance_id=current.instance_id,
            created_at=current.created_at,
            updated_at=now,
            nox_version=__version__,
            last_known_workspace_root_path=workspace_root_path.resolve(strict=False),
            engine=get_engine_reference(),
        )
        _write_identity(identity_path, identity)
        return identity

    identity = WorkspaceIdentity(
        workspace_id=_new_id("ws"),
        instance_id=_new_id("inst"),
        created_at=now,
        updated_at=now,
        nox_version=__version__,
        last_known_workspace_root_path=workspace_root_path.resolve(strict=False),
        engine=get_engine_reference(),
    )
    _write_identity(identity_path, identity)
    return identity


def _ensure_directory(path: Path, label: str) -> None:
    if path.exists():
        if path.is_dir():
            return
        raise WorkspaceError(f"{label} exists but is not a directory: {path}")

    try:
        makedirs(path, exist_ok=True)
    except OSError as exc:
        parent = path.parent
        parent_exists = parent.exists()
        parent_is_dir = parent.is_dir()
        raise WorkspaceError(
            f"Could not create {label}: {path}. {exc}. "
            f"Parent exists: {parent_exists}. Parent is directory: {parent_is_dir}."
        ) from exc


def _check_writable_directory(path: Path) -> None:
    try:
        with tempfile.NamedTemporaryFile(prefix=".nox-write-test-", dir=path, delete=True):
            pass
    except OSError as exc:
        raise WorkspaceError(f"Workspace directory is not writable: {path}. {exc}") from exc


def is_inside_workspace_metadata(path: Path) -> bool:
    resolved = path.resolve(strict=False)
    return any(part.lower() == WORKSPACE_DIR_NAME for part in resolved.parts)


def _check_not_inside_workspace_metadata(path: Path) -> None:
    if is_inside_workspace_metadata(path):
        raise WorkspaceError(
            f"Refusing to initialize a Nox workspace inside {WORKSPACE_DIR_NAME} metadata: {path}. "
            "Move to the project root and run: nox init"
        )


def render_system_prompt() -> str:
    engine = get_engine_reference()
    return f"""---
nox_workspace_version: 1
nox_required_version: {_frontmatter_string(__version__)}
profile: default
created_by: nox init
engine:
  mode: {_frontmatter_string(engine.mode)}
  package: {_frontmatter_string(engine.package)}
  import_name: {_frontmatter_string(engine.import_name)}
  version: {_frontmatter_string(engine.version)}
  install_root_path: {_frontmatter_string(engine.install_root_path)}
  package_path: {_frontmatter_string(engine.package_path)}
  executable_path: {_frontmatter_string(engine.executable_path)}
---

# Nox Workspace System Prompt

This workspace is a local Nox instance that uses the installed Nox engine
referenced in the frontmatter.

Workspace identity lives in `.nox/{IDENTITY_NAME}`. Use `workspace_id` for stable
project-level correlation and `instance_id` for this concrete `.nox` instance.

The local `.nox` directory should stay small. It points Nox at this workspace and
lets the installed engine provide runtime code, policies, adapters, schemas and
defaults.

Engine resolution:

- Import `{engine.import_name}` from `engine.package_path`.
- Treat `engine.install_root_path` as the installed engine root.
- Use `engine.executable_path` as the command entrypoint that created or updated this workspace.
- Treat the installed package as the source of runtime code, policies, adapters, schemas and defaults.
- Treat this `.nox` directory as workspace metadata and local workspace state, not as the engine itself.
- Treat `.nox/{EVENT_LOG_NAME}` as the workspace event log until a stronger storage adapter is configured.

Workspace rules:

- Treat this directory as the active project workspace.
- Do not assume runtime tools or models live inside `.nox`.
- Resolve engine capabilities from the installed Nox package referenced above.
- Ask for human approval before sensitive, external or irreversible actions.
"""


def create_workspace(path: Path, force: bool = False) -> WorkspaceInitResult:
    root = path.resolve(strict=False)
    workspace_dir = root / WORKSPACE_DIR_NAME
    system_prompt_path = workspace_dir / SYSTEM_PROMPT_NAME

    _check_not_inside_workspace_metadata(root)
    _ensure_directory(root, "workspace directory")
    _check_writable_directory(root)
    _ensure_directory(workspace_dir, "Nox workspace directory")
    identity = ensure_workspace_identity(
        workspace_dir,
        root,
        refresh=force or not system_prompt_path.exists(),
    )
    identity_path = workspace_dir / IDENTITY_NAME
    event_log_path = workspace_dir / EVENT_LOG_NAME
    if not event_log_path.exists():
        try:
            event_log_path.touch()
        except OSError as exc:
            raise WorkspaceError(f"Could not create event log: {event_log_path}. {exc}") from exc

    if system_prompt_path.exists() and not force:
        return WorkspaceInitResult(
            workspace_dir=workspace_dir,
            system_prompt_path=system_prompt_path,
            identity_path=identity_path,
            identity=identity,
            created=False,
        )

    try:
        system_prompt_path.write_text(render_system_prompt(), encoding="utf-8")
    except OSError as exc:
        raise WorkspaceError(f"Could not write system prompt: {system_prompt_path}. {exc}") from exc

    return WorkspaceInitResult(
        workspace_dir=workspace_dir,
        system_prompt_path=system_prompt_path,
        identity_path=identity_path,
        identity=identity,
        created=True,
    )


def update_workspace(path: Path) -> WorkspaceInitResult:
    root = path.resolve(strict=False)
    workspace_dir = root / WORKSPACE_DIR_NAME
    system_prompt_path = workspace_dir / SYSTEM_PROMPT_NAME

    _check_not_inside_workspace_metadata(root)
    _ensure_directory(root, "workspace directory")
    _check_writable_directory(root)

    if not system_prompt_path.exists():
        return create_workspace(root, force=True)

    identity = ensure_workspace_identity(workspace_dir, root, refresh=True)

    try:
        system_prompt_path.write_text(render_system_prompt(), encoding="utf-8")
    except OSError as exc:
        raise WorkspaceError(f"Could not write system prompt: {system_prompt_path}. {exc}") from exc

    return WorkspaceInitResult(
        workspace_dir=workspace_dir,
        system_prompt_path=system_prompt_path,
        identity_path=workspace_dir / IDENTITY_NAME,
        identity=identity,
        created=False,
    )


def find_workspace(path: Path) -> Workspace | None:
    current = path.resolve()

    for candidate in (current, *current.parents):
        workspace_dir = candidate / WORKSPACE_DIR_NAME
        system_prompt_path = workspace_dir / SYSTEM_PROMPT_NAME
        if system_prompt_path.exists():
            identity = ensure_workspace_identity(workspace_dir, candidate)
            return Workspace(
                workspace_dir=workspace_dir,
                system_prompt_path=system_prompt_path,
                identity_path=workspace_dir / IDENTITY_NAME,
                identity=identity,
            )

    return None

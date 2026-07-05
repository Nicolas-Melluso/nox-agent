from __future__ import annotations

import sys
import tempfile
from dataclasses import dataclass
from os import makedirs
from pathlib import Path

import nox_agent_os
from nox_agent_os import __version__

WORKSPACE_DIR_NAME = ".nox"
SYSTEM_PROMPT_NAME = "system.prompt.md"
EVENT_LOG_NAME = "events.jsonl"


@dataclass(frozen=True)
class WorkspaceInitResult:
    workspace_dir: Path
    system_prompt_path: Path
    created: bool


@dataclass(frozen=True)
class Workspace:
    workspace_dir: Path
    system_prompt_path: Path

    @property
    def event_log_path(self) -> Path:
        return self.workspace_dir / EVENT_LOG_NAME


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

This workspace uses the installed Nox engine referenced in the frontmatter.

The local `.nox` directory should stay small. It points Nox at this workspace and
lets the installed engine provide runtime code, policies, adapters, schemas and
defaults.

Engine resolution:

- Import `{engine.import_name}` from `engine.package_path`.
- Treat `engine.install_root_path` as the installed engine root.
- Use `engine.executable_path` as the command entrypoint that created or updated this workspace.
- Treat the installed package as the source of runtime code, policies, adapters, schemas and defaults.
- Treat this `.nox` directory as workspace metadata, not as the engine itself.
- Treat `.nox/{EVENT_LOG_NAME}` as the workspace event log until a stronger storage adapter is configured.

Workspace rules:

- Treat this directory as the active project workspace.
- Do not assume tools, models or storage live inside `.nox`.
- Resolve engine capabilities from the installed Nox package referenced above.
- Ask for human approval before sensitive, external or irreversible actions.
"""


def create_workspace(path: Path, force: bool = False) -> WorkspaceInitResult:
    root = path.resolve(strict=False)
    workspace_dir = root / WORKSPACE_DIR_NAME
    system_prompt_path = workspace_dir / SYSTEM_PROMPT_NAME

    _ensure_directory(root, "workspace directory")
    _check_writable_directory(root)
    _ensure_directory(workspace_dir, "Nox workspace directory")
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
            created=False,
        )

    try:
        system_prompt_path.write_text(render_system_prompt(), encoding="utf-8")
    except OSError as exc:
        raise WorkspaceError(f"Could not write system prompt: {system_prompt_path}. {exc}") from exc

    return WorkspaceInitResult(
        workspace_dir=workspace_dir,
        system_prompt_path=system_prompt_path,
        created=True,
    )


def update_workspace(path: Path) -> WorkspaceInitResult:
    root = path.resolve(strict=False)
    workspace_dir = root / WORKSPACE_DIR_NAME
    system_prompt_path = workspace_dir / SYSTEM_PROMPT_NAME

    _ensure_directory(root, "workspace directory")
    _check_writable_directory(root)

    if not system_prompt_path.exists():
        return create_workspace(root, force=True)

    try:
        system_prompt_path.write_text(render_system_prompt(), encoding="utf-8")
    except OSError as exc:
        raise WorkspaceError(f"Could not write system prompt: {system_prompt_path}. {exc}") from exc

    return WorkspaceInitResult(
        workspace_dir=workspace_dir,
        system_prompt_path=system_prompt_path,
        created=False,
    )


def find_workspace(path: Path) -> Workspace | None:
    current = path.resolve()

    for candidate in (current, *current.parents):
        workspace_dir = candidate / WORKSPACE_DIR_NAME
        system_prompt_path = workspace_dir / SYSTEM_PROMPT_NAME
        if system_prompt_path.exists():
            return Workspace(workspace_dir=workspace_dir, system_prompt_path=system_prompt_path)

    return None

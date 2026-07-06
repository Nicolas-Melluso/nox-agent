from __future__ import annotations

import platform
import shlex
import sys
from pathlib import Path

import typer

from nox_agent_os import __version__
from nox_agent_os.cli.runtime import CliKernelContext, load_kernel_context
from nox_agent_os.governance import (
    ApprovalAlreadyResolvedError,
    ApprovalNotFoundError,
    ApprovalStatus,
    Capability,
    ControlScope,
)
from nox_agent_os.kernel import (
    EventRecord,
    EventStoreError,
    EventType,
    KernelControlBlockedError,
    TaskStatus,
)
from nox_agent_os.kernel.kernel import TaskNotFoundError
from nox_agent_os.storage import StorageError, backup_file, export_events
from nox_agent_os.workspace import (
    SYSTEM_PROMPT_NAME,
    WORKSPACE_DIR_NAME,
    WorkspaceError,
    create_workspace,
    find_workspace,
    get_engine_reference,
    is_inside_workspace_metadata,
    render_system_prompt,
    update_workspace,
)

app = typer.Typer(
    name="nox",
    help="Local agent OS workspace launcher.",
    add_completion=False,
    invoke_without_command=True,
    no_args_is_help=False,
)
task_app = typer.Typer(help="Manage kernel tasks.")
logs_app = typer.Typer(help="Inspect workspace logs and event history.")
policy_app = typer.Typer(help="Evaluate governed capabilities.")
approvals_app = typer.Typer(help="Inspect and resolve human approvals.")
kill_app = typer.Typer(help="Control the kernel kill switch.")
api_app = typer.Typer(help="Serve the local HTTP API.")
storage_app = typer.Typer(help="Inspect, back up and export workspace storage.")

app.add_typer(task_app, name="task")
app.add_typer(logs_app, name="logs")
app.add_typer(policy_app, name="policy")
app.add_typer(approvals_app, name="approvals")
app.add_typer(kill_app, name="kill")
app.add_typer(api_app, name="api")
app.add_typer(storage_app, name="storage")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Nox command root."""
    if ctx.invoked_subcommand is None:
        print_banner()
        typer.echo(ctx.get_help())
        raise typer.Exit()


def print_banner() -> None:
    typer.secho(" _   _  ___  __  __", fg=typer.colors.RED, bold=True)
    typer.secho("| \\ | |/ _ \\ \\ \\/ /", fg=typer.colors.RED, bold=True)
    typer.secho("|  \\| | | | | \\  / ", fg=typer.colors.RED, bold=True)
    typer.secho("| |\\  | |_| | /  \\ ", fg=typer.colors.RED, bold=True)
    typer.secho("|_| \\_|\\___/ /_/\\_\\", fg=typer.colors.RED, bold=True)
    typer.secho("Local Agent OS", fg=typer.colors.RED)


def print_runtime_diagnostic() -> None:
    engine = get_engine_reference()
    typer.echo(f"[hint] nox version: {__version__}", err=True)
    typer.echo(f"[hint] runtime mode: {engine.mode}", err=True)
    typer.echo(f"[hint] executable: {engine.executable_path}", err=True)
    typer.echo(f"[hint] package path: {engine.package_path}", err=True)
    typer.echo(f"[hint] sys.executable: {Path(sys.executable).resolve()}", err=True)
    typer.echo("[hint] PowerShell: Get-Command nox -All", err=True)


def load_cli_context(path: Path | None = None) -> CliKernelContext:
    try:
        return load_kernel_context(path)
    except (WorkspaceError, EventStoreError) as exc:
        typer.secho(f"[error] {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc


def print_task(task) -> None:
    typer.echo(f"Task ID: {task.task_id}")
    typer.echo(f"Status: {task.status.value}")
    typer.echo(f"Trace ID: {task.trace_id}")
    typer.echo(f"Workspace: {task.workspace_id}")
    typer.echo(f"Goal: {task.user_goal}")


def print_event(event: EventRecord) -> None:
    risk = f" risk={event.risk_level}" if event.risk_level else ""
    decision = (
        f" decision={event.decision_record_id}" if event.decision_record_id else ""
    )
    instance = f" instance={event.instance_id}" if event.instance_id else ""
    typer.echo(
        f"{event.timestamp.isoformat()} "
        f"{event.event_type.value} workspace={event.workspace_id} "
        f"task={event.task_id} actor={event.actor}"
        f"{instance}"
        f"{risk}{decision}"
    )


def print_snapshot(context: CliKernelContext) -> None:
    snapshot = context.kernel.resource_snapshot()
    typer.echo(f"Workspace: {context.workspace.workspace_dir.parent}")
    typer.echo(f"Workspace ID: {context.workspace.workspace_id}")
    typer.echo(f"Instance ID: {context.workspace.instance_id}")
    typer.echo(f"Event log: {context.workspace.event_log_path}")
    typer.echo(f"Health: {snapshot.health}")
    typer.echo(f"Tasks: {snapshot.total_tasks}")
    typer.echo(f"Events: {snapshot.total_events}")
    typer.echo(f"Pending approvals: {snapshot.pending_approvals}")
    typer.echo(
        f"Kill switch: {'active' if snapshot.kill_switch_active else 'inactive'} "
        f"scope={snapshot.kill_switch_scope}"
    )
    typer.echo(f"Task statuses: {snapshot.task_status_counts}")
    typer.echo(f"Last event: {snapshot.last_event_type or 'none'}")


def print_storage_info(context: CliKernelContext) -> None:
    events = context.event_store.list_all()
    typer.echo("Storage backend: jsonl")
    typer.echo(f"Workspace: {context.workspace.workspace_dir.parent}")
    typer.echo(f"Workspace ID: {context.workspace.workspace_id}")
    typer.echo(f"Instance ID: {context.workspace.instance_id}")
    typer.echo(f"Event log: {context.workspace.event_log_path}")
    typer.echo(f"Events: {len(events)}")
    typer.echo("SQLite adapter: available")


@app.command(help=f"Show Nox version ({__version__}).")
def version() -> None:
    print_banner()
    typer.echo(f"nox {__version__}")


@app.command()
def init(
    path: Path | None = typer.Argument(
        None,
        help="Workspace directory where .nox should be created.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite an existing .nox/system.prompt.md.",
    ),
) -> None:
    """Initialize a Nox workspace."""
    print_banner()
    target_path = Path.cwd() if path is None else path

    try:
        result = create_workspace(path=target_path, force=force)
    except WorkspaceError as exc:
        typer.secho(f"[error] {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    if result.created:
        typer.echo(f"Initialized Nox workspace: {result.workspace_dir}")
        typer.echo(f"Created: {result.system_prompt_path}")
        typer.echo(f"Created: {result.identity_path}")
        return

    typer.echo(f"Nox workspace already exists: {result.workspace_dir}")
    typer.echo(f"System prompt: {result.system_prompt_path}")
    typer.echo(f"Identity: {result.identity_path}")


@app.command()
def update(path: Path | None = typer.Argument(None, help="Workspace directory to update.")) -> None:
    """Refresh the local .nox workspace metadata."""
    print_banner()
    target_path = Path.cwd() if path is None else path

    try:
        result = update_workspace(path=target_path)
    except WorkspaceError as exc:
        typer.secho(f"[error] {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(f"Updated Nox workspace: {result.workspace_dir}")
    typer.echo(f"System prompt: {result.system_prompt_path}")
    typer.echo(f"Identity: {result.identity_path}")


@app.command()
def upgrade(
    check: bool = typer.Option(
        False,
        "--check",
        help="Show upgrade source and current engine details without changing anything.",
    ),
    source: str = typer.Option(
        "https://github.com/Nicolas-Melluso/nox-agent",
        "--source",
        help="Upgrade source repository or release feed.",
    ),
) -> None:
    """Upgrade the installed Nox engine."""
    print_banner()
    engine = get_engine_reference()

    typer.echo(f"Current version: {__version__}")
    typer.echo(f"Engine mode: {engine.mode}")
    typer.echo(f"Engine executable: {engine.executable_path}")
    typer.echo(f"Upgrade source: {source}")

    if check:
        typer.echo("Upgrade check only. No files changed.")
        return

    typer.echo(
        "Automatic engine upgrade is not implemented yet. "
        "For now, build and install a fresh NoxSetup.exe from the repo."
    )
    typer.echo(
        "Development flow: powershell -ExecutionPolicy Bypass -File "
        ".\\scripts\\build_nox_setup.ps1 -Clean"
    )
    raise typer.Exit(code=1)


@app.command()
def doctor(path: Path | None = typer.Argument(None, help="Workspace directory to inspect.")) -> None:
    """Show health for the Nox engine and current workspace."""
    print_banner()
    target_path = Path.cwd() if path is None else path
    root = target_path.resolve()
    try:
        workspace = find_workspace(root)
    except WorkspaceError as exc:
        typer.secho(f"[error] {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc
    engine = get_engine_reference()

    checks = [
        ("nox version", __version__),
        ("python", platform.python_version()),
        ("package", "nox_agent_os importable"),
        ("engine mode", engine.mode),
        ("engine install root", str(engine.install_root_path)),
        ("engine package path", str(engine.package_path)),
        ("engine executable", str(engine.executable_path)),
        ("cwd", str(root)),
    ]

    for label, value in checks:
        typer.echo(f"[ok] {label}: {value}")

    if is_inside_workspace_metadata(root):
        typer.echo(
            f"[warn] cwd: inside {WORKSPACE_DIR_NAME} metadata; "
            "run workspace commands from the project root"
        )

    if workspace is None:
        typer.echo(f"[warn] workspace: no {WORKSPACE_DIR_NAME}/{SYSTEM_PROMPT_NAME} found")
        typer.echo("       run: nox init")
        raise typer.Exit(code=1)

    typer.echo(f"[ok] workspace: {workspace.workspace_dir}")
    typer.echo(f"[ok] identity: {workspace.identity_path}")
    typer.echo(f"[ok] workspace_id: {workspace.workspace_id}")
    typer.echo(f"[ok] instance_id: {workspace.instance_id}")
    typer.echo(f"[ok] identity updated_at: {workspace.identity.updated_at}")
    typer.echo(f"[ok] system prompt: {workspace.system_prompt_path}")
    typer.echo(f"[ok] event log: {workspace.event_log_path}")


@app.command()
def prompt() -> None:
    """Print the default workspace system prompt template."""
    typer.echo(render_system_prompt())


@app.command()
def status(
    path: Path | None = typer.Option(None, "--path", "-p", help="Workspace to inspect."),
) -> None:
    """Show the current kernel resource snapshot."""
    print_banner()
    print_snapshot(load_cli_context(path))


@task_app.command("create")
def task_create(
    goal: str = typer.Argument(..., help="User goal for the new task."),
    path: Path | None = typer.Option(None, "--path", "-p", help="Workspace to use."),
) -> None:
    """Create a task and persist its event."""
    print_banner()
    context = load_cli_context(path)
    try:
        task = context.kernel.create_task(
            goal,
            workspace_id=context.workspace.workspace_id,
            instance_id=context.workspace.instance_id,
        )
    except KernelControlBlockedError as exc:
        typer.secho(f"[error] {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    print_task(task)


@task_app.command("list")
def task_list(
    path: Path | None = typer.Option(None, "--path", "-p", help="Workspace to use."),
) -> None:
    """List tasks reconstructed from the event log."""
    print_banner()
    context = load_cli_context(path)
    created_events = context.kernel.audit_trail.list_events(
        event_type=EventType.TASK_CREATED
    )
    if not created_events:
        typer.echo("No tasks.")
        return

    for event in created_events:
        task = context.kernel.get_task(event.task_id)
        typer.echo(f"{task.task_id} {task.status.value} {task.user_goal}")


@task_app.command("show")
def task_show(
    task_id: str = typer.Argument(..., help="Task ID to inspect."),
    path: Path | None = typer.Option(None, "--path", "-p", help="Workspace to use."),
) -> None:
    """Show a task reconstructed by replay."""
    print_banner()
    context = load_cli_context(path)
    try:
        print_task(context.kernel.get_task(task_id))
    except TaskNotFoundError as exc:
        typer.secho(f"[error] {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc


@task_app.command("transition")
def task_transition(
    task_id: str = typer.Argument(..., help="Task ID to transition."),
    status: TaskStatus = typer.Argument(..., help="Target task status."),
    reason: str = typer.Option(..., "--reason", "-r", help="Reason for the transition."),
    path: Path | None = typer.Option(None, "--path", "-p", help="Workspace to use."),
) -> None:
    """Transition a task through the kernel state machine."""
    print_banner()
    context = load_cli_context(path)
    try:
        task = context.kernel.transition_task(task_id, status, reason=reason, actor="user")
    except TaskNotFoundError as exc:
        typer.secho(f"[error] {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    print_task(task)


@logs_app.command("list")
def logs_list(
    limit: int = typer.Option(20, "--limit", "-n", min=1, help="Maximum events to show."),
    event_type: str | None = typer.Option(None, "--type", help="Optional event type filter."),
    path: Path | None = typer.Option(None, "--path", "-p", help="Workspace to use."),
) -> None:
    """List recent workspace log events."""
    print_banner()
    context = load_cli_context(path)
    try:
        events = context.kernel.audit_trail.list_events(event_type=event_type)
    except ValueError as exc:
        typer.secho(f"[error] Invalid event type: {event_type}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    for event in events[-limit:]:
        print_event(event)


@logs_app.command("task")
def logs_task(
    task_id: str = typer.Argument(..., help="Task ID to inspect."),
    path: Path | None = typer.Option(None, "--path", "-p", help="Workspace to use."),
) -> None:
    """List log events for one task."""
    print_banner()
    context = load_cli_context(path)
    for event in context.kernel.audit_trail.list_events(task_id=task_id):
        print_event(event)


@policy_app.command("check")
def policy_check(
    task_id: str = typer.Argument(..., help="Task ID requesting the capability."),
    capability: Capability = typer.Argument(..., help="Capability to evaluate."),
    target: str | None = typer.Option(None, "--target", "-t", help="Optional target."),
    description: str | None = typer.Option(None, "--description", "-d", help="Request reason."),
    path: Path | None = typer.Option(None, "--path", "-p", help="Workspace to use."),
) -> None:
    """Evaluate a capability through the PolicyEngine."""
    print_banner()
    context = load_cli_context(path)
    try:
        result = context.kernel.request_capability(
            task_id,
            capability,
            description=description or f"Request {capability.value}",
            target=target,
            actor="user",
        )
    except TaskNotFoundError as exc:
        typer.secho(f"[error] {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(f"Decision: {result.decision.decision.value}")
    typer.echo(f"Risk: {result.decision.risk_level.value}")
    typer.echo(f"Reason: {result.decision.reason}")
    typer.echo(f"Decision record: {result.decision.decision_record_id}")
    if result.approval is not None:
        typer.echo(f"Approval ID: {result.approval.approval_id}")
    if result.blocked_reason is not None:
        typer.echo(f"Blocked: {result.blocked_reason}")


@approvals_app.command("list")
def approvals_list(
    path: Path | None = typer.Option(None, "--path", "-p", help="Workspace to use."),
) -> None:
    """List pending approvals rehydrated from events."""
    print_banner()
    context = load_cli_context(path)
    approvals = context.kernel.approval_queue.list_pending()
    if not approvals:
        typer.echo("No pending approvals.")
        return

    for approval in approvals:
        typer.echo(
            f"{approval.approval_id} {approval.capability.value} "
            f"risk={approval.risk_level.value} task={approval.task_id} target={approval.target}"
        )


@approvals_app.command("approve")
def approvals_approve(
    approval_id: str = typer.Argument(..., help="Approval ID to approve."),
    reason: str = typer.Option("approved by user", "--reason", "-r", help="Resolution reason."),
    path: Path | None = typer.Option(None, "--path", "-p", help="Workspace to use."),
) -> None:
    """Approve a pending approval."""
    print_banner()
    context = load_cli_context(path)
    try:
        approval = context.kernel.resolve_approval(
            approval_id,
            approved=True,
            actor="user",
            reason=reason,
        )
    except (ApprovalNotFoundError, ApprovalAlreadyResolvedError) as exc:
        typer.secho(f"[error] {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(f"Approval {approval.approval_id}: {approval.status.value}")


@approvals_app.command("reject")
def approvals_reject(
    approval_id: str = typer.Argument(..., help="Approval ID to reject."),
    reason: str = typer.Option("rejected by user", "--reason", "-r", help="Resolution reason."),
    path: Path | None = typer.Option(None, "--path", "-p", help="Workspace to use."),
) -> None:
    """Reject a pending approval."""
    print_banner()
    context = load_cli_context(path)
    try:
        approval = context.kernel.resolve_approval(
            approval_id,
            approved=False,
            actor="user",
            reason=reason,
        )
    except (ApprovalNotFoundError, ApprovalAlreadyResolvedError) as exc:
        typer.secho(f"[error] {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(f"Approval {approval.approval_id}: {approval.status.value}")


@kill_app.command("status")
def kill_status(
    path: Path | None = typer.Option(None, "--path", "-p", help="Workspace to use."),
) -> None:
    """Show kill switch state."""
    print_banner()
    snapshot = load_cli_context(path).kernel.kill_switch.snapshot()
    typer.echo(f"Kill switch: {'active' if snapshot.active else 'inactive'}")
    typer.echo(f"Scope: {snapshot.scope.value}")
    typer.echo(f"Reason: {snapshot.reason or 'none'}")


@kill_app.command("on")
def kill_on(
    reason: str = typer.Option(..., "--reason", "-r", help="Reason to activate."),
    scope: ControlScope = typer.Option(ControlScope.ALL, "--scope", "-s", help="Scope to block."),
    path: Path | None = typer.Option(None, "--path", "-p", help="Workspace to use."),
) -> None:
    """Activate the kill switch."""
    print_banner()
    context = load_cli_context(path)
    snapshot = context.kernel.activate_kill_switch(
        reason=reason,
        actor="user",
        scope=scope,
        workspace_id=context.workspace.workspace_id,
        instance_id=context.workspace.instance_id,
    )
    typer.echo(f"Kill switch: {'active' if snapshot.active else 'inactive'}")
    typer.echo(f"Scope: {snapshot.scope.value}")


@kill_app.command("off")
def kill_off(
    reason: str = typer.Option("resumed by user", "--reason", "-r", help="Reason to deactivate."),
    path: Path | None = typer.Option(None, "--path", "-p", help="Workspace to use."),
) -> None:
    """Deactivate the kill switch."""
    print_banner()
    context = load_cli_context(path)
    snapshot = context.kernel.deactivate_kill_switch(
        reason=reason,
        actor="user",
        workspace_id=context.workspace.workspace_id,
        instance_id=context.workspace.instance_id,
    )
    typer.echo(f"Kill switch: {'active' if snapshot.active else 'inactive'}")
    typer.echo(f"Scope: {snapshot.scope.value}")


@api_app.command("serve")
def api_serve(
    host: str = typer.Option("127.0.0.1", "--host", help="Bind host."),
    port: int = typer.Option(8787, "--port", help="Bind port."),
    path: Path | None = typer.Option(None, "--path", "-p", help="Workspace to serve."),
) -> None:
    """Serve the local HTTP API for a Nox workspace."""
    print_banner()
    workspace_path = Path.cwd() if path is None else path

    try:
        load_kernel_context(workspace_path)
    except (WorkspaceError, EventStoreError) as exc:
        typer.secho(f"[error] {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    try:
        import uvicorn
    except ImportError as exc:
        typer.secho(
            "[error] Uvicorn is not installed in the active Nox runtime.",
            fg=typer.colors.RED,
            err=True,
        )
        print_runtime_diagnostic()
        typer.echo(
            "[hint] If NoxSetup.exe is installed, another older nox command may be earlier in PATH.",
            err=True,
        )
        typer.echo("[hint] Dev reinstall: uv tool install --editable . --reinstall", err=True)
        raise typer.Exit(code=1) from exc

    from nox_agent_os.api import create_app

    typer.echo(f"Serving Nox API at http://{host}:{port}")
    typer.echo(f"Workspace: {workspace_path.resolve()}")
    uvicorn.run(
        create_app(workspace_path=workspace_path),
        host=host,
        port=port,
        log_level="info",
    )


@storage_app.command("info")
def storage_info(
    path: Path | None = typer.Option(None, "--path", "-p", help="Workspace to inspect."),
) -> None:
    """Show workspace storage details."""
    print_banner()
    print_storage_info(load_cli_context(path))


@storage_app.command("backup")
def storage_backup(
    path: Path | None = typer.Option(None, "--path", "-p", help="Workspace to back up."),
    output_dir: Path | None = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Directory for the backup file. Defaults to .nox/backups.",
    ),
) -> None:
    """Back up the current workspace event log."""
    print_banner()
    context = load_cli_context(path)
    try:
        backup_path = backup_file(context.workspace.event_log_path, output_dir)
    except StorageError as exc:
        typer.secho(f"[error] {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(f"Backup: {backup_path}")


@storage_app.command("export-events")
def storage_export_events(
    output: Path = typer.Option(..., "--output", "-o", help="JSON export path."),
    path: Path | None = typer.Option(None, "--path", "-p", help="Workspace to export."),
) -> None:
    """Export workspace events as normalized JSON."""
    print_banner()
    context = load_cli_context(path)
    try:
        export_path = export_events(context.event_store, output)
    except StorageError as exc:
        typer.secho(f"[error] {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(f"Export: {export_path}")


@app.command("cli")
def cli(
    path: Path | None = typer.Option(None, "--path", "-p", help="Workspace to use."),
) -> None:
    """Start an interactive Nox CLI session."""
    print_banner()
    context = load_cli_context(path)
    typer.echo("Nox CLI. Type 'help' for commands, 'exit' to quit.")

    while True:
        try:
            line = input("nox> ")
        except EOFError:
            typer.echo()
            return
        except KeyboardInterrupt:
            typer.echo()
            return

        if not line.strip():
            continue

        if line.strip().lower() in {"exit", "quit"}:
            return

        handle_shell_line(context, line)


def handle_shell_line(context: CliKernelContext, line: str) -> None:
    try:
        parts = shlex.split(line)
    except ValueError as exc:
        typer.secho(f"[error] {exc}", fg=typer.colors.RED)
        return

    if not parts:
        return

    try:
        run_shell_command(context, parts)
    except Exception as exc:
        typer.secho(f"[error] {exc}", fg=typer.colors.RED)


def run_shell_command(context: CliKernelContext, parts: list[str]) -> None:
    command = parts[0].lower()

    if command == "help":
        typer.echo("status")
        typer.echo("task create <goal>")
        typer.echo("task show <task_id>")
        typer.echo("task transition <task_id> <status> <reason>")
        typer.echo("logs [task_id]")
        typer.echo("policy <task_id> <capability> [target]")
        typer.echo("approvals")
        typer.echo("approve <approval_id> [reason]")
        typer.echo("reject <approval_id> [reason]")
        typer.echo("kill on|off|status [reason]")
        return

    if command == "status":
        print_snapshot(context)
        return

    if command == "task" and len(parts) >= 3 and parts[1] == "create":
        task = context.kernel.create_task(
            " ".join(parts[2:]),
            workspace_id=context.workspace.workspace_id,
            instance_id=context.workspace.instance_id,
        )
        print_task(task)
        return

    if command == "task" and len(parts) == 3 and parts[1] == "show":
        print_task(context.kernel.get_task(parts[2]))
        return

    if command == "task" and len(parts) >= 5 and parts[1] == "transition":
        task = context.kernel.transition_task(
            parts[2],
            TaskStatus(parts[3]),
            reason=" ".join(parts[4:]),
            actor="user",
        )
        print_task(task)
        return

    if command in {"logs", "events"}:
        events = (
            context.kernel.audit_trail.list_events(task_id=parts[1])
            if len(parts) > 1
            else context.kernel.audit_trail.list_events()
        )
        for event in events[-20:]:
            print_event(event)
        return

    if command == "policy" and len(parts) >= 3:
        result = context.kernel.request_capability(
            parts[1],
            Capability(parts[2]),
            description=f"Shell request {parts[2]}",
            target=parts[3] if len(parts) > 3 else None,
            actor="user",
        )
        typer.echo(f"Decision: {result.decision.decision.value}")
        if result.approval is not None:
            typer.echo(f"Approval ID: {result.approval.approval_id}")
        return

    if command == "approvals":
        approvals = context.kernel.approval_queue.list_pending()
        if not approvals:
            typer.echo("No pending approvals.")
            return
        for approval in approvals:
            typer.echo(
                f"{approval.approval_id} {approval.capability.value} "
                f"{approval.status.value} task={approval.task_id}"
            )
        return

    if command in {"approve", "reject"} and len(parts) >= 2:
        approved = command == "approve"
        reason = " ".join(parts[2:]) if len(parts) > 2 else f"{command}d in cli"
        approval = context.kernel.resolve_approval(
            parts[1],
            approved=approved,
            actor="user",
            reason=reason,
        )
        expected_status = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
        typer.echo(f"Approval {approval.approval_id}: {expected_status.value}")
        return

    if command == "kill" and len(parts) >= 2:
        subcommand = parts[1].lower()
        if subcommand == "status":
            snapshot = context.kernel.kill_switch.snapshot()
            typer.echo(f"Kill switch: {'active' if snapshot.active else 'inactive'}")
            typer.echo(f"Scope: {snapshot.scope.value}")
            return
        if subcommand == "on":
            reason = " ".join(parts[2:]) if len(parts) > 2 else "enabled in cli"
            snapshot = context.kernel.activate_kill_switch(
                reason=reason,
                actor="user",
                workspace_id=context.workspace.workspace_id,
                instance_id=context.workspace.instance_id,
            )
            typer.echo(f"Kill switch: {'active' if snapshot.active else 'inactive'}")
            return
        if subcommand == "off":
            reason = " ".join(parts[2:]) if len(parts) > 2 else "disabled in cli"
            snapshot = context.kernel.deactivate_kill_switch(
                reason=reason,
                actor="user",
                workspace_id=context.workspace.workspace_id,
                instance_id=context.workspace.instance_id,
            )
            typer.echo(f"Kill switch: {'active' if snapshot.active else 'inactive'}")
            return

    typer.echo("Unknown command. Type 'help' for commands.")

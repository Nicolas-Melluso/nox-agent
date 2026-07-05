from __future__ import annotations

import platform
from pathlib import Path

import typer

from nox_agent_os import __version__
from nox_agent_os.workspace import (
    SYSTEM_PROMPT_NAME,
    WORKSPACE_DIR_NAME,
    WorkspaceError,
    create_workspace,
    find_workspace,
    get_engine_reference,
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


@app.command()
def version() -> None:
    """Show the installed Nox version."""
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
        return

    typer.echo(f"Nox workspace already exists: {result.workspace_dir}")
    typer.echo(f"System prompt: {result.system_prompt_path}")


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


@app.command()
def doctor(path: Path | None = typer.Argument(None, help="Workspace directory to inspect.")) -> None:
    """Inspect the local Nox installation and current workspace."""
    print_banner()
    target_path = Path.cwd() if path is None else path
    root = target_path.resolve()
    workspace = find_workspace(root)
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

    if workspace is None:
        typer.echo(f"[warn] workspace: no {WORKSPACE_DIR_NAME}/{SYSTEM_PROMPT_NAME} found")
        typer.echo("       run: nox init")
        raise typer.Exit(code=1)

    typer.echo(f"[ok] workspace: {workspace.workspace_dir}")
    typer.echo(f"[ok] system prompt: {workspace.system_prompt_path}")


@app.command()
def prompt() -> None:
    """Print the default workspace system prompt template."""
    typer.echo(render_system_prompt())

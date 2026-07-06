import json

from typer.testing import CliRunner

from nox_agent_os.cli.main import app

runner = CliRunner()


def _task_id(output: str) -> str:
    for line in output.splitlines():
        if line.startswith("Task ID: "):
            return line.removeprefix("Task ID: ").strip()
    raise AssertionError(f"No task id in output:\n{output}")


def _approval_id(output: str) -> str:
    for line in output.splitlines():
        if line.startswith("Approval ID: "):
            return line.removeprefix("Approval ID: ").strip()
    raise AssertionError(f"No approval id in output:\n{output}")


def test_init_creates_workspace_event_log(tmp_path) -> None:
    result = runner.invoke(app, ["init", str(tmp_path)])

    assert result.exit_code == 0
    assert (tmp_path / ".nox" / "events.jsonl").exists()


def test_task_create_and_show_persist_between_cli_invocations(tmp_path) -> None:
    runner.invoke(app, ["init", str(tmp_path)])
    identity = json.loads((tmp_path / ".nox" / "identity.json").read_text(encoding="utf-8"))

    created = runner.invoke(app, ["task", "create", "build cli", "--path", str(tmp_path)])
    task_id = _task_id(created.output)
    shown = runner.invoke(app, ["task", "show", task_id, "--path", str(tmp_path)])
    events = runner.invoke(app, ["logs", "task", task_id, "--path", str(tmp_path)])

    assert created.exit_code == 0
    assert shown.exit_code == 0
    assert events.exit_code == 0
    assert "Goal: build cli" in shown.output
    assert f"Workspace: {identity['workspace_id']}" in shown.output
    assert f"workspace={identity['workspace_id']}" in events.output
    assert f"instance={identity['instance_id']}" in events.output
    assert "task_created" in events.output


def test_status_reads_persistent_resource_snapshot(tmp_path) -> None:
    runner.invoke(app, ["init", str(tmp_path)])
    runner.invoke(app, ["task", "create", "one task", "--path", str(tmp_path)])

    result = runner.invoke(app, ["status", "--path", str(tmp_path)])

    assert result.exit_code == 0
    assert "Health: ok" in result.output
    assert "Tasks: 1" in result.output
    assert "Events: 1" in result.output


def test_policy_check_creates_rehydratable_pending_approval(tmp_path) -> None:
    runner.invoke(app, ["init", str(tmp_path)])
    created = runner.invoke(app, ["task", "create", "write docs", "--path", str(tmp_path)])
    task_id = _task_id(created.output)

    policy = runner.invoke(
        app,
        [
            "policy",
            "check",
            task_id,
            "write",
            "--target",
            "docs/example.md",
            "--path",
            str(tmp_path),
        ],
    )
    approval_id = _approval_id(policy.output)
    listed = runner.invoke(app, ["approvals", "list", "--path", str(tmp_path)])
    resolved = runner.invoke(
        app,
        ["approvals", "approve", approval_id, "--path", str(tmp_path)],
    )
    listed_after = runner.invoke(app, ["approvals", "list", "--path", str(tmp_path)])

    assert policy.exit_code == 0
    assert "Decision: ask" in policy.output
    assert approval_id in listed.output
    assert resolved.exit_code == 0
    assert "approved" in resolved.output
    assert "No pending approvals." in listed_after.output


def test_kill_switch_persists_between_cli_invocations(tmp_path) -> None:
    runner.invoke(app, ["init", str(tmp_path)])

    enabled = runner.invoke(
        app,
        [
            "kill",
            "on",
            "--scope",
            "new_tasks",
            "--reason",
            "freeze",
            "--path",
            str(tmp_path),
        ],
    )
    blocked = runner.invoke(app, ["task", "create", "blocked", "--path", str(tmp_path)])
    status = runner.invoke(app, ["kill", "status", "--path", str(tmp_path)])

    assert enabled.exit_code == 0
    assert blocked.exit_code == 1
    assert "Kill switch blocks new tasks." in blocked.output
    assert "Kill switch: active" in status.output
    assert "Scope: new_tasks" in status.output


def test_cli_runs_basic_kernel_session(tmp_path) -> None:
    runner.invoke(app, ["init", str(tmp_path)])

    result = runner.invoke(
        app,
        ["cli", "--path", str(tmp_path)],
        input="task create shell task\nstatus\nexit\n",
    )

    assert result.exit_code == 0
    assert "Nox CLI" in result.output
    assert "Goal: shell task" in result.output
    assert "Tasks: 1" in result.output

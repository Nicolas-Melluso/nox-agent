import json

from typer.testing import CliRunner

from nox_agent_os.cli.main import app

runner = CliRunner()


def test_help_smoke() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Local agent OS workspace launcher" in result.output
    assert "api" in result.output
    assert "cli" in result.output
    assert "logs" in result.output
    assert "upgrade" in result.output
    assert "--install-completion" not in result.output


def test_no_args_shows_banner_and_help() -> None:
    result = runner.invoke(app, [])

    assert result.exit_code == 0
    assert "Local Agent OS" in result.output
    assert "Usage:" in result.output


def test_api_help_smoke() -> None:
    result = runner.invoke(app, ["api", "serve", "--help"])

    assert result.exit_code == 0
    assert "Serve the local HTTP API" in result.output
    assert "--host" in result.output
    assert "--port" in result.output


def test_upgrade_check_is_non_destructive() -> None:
    result = runner.invoke(app, ["upgrade", "--check"])

    assert result.exit_code == 0
    assert "Upgrade check only" in result.output
    assert "Current version:" in result.output


def test_init_creates_workspace_prompt(tmp_path) -> None:
    result = runner.invoke(app, ["init", str(tmp_path)])

    assert result.exit_code == 0
    assert "Local Agent OS" in result.output
    assert "___" in result.output
    assert (tmp_path / ".nox" / "system.prompt.md").exists()
    assert (tmp_path / ".nox" / "identity.json").exists()
    assert (tmp_path / ".nox" / "events.jsonl").exists()

    identity = json.loads((tmp_path / ".nox" / "identity.json").read_text(encoding="utf-8"))
    assert identity["workspace_id"].startswith("ws_")
    assert identity["instance_id"].startswith("inst_")
    assert identity["nox_version"]
    prompt = (tmp_path / ".nox" / "system.prompt.md").read_text(encoding="utf-8")
    assert "install_root_path:" in prompt
    assert "package_path:" in prompt
    assert "executable_path:" in prompt
    assert "import_name: 'nox_agent_os'" in prompt


def test_init_creates_missing_workspace_directory(tmp_path) -> None:
    workspace = tmp_path / "new-workspace"

    result = runner.invoke(app, ["init", str(workspace)])

    assert result.exit_code == 0
    assert (workspace / ".nox" / "system.prompt.md").exists()


def test_init_without_path_uses_current_directory(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["init"])

    assert result.exit_code == 0
    assert "Initialized Nox workspace" in result.output
    assert (tmp_path / ".nox" / "system.prompt.md").exists()


def test_init_refuses_workspace_metadata_directory(tmp_path) -> None:
    runner.invoke(app, ["init", str(tmp_path)])

    result = runner.invoke(app, ["init", str(tmp_path / ".nox")])

    assert result.exit_code == 1
    assert "inside .nox metadata" in result.output
    assert not (tmp_path / ".nox" / ".nox").exists()


def test_doctor_warns_when_run_inside_workspace_metadata(tmp_path) -> None:
    runner.invoke(app, ["init", str(tmp_path)])

    result = runner.invoke(app, ["doctor", str(tmp_path / ".nox")])

    assert result.exit_code == 0
    assert "inside .nox metadata" in result.output


def test_update_refreshes_workspace_prompt(tmp_path) -> None:
    runner.invoke(app, ["init", str(tmp_path)])
    prompt_path = tmp_path / ".nox" / "system.prompt.md"
    prompt_path.write_text("old prompt", encoding="utf-8")

    result = runner.invoke(app, ["update", str(tmp_path)])

    assert result.exit_code == 0
    assert "Updated Nox workspace" in result.output
    assert "package_path:" in prompt_path.read_text(encoding="utf-8")


def test_update_preserves_workspace_identity(tmp_path) -> None:
    runner.invoke(app, ["init", str(tmp_path)])
    identity_path = tmp_path / ".nox" / "identity.json"
    before = json.loads(identity_path.read_text(encoding="utf-8"))

    result = runner.invoke(app, ["update", str(tmp_path)])
    after = json.loads(identity_path.read_text(encoding="utf-8"))

    assert result.exit_code == 0
    assert before["workspace_id"] == after["workspace_id"]
    assert before["instance_id"] == after["instance_id"]
    assert "Identity:" in result.output


def test_doctor_fails_without_workspace(tmp_path) -> None:
    result = runner.invoke(app, ["doctor", str(tmp_path)])

    assert result.exit_code == 1
    assert "run: nox init" in result.output

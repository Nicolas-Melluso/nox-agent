import json

from typer.testing import CliRunner

from nox_agent_os.cli.main import app

runner = CliRunner()


def _read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _event_lines(tmp_path) -> list[dict]:
    event_log = tmp_path / ".nox" / "events.jsonl"
    return [
        json.loads(line)
        for line in event_log.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_init_creates_model_config(tmp_path) -> None:
    result = runner.invoke(app, ["init", str(tmp_path)])
    config_path = tmp_path / ".nox" / "model.config.json"

    assert result.exit_code == 0
    assert config_path.exists()
    config = _read_json(config_path)
    assert config["default_model"] == "mock-balanced"
    assert config["audit_level"] == "normal"


def test_model_list_set_and_limit_update_workspace_config(tmp_path) -> None:
    runner.invoke(app, ["init", str(tmp_path)])

    listed = runner.invoke(app, ["model", "list", "--path", str(tmp_path)])
    set_model = runner.invoke(app, ["model", "set", "mock-fast", "--path", str(tmp_path)])
    limited = runner.invoke(
        app,
        ["model", "limit", "mock-fast", "to", "256", "--path", str(tmp_path)],
    )
    config = _read_json(tmp_path / ".nox" / "model.config.json")

    assert listed.exit_code == 0
    assert "mock-balanced" in listed.output
    assert "Audit level: normal" in listed.output
    assert set_model.exit_code == 0
    assert limited.exit_code == 0
    assert config["default_model"] == "mock-fast"
    assert config["limits"]["mock-fast"]["max_tokens"] == 256


def test_model_limit_requires_to_syntax(tmp_path) -> None:
    runner.invoke(app, ["init", str(tmp_path)])

    result = runner.invoke(
        app,
        ["model", "limit", "mock-fast", "256", "999", "--path", str(tmp_path)],
    )

    assert result.exit_code == 1
    assert "Expected syntax" in result.output


def test_model_route_emits_events_until_audit_is_off(tmp_path) -> None:
    runner.invoke(app, ["init", str(tmp_path)])

    routed = runner.invoke(
        app,
        ["model", "route", "explain nox", "--path", str(tmp_path)],
    )
    disabled = runner.invoke(app, ["audit", "off", "--path", str(tmp_path)])
    quiet = runner.invoke(
        app,
        ["model", "route", "quiet nox", "--path", str(tmp_path)],
    )
    events = _event_lines(tmp_path)

    assert routed.exit_code == 0
    assert "Model: mock-balanced" in routed.output
    assert "Mock response from mock-balanced" in routed.output
    assert disabled.exit_code == 0
    assert quiet.exit_code == 0
    assert [event["event_type"] for event in events] == [
        "model_route_selected",
        "model_invocation_completed",
    ]


def test_audit_level_command_updates_workspace_config(tmp_path) -> None:
    runner.invoke(app, ["init", str(tmp_path)])

    result = runner.invoke(app, ["audit", "level", "debug", "--path", str(tmp_path)])
    status = runner.invoke(app, ["audit", "status", "--path", str(tmp_path)])
    config = _read_json(tmp_path / ".nox" / "model.config.json")

    assert result.exit_code == 0
    assert "Audit level: debug" in result.output
    assert "Audit level: debug" in status.output
    assert config["audit_level"] == "debug"

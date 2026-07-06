from nox_agent_os.kernel import AgentKernel, EventType
from nox_agent_os.modeling import AuditLevel, set_audit_level, set_model_limit
from nox_agent_os.modeling.config import default_model_config


def test_model_router_uses_mock_backend_and_emits_audit_events() -> None:
    kernel = AgentKernel()
    config = default_model_config()

    result = kernel.route_model(
        "summarize this workspace",
        config=config,
        workspace_id="workspace-a",
        instance_id="instance-a",
    )
    events = kernel.event_store.list_all()

    assert result.route.model.model_id == "mock-balanced"
    assert result.route.max_tokens == 4096
    assert "Mock response from mock-balanced" in result.response.text
    assert [event.event_type for event in events] == [
        EventType.MODEL_ROUTE_SELECTED,
        EventType.MODEL_INVOCATION_COMPLETED,
    ]
    assert events[0].workspace_id == "workspace-a"
    assert events[0].instance_id == "instance-a"
    assert kernel.audit_trail.summary().model_invocations == 1


def test_model_router_respects_workspace_token_limit() -> None:
    kernel = AgentKernel()
    config = set_model_limit(default_model_config(), "mock-balanced", 128)

    result = kernel.route_model("short task", config=config)

    assert result.route.max_tokens == 128


def test_model_router_audit_off_does_not_emit_model_events() -> None:
    kernel = AgentKernel()
    config = set_audit_level(default_model_config(), AuditLevel.OFF)

    result = kernel.route_model("quiet route", config=config)

    assert result.route.audit_level == AuditLevel.OFF
    assert kernel.event_store.list_all() == []

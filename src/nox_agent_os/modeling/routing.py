from __future__ import annotations

from nox_agent_os.kernel.contracts import EventType
from nox_agent_os.kernel.events import EventBus
from nox_agent_os.modeling.config import ModelWorkspaceConfig
from nox_agent_os.modeling.contracts import (
    AuditLevel,
    ModelInvocationResult,
    ModelRequest,
    ModelRoute,
)
from nox_agent_os.modeling.profiles import get_profile
from nox_agent_os.modeling.registry import ModelRegistry, create_default_model_registry


class ModelRoutingError(RuntimeError):
    pass


class RoutingPolicy:
    def select(
        self,
        request: ModelRequest,
        config: ModelWorkspaceConfig,
        registry: ModelRegistry,
    ) -> ModelRoute:
        model_id = request.model_id or config.default_model
        try:
            model = registry.get_model(model_id)
        except KeyError as exc:
            raise ModelRoutingError(str(exc)) from exc

        profile = get_profile(request.profile)
        configured_limit = config.limit_for(model.model_id)
        requested_limit = request.max_tokens
        candidate_limits = [
            model.max_output_tokens,
            profile.default_max_tokens,
        ]
        if configured_limit is not None:
            candidate_limits.append(configured_limit.max_tokens)
        if requested_limit is not None:
            candidate_limits.append(requested_limit)
        max_tokens = min(candidate_limits)

        return ModelRoute(
            model=model,
            profile=profile,
            max_tokens=max_tokens,
            audit_level=config.audit_level,
            reason=(
                f"Selected {model.model_id} from "
                f"{'request' if request.model_id else 'workspace default'} "
                f"with {profile.name} profile."
            ),
        )


class ModelRouter:
    def __init__(
        self,
        *,
        registry: ModelRegistry | None = None,
        routing_policy: RoutingPolicy | None = None,
    ) -> None:
        self.registry = registry or create_default_model_registry()
        self.routing_policy = routing_policy or RoutingPolicy()

    def list_models(self):
        return self.registry.list_models()

    def route(
        self,
        request: ModelRequest,
        config: ModelWorkspaceConfig,
        event_bus: EventBus,
    ) -> ModelInvocationResult:
        route = self.routing_policy.select(request, config, self.registry)
        backend = self.registry.backend_for_model(route.model.model_id)
        _emit_route_selected(event_bus, request, route)
        response = backend.invoke(
            request,
            model=route.model,
            profile=route.profile,
            max_tokens=route.max_tokens,
        )
        _emit_invocation_completed(event_bus, request, route, response)
        return ModelInvocationResult(request=request, route=route, response=response)


def create_default_model_router() -> ModelRouter:
    return ModelRouter()


def _emit_route_selected(
    event_bus: EventBus,
    request: ModelRequest,
    route: ModelRoute,
) -> None:
    if route.audit_level == AuditLevel.OFF:
        return

    payload = {
        "model_id": route.model.model_id,
        "backend": route.model.backend_name,
        "provider": route.model.provider.value,
        "profile": route.profile.name,
        "max_tokens": route.max_tokens,
        "reason": route.reason,
    }
    if route.audit_level in {AuditLevel.DEBUG, AuditLevel.TRACE}:
        payload["prompt_preview"] = _prompt_preview(request.prompt)
    if route.audit_level == AuditLevel.TRACE:
        payload["prompt"] = request.prompt

    event_bus.emit(
        event_type=EventType.MODEL_ROUTE_SELECTED,
        trace_id=request.trace_id,
        task_id=request.task_id,
        session_id=request.session_id,
        workspace_id=request.workspace_id,
        instance_id=request.instance_id,
        actor=request.actor,
        payload=payload,
        source_module="model_router",
    )


def _emit_invocation_completed(
    event_bus: EventBus,
    request: ModelRequest,
    route: ModelRoute,
    response,
) -> None:
    if route.audit_level == AuditLevel.OFF:
        return

    payload = {
        "model_id": response.model_id,
        "backend": response.backend_name,
        "profile": response.profile,
        "finish_reason": response.finish_reason.value,
    }
    if route.audit_level in {AuditLevel.NORMAL, AuditLevel.DEBUG, AuditLevel.TRACE}:
        payload.update(
            {
                "duration_ms": response.duration_ms,
                "input_tokens_estimate": response.input_tokens_estimate,
                "output_tokens_estimate": response.output_tokens_estimate,
            }
        )
    if route.audit_level in {AuditLevel.DEBUG, AuditLevel.TRACE}:
        payload["response_preview"] = _prompt_preview(response.text)
    if route.audit_level == AuditLevel.TRACE:
        payload["response"] = response.text

    event_bus.emit(
        event_type=EventType.MODEL_INVOCATION_COMPLETED,
        trace_id=request.trace_id,
        task_id=request.task_id,
        session_id=request.session_id,
        workspace_id=request.workspace_id,
        instance_id=request.instance_id,
        actor="model_router",
        payload=payload,
        source_module="model_router",
    )


def _prompt_preview(text: str, limit: int = 160) -> str:
    return " ".join(text.split())[:limit]

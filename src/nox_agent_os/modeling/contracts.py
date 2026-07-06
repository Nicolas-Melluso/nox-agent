from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol
from uuid import uuid4


class AuditLevel(StrEnum):
    OFF = "off"
    MINIMAL = "minimal"
    NORMAL = "normal"
    DEBUG = "debug"
    TRACE = "trace"


class ProviderKind(StrEnum):
    MOCK = "mock"
    LOCAL = "local"
    OPENAI = "openai"
    CODEX = "codex"


class ModelFinishReason(StrEnum):
    STOP = "stop"
    LENGTH = "length"
    ERROR = "error"


@dataclass(frozen=True)
class ModelInfo:
    model_id: str
    display_name: str
    backend_name: str
    provider: ProviderKind
    context_window: int
    max_output_tokens: int
    supports_tools: bool = False
    supports_streaming: bool = False
    requires_network: bool = False
    requires_credentials: bool = False
    notes: str = ""


@dataclass(frozen=True)
class ReasoningProfile:
    name: str
    description: str
    default_max_tokens: int
    quality_bias: str
    latency_bias: str


@dataclass(frozen=True)
class ModelRequest:
    prompt: str
    workspace_id: str
    instance_id: str | None
    model_id: str | None = None
    profile: str = "balanced"
    max_tokens: int | None = None
    task_id: str = "model"
    session_id: str = field(default_factory=lambda: str(uuid4()))
    trace_id: str = field(default_factory=lambda: str(uuid4()))
    actor: str = "user"


@dataclass(frozen=True)
class ModelRoute:
    model: ModelInfo
    profile: ReasoningProfile
    max_tokens: int
    audit_level: AuditLevel
    reason: str


@dataclass(frozen=True)
class ModelResponse:
    text: str
    model_id: str
    backend_name: str
    profile: str
    input_tokens_estimate: int
    output_tokens_estimate: int
    duration_ms: int
    finish_reason: ModelFinishReason = ModelFinishReason.STOP


@dataclass(frozen=True)
class ModelInvocationResult:
    request: ModelRequest
    route: ModelRoute
    response: ModelResponse


class ModelBackend(Protocol):
    name: str
    provider: ProviderKind

    def list_models(self) -> list[ModelInfo]:
        ...

    def invoke(
        self,
        request: ModelRequest,
        *,
        model: ModelInfo,
        profile: ReasoningProfile,
        max_tokens: int,
    ) -> ModelResponse:
        ...

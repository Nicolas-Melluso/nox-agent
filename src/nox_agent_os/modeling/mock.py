from __future__ import annotations

from time import perf_counter

from nox_agent_os.modeling.contracts import (
    ModelBackend,
    ModelInfo,
    ModelRequest,
    ModelResponse,
    ProviderKind,
    ReasoningProfile,
)


class MockBackend(ModelBackend):
    name = "mock"
    provider = ProviderKind.MOCK

    def list_models(self) -> list[ModelInfo]:
        return [
            ModelInfo(
                model_id="mock-fast",
                display_name="Mock Fast",
                backend_name=self.name,
                provider=self.provider,
                context_window=8192,
                max_output_tokens=2048,
                notes="Fast deterministic mock model for smoke checks.",
            ),
            ModelInfo(
                model_id="mock-balanced",
                display_name="Mock Balanced",
                backend_name=self.name,
                provider=self.provider,
                context_window=16384,
                max_output_tokens=4096,
                notes="Default deterministic mock model.",
            ),
            ModelInfo(
                model_id="mock-deep",
                display_name="Mock Deep",
                backend_name=self.name,
                provider=self.provider,
                context_window=32768,
                max_output_tokens=8192,
                notes="Higher-budget deterministic mock model.",
            ),
        ]

    def invoke(
        self,
        request: ModelRequest,
        *,
        model: ModelInfo,
        profile: ReasoningProfile,
        max_tokens: int,
    ) -> ModelResponse:
        started = perf_counter()
        prompt_preview = " ".join(request.prompt.split())[:120]
        text = (
            f"Mock response from {model.model_id} using {profile.name}: "
            f"{prompt_preview}"
        )
        duration_ms = max(0, int((perf_counter() - started) * 1000))
        return ModelResponse(
            text=text,
            model_id=model.model_id,
            backend_name=self.name,
            profile=profile.name,
            input_tokens_estimate=_estimate_tokens(request.prompt),
            output_tokens_estimate=_estimate_tokens(text),
            duration_ms=duration_ms,
        )


def _estimate_tokens(text: str) -> int:
    words = [word for word in text.split() if word]
    return max(1, len(words))

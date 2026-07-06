from __future__ import annotations

from nox_agent_os.modeling.contracts import ModelBackend, ModelInfo
from nox_agent_os.modeling.mock import MockBackend


class ModelRegistry:
    def __init__(self, backends: list[ModelBackend] | None = None) -> None:
        self._backends: dict[str, ModelBackend] = {}
        for backend in backends or []:
            self.register(backend)

    def register(self, backend: ModelBackend) -> None:
        self._backends[backend.name] = backend

    def list_backends(self) -> list[ModelBackend]:
        return list(self._backends.values())

    def list_models(self) -> list[ModelInfo]:
        models: list[ModelInfo] = []
        for backend in self.list_backends():
            models.extend(backend.list_models())
        return sorted(models, key=lambda model: model.model_id)

    def get_model(self, model_id: str) -> ModelInfo:
        for model in self.list_models():
            if model.model_id == model_id:
                return model
        raise KeyError(f"Unknown model: {model_id}")

    def backend_for_model(self, model_id: str) -> ModelBackend:
        model = self.get_model(model_id)
        return self._backends[model.backend_name]


def create_default_model_registry() -> ModelRegistry:
    return ModelRegistry([MockBackend()])

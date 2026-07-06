from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from nox_agent_os.modeling.contracts import AuditLevel

MODEL_CONFIG_SCHEMA_VERSION = 1
DEFAULT_MODEL_ID = "mock-balanced"
DEFAULT_AUDIT_LEVEL = AuditLevel.NORMAL


class ModelConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class ModelLimit:
    max_tokens: int


@dataclass(frozen=True)
class ModelWorkspaceConfig:
    default_model: str = DEFAULT_MODEL_ID
    audit_level: AuditLevel = DEFAULT_AUDIT_LEVEL
    limits: dict[str, ModelLimit] = field(default_factory=dict)
    schema_version: int = MODEL_CONFIG_SCHEMA_VERSION

    def limit_for(self, model_id: str) -> ModelLimit | None:
        return self.limits.get(model_id)


def default_model_config() -> ModelWorkspaceConfig:
    return ModelWorkspaceConfig(
        limits={
            DEFAULT_MODEL_ID: ModelLimit(max_tokens=4096),
        }
    )


def ensure_model_config(path: Path) -> ModelWorkspaceConfig:
    if not path.exists():
        config = default_model_config()
        save_model_config(path, config)
        return config
    return load_model_config(path)


def load_model_config(path: Path) -> ModelWorkspaceConfig:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise TypeError("model config must be a JSON object")
        return model_config_from_dict(data)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ModelConfigError(f"Invalid model config: {path}. {exc}") from exc


def save_model_config(path: Path, config: ModelWorkspaceConfig) -> ModelWorkspaceConfig:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(
            json.dumps(model_config_to_dict(config), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        raise ModelConfigError(f"Could not write model config: {path}. {exc}") from exc
    return config


def set_default_model(config: ModelWorkspaceConfig, model_id: str) -> ModelWorkspaceConfig:
    return ModelWorkspaceConfig(
        schema_version=config.schema_version,
        default_model=model_id,
        audit_level=config.audit_level,
        limits=dict(config.limits),
    )


def set_model_limit(
    config: ModelWorkspaceConfig,
    model_id: str,
    max_tokens: int,
) -> ModelWorkspaceConfig:
    if max_tokens < 1:
        raise ModelConfigError("max_tokens must be greater than zero")
    limits = dict(config.limits)
    limits[model_id] = ModelLimit(max_tokens=max_tokens)
    return ModelWorkspaceConfig(
        schema_version=config.schema_version,
        default_model=config.default_model,
        audit_level=config.audit_level,
        limits=limits,
    )


def set_audit_level(
    config: ModelWorkspaceConfig,
    audit_level: AuditLevel,
) -> ModelWorkspaceConfig:
    return ModelWorkspaceConfig(
        schema_version=config.schema_version,
        default_model=config.default_model,
        audit_level=audit_level,
        limits=dict(config.limits),
    )


def model_config_to_dict(config: ModelWorkspaceConfig) -> dict[str, Any]:
    return {
        "schema_version": config.schema_version,
        "default_model": config.default_model,
        "audit_level": config.audit_level.value,
        "limits": {
            model_id: {"max_tokens": limit.max_tokens}
            for model_id, limit in sorted(config.limits.items())
        },
    }


def model_config_from_dict(data: dict[str, Any]) -> ModelWorkspaceConfig:
    limits_data = data.get("limits") or {}
    if not isinstance(limits_data, dict):
        raise TypeError("limits must be an object")

    return ModelWorkspaceConfig(
        schema_version=int(data.get("schema_version") or MODEL_CONFIG_SCHEMA_VERSION),
        default_model=str(data.get("default_model") or DEFAULT_MODEL_ID),
        audit_level=AuditLevel(data.get("audit_level") or DEFAULT_AUDIT_LEVEL.value),
        limits={
            str(model_id): ModelLimit(max_tokens=int(limit_data["max_tokens"]))
            for model_id, limit_data in limits_data.items()
        },
    )

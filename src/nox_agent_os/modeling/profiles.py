from __future__ import annotations

from nox_agent_os.modeling.contracts import ReasoningProfile


DEFAULT_PROFILE = "balanced"


PROFILES: dict[str, ReasoningProfile] = {
    "fast": ReasoningProfile(
        name="fast",
        description="Low-latency routing for simple tasks.",
        default_max_tokens=1024,
        quality_bias="low",
        latency_bias="high",
    ),
    "balanced": ReasoningProfile(
        name="balanced",
        description="Default routing for general workspace tasks.",
        default_max_tokens=4096,
        quality_bias="medium",
        latency_bias="medium",
    ),
    "deep": ReasoningProfile(
        name="deep",
        description="Higher-budget routing for complex reasoning.",
        default_max_tokens=8192,
        quality_bias="high",
        latency_bias="low",
    ),
    "local_only": ReasoningProfile(
        name="local_only",
        description="Restrict routing to local or offline-capable backends.",
        default_max_tokens=4096,
        quality_bias="medium",
        latency_bias="medium",
    ),
}


def list_profiles() -> list[ReasoningProfile]:
    return list(PROFILES.values())


def get_profile(name: str | None) -> ReasoningProfile:
    profile_name = name or DEFAULT_PROFILE
    try:
        return PROFILES[profile_name]
    except KeyError as exc:
        raise ValueError(f"Unknown reasoning profile: {profile_name}") from exc

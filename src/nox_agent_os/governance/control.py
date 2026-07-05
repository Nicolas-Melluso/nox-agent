from __future__ import annotations

from datetime import UTC, datetime

from nox_agent_os.governance.contracts import ControlScope, KillSwitchSnapshot


class KillSwitchActiveError(RuntimeError):
    pass


class KillSwitch:
    def __init__(self) -> None:
        self._active = False
        self._reason: str | None = None
        self._actor: str | None = None
        self._scope = ControlScope.ALL
        self._changed_at: datetime | None = None

    def activate(
        self,
        *,
        reason: str,
        actor: str,
        scope: ControlScope = ControlScope.ALL,
    ) -> KillSwitchSnapshot:
        self._active = True
        self._reason = reason
        self._actor = actor
        self._scope = ControlScope(scope)
        self._changed_at = datetime.now(UTC)
        return self.snapshot()

    def deactivate(self, *, actor: str, reason: str) -> KillSwitchSnapshot:
        self._active = False
        self._reason = reason
        self._actor = actor
        self._changed_at = datetime.now(UTC)
        return self.snapshot()

    def restore(
        self,
        *,
        active: bool,
        reason: str | None,
        actor: str | None,
        scope: ControlScope,
        changed_at: datetime | None,
    ) -> KillSwitchSnapshot:
        self._active = active
        self._reason = reason
        self._actor = actor
        self._scope = ControlScope(scope)
        self._changed_at = changed_at
        return self.snapshot()

    def blocks(self, scope: ControlScope) -> bool:
        requested_scope = ControlScope(scope)
        return self._active and (
            self._scope == ControlScope.ALL or self._scope == requested_scope
        )

    def ensure_allowed(self, scope: ControlScope) -> None:
        if self.blocks(scope):
            raise KillSwitchActiveError(self._reason or "Kill switch is active.")

    def snapshot(self) -> KillSwitchSnapshot:
        return KillSwitchSnapshot(
            active=self._active,
            reason=self._reason,
            actor=self._actor,
            scope=self._scope,
            changed_at=self._changed_at,
        )

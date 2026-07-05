from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol

from nox_agent_os.governance.contracts import (
    ActionRequest,
    Capability,
    PermissionDecision,
    PolicyDecision,
    RiskLevel,
)


@dataclass(frozen=True)
class PolicyRule:
    decision: PermissionDecision
    risk_level: RiskLevel
    reason: str
    requires_approval: bool = False


class PolicyEngine(Protocol):
    def evaluate(self, request: ActionRequest) -> PolicyDecision:
        ...


class DefaultPolicyEngine:
    DEFAULT_RULES: Mapping[Capability, PolicyRule] = {
        Capability.READ: PolicyRule(
            decision=PermissionDecision.ALLOW,
            risk_level=RiskLevel.LOW,
            reason="Read-only actions are allowed by default.",
        ),
        Capability.WRITE: PolicyRule(
            decision=PermissionDecision.ASK,
            risk_level=RiskLevel.MEDIUM,
            reason="Write actions require human approval.",
            requires_approval=True,
        ),
        Capability.EXECUTE: PolicyRule(
            decision=PermissionDecision.ASK,
            risk_level=RiskLevel.HIGH,
            reason="Execution requires human approval.",
            requires_approval=True,
        ),
        Capability.NETWORK: PolicyRule(
            decision=PermissionDecision.ASK,
            risk_level=RiskLevel.MEDIUM,
            reason="Network access requires human approval.",
            requires_approval=True,
        ),
        Capability.DELETE: PolicyRule(
            decision=PermissionDecision.DENY,
            risk_level=RiskLevel.CRITICAL,
            reason="Destructive delete actions are denied by default.",
        ),
        Capability.SEND: PolicyRule(
            decision=PermissionDecision.ASK,
            risk_level=RiskLevel.HIGH,
            reason="External send actions require human approval.",
            requires_approval=True,
        ),
        Capability.CREDENTIALS: PolicyRule(
            decision=PermissionDecision.DENY,
            risk_level=RiskLevel.CRITICAL,
            reason="Credential access is denied by default.",
        ),
    }

    def __init__(self, rules: Mapping[Capability, PolicyRule] | None = None) -> None:
        self._rules = dict(self.DEFAULT_RULES)
        if rules is not None:
            self._rules.update(rules)

    def evaluate(self, request: ActionRequest) -> PolicyDecision:
        capability = Capability(request.capability)
        rule = self._rules[capability]

        return PolicyDecision(
            action_id=request.action_id,
            capability=capability,
            decision=rule.decision,
            risk_level=rule.risk_level,
            reason=rule.reason,
            task_id=request.task_id,
            trace_id=request.trace_id,
            workspace_id=request.workspace_id,
            session_id=request.session_id,
            actor=request.actor,
            requires_approval=rule.requires_approval,
        )

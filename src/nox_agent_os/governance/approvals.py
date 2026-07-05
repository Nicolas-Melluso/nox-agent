from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

from nox_agent_os.governance.contracts import (
    ActionRequest,
    ApprovalRequest,
    ApprovalStatus,
    PermissionDecision,
    PolicyDecision,
)


class ApprovalQueueError(RuntimeError):
    pass


class ApprovalNotFoundError(ApprovalQueueError):
    pass


class ApprovalAlreadyResolvedError(ApprovalQueueError):
    pass


class InMemoryApprovalQueue:
    def __init__(self) -> None:
        self._requests: dict[str, ApprovalRequest] = {}

    def request(self, decision: PolicyDecision, action: ActionRequest) -> ApprovalRequest:
        if decision.decision != PermissionDecision.ASK:
            raise ApprovalQueueError("Only ask decisions can create approval requests.")

        approval = ApprovalRequest(
            decision_record_id=decision.decision_record_id,
            action_id=action.action_id,
            capability=action.capability,
            risk_level=decision.risk_level,
            task_id=action.task_id,
            trace_id=action.trace_id,
            workspace_id=action.workspace_id,
            session_id=action.session_id,
            actor=action.actor,
            reason=decision.reason,
            requested_by=action.actor,
            target=action.target,
            metadata=action.metadata,
        )
        self._requests[approval.approval_id] = approval
        return approval

    def get(self, approval_id: str) -> ApprovalRequest:
        try:
            return self._requests[approval_id]
        except KeyError as exc:
            raise ApprovalNotFoundError(f"Approval request not found: {approval_id}") from exc

    def list_pending(self) -> list[ApprovalRequest]:
        return [
            approval
            for approval in self._requests.values()
            if approval.status == ApprovalStatus.PENDING
        ]

    def restore_pending(self, approval: ApprovalRequest) -> ApprovalRequest:
        if approval.status != ApprovalStatus.PENDING:
            raise ApprovalQueueError("Only pending approvals can be restored.")
        self._requests[approval.approval_id] = approval
        return approval

    def approve(self, approval_id: str, *, actor: str, reason: str) -> ApprovalRequest:
        return self._resolve(
            approval_id,
            status=ApprovalStatus.APPROVED,
            actor=actor,
            reason=reason,
        )

    def reject(self, approval_id: str, *, actor: str, reason: str) -> ApprovalRequest:
        return self._resolve(
            approval_id,
            status=ApprovalStatus.REJECTED,
            actor=actor,
            reason=reason,
        )

    def _resolve(
        self,
        approval_id: str,
        *,
        status: ApprovalStatus,
        actor: str,
        reason: str,
    ) -> ApprovalRequest:
        current = self.get(approval_id)
        if current.status != ApprovalStatus.PENDING:
            raise ApprovalAlreadyResolvedError(
                f"Approval request already resolved: {approval_id}"
            )

        resolved = replace(
            current,
            status=status,
            resolved_by=actor,
            resolved_reason=reason,
            resolved_at=datetime.now(UTC),
        )
        self._requests[approval_id] = resolved
        return resolved

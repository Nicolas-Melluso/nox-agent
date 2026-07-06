from __future__ import annotations

import json
from uuid import uuid4

from nox_agent_os.governance import (
    ActionRequest,
    ApprovalRequest,
    Capability,
    ControlScope,
    DefaultPolicyEngine,
    DoomLoopGuard,
    GovernedActionResult,
    InMemoryApprovalQueue,
    KillSwitch,
    KillSwitchSnapshot,
    PermissionDecision,
    PolicyDecision,
    PolicyEngine,
    RiskLevel,
)
from nox_agent_os.kernel.contracts import EventType, TaskState, TaskStatus
from nox_agent_os.kernel.audit import AuditTrail
from nox_agent_os.kernel.events import EventBus, EventStore, InMemoryEventStore
from nox_agent_os.kernel.monitor import KernelResourceSnapshot, ResourceMonitor
from nox_agent_os.kernel.state import StateMachineKernel

KERNEL_TASK_ID = "kernel"


class TaskNotFoundError(RuntimeError):
    pass


class KernelControlBlockedError(RuntimeError):
    pass


class AgentKernel:
    def __init__(
        self,
        *,
        event_store: EventStore | None = None,
        state_machine: StateMachineKernel | None = None,
        policy_engine: PolicyEngine | None = None,
        approval_queue: InMemoryApprovalQueue | None = None,
        kill_switch: KillSwitch | None = None,
        doom_loop_guard: DoomLoopGuard | None = None,
    ) -> None:
        self.event_store = event_store or InMemoryEventStore()
        self.event_bus = EventBus(self.event_store)
        self.state_machine = state_machine or StateMachineKernel()
        self.policy_engine = policy_engine or DefaultPolicyEngine()
        self.approval_queue = approval_queue or InMemoryApprovalQueue()
        self.kill_switch = kill_switch or KillSwitch()
        self.doom_loop_guard = doom_loop_guard or DoomLoopGuard()
        self.audit_trail = AuditTrail(self.event_store)
        self.resource_monitor = ResourceMonitor(
            event_store=self.event_store,
            state_machine=self.state_machine,
            approval_queue=self.approval_queue,
            kill_switch=self.kill_switch,
        )

    def create_task(
        self,
        user_goal: str,
        *,
        workspace_id: str = "default",
        instance_id: str | None = None,
        session_id: str | None = None,
        actor: str = "user",
    ) -> TaskState:
        task_id = str(uuid4())
        trace_id = str(uuid4())
        resolved_session_id = session_id or str(uuid4())

        if self.kill_switch.blocks(ControlScope.NEW_TASKS):
            self._emit_kill_switch_blocked(
                trace_id=trace_id,
                task_id=task_id,
                session_id=resolved_session_id,
                workspace_id=workspace_id,
                actor=actor,
                operation="create_task",
                instance_id=instance_id,
            )
            raise KernelControlBlockedError("Kill switch blocks new tasks.")

        self.event_bus.emit(
            event_type=EventType.TASK_CREATED,
            trace_id=trace_id,
            task_id=task_id,
            session_id=resolved_session_id,
            workspace_id=workspace_id,
            actor=actor,
            payload={"user_goal": user_goal},
            instance_id=instance_id,
        )

        return self.get_task(task_id)

    def request_capability(
        self,
        task_id: str,
        capability: Capability | str,
        *,
        description: str,
        target: str | None = None,
        actor: str = "system",
        metadata: dict | None = None,
    ) -> GovernedActionResult:
        current = self.get_task(task_id)
        request = ActionRequest(
            capability=Capability(capability),
            description=description,
            task_id=current.task_id,
            trace_id=current.trace_id,
            workspace_id=current.workspace_id,
            instance_id=current.instance_id,
            session_id=current.session_id,
            actor=actor,
            target=target,
            metadata=metadata or {},
        )

        if self.kill_switch.blocks(ControlScope.ACTIONS):
            self._emit_kill_switch_blocked(
                trace_id=current.trace_id,
                task_id=current.task_id,
                session_id=current.session_id,
                workspace_id=current.workspace_id,
                actor=actor,
                operation=f"capability:{request.capability.value}",
                instance_id=current.instance_id,
            )
            decision = self._deny_request(
                request,
                reason="Kill switch blocks governed actions.",
                risk_level=RiskLevel.CRITICAL,
            )
            self._emit_policy_decision(decision)
            return GovernedActionResult(
                request=request,
                decision=decision,
                blocked_reason=decision.reason,
            )

        doom_observation = self.doom_loop_guard.observe(
            task_id=current.task_id,
            trace_id=current.trace_id,
            action_name=request.capability.value,
            normalized_input=self._normalize_action_input(request),
        )
        if doom_observation.detected:
            self.event_bus.emit(
                event_type=EventType.DOOM_LOOP_DETECTED,
                trace_id=current.trace_id,
                task_id=current.task_id,
                session_id=current.session_id,
                workspace_id=current.workspace_id,
                actor=actor,
                payload={
                    "action_name": doom_observation.action_name,
                    "normalized_input": doom_observation.normalized_input,
                    "count": doom_observation.count,
                    "threshold": doom_observation.threshold,
                    "reason": doom_observation.reason,
                },
                source_module="governance",
                risk_level=RiskLevel.HIGH.value,
                instance_id=current.instance_id,
            )
            decision = self._deny_request(
                request,
                reason=doom_observation.reason or "Doom loop detected.",
                risk_level=RiskLevel.HIGH,
            )
            self._emit_policy_decision(decision)
            if current.status != TaskStatus.BLOCKED:
                self.event_bus.emit(
                    event_type=EventType.TASK_STATUS_CHANGED,
                    trace_id=current.trace_id,
                    task_id=current.task_id,
                    session_id=current.session_id,
                    workspace_id=current.workspace_id,
                    actor="governance",
                    payload={
                        "from": current.status.value,
                        "to": TaskStatus.BLOCKED.value,
                        "reason": "doom_loop_detected",
                    },
                    source_module="governance",
                    risk_level=RiskLevel.HIGH.value,
                    decision_record_id=decision.decision_record_id,
                    instance_id=current.instance_id,
                )
            return GovernedActionResult(
                request=request,
                decision=decision,
                blocked_reason=decision.reason,
            )

        decision = self.policy_engine.evaluate(request)
        self._emit_policy_decision(decision)

        approval: ApprovalRequest | None = None
        if decision.decision == PermissionDecision.ASK:
            approval = self.approval_queue.request(decision, request)
            self.event_bus.emit(
                event_type=EventType.APPROVAL_REQUESTED,
                trace_id=current.trace_id,
                task_id=current.task_id,
                session_id=current.session_id,
                workspace_id=current.workspace_id,
                actor=actor,
                payload={
                    "approval_id": approval.approval_id,
                    "action_id": approval.action_id,
                    "capability": approval.capability.value,
                    "status": approval.status.value,
                    "reason": approval.reason,
                    "target": approval.target,
                    "metadata": approval.metadata,
                },
                source_module="governance",
                risk_level=approval.risk_level.value,
                decision_record_id=approval.decision_record_id,
                instance_id=current.instance_id,
            )

        return GovernedActionResult(request=request, decision=decision, approval=approval)

    def resolve_approval(
        self,
        approval_id: str,
        *,
        approved: bool,
        actor: str,
        reason: str,
    ) -> ApprovalRequest:
        if approved:
            approval = self.approval_queue.approve(
                approval_id,
                actor=actor,
                reason=reason,
            )
        else:
            approval = self.approval_queue.reject(
                approval_id,
                actor=actor,
                reason=reason,
            )

        self.event_bus.emit(
            event_type=EventType.APPROVAL_RESOLVED,
            trace_id=approval.trace_id,
            task_id=approval.task_id,
            session_id=approval.session_id,
            workspace_id=approval.workspace_id,
            actor=actor,
            payload={
                "approval_id": approval.approval_id,
                "capability": approval.capability.value,
                "status": approval.status.value,
                "reason": reason,
            },
            source_module="governance",
            risk_level=approval.risk_level.value,
            decision_record_id=approval.decision_record_id,
            instance_id=approval.instance_id,
        )
        return approval

    def activate_kill_switch(
        self,
        *,
        reason: str,
        actor: str = "user",
        scope: ControlScope | str = ControlScope.ALL,
        workspace_id: str = "global",
        instance_id: str | None = None,
    ) -> KillSwitchSnapshot:
        snapshot = self.kill_switch.activate(
            reason=reason,
            actor=actor,
            scope=ControlScope(scope),
        )
        self._emit_kill_switch_changed(
            snapshot,
            actor=actor,
            workspace_id=workspace_id,
            instance_id=instance_id,
        )
        return snapshot

    def deactivate_kill_switch(
        self,
        *,
        reason: str,
        actor: str = "user",
        workspace_id: str = "global",
        instance_id: str | None = None,
    ) -> KillSwitchSnapshot:
        snapshot = self.kill_switch.deactivate(actor=actor, reason=reason)
        self._emit_kill_switch_changed(
            snapshot,
            actor=actor,
            workspace_id=workspace_id,
            instance_id=instance_id,
        )
        return snapshot

    def resource_snapshot(self) -> KernelResourceSnapshot:
        return self.resource_monitor.snapshot()

    def get_task(self, task_id: str) -> TaskState:
        events = self.event_store.list_for_task(task_id)
        if not events:
            raise TaskNotFoundError(f"Task not found: {task_id}")
        return self.state_machine.replay(events)

    def transition_task(
        self,
        task_id: str,
        target_status: TaskStatus,
        *,
        reason: str,
        actor: str = "system",
    ) -> TaskState:
        current = self.get_task(task_id)

        if not self.state_machine.can_transition(current.status, target_status):
            self.event_bus.emit(
                event_type=EventType.STATE_TRANSITION_DENIED,
                trace_id=current.trace_id,
                task_id=current.task_id,
                session_id=current.session_id,
                workspace_id=current.workspace_id,
                actor=actor,
                payload={
                    "from": current.status.value,
                    "to": target_status.value,
                    "reason": reason,
                },
                instance_id=current.instance_id,
            )
            return self.get_task(task_id)

        self.event_bus.emit(
            event_type=EventType.TASK_STATUS_CHANGED,
            trace_id=current.trace_id,
            task_id=current.task_id,
            session_id=current.session_id,
            workspace_id=current.workspace_id,
            actor=actor,
            payload={
                "from": current.status.value,
                "to": target_status.value,
                "reason": reason,
            },
            instance_id=current.instance_id,
        )
        return self.get_task(task_id)

    def _deny_request(
        self,
        request: ActionRequest,
        *,
        reason: str,
        risk_level: RiskLevel,
    ) -> PolicyDecision:
        return PolicyDecision(
            action_id=request.action_id,
            capability=request.capability,
            decision=PermissionDecision.DENY,
            risk_level=risk_level,
            reason=reason,
            task_id=request.task_id,
            trace_id=request.trace_id,
            workspace_id=request.workspace_id,
            instance_id=request.instance_id,
            session_id=request.session_id,
            actor=request.actor,
        )

    def _emit_policy_decision(self, decision: PolicyDecision) -> None:
        self.event_bus.emit(
            event_type=EventType.POLICY_DECISION_RECORDED,
            trace_id=decision.trace_id,
            task_id=decision.task_id,
            session_id=decision.session_id,
            workspace_id=decision.workspace_id,
            actor=decision.actor,
            payload={
                "action_id": decision.action_id,
                "capability": decision.capability.value,
                "decision": decision.decision.value,
                "requires_approval": decision.requires_approval,
                "reason": decision.reason,
            },
            source_module="governance",
            risk_level=decision.risk_level.value,
            decision_record_id=decision.decision_record_id,
            instance_id=decision.instance_id,
        )

    def _emit_kill_switch_changed(
        self,
        snapshot: KillSwitchSnapshot,
        *,
        actor: str,
        workspace_id: str,
        instance_id: str | None,
    ) -> None:
        self.event_bus.emit(
            event_type=EventType.KILL_SWITCH_CHANGED,
            trace_id=str(uuid4()),
            task_id=KERNEL_TASK_ID,
            session_id=str(uuid4()),
            workspace_id=workspace_id,
            actor=actor,
            payload={
                "active": snapshot.active,
                "reason": snapshot.reason,
                "scope": snapshot.scope.value,
            },
            source_module="governance",
            risk_level=RiskLevel.CRITICAL.value if snapshot.active else RiskLevel.LOW.value,
            instance_id=instance_id,
        )

    def _emit_kill_switch_blocked(
        self,
        *,
        trace_id: str,
        task_id: str,
        session_id: str,
        workspace_id: str,
        actor: str,
        operation: str,
        instance_id: str | None = None,
    ) -> None:
        snapshot = self.kill_switch.snapshot()
        self.event_bus.emit(
            event_type=EventType.KILL_SWITCH_BLOCKED,
            trace_id=trace_id,
            task_id=task_id,
            session_id=session_id,
            workspace_id=workspace_id,
            actor=actor,
            payload={
                "operation": operation,
                "reason": snapshot.reason,
                "scope": snapshot.scope.value,
            },
            source_module="governance",
            risk_level=RiskLevel.CRITICAL.value,
            instance_id=instance_id,
        )

    def _normalize_action_input(self, request: ActionRequest) -> str:
        return json.dumps(
            {
                "capability": request.capability.value,
                "target": request.target,
                "metadata": request.metadata,
            },
            sort_keys=True,
            default=str,
        )

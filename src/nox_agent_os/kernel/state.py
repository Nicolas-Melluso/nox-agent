from __future__ import annotations

from dataclasses import replace

from nox_agent_os.kernel.contracts import (
    TERMINAL_TASK_STATUSES,
    EventRecord,
    EventType,
    TaskState,
    TaskStatus,
)


class StateReplayError(RuntimeError):
    pass


class StateMachineKernel:
    def replay(self, events: list[EventRecord]) -> TaskState:
        state: TaskState | None = None

        for event in events:
            state = self.apply(state, event)

        if state is None:
            raise StateReplayError("Cannot replay task state without events.")

        return state

    def apply(self, state: TaskState | None, event: EventRecord) -> TaskState | None:
        if event.event_type == EventType.TASK_CREATED:
            return TaskState(
                task_id=event.task_id,
                user_goal=str(event.payload["user_goal"]),
                workspace_id=event.workspace_id,
                session_id=event.session_id,
                trace_id=event.trace_id,
                status=TaskStatus.CREATED,
                current_state={"created_at": event.timestamp.isoformat()},
            )

        if event.event_type == EventType.TASK_STATUS_CHANGED:
            if state is None:
                raise StateReplayError("Status changed before task was created.")
            return TaskState(
                task_id=state.task_id,
                user_goal=state.user_goal,
                workspace_id=state.workspace_id,
                session_id=state.session_id,
                trace_id=state.trace_id,
                status=TaskStatus(event.payload["to"]),
                current_state={
                    **state.current_state,
                    "last_transition_reason": event.payload.get("reason"),
                },
            )

        if event.event_type == EventType.STATE_TRANSITION_DENIED:
            return state

        if event.event_type == EventType.POLICY_DECISION_RECORDED:
            if state is None:
                return state
            return replace(
                state,
                current_state={
                    **state.current_state,
                    "last_policy_decision": {
                        "decision_record_id": event.decision_record_id,
                        "decision": event.payload.get("decision"),
                        "capability": event.payload.get("capability"),
                        "risk_level": event.risk_level,
                        "reason": event.payload.get("reason"),
                    },
                },
            )

        if event.event_type == EventType.APPROVAL_REQUESTED:
            if state is None:
                return state
            return replace(
                state,
                current_state={
                    **state.current_state,
                    "pending_approval_id": event.payload.get("approval_id"),
                    "pending_approval_capability": event.payload.get("capability"),
                },
            )

        if event.event_type == EventType.APPROVAL_RESOLVED:
            if state is None:
                return state
            return replace(
                state,
                current_state={
                    **state.current_state,
                    "pending_approval_id": None,
                    "last_approval": {
                        "approval_id": event.payload.get("approval_id"),
                        "status": event.payload.get("status"),
                        "reason": event.payload.get("reason"),
                    },
                },
            )

        if event.event_type == EventType.DOOM_LOOP_DETECTED:
            if state is None:
                return state
            return replace(
                state,
                current_state={
                    **state.current_state,
                    "doom_loop_detected": True,
                    "doom_loop_reason": event.payload.get("reason"),
                },
            )

        return state

    def can_transition(self, current: TaskStatus, target: TaskStatus) -> bool:
        if current in TERMINAL_TASK_STATUSES and target == TaskStatus.RUNNING:
            return False
        return True

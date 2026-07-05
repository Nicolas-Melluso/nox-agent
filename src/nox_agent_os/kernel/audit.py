from __future__ import annotations

from dataclasses import dataclass

from nox_agent_os.kernel.contracts import EventRecord, EventType
from nox_agent_os.kernel.events import EventStore


@dataclass(frozen=True)
class AuditSummary:
    total_events: int
    policy_decisions: int
    approval_requests: int
    approval_resolutions: int
    kill_switch_events: int
    blocked_events: int
    doom_loop_events: int


class AuditTrail:
    def __init__(self, event_store: EventStore) -> None:
        self._event_store = event_store

    def list_events(
        self,
        *,
        task_id: str | None = None,
        trace_id: str | None = None,
        event_type: EventType | str | None = None,
    ) -> list[EventRecord]:
        events = (
            self._event_store.list_for_task(task_id)
            if task_id is not None
            else self._event_store.list_all()
        )

        if trace_id is not None:
            events = [event for event in events if event.trace_id == trace_id]

        if event_type is not None:
            resolved_event_type = EventType(event_type)
            events = [event for event in events if event.event_type == resolved_event_type]

        return events

    def list_for_trace(self, trace_id: str) -> list[EventRecord]:
        return self.list_events(trace_id=trace_id)

    def list_policy_decisions(self) -> list[EventRecord]:
        return self.list_events(event_type=EventType.POLICY_DECISION_RECORDED)

    def list_approvals(self) -> list[EventRecord]:
        return [
            event
            for event in self._event_store.list_all()
            if event.event_type
            in {
                EventType.APPROVAL_REQUESTED,
                EventType.APPROVAL_RESOLVED,
            }
        ]

    def list_blocks(self) -> list[EventRecord]:
        return [
            event
            for event in self._event_store.list_all()
            if event.event_type
            in {
                EventType.KILL_SWITCH_BLOCKED,
                EventType.DOOM_LOOP_DETECTED,
                EventType.STATE_TRANSITION_DENIED,
            }
        ]

    def summary(self) -> AuditSummary:
        events = self._event_store.list_all()
        event_types = [event.event_type for event in events]

        return AuditSummary(
            total_events=len(events),
            policy_decisions=event_types.count(EventType.POLICY_DECISION_RECORDED),
            approval_requests=event_types.count(EventType.APPROVAL_REQUESTED),
            approval_resolutions=event_types.count(EventType.APPROVAL_RESOLVED),
            kill_switch_events=event_types.count(EventType.KILL_SWITCH_CHANGED)
            + event_types.count(EventType.KILL_SWITCH_BLOCKED),
            blocked_events=len(self.list_blocks()),
            doom_loop_events=event_types.count(EventType.DOOM_LOOP_DETECTED),
        )

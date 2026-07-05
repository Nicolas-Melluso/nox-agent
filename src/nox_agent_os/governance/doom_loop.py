from __future__ import annotations

from nox_agent_os.governance.contracts import DoomLoopObservation


class DoomLoopGuard:
    def __init__(self, *, threshold: int = 3) -> None:
        if threshold < 2:
            raise ValueError("Doom loop threshold must be at least 2.")
        self.threshold = threshold
        self._counts: dict[tuple[str, str, str], int] = {}

    def observe(
        self,
        *,
        task_id: str,
        trace_id: str,
        action_name: str,
        normalized_input: str,
    ) -> DoomLoopObservation:
        key = (task_id, action_name, normalized_input)
        count = self._counts.get(key, 0) + 1
        self._counts[key] = count
        detected = count >= self.threshold

        reason = None
        if detected:
            reason = (
                f"Repeated action '{action_name}' reached "
                f"{count}/{self.threshold} attempts without new input."
            )

        return DoomLoopObservation(
            task_id=task_id,
            trace_id=trace_id,
            action_name=action_name,
            normalized_input=normalized_input,
            count=count,
            threshold=self.threshold,
            detected=detected,
            reason=reason,
        )

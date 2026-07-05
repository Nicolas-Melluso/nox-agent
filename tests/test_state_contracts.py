from nox_agent_os.governance import PermissionDecision
from nox_agent_os.kernel import AgentKernel
from nox_agent_os.kernel.contracts import (
    TERMINAL_TASK_STATUSES,
    AgentStatus,
    RecoveryState,
    RunMode,
    TaskStatus,
    TerminationReason,
)


def test_task_state_has_initial_orthogonal_axes() -> None:
    kernel = AgentKernel()

    task = kernel.create_task("inspect state axes")

    assert task.status == TaskStatus.CREATED
    assert task.agent_status == AgentStatus.IDLE
    assert task.run_mode == RunMode.PLAN
    assert task.recovery_state is None
    assert task.termination_reason is None


def test_state_contracts_include_planned_axes() -> None:
    assert TaskStatus.WAITING_APPROVAL.value == "waiting_approval"
    assert TaskStatus.WAITING_TOOL.value == "waiting_tool"
    assert AgentStatus.AWAITING_CONFIRMATION.value == "awaiting_confirmation"
    assert RunMode.INCIDENT_MODE.value == "incident_mode"
    assert RecoveryState.REWIND_REQUESTED.value == "rewind_requested"
    assert TerminationReason.DOOM_LOOP_DETECTED.value == "doom_loop_detected"


def test_terminal_task_statuses_include_timeout() -> None:
    assert TaskStatus.TIMED_OUT in TERMINAL_TASK_STATUSES


def test_permission_decision_contract_keeps_future_hitl_states() -> None:
    assert PermissionDecision.ALLOW.value == "allow"
    assert PermissionDecision.ASK.value == "ask"
    assert PermissionDecision.DENY.value == "deny"
    assert PermissionDecision.APPROVED_ONCE.value == "approved_once"
    assert PermissionDecision.APPROVED_SESSION.value == "approved_session"
    assert PermissionDecision.AUTO_DENIED.value == "auto_denied"

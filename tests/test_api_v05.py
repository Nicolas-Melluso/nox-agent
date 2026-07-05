from fastapi.testclient import TestClient

from nox_agent_os.api import create_app
from nox_agent_os.workspace import create_workspace


def test_health_and_status(tmp_path) -> None:
    create_workspace(tmp_path)
    client = TestClient(create_app(workspace_path=tmp_path))

    health = client.get("/health")
    status = client.get("/status")

    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert status.status_code == 200
    assert status.json()["total_tasks"] == 0
    assert status.json()["kill_switch_active"] is False


def test_task_lifecycle_and_events(tmp_path) -> None:
    create_workspace(tmp_path)
    client = TestClient(create_app(workspace_path=tmp_path))

    created = client.post("/tasks", json={"goal": "build local api"})
    task_id = created.json()["task_id"]
    listed = client.get("/tasks")
    shown = client.get(f"/tasks/{task_id}")
    transitioned = client.post(
        f"/tasks/{task_id}/transitions",
        json={"status": "running", "reason": "start"},
    )
    events = client.get(f"/tasks/{task_id}/events")

    assert created.status_code == 201
    assert listed.status_code == 200
    assert shown.status_code == 200
    assert transitioned.status_code == 200
    assert events.status_code == 200
    assert listed.json()[0]["task_id"] == task_id
    assert shown.json()["user_goal"] == "build local api"
    assert transitioned.json()["status"] == "running"
    assert [event["event_type"] for event in events.json()] == [
        "task_created",
        "task_status_changed",
    ]


def test_policy_approval_flow_is_rehydrated_between_requests(tmp_path) -> None:
    create_workspace(tmp_path)
    client = TestClient(create_app(workspace_path=tmp_path))
    task_id = client.post("/tasks", json={"goal": "write docs"}).json()["task_id"]

    policy = client.post(
        "/policy/check",
        json={
            "task_id": task_id,
            "capability": "write",
            "target": "docs/example.md",
        },
    )
    approval_id = policy.json()["approval"]["approval_id"]
    approvals = client.get("/approvals")
    resolved = client.post(
        f"/approvals/{approval_id}/approve",
        json={"reason": "approved for api test"},
    )
    approvals_after = client.get("/approvals")

    assert policy.status_code == 200
    assert policy.json()["decision"] == "ask"
    assert approvals.status_code == 200
    assert approvals.json()[0]["approval_id"] == approval_id
    assert resolved.status_code == 200
    assert resolved.json()["status"] == "approved"
    assert approvals_after.json() == []


def test_kill_switch_blocks_new_tasks(tmp_path) -> None:
    create_workspace(tmp_path)
    client = TestClient(create_app(workspace_path=tmp_path))

    enabled = client.post(
        "/kill/on",
        json={"reason": "freeze tasks", "scope": "new_tasks"},
    )
    blocked = client.post("/tasks", json={"goal": "blocked task"})
    status = client.get("/kill")

    assert enabled.status_code == 200
    assert enabled.json()["active"] is True
    assert blocked.status_code == 423
    assert status.json()["scope"] == "new_tasks"

"""End-to-end tests for the workflow create + run routes."""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routes.workflows import (
    get_step_resolver,
    get_workflow_store,
)
from app.services.workflows.models import Workflow, WorkflowStep
from app.services.workflows.runner import StepResult


@pytest.fixture
def client() -> TestClient:
    fresh_store: dict[UUID, Workflow] = {}
    call_log: list[str] = []

    def _override_store() -> dict[UUID, Workflow]:
        return fresh_store

    def _resolver(step: WorkflowStep) -> Any:
        def _execute(step: WorkflowStep, context: dict[str, Any]) -> StepResult:
            call_log.append(step.name)
            return StepResult(output={"echoed": step.name})

        return _execute

    app.dependency_overrides[get_workflow_store] = _override_store
    app.dependency_overrides[get_step_resolver] = lambda: _resolver

    test_client = TestClient(app)
    test_client.call_log = call_log  # type: ignore[attr-defined]
    yield test_client
    app.dependency_overrides.clear()


def _create_payload(name: str = "demo") -> dict[str, Any]:
    return {
        "account_id": str(uuid4()),
        "name": name,
        "description": "test workflow",
        "steps": [
            {"ordinal": 0, "name": "alpha", "action": "noop", "config": {}},
            {"ordinal": 1, "name": "beta", "action": "noop", "config": {}},
        ],
    }


def test_create_workflow_returns_persisted_payload(client: TestClient) -> None:
    payload = _create_payload()
    resp = client.post("/workflows", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "demo"
    assert body["account_id"] == payload["account_id"]
    assert len(body["steps"]) == 2
    assert body["steps"][0]["name"] == "alpha"
    UUID(body["id"])


def test_run_workflow_executes_all_steps(client: TestClient) -> None:
    create = client.post("/workflows", json=_create_payload()).json()
    workflow_id = create["id"]

    resp = client.post(
        f"/workflows/{workflow_id}/run",
        json={"triggered_by": "tester", "input": {"x": 1}},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["workflow_id"] == workflow_id
    assert body["status"] == "succeeded"
    assert body["triggered_by"] == "tester"
    assert body["input"] == {"x": 1}
    assert [sr["status"] for sr in body["step_runs"]] == ["succeeded", "succeeded"]
    assert client.call_log == ["alpha", "beta"]  # type: ignore[attr-defined]


def test_run_workflow_idempotent_replay_skips_re_execution(client: TestClient) -> None:
    create = client.post("/workflows", json=_create_payload()).json()
    workflow_id = create["id"]
    headers = {"Idempotency-Key": "key-123"}
    body = {"triggered_by": "tester", "input": {}}

    first = client.post(f"/workflows/{workflow_id}/run", json=body, headers=headers)
    second = client.post(f"/workflows/{workflow_id}/run", json=body, headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]
    assert client.call_log == ["alpha", "beta"]  # type: ignore[attr-defined]


def test_run_workflow_returns_404_for_unknown_id(client: TestClient) -> None:
    missing_id = uuid4()
    resp = client.post(
        f"/workflows/{missing_id}/run",
        json={"triggered_by": "tester", "input": {}},
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "workflow not found"

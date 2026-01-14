"""Tests for the idempotency store and its integration with the runner."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import pytest

from app.services.workflows.idempotency import InMemoryIdempotencyStore
from app.services.workflows.models import (
    RunStatus,
    StepStatus,
    Workflow,
    WorkflowStep,
)
from app.services.workflows.runner import SequentialWorkflowRunner, StepResult


class _ManualClock:
    def __init__(self, start: datetime) -> None:
        self._now = start

    def __call__(self) -> datetime:
        return self._now

    def advance(self, delta: timedelta) -> None:
        self._now += delta


def _build_step(ordinal: int, name: str) -> WorkflowStep:
    return WorkflowStep(
        id=uuid4(),
        workflow_id=uuid4(),
        ordinal=ordinal,
        name=name,
        action="noop",
        config={},
    )


def _build_workflow(steps: tuple[WorkflowStep, ...]) -> Workflow:
    now = datetime.now(tz=timezone.utc)
    workflow_id = uuid4()
    bound = tuple(s.model_copy(update={"workflow_id": workflow_id}) for s in steps)
    return Workflow(
        id=workflow_id,
        account_id=uuid4(),
        name="wf",
        description=None,
        steps=bound,
        created_at=now,
        updated_at=now,
    )


def test_replay_returns_cached_run_without_re_executing() -> None:
    workflow = _build_workflow((_build_step(0, "alpha"),))
    call_log: list[str] = []

    def executor(step: WorkflowStep, context: dict[str, Any]) -> StepResult:
        call_log.append(step.name)
        return StepResult(output={"echo": step.name})

    def resolver(step: WorkflowStep) -> Any:
        return executor

    store = InMemoryIdempotencyStore(ttl=timedelta(hours=24))
    runner = SequentialWorkflowRunner(resolver=resolver, idempotency_store=store)

    first = runner.run(workflow, triggered_by="user-1", idempotency_key="abc")
    second = runner.run(workflow, triggered_by="user-1", idempotency_key="abc")

    assert call_log == ["alpha"]
    assert first.id == second.id
    assert second.status is RunStatus.SUCCEEDED
    assert second.step_runs[0].output == {"echo": "alpha"}


def test_store_releases_keys_past_ttl() -> None:
    start = datetime(2026, 1, 13, 12, 0, tzinfo=timezone.utc)
    clock = _ManualClock(start)
    store = InMemoryIdempotencyStore(ttl=timedelta(minutes=5), clock=clock)

    workflow = _build_workflow((_build_step(0, "alpha"),))
    call_log: list[str] = []

    def executor(step: WorkflowStep, context: dict[str, Any]) -> StepResult:
        call_log.append(step.name)
        return StepResult(output={})

    def resolver(step: WorkflowStep) -> Any:
        return executor

    runner = SequentialWorkflowRunner(resolver=resolver, idempotency_store=store)

    runner.run(workflow, triggered_by="user-1", idempotency_key="key-x")
    assert call_log == ["alpha"]

    clock.advance(timedelta(minutes=5))

    runner.run(workflow, triggered_by="user-1", idempotency_key="key-x")
    assert call_log == ["alpha", "alpha"]


def test_failed_runs_are_not_cached() -> None:
    workflow = _build_workflow((_build_step(0, "boom"),))
    call_log: list[str] = []

    def executor(step: WorkflowStep, context: dict[str, Any]) -> StepResult:
        call_log.append(step.name)
        raise RuntimeError("transient failure")

    def resolver(step: WorkflowStep) -> Any:
        return executor

    store = InMemoryIdempotencyStore(ttl=timedelta(hours=1))
    runner = SequentialWorkflowRunner(resolver=resolver, idempotency_store=store)

    first = runner.run(workflow, triggered_by="user-1", idempotency_key="retry-me")
    second = runner.run(workflow, triggered_by="user-1", idempotency_key="retry-me")

    assert first.status is RunStatus.FAILED
    assert second.status is RunStatus.FAILED
    assert call_log == ["boom", "boom"]
    assert first.id != second.id
    assert store.get("retry-me") is None
    assert first.step_runs[0].status is StepStatus.FAILED


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))

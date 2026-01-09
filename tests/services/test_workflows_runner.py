"""Tests for the sequential workflow runner."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import pytest

from app.services.workflows.models import (
    RunStatus,
    StepStatus,
    Workflow,
    WorkflowStep,
)
from app.services.workflows.runner import SequentialWorkflowRunner


def _build_step(ordinal: int, name: str, action: str = "noop") -> WorkflowStep:
    return WorkflowStep(
        id=uuid4(),
        workflow_id=uuid4(),
        ordinal=ordinal,
        name=name,
        action=action,
        config={},
    )


def _build_workflow(steps: tuple[WorkflowStep, ...]) -> Workflow:
    now = datetime.now(tz=timezone.utc)
    workflow_id = uuid4()
    bound_steps = tuple(s.model_copy(update={"workflow_id": workflow_id}) for s in steps)
    return Workflow(
        id=workflow_id,
        account_id=uuid4(),
        name="test-workflow",
        description=None,
        steps=bound_steps,
        created_at=now,
        updated_at=now,
    )


def test_runner_executes_steps_in_order_and_records_outputs() -> None:
    step_a = _build_step(0, "alpha")
    step_b = _build_step(1, "beta")
    workflow = _build_workflow((step_a, step_b))
    call_log: list[str] = []

    def executor(step: WorkflowStep, context: dict[str, Any]) -> dict[str, Any]:
        call_log.append(step.name)
        return {"echoed": step.name, "context_outputs_seen": list(context["outputs"].keys())}

    def resolver(step: WorkflowStep) -> Any:
        return executor

    runner = SequentialWorkflowRunner(resolver=resolver)
    run = runner.run(workflow, triggered_by="test-user", input={"x": 1})

    assert call_log == ["alpha", "beta"]
    assert run.status is RunStatus.SUCCEEDED
    assert run.triggered_by == "test-user"
    assert run.input == {"x": 1}
    assert len(run.step_runs) == 2
    assert [sr.status for sr in run.step_runs] == [StepStatus.SUCCEEDED, StepStatus.SUCCEEDED]
    assert run.step_runs[0].output == {"echoed": "alpha", "context_outputs_seen": []}
    assert run.step_runs[1].output == {"echoed": "beta", "context_outputs_seen": ["alpha"]}
    assert run.started_at is not None
    assert run.finished_at is not None
    assert run.finished_at >= run.started_at


def test_runner_halts_on_step_failure_and_marks_subsequent_pending() -> None:
    step_a = _build_step(0, "alpha")
    step_b = _build_step(1, "boom")
    step_c = _build_step(2, "never_runs")
    workflow = _build_workflow((step_a, step_b, step_c))
    call_log: list[str] = []

    def executor(step: WorkflowStep, context: dict[str, Any]) -> dict[str, Any]:
        call_log.append(step.name)
        if step.name == "boom":
            raise RuntimeError("step exploded")
        return {"ok": True}

    def resolver(step: WorkflowStep) -> Any:
        return executor

    runner = SequentialWorkflowRunner(resolver=resolver)
    run = runner.run(workflow, triggered_by="test-user")

    assert call_log == ["alpha", "boom"]
    assert run.status is RunStatus.FAILED
    assert len(run.step_runs) == 3
    assert run.step_runs[0].status is StepStatus.SUCCEEDED
    assert run.step_runs[1].status is StepStatus.FAILED
    assert run.step_runs[1].error == "step exploded"
    assert run.step_runs[1].output is None
    assert run.step_runs[2].status is StepStatus.PENDING
    assert run.step_runs[2].started_at is None
    assert run.step_runs[2].finished_at is None


def test_runner_completes_workflow_with_no_steps() -> None:
    workflow = _build_workflow(())

    def resolver(step: WorkflowStep) -> Any:
        raise AssertionError("resolver should not be called for an empty workflow")

    runner = SequentialWorkflowRunner(resolver=resolver)
    run = runner.run(workflow, triggered_by="test-user")

    assert run.status is RunStatus.SUCCEEDED
    assert run.step_runs == ()
    assert run.started_at is not None
    assert run.finished_at is not None
    assert run.finished_at >= run.started_at


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))

"""Sequential workflow runner.

Executes a workflow's steps in declared order against a step resolver.
The runner is intentionally synchronous and single-threaded — concurrency
belongs in a later iteration once at least one consumer asks for it.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable
from uuid import UUID, uuid4

from .models import (
    RunStatus,
    StepStatus,
    Workflow,
    WorkflowRun,
    WorkflowStep,
    WorkflowStepRun,
)

StepCallable = Callable[[WorkflowStep, dict[str, Any]], dict[str, Any]]
StepResolverFn = Callable[[WorkflowStep], StepCallable]


def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


class SequentialWorkflowRunner:
    """Runs a workflow's steps end-to-end in ordinal order."""

    def __init__(self, resolver: StepResolverFn) -> None:
        self._resolver = resolver

    def run(
        self,
        workflow: Workflow,
        triggered_by: str,
        input: dict[str, Any] | None = None,
    ) -> WorkflowRun:
        run_id = uuid4()
        started_at = _now()
        ordered = sorted(workflow.steps, key=lambda s: s.ordinal)
        context: dict[str, Any] = {"input": dict(input or {}), "outputs": {}}
        step_runs: list[WorkflowStepRun] = []
        run_status = RunStatus.SUCCEEDED

        halted = False
        for step in ordered:
            if halted:
                step_runs.append(self._pending_step_run(run_id, step))
                continue
            step_run = self._execute_step(run_id, step, context)
            step_runs.append(step_run)
            if step_run.status is StepStatus.FAILED:
                halted = True
                run_status = RunStatus.FAILED

        finished_at = _now()
        return WorkflowRun(
            id=run_id,
            workflow_id=workflow.id,
            account_id=workflow.account_id,
            status=run_status,
            triggered_by=triggered_by,
            input=dict(input or {}),
            step_runs=tuple(step_runs),
            created_at=started_at,
            started_at=started_at,
            finished_at=finished_at,
        )

    def _execute_step(
        self,
        run_id: UUID,
        step: WorkflowStep,
        context: dict[str, Any],
    ) -> WorkflowStepRun:
        executor = self._resolver(step)
        started_at = _now()
        try:
            output = executor(step, context)
        except Exception as exc:
            return WorkflowStepRun(
                id=uuid4(),
                run_id=run_id,
                step_id=step.id,
                ordinal=step.ordinal,
                status=StepStatus.FAILED,
                started_at=started_at,
                finished_at=_now(),
                output=None,
                error=str(exc),
            )
        context["outputs"][step.name] = output
        return WorkflowStepRun(
            id=uuid4(),
            run_id=run_id,
            step_id=step.id,
            ordinal=step.ordinal,
            status=StepStatus.SUCCEEDED,
            started_at=started_at,
            finished_at=_now(),
            output=output,
            error=None,
        )

    def _pending_step_run(
        self, run_id: UUID, step: WorkflowStep
    ) -> WorkflowStepRun:
        return WorkflowStepRun(
            id=uuid4(),
            run_id=run_id,
            step_id=step.id,
            ordinal=step.ordinal,
            status=StepStatus.PENDING,
        )

"""HTTP routes for workflow create + run.

The route layer is intentionally thin — request validation and HTTP
translation only. Execution lives in `app.services.workflows.runner`.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field

from app.auth.api_key import api_key_auth
from app.models.api_key import ApiKey
from app.services.workflows.idempotency import (
    IdempotencyStore,
    InMemoryIdempotencyStore,
)
from app.services.workflows.models import Workflow, WorkflowRun, WorkflowStep
from app.services.workflows.runner import (
    SequentialWorkflowRunner,
    StepResolverFn,
    StepResult,
)


workflows_router = APIRouter(prefix="/workflows", tags=["workflows"])


_workflow_store: dict[UUID, Workflow] = {}


def get_workflow_store() -> dict[UUID, Workflow]:
    return _workflow_store


def _default_resolver(step: WorkflowStep) -> Any:
    def _execute(step: WorkflowStep, context: dict[str, Any]) -> StepResult:
        return StepResult(output={"action": step.action, "name": step.name})

    return _execute


def get_step_resolver() -> StepResolverFn:
    return _default_resolver


_default_idempotency_store: IdempotencyStore = InMemoryIdempotencyStore(
    ttl=timedelta(hours=24)
)


def get_idempotency_store() -> IdempotencyStore:
    return _default_idempotency_store


def get_runner(
    resolver: StepResolverFn = Depends(get_step_resolver),
    store: IdempotencyStore = Depends(get_idempotency_store),
) -> SequentialWorkflowRunner:
    return SequentialWorkflowRunner(resolver=resolver, idempotency_store=store)


class WorkflowStepIn(BaseModel):
    ordinal: int = Field(ge=0)
    name: str
    action: str
    config: dict[str, Any] = Field(default_factory=dict)


class WorkflowCreateIn(BaseModel):
    account_id: UUID
    name: str
    description: str | None = None
    steps: list[WorkflowStepIn] = Field(default_factory=list)


class WorkflowRunIn(BaseModel):
    triggered_by: str
    input: dict[str, Any] = Field(default_factory=dict)


@workflows_router.post("", status_code=status.HTTP_201_CREATED)
def create_workflow(
    payload: WorkflowCreateIn,
    store: dict[UUID, Workflow] = Depends(get_workflow_store),
) -> dict[str, Any]:
    now = datetime.now(tz=timezone.utc)
    workflow_id = uuid4()
    steps = tuple(
        WorkflowStep(
            id=uuid4(),
            workflow_id=workflow_id,
            ordinal=s.ordinal,
            name=s.name,
            action=s.action,
            config=s.config,
        )
        for s in payload.steps
    )
    workflow = Workflow(
        id=workflow_id,
        account_id=payload.account_id,
        name=payload.name,
        description=payload.description,
        steps=steps,
        created_at=now,
        updated_at=now,
    )
    store[workflow_id] = workflow
    return {
        "id": str(workflow.id),
        "account_id": str(workflow.account_id),
        "name": workflow.name,
        "description": workflow.description,
        "steps": [
            {
                "id": str(s.id),
                "ordinal": s.ordinal,
                "name": s.name,
                "action": s.action,
                "config": s.config,
            }
            for s in workflow.steps
        ],
    }


def _serialize_run(run: WorkflowRun) -> dict[str, Any]:
    return {
        "id": str(run.id),
        "workflow_id": str(run.workflow_id),
        "account_id": str(run.account_id),
        "status": run.status.value,
        "triggered_by": run.triggered_by,
        "input": run.input,
        "step_runs": [
            {
                "id": str(sr.id),
                "step_id": str(sr.step_id),
                "ordinal": sr.ordinal,
                "status": sr.status.value,
                "output": sr.output,
                "error": sr.error,
            }
            for sr in run.step_runs
        ],
    }


@workflows_router.post("/{workflow_id}/run")
def run_workflow(
    workflow_id: UUID,
    payload: WorkflowRunIn,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    store: dict[UUID, Workflow] = Depends(get_workflow_store),
    runner: SequentialWorkflowRunner = Depends(get_runner),
    caller: ApiKey = Depends(api_key_auth),
) -> dict[str, Any]:
    workflow = store.get(workflow_id)
    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="workflow not found",
        )
    run = runner.run(
        workflow,
        triggered_by=payload.triggered_by,
        input=payload.input,
        idempotency_key=idempotency_key,
    )
    return _serialize_run(run)

"""HTTP routes for workflow create + run.

The route layer is intentionally thin — request validation and HTTP
translation only. Execution lives in `app.services.workflows.runner`.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from app.services.workflows.models import Workflow, WorkflowStep


workflows_router = APIRouter(prefix="/workflows", tags=["workflows"])


_workflow_store: dict[UUID, Workflow] = {}


def get_workflow_store() -> dict[UUID, Workflow]:
    return _workflow_store


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

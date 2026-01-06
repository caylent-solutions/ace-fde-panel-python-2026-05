"""Pydantic schemas for workflow definitions, runs, and steps."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStep(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    workflow_id: UUID
    ordinal: int = Field(ge=0)
    name: str
    action: str
    config: dict[str, Any] = Field(default_factory=dict)


class Workflow(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    account_id: UUID
    name: str
    description: str | None = None
    steps: tuple[WorkflowStep, ...] = ()
    created_at: datetime
    updated_at: datetime


class WorkflowStepRun(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    run_id: UUID
    step_id: UUID
    ordinal: int = Field(ge=0)
    status: StepStatus = StepStatus.PENDING
    started_at: datetime | None = None
    finished_at: datetime | None = None
    output: dict[str, Any] | None = None
    error: str | None = None


class WorkflowRun(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    workflow_id: UUID
    account_id: UUID
    status: RunStatus = RunStatus.PENDING
    triggered_by: str
    input: dict[str, Any] = Field(default_factory=dict)
    step_runs: tuple[WorkflowStepRun, ...] = ()
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None

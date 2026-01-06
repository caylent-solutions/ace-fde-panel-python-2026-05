"""Protocol surface for workflow runner and step resolver.

Pinning the protocol surface here lets the implementation modules
land independently without a circular import between the runner and
the step resolver.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable
from uuid import UUID

from .models import Workflow, WorkflowRun, WorkflowStep, WorkflowStepRun


@runtime_checkable
class StepResolver(Protocol):
    """Resolves a step's action name to an executable callable."""

    def resolve(self, step: WorkflowStep) -> "StepExecutor": ...


class StepExecutor(Protocol):
    """Executes a single step against a run's input/context."""

    def __call__(
        self, step: WorkflowStep, context: dict[str, Any]
    ) -> dict[str, Any]: ...


@runtime_checkable
class WorkflowRunner(Protocol):
    """Orchestrates a workflow run end-to-end."""

    def start(
        self,
        workflow: Workflow,
        triggered_by: str,
        input: dict[str, Any],
    ) -> WorkflowRun: ...

    def advance(self, run_id: UUID) -> WorkflowStepRun: ...

    def cancel(self, run_id: UUID, reason: str) -> WorkflowRun: ...

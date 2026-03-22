import React from "react";
import type { WorkflowSummary } from "../hooks/useWorkflows";

export interface WorkflowListProps {
  workflows: ReadonlyArray<WorkflowSummary>;
  emptyMessage?: string;
}

export function WorkflowList({
  workflows,
  emptyMessage = "No workflows yet. Create your first one to get started.",
}: WorkflowListProps): JSX.Element {
  if (workflows.length === 0) {
    return (
      <p data-testid="workflow-list-empty" role="status">
        {emptyMessage}
      </p>
    );
  }

  return (
    <ul data-testid="workflow-list" aria-label="workflows">
      {workflows.map((workflow) => (
        <li key={workflow.id} data-testid="workflow-list-item">
          <strong>{workflow.name}</strong>
          {workflow.description !== null && <p>{workflow.description}</p>}
          <small>{workflow.step_count} steps</small>
        </li>
      ))}
    </ul>
  );
}

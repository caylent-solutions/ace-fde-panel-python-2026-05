import React from "react";

export interface WorkflowStepView {
  id: string;
  ordinal: number;
  name: string;
  action: string;
}

export interface StepListProps {
  steps: ReadonlyArray<WorkflowStepView>;
  emptyMessage?: string;
}

export function StepList({
  steps,
  emptyMessage = "This workflow has no steps yet.",
}: StepListProps): JSX.Element {
  if (steps.length === 0) {
    return (
      <p data-testid="step-list-empty" role="status">
        {emptyMessage}
      </p>
    );
  }

  return (
    <ol data-testid="step-list" aria-label="workflow steps">
      {steps.map((step) => (
        <li key={step.id} data-testid="step-list-item">
          <span data-testid="step-ordinal">{step.ordinal}</span>
          <strong>{step.name}</strong>
          <code>{step.action}</code>
        </li>
      ))}
    </ol>
  );
}

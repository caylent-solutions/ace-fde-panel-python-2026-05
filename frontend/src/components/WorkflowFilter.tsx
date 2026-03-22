import React from "react";

export interface WorkflowFilterProps {
  query: string;
  onQueryChange: (next: string) => void;
}

export function WorkflowFilter({
  query,
  onQueryChange,
}: WorkflowFilterProps): JSX.Element {
  return (
    <label>
      Filter
      <input
        type="search"
        data-testid="workflow-filter-input"
        placeholder="Filter workflows by name…"
        value={query}
        onChange={(event) => onQueryChange(event.target.value)}
      />
    </label>
  );
}

import React, { useMemo, useState } from "react";
import { WorkflowFilter } from "../../components/WorkflowFilter";
import { WorkflowList } from "../../components/WorkflowList";
import { useWorkflows, type WorkflowSummary } from "../../hooks/useWorkflows";

function filterWorkflows(
  workflows: ReadonlyArray<WorkflowSummary>,
  query: string,
): ReadonlyArray<WorkflowSummary> {
  const trimmed = query.trim().toLowerCase();
  if (trimmed.length === 0) {
    return workflows;
  }
  return workflows.filter((workflow) =>
    workflow.name.toLowerCase().includes(trimmed),
  );
}

export default function WorkflowsIndexPage(): JSX.Element {
  const state = useWorkflows();
  const [query, setQuery] = useState<string>("");

  const visibleWorkflows = useMemo(() => {
    if (state.status !== "data") {
      return [];
    }
    return filterWorkflows(state.workflows, query);
  }, [state, query]);

  return (
    <main>
      <header>
        <h1>Workflows</h1>
      </header>

      {state.status === "loading" && (
        <p data-testid="workflows-loading" role="status">
          Loading workflows…
        </p>
      )}

      {state.status === "error" && (
        <p data-testid="workflows-error" role="alert">
          Could not load workflows: {state.error.message}
        </p>
      )}

      {state.status === "data" && (
        <>
          <WorkflowFilter query={query} onQueryChange={setQuery} />
          <WorkflowList workflows={visibleWorkflows} />
        </>
      )}
    </main>
  );
}

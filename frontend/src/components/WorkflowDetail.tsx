import React, { useEffect, useState } from "react";
import { StepList, type WorkflowStepView } from "./StepList";

export interface WorkflowDetailData {
  id: string;
  name: string;
  description: string | null;
  account_id: string;
  steps: ReadonlyArray<WorkflowStepView>;
  updated_at: string;
}

export type WorkflowDetailState =
  | { status: "loading" }
  | { status: "not_found" }
  | { status: "error"; error: Error }
  | { status: "data"; workflow: WorkflowDetailData };

export interface WorkflowDetailProps {
  workflowId: string;
  fetcher?: (input: RequestInfo, init?: RequestInit) => Promise<Response>;
  endpointBase?: string;
}

const DEFAULT_ENDPOINT = "/api/workflows";

export function WorkflowDetail({
  workflowId,
  fetcher = fetch,
  endpointBase = DEFAULT_ENDPOINT,
}: WorkflowDetailProps): JSX.Element {
  const [state, setState] = useState<WorkflowDetailState>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;

    async function load(): Promise<void> {
      try {
        const response = await fetcher(`${endpointBase}/${workflowId}`);
        if (response.status === 404) {
          if (!cancelled) {
            setState({ status: "not_found" });
          }
          return;
        }
        if (!response.ok) {
          throw new Error(`workflow fetch failed: ${response.status}`);
        }
        const body = (await response.json()) as WorkflowDetailData;
        if (!cancelled) {
          setState({ status: "data", workflow: body });
        }
      } catch (err) {
        if (!cancelled) {
          setState({
            status: "error",
            error: err instanceof Error ? err : new Error(String(err)),
          });
        }
      }
    }

    setState({ status: "loading" });
    void load();

    return () => {
      cancelled = true;
    };
  }, [fetcher, endpointBase, workflowId]);

  if (state.status === "loading") {
    return (
      <p data-testid="workflow-detail-loading" role="status">
        Loading workflow…
      </p>
    );
  }

  if (state.status === "not_found") {
    return (
      <section data-testid="workflow-detail-not-found">
        <h1>Workflow not found</h1>
        <p>The workflow you requested does not exist or has been deleted.</p>
      </section>
    );
  }

  if (state.status === "error") {
    return (
      <p data-testid="workflow-detail-error" role="alert">
        Could not load workflow: {state.error.message}
      </p>
    );
  }

  const { workflow } = state;
  return (
    <article data-testid="workflow-detail">
      <header>
        <h1>{workflow.name}</h1>
        {workflow.description !== null && <p>{workflow.description}</p>}
        <small>Last updated {workflow.updated_at}</small>
      </header>
      <section>
        <h2>Steps</h2>
        <StepList steps={workflow.steps} />
      </section>
    </article>
  );
}

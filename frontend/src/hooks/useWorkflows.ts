import { useEffect, useState } from "react";

export interface WorkflowSummary {
  id: string;
  name: string;
  description: string | null;
  step_count: number;
  updated_at: string;
}

export type WorkflowsState =
  | { status: "loading" }
  | { status: "error"; error: Error }
  | { status: "data"; workflows: ReadonlyArray<WorkflowSummary> };

export interface UseWorkflowsOptions {
  fetcher?: (input: RequestInfo, init?: RequestInit) => Promise<Response>;
  endpoint?: string;
}

const DEFAULT_ENDPOINT = "/api/workflows";

export function useWorkflows(options: UseWorkflowsOptions = {}): WorkflowsState {
  const { fetcher = fetch, endpoint = DEFAULT_ENDPOINT } = options;
  const [state, setState] = useState<WorkflowsState>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;

    async function load(): Promise<void> {
      try {
        const response = await fetcher(endpoint);
        if (!response.ok) {
          throw new Error(`workflows fetch failed: ${response.status}`);
        }
        const body = (await response.json()) as ReadonlyArray<WorkflowSummary>;
        if (!cancelled) {
          setState({ status: "data", workflows: body });
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
  }, [fetcher, endpoint]);

  return state;
}

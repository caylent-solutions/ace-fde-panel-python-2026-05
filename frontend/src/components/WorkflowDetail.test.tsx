import React from "react";
import { describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";

import { WorkflowDetail, type WorkflowDetailData } from "./WorkflowDetail";

function jsonResponse(body: unknown, init: ResponseInit = {}): Response {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { "Content-Type": "application/json" },
    ...init,
  });
}

function notFoundResponse(): Response {
  return new Response("not found", { status: 404 });
}

function serverErrorResponse(): Response {
  return new Response("boom", { status: 500 });
}

const SAMPLE_WORKFLOW: WorkflowDetailData = {
  id: "wf_42",
  name: "Daily rollup",
  description: "Aggregates yesterday's events",
  account_id: "acct_1",
  steps: [
    { id: "s_0", ordinal: 0, name: "Fetch", action: "http.get" },
    { id: "s_1", ordinal: 1, name: "Notify", action: "slack.post" },
  ],
  updated_at: "2026-03-30T17:00:00Z",
};

describe("WorkflowDetail", () => {
  it("renders a not-found page when the API returns 404", async () => {
    const fetcher = vi.fn().mockResolvedValue(notFoundResponse());

    render(<WorkflowDetail workflowId="wf_missing" fetcher={fetcher} />);

    await waitFor(() => {
      expect(screen.getByTestId("workflow-detail-not-found")).toBeInTheDocument();
    });
    expect(screen.getByRole("heading", { name: /not found/i })).toBeInTheDocument();
    expect(screen.queryByTestId("workflow-detail-error")).toBeNull();
    expect(fetcher).toHaveBeenCalledWith("/api/workflows/wf_missing");
  });

  it("renders the error state when the API returns a non-404 failure", async () => {
    const fetcher = vi.fn().mockResolvedValue(serverErrorResponse());

    render(<WorkflowDetail workflowId="wf_x" fetcher={fetcher} />);

    await waitFor(() => {
      expect(screen.getByTestId("workflow-detail-error")).toBeInTheDocument();
    });
    expect(screen.getByRole("alert")).toHaveTextContent(/500/);
    expect(screen.queryByTestId("workflow-detail-not-found")).toBeNull();
  });

  it("renders the workflow detail with steps on success", async () => {
    const fetcher = vi.fn().mockResolvedValue(jsonResponse(SAMPLE_WORKFLOW));

    render(<WorkflowDetail workflowId="wf_42" fetcher={fetcher} />);

    await waitFor(() => {
      expect(screen.getByTestId("workflow-detail")).toBeInTheDocument();
    });
    expect(screen.getByRole("heading", { name: "Daily rollup" })).toBeInTheDocument();
    expect(screen.getByText(/Aggregates yesterday/)).toBeInTheDocument();
    expect(screen.getAllByTestId("step-list-item")).toHaveLength(2);
  });

  it("shows the loading state before the fetch resolves", () => {
    const fetcher = vi.fn().mockImplementation(() => new Promise(() => undefined));

    render(<WorkflowDetail workflowId="wf_pending" fetcher={fetcher} />);

    expect(screen.getByTestId("workflow-detail-loading")).toBeInTheDocument();
  });

  it("renders the network-error state when the fetcher rejects", async () => {
    const fetcher = vi.fn().mockRejectedValue(new Error("offline"));

    render(<WorkflowDetail workflowId="wf_x" fetcher={fetcher} />);

    await waitFor(() => {
      expect(screen.getByTestId("workflow-detail-error")).toBeInTheDocument();
    });
    expect(screen.getByRole("alert")).toHaveTextContent("offline");
  });
});

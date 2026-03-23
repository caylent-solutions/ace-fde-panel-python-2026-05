import React from "react";
import { describe, expect, it } from "vitest";
import { render, screen, within } from "@testing-library/react";

import { WorkflowList } from "./WorkflowList";
import type { WorkflowSummary } from "../hooks/useWorkflows";

function fixture(overrides: Partial<WorkflowSummary>): WorkflowSummary {
  return {
    id: "wf_1",
    name: "Daily rollup",
    description: "Aggregates yesterday's events",
    step_count: 3,
    updated_at: "2026-03-22T10:00:00Z",
    ...overrides,
  };
}

describe("WorkflowList", () => {
  it("renders the empty-state message when given no workflows", () => {
    render(<WorkflowList workflows={[]} />);

    const empty = screen.getByTestId("workflow-list-empty");
    expect(empty).toBeInTheDocument();
    expect(empty).toHaveTextContent(/No workflows yet/i);
    expect(screen.queryByTestId("workflow-list")).toBeNull();
  });

  it("uses the custom emptyMessage when provided", () => {
    render(<WorkflowList workflows={[]} emptyMessage="Nothing to show." />);

    expect(screen.getByTestId("workflow-list-empty")).toHaveTextContent(
      "Nothing to show.",
    );
  });

  it("renders a list item per workflow with name and step count", () => {
    const workflows: ReadonlyArray<WorkflowSummary> = [
      fixture({ id: "wf_a", name: "Alpha", step_count: 2 }),
      fixture({ id: "wf_b", name: "Beta", step_count: 5, description: null }),
    ];
    render(<WorkflowList workflows={workflows} />);

    const items = screen.getAllByTestId("workflow-list-item");
    expect(items).toHaveLength(2);
    expect(within(items[0]).getByText("Alpha")).toBeInTheDocument();
    expect(within(items[0]).getByText(/2 steps/)).toBeInTheDocument();
    expect(within(items[1]).getByText("Beta")).toBeInTheDocument();
    expect(within(items[1]).getByText(/5 steps/)).toBeInTheDocument();
  });

  it("omits the description paragraph when description is null", () => {
    const workflows: ReadonlyArray<WorkflowSummary> = [
      fixture({ id: "wf_x", name: "Bare", description: null }),
    ];
    const { container } = render(<WorkflowList workflows={workflows} />);

    expect(container.querySelectorAll("li > p")).toHaveLength(0);
  });

  it("renders empty state — not a loading spinner — for an empty array (regression)", () => {
    render(<WorkflowList workflows={[]} />);

    expect(screen.queryByText(/loading/i)).toBeNull();
    expect(screen.getByTestId("workflow-list-empty")).toBeInTheDocument();
  });
});

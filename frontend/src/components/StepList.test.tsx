import React from "react";
import { describe, expect, it } from "vitest";
import { render, screen, within } from "@testing-library/react";

import { StepList, type WorkflowStepView } from "./StepList";

function fixture(overrides: Partial<WorkflowStepView>): WorkflowStepView {
  return {
    id: "step_1",
    ordinal: 0,
    name: "Fetch source data",
    action: "http.get",
    ...overrides,
  };
}

describe("StepList", () => {
  it("renders the empty-state message when given no steps", () => {
    render(<StepList steps={[]} />);

    const empty = screen.getByTestId("step-list-empty");
    expect(empty).toBeInTheDocument();
    expect(empty).toHaveTextContent(/no steps/i);
    expect(screen.queryByTestId("step-list")).toBeNull();
  });

  it("uses the custom emptyMessage when provided", () => {
    render(<StepList steps={[]} emptyMessage="Add a step to get started." />);

    expect(screen.getByTestId("step-list-empty")).toHaveTextContent(
      "Add a step to get started.",
    );
  });

  it("renders steps in the order provided by the API, not sorted client-side", () => {
    const steps: ReadonlyArray<WorkflowStepView> = [
      fixture({ id: "s_two", ordinal: 2, name: "Send email" }),
      fixture({ id: "s_zero", ordinal: 0, name: "Lookup record" }),
      fixture({ id: "s_one", ordinal: 1, name: "Transform payload" }),
    ];
    render(<StepList steps={steps} />);

    const items = screen.getAllByTestId("step-list-item");
    expect(items).toHaveLength(3);
    expect(within(items[0]).getByText("Send email")).toBeInTheDocument();
    expect(within(items[1]).getByText("Lookup record")).toBeInTheDocument();
    expect(within(items[2]).getByText("Transform payload")).toBeInTheDocument();
  });

  it("renders each step's ordinal and action", () => {
    const steps: ReadonlyArray<WorkflowStepView> = [
      fixture({ id: "s_a", ordinal: 0, name: "alpha", action: "http.get" }),
      fixture({ id: "s_b", ordinal: 1, name: "beta", action: "slack.post" }),
    ];
    render(<StepList steps={steps} />);

    const items = screen.getAllByTestId("step-list-item");
    expect(within(items[0]).getByTestId("step-ordinal")).toHaveTextContent("0");
    expect(within(items[0]).getByText("http.get")).toBeInTheDocument();
    expect(within(items[1]).getByTestId("step-ordinal")).toHaveTextContent("1");
    expect(within(items[1]).getByText("slack.post")).toBeInTheDocument();
  });
});

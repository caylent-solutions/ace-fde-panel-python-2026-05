import React from "react";
import { WorkflowDetail } from "../../components/WorkflowDetail";

export interface WorkflowDetailPageProps {
  workflowId: string;
}

export default function WorkflowDetailPage({
  workflowId,
}: WorkflowDetailPageProps): JSX.Element {
  return (
    <main>
      <nav aria-label="breadcrumb">
        <a href="/workflows">Workflows</a>
      </nav>
      <WorkflowDetail workflowId={workflowId} />
    </main>
  );
}

import React, { useState } from "react";
import { ApiKeyForm } from "../../components/ApiKeyForm";

export default function NewApiKeyPage() {
  const [created, setCreated] = useState<any>(null);

  if (created) {
    return (
      <div>
        <h1>Key created</h1>
        <p>Copy your key now — it won't be shown again.</p>
        <code>{created.key}</code>
        <br />
        <a href="/api-keys">Back to API keys</a>
      </div>
    );
  }

  return (
    <div>
      <h1>Create API Key</h1>
      <ApiKeyForm onCreated={setCreated} />
    </div>
  );
}

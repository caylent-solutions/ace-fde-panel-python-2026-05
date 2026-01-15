import React, { useState } from "react";

interface Props {
  onCreated: (key: any) => void;
}

export function ApiKeyForm({ onCreated }: Props) {
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) {
      setError("Name is required");
      return;
    }
    fetch("/api/api-keys", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    })
      .then((r) => r.json())
      .then((data) => onCreated(data));
  }

  return (
    <form onSubmit={handleSubmit}>
      <label>
        Key name
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      </label>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <button type="submit">Create</button>
    </form>
  );
}

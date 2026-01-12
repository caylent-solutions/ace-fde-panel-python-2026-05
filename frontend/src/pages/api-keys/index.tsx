import React, { useEffect, useState } from "react";
import { ApiKeyRow } from "../../components/ApiKeyRow";

export default function ApiKeysPage() {
  const [keys, setKeys] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/api-keys")
      .then((r) => r.json())
      .then((data) => {
        setKeys(data);
        setLoading(false);
      });
  }, []);

  function handleRevoke(id: string) {
    fetch(`/api/api-keys/${id}`, { method: "DELETE" }).then(() => {
      setKeys(keys.filter((k) => k.id !== id));
    });
  }

  if (loading) return <p>Loading...</p>;

  return (
    <div>
      <h1>API Keys</h1>
      <a href="/api-keys/new">Create new key</a>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Key</th>
            <th>Created</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {keys.map((k) => (
            <ApiKeyRow key={k.id} apiKey={k} onRevoke={handleRevoke} />
          ))}
        </tbody>
      </table>
    </div>
  );
}

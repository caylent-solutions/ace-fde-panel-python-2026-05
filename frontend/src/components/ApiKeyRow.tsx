import React from "react";

interface ApiKey {
  id: string;
  name: string;
  prefix: string;
  created_at: string;
}

interface Props {
  apiKey: ApiKey;
  onRevoke: (id: string) => void;
}

export function ApiKeyRow({ apiKey, onRevoke }: Props) {
  return (
    <tr>
      <td>{apiKey.name}</td>
      <td>
        <code>{apiKey.prefix}...</code>
      </td>
      <td>{apiKey.created_at}</td>
      <td>
        <button onClick={() => onRevoke(apiKey.id)} data-testid="revoke-btn">
          Revoke
        </button>
      </td>
    </tr>
  );
}

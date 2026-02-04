import React from "react";

interface SettingsSection {
  title: string;
  content: React.ReactNode;
}

function Section({ title, content }: SettingsSection) {
  return (
    <section style={{ marginBottom: "2rem" }}>
      <h2>{title}</h2>
      {content}
    </section>
  );
}

export default function SettingsPage() {
  return (
    <div>
      <h1>Settings</h1>
      <Section
        title="Account"
        content={
          <div>
            {/* TODO: name, email, password change */}
            <p>Account settings coming soon.</p>
          </div>
        }
      />
      <Section
        title="Notifications"
        content={
          <div>
            {/* TODO: email notification preferences */}
            <p>Notification preferences coming soon.</p>
          </div>
        }
      />
      <Section
        title="Integrations"
        content={
          <div>
            {/* TODO: link to integrations page */}
            <p>Manage integrations coming soon.</p>
          </div>
        }
      />
    </div>
  );
}

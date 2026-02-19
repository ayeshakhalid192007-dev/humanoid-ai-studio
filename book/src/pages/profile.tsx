import React from "react";
import Layout from "@theme/Layout";
import Link from "@docusaurus/Link";

export default function ProfilePage(): JSX.Element {
  return (
    <Layout title="Profile" description="Your Profile">
      <main style={{ maxWidth: 600, margin: "4rem auto", padding: "0 1rem", textAlign: "center" }}>
        <h1>Your Profile</h1>
        <p style={{ fontSize: "1.2rem", color: "var(--ifm-color-emphasis-600)", marginBottom: "2rem" }}>
          Coming Soon
        </p>
        <p>Profile management features are under development.</p>
        <Link to="/dashboard" style={{ display: "inline-block", marginTop: "1.5rem" }}>
          &larr; Back to Dashboard
        </Link>
      </main>
    </Layout>
  );
}

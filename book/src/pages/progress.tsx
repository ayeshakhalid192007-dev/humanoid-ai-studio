import React from "react";
import Link from "@docusaurus/Link";
import { AppLayout } from "../components/Layout/AppLayout";
import ErrorBoundary from "../components/ErrorBoundary";

export default function ProgressPage(): JSX.Element {
  return (
    <AppLayout title="Progress" description="Progress Tracking" background="default">
      <ErrorBoundary>
        <div style={{ maxWidth: 600, margin: "4rem auto", padding: "0 1rem", textAlign: "center" }}>
          <h1>Progress Tracking</h1>
          <p style={{ fontSize: "1.2rem", color: "var(--ifm-color-emphasis-600)", marginBottom: "2rem" }}>
            Coming Soon
          </p>
          <p>Progress tracking features are under development.</p>
          <Link to="/dashboard" style={{ display: "inline-block", marginTop: "1.5rem" }}>
            &larr; Back to Dashboard
          </Link>
        </div>
      </ErrorBoundary>
    </AppLayout>
  );
}

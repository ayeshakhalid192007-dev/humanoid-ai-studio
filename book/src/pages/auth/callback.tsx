/**
 * OAuth Callback Page — /auth/callback
 *
 * Handles the redirect from the auth server after the user authenticates.
 * Flow:
 *   1. Extract `code` and `state` from URL params
 *   2. Validate CSRF state
 *   3. Retrieve PKCE code_verifier from sessionStorage
 *   4. Exchange code for tokens (access + refresh)
 *   5. Store tokens in localStorage
 *   6. Redirect to the originally requested route (or /dashboard)
 */

import React from "react";
import Layout from "@theme/Layout";
import BrowserOnly from "@docusaurus/BrowserOnly";

function OAuthCallbackContent() {
  const { useHistory, useLocation } = require("@docusaurus/router");
  const { useAuth } = require("../../context/AuthContext");

  const history = useHistory();
  const location = useLocation();
  const { handleOAuthCallback } = useAuth();

  const [status, setStatus] = React.useState<"processing" | "error">("processing");
  const [errorMessage, setErrorMessage] = React.useState("");

  // Guard against running the callback exchange twice (e.g. StrictMode double-invoke
  // or component re-mount). The auth code is single-use — a second exchange would fail.
  const processed = React.useRef(false);

  React.useEffect(() => {
    if (processed.current) return;
    processed.current = true;

    async function processCallback() {
      const params = new URLSearchParams(location.search);
      const code = params.get("code");
      const state = params.get("state");
      const error = params.get("error");

      if (error) {
        // GitHub returns no_email when the user's email is set to private
        const friendlyMessage = error === "no_email"
          ? "We couldn't retrieve your email from GitHub. Please make your GitHub email public, or use email/password sign-up."
          : `Authorization error: ${params.get("error_description") ?? error}`;
        setErrorMessage(friendlyMessage);
        setStatus("error");
        return;
      }

      if (!code || !state) {
        setErrorMessage("Missing authorization code or state parameter.");
        setStatus("error");
        return;
      }

      const result = await handleOAuthCallback(code, state);

      if (result.success) {
        const redirectPath = sessionStorage.getItem("auth_redirect") || "/dashboard";
        sessionStorage.removeItem("auth_redirect");
        history.replace(redirectPath);
      } else {
        setErrorMessage(result.error ?? "Authentication failed. Please try again.");
        setStatus("error");
      }
    }

    processCallback();
  }, [handleOAuthCallback, history, location.search]);

  if (status === "error") {
    return (
      <div style={{ padding: "2rem", textAlign: "center" }}>
        <h2>Authentication Failed</h2>
        <p style={{ color: "var(--ifm-color-danger)" }}>{errorMessage}</p>
        <button
          onClick={() => history.replace("/auth/login")}
          style={{ marginTop: "1rem", padding: "0.5rem 1.5rem", cursor: "pointer" }}
        >
          Back to Login
        </button>
      </div>
    );
  }

  return (
    <div style={{ padding: "2rem", textAlign: "center" }}>
      <p>Completing sign-in…</p>
    </div>
  );
}

export default function OAuthCallbackPage(): JSX.Element {
  return (
    <Layout title="Signing in…" description="Completing authentication">
      <BrowserOnly fallback={<div style={{ padding: "2rem", textAlign: "center" }}>Signing in…</div>}>
        {() => <OAuthCallbackContent />}
      </BrowserOnly>
    </Layout>
  );
}

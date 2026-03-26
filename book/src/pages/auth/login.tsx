/**
 * Login Page
 *
 * Standalone login page for returning users.
 */

import React from "react";
import Layout from "@theme/Layout";
import BrowserOnly from "@docusaurus/BrowserOnly";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import styles from "../../components/Auth/Auth.module.css";

function LoginPageContent() {
  const { useAuth } = require("../../context/AuthContext");
  const { LoginForm } = require("../../components/Auth");
  const { siteConfig } = useDocusaurusContext();

  const { isAuthenticated, isLoading } = useAuth();

  // history.push() from @docusaurus/router does not apply basename on GitHub Pages.
  // Use window.location with siteConfig.baseUrl instead.
  const navigate = (path: string) => {
    const base = (siteConfig.baseUrl || "/").replace(/\/$/, "");
    window.location.replace(base + (path.startsWith("/") ? path : "/" + path));
  };

  React.useEffect(() => {
    if (!isLoading && isAuthenticated) {
      navigate("/dashboard");
    }
  }, [isAuthenticated, isLoading]);

  const handleSuccess = () => {
    const redirectPath = sessionStorage.getItem("auth_redirect");
    sessionStorage.removeItem("auth_redirect");
    navigate(redirectPath || "/dashboard");
  };

  const handleSwitchToSignUp = () => {
    navigate("/auth/signup");
  };

  return (
    <div className={styles.authPage}>
      <div className={styles.authContainer}>
        <LoginForm
          onSuccess={handleSuccess}
          onSwitchToSignUp={handleSwitchToSignUp}
        />
      </div>
    </div>
  );
}

export default function LoginPage(): JSX.Element {
  return (
    <Layout title="Sign In" description="Sign in to Physical AI Platform">
      <BrowserOnly fallback={<div className={styles.authPage} />}>
        {() => <LoginPageContent />}
      </BrowserOnly>
    </Layout>
  );
}

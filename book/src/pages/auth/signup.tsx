/**
 * Sign Up Page
 *
 * Default entry point for unauthenticated users.
 * Collects account info + background profile in one step.
 */

import React from "react";
import Layout from "@theme/Layout";
import BrowserOnly from "@docusaurus/BrowserOnly";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import styles from "../../components/Auth/Auth.module.css";

function SignUpPageContent() {
  const { useAuth } = require("../../context/AuthContext");
  const { SignUpForm } = require("../../components/Auth");
  const { siteConfig } = useDocusaurusContext();

  const { isAuthenticated, isLoading } = useAuth();

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

  const handleSwitchToLogin = () => {
    navigate("/auth/login");
  };

  return (
    <div className={styles.authPage}>
      <div className={styles.authContainerWide}>
        <SignUpForm onSuccess={handleSuccess} onSwitchToLogin={handleSwitchToLogin} />
      </div>
    </div>
  );
}

export default function SignUpPage(): JSX.Element {
  return (
    <Layout title="Sign Up" description="Create an account on Physical AI Platform">
      <BrowserOnly fallback={<div className={styles.authPage} />}>
        {() => <SignUpPageContent />}
      </BrowserOnly>
    </Layout>
  );
}

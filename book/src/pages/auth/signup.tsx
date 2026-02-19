/**
 * Sign Up Page
 *
 * Default entry point for unauthenticated users.
 * Collects account info + background profile in one step.
 */

import React from "react";
import Layout from "@theme/Layout";
import BrowserOnly from "@docusaurus/BrowserOnly";
import styles from "../../components/Auth/Auth.module.css";

function SignUpPageContent() {
  const { useHistory } = require("@docusaurus/router");
  const { useAuth } = require("../../context/AuthContext");
  const { SignUpForm } = require("../../components/Auth");

  const { isAuthenticated, isLoading } = useAuth();
  const history = useHistory();

  React.useEffect(() => {
    if (!isLoading && isAuthenticated) {
      history.push("/dashboard");
    }
  }, [isAuthenticated, isLoading, history]);

  const handleSuccess = () => {
    const redirectPath = sessionStorage.getItem("auth_redirect");
    sessionStorage.removeItem("auth_redirect");
    history.push(redirectPath || "/dashboard");
  };

  const handleSwitchToLogin = () => {
    history.push("/auth/login");
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

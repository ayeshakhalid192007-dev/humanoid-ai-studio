/**
 * Login Page
 *
 * Standalone login page for returning users.
 */

import React from "react";
import Layout from "@theme/Layout";
import BrowserOnly from "@docusaurus/BrowserOnly";
import styles from "../../components/Auth/Auth.module.css";

function LoginPageContent() {
  const { useHistory } = require("@docusaurus/router");
  const { useAuth } = require("../../context/AuthContext");
  const { LoginForm } = require("../../components/Auth");

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

  const handleSwitchToSignUp = () => {
    history.push("/auth/signup");
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

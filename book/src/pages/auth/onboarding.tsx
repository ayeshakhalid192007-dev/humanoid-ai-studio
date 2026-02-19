/**
 * Onboarding Page
 *
 * Post-signup page for collecting user background info.
 */

import React from "react";
import Layout from "@theme/Layout";
import BrowserOnly from "@docusaurus/BrowserOnly";
import styles from "../../components/Auth/Auth.module.css";

function OnboardingPageContent() {
  const { useHistory } = require("@docusaurus/router");
  const { useAuth } = require("../../context/AuthContext");
  const { OnboardingForm } = require("../../components/Auth");

  const { isAuthenticated, user, isLoading } = useAuth();
  const history = useHistory();

  React.useEffect(() => {
    if (isLoading) return;

    if (!isAuthenticated) {
      history.push("/auth/login");
      return;
    }

    if (user?.onboardingCompleted) {
      history.push("/dashboard");
      return;
    }
  }, [isAuthenticated, user, isLoading, history]);

  const handleComplete = () => {
    history.push("/dashboard");
  };

  if (isLoading) {
    return (
      <div className={styles.authPage}>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className={styles.authPage}>
      <div className={styles.authContainer}>
        <OnboardingForm onComplete={handleComplete} />
      </div>
    </div>
  );
}

export default function OnboardingPage(): JSX.Element {
  return (
    <Layout title="Onboarding" description="Set up your profile">
      <BrowserOnly fallback={<div className={styles.authPage} />}>
        {() => <OnboardingPageContent />}
      </BrowserOnly>
    </Layout>
  );
}

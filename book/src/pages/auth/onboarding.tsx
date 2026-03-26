/**
 * Onboarding Page
 *
 * Post-signup page for collecting user background info.
 */

import React from "react";
import Layout from "@theme/Layout";
import BrowserOnly from "@docusaurus/BrowserOnly";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import styles from "../../components/Auth/Auth.module.css";

function OnboardingPageContent() {
  const { useAuth } = require("../../context/AuthContext");
  const { OnboardingForm } = require("../../components/Auth");
  const { siteConfig } = useDocusaurusContext();

  const { isAuthenticated, user, isLoading } = useAuth();

  const navigate = (path: string) => {
    const base = (siteConfig.baseUrl || "/").replace(/\/$/, "");
    window.location.replace(base + (path.startsWith("/") ? path : "/" + path));
  };

  React.useEffect(() => {
    if (isLoading) return;
    if (!isAuthenticated) { navigate("/auth/login"); return; }
    if (user?.onboardingCompleted) { navigate("/dashboard"); return; }
  }, [isAuthenticated, user, isLoading]);

  const handleComplete = () => {
    navigate("/dashboard");
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

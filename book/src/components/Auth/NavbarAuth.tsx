/**
 * Navbar Auth Component
 *
 * Shows login button or user menu in navbar based on auth state.
 * Wrapped in BrowserOnly to prevent SSR errors.
 */

import React, { useState } from "react";
import BrowserOnly from "@docusaurus/BrowserOnly";
import styles from "./Auth.module.css";

function NavbarAuthInner() {
  const { useAuth } = require("../../context/AuthContext");
  const { AuthModal } = require("./AuthModal");
  const { UserMenu } = require("./UserMenu");

  const { isAuthenticated, isLoading } = useAuth();
  const [showModal, setShowModal] = useState(false);

  if (isLoading) {
    return (
      <button className={styles.navbarAuthButton} disabled>
        Loading...
      </button>
    );
  }

  if (isAuthenticated) {
    return <UserMenu />;
  }

  return (
    <>
      <button
        className={styles.navbarAuthButton}
        onClick={() => setShowModal(true)}
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M8 8C9.65685 8 11 6.65685 11 5C11 3.34315 9.65685 2 8 2C6.34315 2 5 3.34315 5 5C5 6.65685 6.34315 8 8 8Z"
            fill="currentColor"
          />
          <path
            d="M8 9C5.33 9 3 10.34 3 12V14H13V12C13 10.34 10.67 9 8 9Z"
            fill="currentColor"
          />
        </svg>
        Sign In
      </button>

      <AuthModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        initialView="login"
      />
    </>
  );
}

export function NavbarAuth() {
  return (
    <BrowserOnly fallback={<div className={styles.navbarAuthButton} style={{ width: 80, minHeight: 40 }} />}>
      {() => <NavbarAuthInner />}
    </BrowserOnly>
  );
}

export default NavbarAuth;

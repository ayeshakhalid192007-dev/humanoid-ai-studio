/**
 * Navbar Auth Component
 *
 * Shows login button or user menu in navbar based on auth state.
 * Wrapped in BrowserOnly to prevent SSR errors.
 */

import React, { useState } from "react";
import BrowserOnly from "@docusaurus/BrowserOnly";
import styles from "./Auth.module.css";
import { useAuth } from "../../context/AuthContext";
import { AuthModal } from "./AuthModal";
import { UserMenu } from "./UserMenu";

function NavbarAuthInner() {

  const { isAuthenticated, isLoading } = useAuth();
  const [showModal, setShowModal] = useState(false);

  if (isLoading) {
    return (
      <button className="navbar-auth-button" disabled>
        Loading...
      </button>
    );
  }

  if (isAuthenticated) {
    return <UserMenu />;
  }

  return (
    <>
      <div className="relative group">
        <button
          className="navbar-auth-button group-hover:bg-white/10 transition-all duration-300"
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

        {/* Tooltip for bonus features */}
        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
          <div className="bg-blue-600 text-white text-xs px-3 py-2 rounded-lg whitespace-nowrap animate-fadeIn">
            Unlock Bonus Features!
            <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-blue-600"></div>
          </div>
        </div>
      </div>

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
    <BrowserOnly fallback={<div className="navbar-auth-button" />}>
      {() => <NavbarAuthInner />}
    </BrowserOnly>
  );
}

export default NavbarAuth;

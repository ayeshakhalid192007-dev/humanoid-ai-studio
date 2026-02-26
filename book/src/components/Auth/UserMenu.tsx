/**
 * User Menu Component
 *
 * Shows user avatar and dropdown menu when logged in.
 * Enhanced with prominent sign-out option and glassmorphism design.
 */

import React, { useState, useRef, useEffect } from "react";
import Link from "@docusaurus/Link";
import { useAuth } from "../../context/AuthContext";
import styles from "./Auth.module.css";

export function UserMenu() {
  const { user, signOut, isLoading } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [isSigningOut, setIsSigningOut] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  if (!user) return null;

  const initials = user.name
    ? user.name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    : user.email[0].toUpperCase();

  const handleSignOut = async () => {
    setIsSigningOut(true);
    setIsOpen(false);
    await signOut();
    setIsSigningOut(false);
  };

  return (
    <div className={styles.userMenu} ref={menuRef}>
      <button
        className={styles.userButton}
        onClick={() => setIsOpen(!isOpen)}
        disabled={isLoading || isSigningOut}
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        <span className={styles.userAvatar}>{initials}</span>
        <span className={styles.userName}>{user.name || user.email.split("@")[0]}</span>
        <svg
          width="12"
          height="12"
          viewBox="0 0 12 12"
          fill="none"
          className={styles.chevronIcon}
          style={{
            transform: isOpen ? "rotate(180deg)" : "rotate(0)",
            transition: "transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
          }}
        >
          <path
            d="M2.5 4.5L6 8L9.5 4.5"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>

      {isOpen && (
        <div className={styles.dropdown}>
          <div className={styles.dropdownArrow} />

          <div className={styles.dropdownHeader}>
            <div className={styles.dropdownAvatarLarge}>{initials}</div>
            <div className={styles.dropdownName}>{user.name || "User"}</div>
            <div className={styles.dropdownEmail}>{user.email}</div>
            {user.role && (
              <div className={styles.dropdownRole}>{user.role}</div>
            )}
          </div>

          <div className={styles.dropdownSection}>
            <Link
              to="/dashboard"
              className={styles.dropdownItem}
              onClick={() => setIsOpen(false)}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path
                  d="M2 8h4m0 0V4m0 4l-4-4m12 4H10m0 0v4m0-4l4 4"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              <span>Dashboard</span>
            </Link>

            <Link
              to="/profile"
              className={styles.dropdownItem}
              onClick={() => setIsOpen(false)}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <circle cx="8" cy="5" r="2.5" stroke="currentColor" strokeWidth="1.5" />
                <path
                  d="M3 13c0-2.5 2-4 5-4s5 1.5 5 4"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                />
              </svg>
              <span>Profile</span>
            </Link>

            <Link
              to="/settings"
              className={styles.dropdownItem}
              onClick={() => setIsOpen(false)}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path
                  d="M8 10a2 2 0 100-4 2 2 0 000 4z"
                  stroke="currentColor"
                  strokeWidth="1.5"
                />
                <path
                  d="M13.5 8c0-.3-.2-.6-.5-.7l-.8-.3c-.1-.3-.2-.6-.4-.9l.4-.7c.2-.3.1-.6-.1-.8l-.7-.7c-.2-.2-.5-.3-.8-.1l-.7.4c-.3-.2-.6-.3-.9-.4l-.3-.8c-.1-.3-.4-.5-.7-.5h-1c-.3 0-.6.2-.7.5l-.3.8c-.3.1-.6.2-.9.4l-.7-.4c-.3-.2-.6-.1-.8.1l-.7.7c-.2.2-.3.5-.1.8l.4.7c-.2.3-.3.6-.4.9l-.8.3c-.3.1-.5.4-.5.7v1c0 .3.2.6.5.7l.8.3c.1.3.2.6.4.9l-.4.7c-.2.3-.1.6.1.8l.7.7c.2.2.5.3.8.1l.7-.4c.3.2.6.3.9.4l.3.8c.1.3.4.5.7.5h1c.3 0 .6-.2.7-.5l.3-.8c.3-.1.6-.2.9-.4l.7.4c.3.2.6.1.8-.1l.7-.7c.2-.2.3-.5.1-.8l-.4-.7c.2-.3.3-.6.4-.9l.8-.3c.3-.1.5-.4.5-.7v-1z"
                  stroke="currentColor"
                  strokeWidth="1.5"
                />
              </svg>
              <span>Settings</span>
            </Link>
          </div>

          <div className={styles.dropdownDivider} />

          <button
            className={`${styles.dropdownItem} ${styles.signOutItem}`}
            onClick={handleSignOut}
            disabled={isSigningOut}
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path
                d="M6 14H3a1 1 0 01-1-1V3a1 1 0 011-1h3M11 11l3-3m0 0l-3-3m3 3H6"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <span>{isSigningOut ? "Signing out..." : "Sign Out"}</span>
            {isSigningOut && <div className={styles.miniSpinner} />}
          </button>
        </div>
      )}
    </div>
  );
}

export default UserMenu;

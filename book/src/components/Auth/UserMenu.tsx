/**
 * User Menu Component
 *
 * Shows user avatar and dropdown menu when logged in.
 */

import React, { useState, useRef, useEffect } from "react";
import Link from "@docusaurus/Link";
import { useAuth } from "../../context/AuthContext";
import styles from "./Auth.module.css";

export function UserMenu() {
  const { user, signOut, isLoading } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
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
    setIsOpen(false);
    await signOut();
  };

  return (
    <div className={styles.userMenu} ref={menuRef}>
      <button
        className={styles.userButton}
        onClick={() => setIsOpen(!isOpen)}
        disabled={isLoading}
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        <span className={styles.userAvatar}>{initials}</span>
        <span>{user.name || user.email.split("@")[0]}</span>
        <svg
          width="12"
          height="12"
          viewBox="0 0 12 12"
          fill="none"
          style={{
            transform: isOpen ? "rotate(180deg)" : "rotate(0)",
            transition: "transform 0.2s",
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
          <div className={styles.dropdownHeader}>
            <div className={styles.dropdownName}>{user.name || "User"}</div>
            <div className={styles.dropdownEmail}>{user.email}</div>
          </div>

          <Link
            to="/dashboard"
            className={styles.dropdownItem}
            onClick={() => setIsOpen(false)}
          >
            Dashboard
          </Link>

          <button
            className={`${styles.dropdownItem} ${styles.signOutItem}`}
            onClick={handleSignOut}
          >
            Sign Out
          </button>
        </div>
      )}
    </div>
  );
}

export default UserMenu;

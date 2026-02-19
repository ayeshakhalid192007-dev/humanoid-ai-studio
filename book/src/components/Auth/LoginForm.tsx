/**
 * Login Form Component
 *
 * Provides email/password login functionality.
 */

import React, { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import styles from "./Auth.module.css";

interface LoginFormProps {
  onSuccess?: () => void;
  onSwitchToSignUp?: () => void;
}

export function LoginForm({ onSuccess, onSwitchToSignUp }: LoginFormProps) {
  const { signIn, isLoading } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!email || !password) {
      setError("Please fill in all fields");
      return;
    }

    const result = await signIn(email, password);

    if (result.success) {
      onSuccess?.();
    } else {
      setError(result.error || "Login failed");
    }
  };

  return (
    <form onSubmit={handleSubmit} className={styles.authForm}>
      <h2 className={styles.authTitle}>Sign In</h2>
      <p className={styles.authSubtitle}>
        Welcome back! Sign in to access your learning progress.
      </p>

      {error && <div className={styles.errorMessage}>{error}</div>}

      <div className={styles.inputGroup}>
        <label htmlFor="email" className={styles.label}>
          Email
        </label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className={styles.input}
          placeholder="you@example.com"
          disabled={isLoading}
          autoComplete="email"
        />
      </div>

      <div className={styles.inputGroup}>
        <label htmlFor="password" className={styles.label}>
          Password
        </label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className={styles.input}
          placeholder="Enter your password"
          disabled={isLoading}
          autoComplete="current-password"
        />
      </div>

      <button
        type="submit"
        className={styles.submitButton}
        disabled={isLoading}
      >
        {isLoading ? "Signing in..." : "Sign In"}
      </button>

      <p className={styles.switchText}>
        Don't have an account?{" "}
        <button
          type="button"
          onClick={onSwitchToSignUp}
          className={styles.switchButton}
        >
          Sign Up
        </button>
      </p>
    </form>
  );
}

export default LoginForm;

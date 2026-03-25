/**
 * Login Form Component
 *
 * Two modes:
 * 1. OAuth relay — URL contains OAuth params (client_id, code_challenge …).
 *    The auth server redirected here after finding no active session.
 *    After credential auth succeeds we forward all params back to the
 *    auth server's /api/auth/oauth2/authorize endpoint so it can issue the code.
 *
 * 2. Standalone — no OAuth params in URL.
 *    Calls signIn() which initiates the full PKCE redirect flow.
 */

import React, { useState } from "react";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import { useAuth } from "../../context/AuthContext";
import styles from "./Auth.module.css";

interface LoginFormProps {
  onSuccess?: () => void;
  onSwitchToSignUp?: () => void;
}

export function LoginForm({ onSuccess, onSwitchToSignUp }: LoginFormProps) {
  const { signIn, signInWithSocial, isLoading } = useAuth();
  const { siteConfig } = useDocusaurusContext();
  const AUTH_API_URL =
    (siteConfig.customFields?.authApiUrl as string) || "http://localhost:3002";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  // Detect OAuth relay mode — auth server redirected us here with these params
  const searchParams =
    typeof window !== "undefined"
      ? new URLSearchParams(window.location.search)
      : new URLSearchParams();

  const oauthParams = {
    client_id: searchParams.get("client_id"),
    redirect_uri: searchParams.get("redirect_uri"),
    response_type: searchParams.get("response_type"),
    scope: searchParams.get("scope"),
    state: searchParams.get("state"),
    code_challenge: searchParams.get("code_challenge"),
    code_challenge_method: searchParams.get("code_challenge_method"),
  };

  // We are in relay mode if the auth server forwarded OAuth params to this page
  const isOAuthRelay = !!(oauthParams.client_id && oauthParams.code_challenge);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!email || !password) {
      setError("Please fill in all fields");
      return;
    }

    if (isOAuthRelay) {
      // ── OAuth relay: do direct credential auth, then bounce back to auth server ──
      try {
        const resp = await fetch(`${AUTH_API_URL}/api/auth/sign-in/email`, {
          method: "POST",
          credentials: "include", // auth server sets the session cookie
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });

        if (!resp.ok) {
          const data = await resp.json().catch(() => ({}));
          setError(data.message ?? data.error ?? "Invalid credentials");
          return;
        }

        // Rebuild authorize URL with ALL original OAuth params (including PKCE)
        const authorizeParams = new URLSearchParams();
        Object.entries(oauthParams).forEach(([k, v]) => {
          if (v) authorizeParams.set(k, v);
        });

        window.location.href = `${AUTH_API_URL}/api/auth/oauth2/authorize?${authorizeParams.toString()}`;
      } catch {
        setError("Network error. Please try again.");
      }
    } else {
      // ── Standalone: initiate the OAuth PKCE flow ──
      const result = await signIn(email, password);
      if (result.success) {
        onSuccess?.();
      } else {
        setError(result.error || "Login failed");
      }
    }
  };

  const handleSocialSignIn = async (provider: 'google' | 'github') => {
    setError("");
    try {
      await signInWithSocial(provider);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Social sign-in failed. Please try again.");
    }
  };

  return (
    <form onSubmit={handleSubmit} className={styles.authForm}>
      <h2 className={styles.authTitle}>Sign In</h2>
      <p className={styles.authSubtitle}>
        Welcome back! Sign in to access your learning progress.
      </p>

      {error && <div className={styles.errorMessage}>{error}</div>}

      {/* Social login buttons */}
      <div className={styles.socialButtons}>
        <button
          type="button"
          onClick={() => handleSocialSignIn('google')}
          className={styles.socialButton}
          disabled={isLoading}
        >
          {/* Google icon */}
          <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          Continue with Google
        </button>
        <button
          type="button"
          onClick={() => handleSocialSignIn('github')}
          className={styles.socialButton}
          disabled={isLoading}
        >
          {/* GitHub icon */}
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/>
          </svg>
          Continue with GitHub
        </button>
      </div>

      <div className={styles.divider}>
        <span>or sign in with email</span>
      </div>

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

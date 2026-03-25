/**
 * Sign Up Form Component
 *
 * Collects account info AND background profile in a single form.
 *
 * Two modes:
 * 1. OAuth relay — URL contains OAuth params.  Creates the account, saves the
 *    profile, then redirects back to the auth server's authorize endpoint.
 * 2. Standalone — initiates the PKCE OAuth flow after account creation.
 */

import React, { useState } from "react";
import { useHistory } from "@docusaurus/router";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import { useAuth } from "../../context/AuthContext";
import styles from "./Auth.module.css";

interface SignUpFormProps {
  onSuccess?: () => void;
  onSwitchToLogin?: () => void;
}

interface FormErrors {
  name?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
  softwareBackground?: string;
  hardwareBackground?: string;
  roboticsKnowledge?: string;
}

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const MAX_BG_LENGTH = 2000;

export function SignUpForm({ onSuccess, onSwitchToLogin }: SignUpFormProps) {
  const { signUpWithProfile, signInWithSocial, isLoading } = useAuth();
  const { siteConfig } = useDocusaurusContext();
  const AUTH_API_URL =
    (siteConfig.customFields?.authApiUrl as string) || "http://localhost:3002";
  const history = useHistory();

  // Detect OAuth relay mode
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

  const isOAuthRelay = !!(oauthParams.client_id && oauthParams.code_challenge);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [softwareBackground, setSoftwareBackground] = useState("");
  const [hardwareBackground, setHardwareBackground] = useState("");
  const [roboticsKnowledge, setRoboticsKnowledge] = useState("");
  const [errors, setErrors] = useState<FormErrors>({});
  const [serverError, setServerError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const validate = (): FormErrors => {
    const errs: FormErrors = {};

    if (!name.trim()) errs.name = "Full name is required.";
    if (!email.trim()) {
      errs.email = "Email is required.";
    } else if (!EMAIL_REGEX.test(email)) {
      errs.email = "Enter a valid email address.";
    }
    if (!password) {
      errs.password = "Password is required.";
    } else if (password.length < 8) {
      errs.password = "Password must be at least 8 characters.";
    }
    if (password !== confirmPassword) {
      errs.confirmPassword = "Passwords do not match.";
    }
    if (!softwareBackground.trim()) {
      errs.softwareBackground = "Describe your software background.";
    }
    if (!hardwareBackground.trim()) {
      errs.hardwareBackground = "Describe your hardware background.";
    }
    if (!roboticsKnowledge) {
      errs.roboticsKnowledge = "Select your robotics knowledge level.";
    }

    return errs;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setServerError("");

    const formErrors = validate();
    setErrors(formErrors);
    if (Object.keys(formErrors).length > 0) return;

    setSubmitting(true);

    if (isOAuthRelay) {
      // ── OAuth relay: create account + profile, then bounce back to auth server ──
      try {
        const signUpResp = await fetch(`${AUTH_API_URL}/api/auth/sign-up/email`, {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password, name: name.trim() }),
        });

        const signUpData = await signUpResp.json();

        if (!signUpResp.ok) {
          setServerError(signUpData.message ?? signUpData.error ?? "Sign up failed.");
          setSubmitting(false);
          return;
        }

        // Better Auth returns a session token on sign-up — use it as Bearer for
        // the profile call so it works cross-origin (GitHub Pages → auth server)
        // where third-party cookies are blocked by the browser.
        // Newer Better Auth versions nest the token under session.token.
        const signUpToken: string | null = signUpData.token ?? signUpData.session?.token ?? null;

        // Save profile (best-effort — user can complete onboarding later)
        try {
          const profileResp = await fetch(`${AUTH_API_URL}/api/profile`, {
            method: "POST",
            credentials: "include",
            headers: {
              "Content-Type": "application/json",
              ...(signUpToken ? { Authorization: `Bearer ${signUpToken}` } : {}),
            },
            body: JSON.stringify({
              softwareBackground: softwareBackground.trim().slice(0, MAX_BG_LENGTH),
              hardwareBackground: hardwareBackground.trim().slice(0, MAX_BG_LENGTH),
              roboticsKnowledge,
            }),
          });
          if (!profileResp.ok) {
            const profileErr = await profileResp.json().catch(() => ({}));
            console.warn(`Profile save failed (${profileResp.status}):`, profileErr);
          }
        } catch (profileNetErr) {
          console.warn("Profile save network error:", profileNetErr);
        }

        // Redirect back to auth server with original OAuth params (including PKCE)
        const authorizeParams = new URLSearchParams();
        Object.entries(oauthParams).forEach(([k, v]) => {
          if (v) authorizeParams.set(k, v);
        });

        window.location.href = `${AUTH_API_URL}/api/auth/oauth2/authorize?${authorizeParams.toString()}`;
      } catch {
        setServerError("Network error. Please try again.");
        setSubmitting(false);
      }
      return;
    }

    // ── Standalone: normal signUpWithProfile flow ──
    const result = await signUpWithProfile(email, password, name.trim(), {
      softwareBackground: softwareBackground.trim().slice(0, MAX_BG_LENGTH),
      hardwareBackground: hardwareBackground.trim().slice(0, MAX_BG_LENGTH),
      roboticsKnowledge,
    });

    setSubmitting(false);

    if (result.success) {
      if (onSuccess) {
        onSuccess();
      } else {
        history.push("/dashboard");
      }
    } else {
      setServerError(result.error || "Sign up failed. Please try again.");
    }
  };

  const handleSocialSignIn = async (provider: 'google' | 'github') => {
    setServerError("");
    try {
      await signInWithSocial(provider);
    } catch (err) {
      setServerError(err instanceof Error ? err.message : "Social sign-in failed. Please try again.");
    }
  };

  const fieldClass = (field: keyof FormErrors) =>
    errors[field] ? `${styles.input} ${styles.inputError}` : styles.input;

  const textareaClass = (field: keyof FormErrors) =>
    errors[field] ? `${styles.textarea} ${styles.inputError}` : styles.textarea;

  const disabled = submitting || isLoading;

  return (
    <form onSubmit={handleSubmit} className={styles.authForm} noValidate>
      <h2 className={styles.authTitle}>Create Account</h2>
      <p className={styles.authSubtitle}>
        Join the Physical AI & Humanoid Robotics learning community.
      </p>

      {serverError && <div className={styles.errorMessage}>{serverError}</div>}

      {/* Social sign-up buttons — Better Auth handles new vs returning user server-side */}
      <div className={styles.socialButtons}>
        <button
          type="button"
          onClick={() => handleSocialSignIn('google')}
          className={styles.socialButton}
          disabled={disabled}
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
          disabled={disabled}
        >
          {/* GitHub icon */}
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/>
          </svg>
          Continue with GitHub
        </button>
      </div>

      <div className={styles.divider}>
        <span>or sign up with email</span>
      </div>

      {/* Account Information */}
      <div className={styles.inputGroup}>
        <label htmlFor="signup-name" className={styles.label}>
          Full Name <span className={styles.required}>*</span>
        </label>
        <input
          id="signup-name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className={fieldClass("name")}
          placeholder="Jane Doe"
          disabled={disabled}
          autoComplete="name"
        />
        {errors.name && <span className={styles.fieldError}>{errors.name}</span>}
      </div>

      <div className={styles.inputGroup}>
        <label htmlFor="signup-email" className={styles.label}>
          Email <span className={styles.required}>*</span>
        </label>
        <input
          id="signup-email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className={fieldClass("email")}
          placeholder="you@example.com"
          disabled={disabled}
          autoComplete="email"
        />
        {errors.email && (
          <span className={styles.fieldError}>{errors.email}</span>
        )}
      </div>

      <div className={styles.inputGroup}>
        <label htmlFor="signup-password" className={styles.label}>
          Password <span className={styles.required}>*</span>
        </label>
        <input
          id="signup-password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className={fieldClass("password")}
          placeholder="At least 8 characters"
          disabled={disabled}
          autoComplete="new-password"
        />
        {errors.password && (
          <span className={styles.fieldError}>{errors.password}</span>
        )}
      </div>

      <div className={styles.inputGroup}>
        <label htmlFor="signup-confirm" className={styles.label}>
          Confirm Password <span className={styles.required}>*</span>
        </label>
        <input
          id="signup-confirm"
          type="password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          className={fieldClass("confirmPassword")}
          placeholder="Confirm your password"
          disabled={disabled}
          autoComplete="new-password"
        />
        {errors.confirmPassword && (
          <span className={styles.fieldError}>{errors.confirmPassword}</span>
        )}
      </div>

      {/* Background Information */}
      <div className={styles.sectionDivider} />
      <p className={styles.sectionLabel}>Your Background</p>

      <div className={styles.inputGroup}>
        <label htmlFor="signup-sw-bg" className={styles.label}>
          Software Background <span className={styles.required}>*</span>
        </label>
        <textarea
          id="signup-sw-bg"
          value={softwareBackground}
          onChange={(e) => setSoftwareBackground(e.target.value)}
          className={textareaClass("softwareBackground")}
          placeholder="e.g., 3 years Python, some C++, familiar with Linux..."
          disabled={disabled}
          maxLength={MAX_BG_LENGTH}
          rows={3}
        />
        <span className={styles.charCount}>
          {softwareBackground.length}/{MAX_BG_LENGTH}
        </span>
        {errors.softwareBackground && (
          <span className={styles.fieldError}>
            {errors.softwareBackground}
          </span>
        )}
      </div>

      <div className={styles.inputGroup}>
        <label htmlFor="signup-hw-bg" className={styles.label}>
          Hardware Background <span className={styles.required}>*</span>
        </label>
        <textarea
          id="signup-hw-bg"
          value={hardwareBackground}
          onChange={(e) => setHardwareBackground(e.target.value)}
          className={textareaClass("hardwareBackground")}
          placeholder="e.g., Arduino projects, basic circuit design, no experience..."
          disabled={disabled}
          maxLength={MAX_BG_LENGTH}
          rows={3}
        />
        <span className={styles.charCount}>
          {hardwareBackground.length}/{MAX_BG_LENGTH}
        </span>
        {errors.hardwareBackground && (
          <span className={styles.fieldError}>
            {errors.hardwareBackground}
          </span>
        )}
      </div>

      <div className={styles.inputGroup}>
        <label htmlFor="signup-robotics" className={styles.label}>
          Robotics Knowledge Level <span className={styles.required}>*</span>
        </label>
        <select
          id="signup-robotics"
          value={roboticsKnowledge}
          onChange={(e) => setRoboticsKnowledge(e.target.value)}
          className={
            errors.roboticsKnowledge
              ? `${styles.select} ${styles.inputError}`
              : styles.select
          }
          disabled={disabled}
        >
          <option value="">Select your level...</option>
          <option value="none">None / Complete beginner</option>
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
        </select>
        {errors.roboticsKnowledge && (
          <span className={styles.fieldError}>
            {errors.roboticsKnowledge}
          </span>
        )}
      </div>

      <button
        type="submit"
        className={styles.submitButton}
        disabled={disabled}
      >
        {submitting ? (
          <span className={styles.buttonLoading}>
            <span className={styles.spinner} />
            Creating account...
          </span>
        ) : (
          "Create Account"
        )}
      </button>

      <p className={styles.switchText}>
        Already have an account?{" "}
        <button
          type="button"
          onClick={onSwitchToLogin}
          className={styles.switchButton}
        >
          Sign In
        </button>
      </p>
    </form>
  );
}

export default SignUpForm;

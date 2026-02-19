/**
 * Sign Up Form Component
 *
 * Collects account info AND background profile in a single form.
 * On success, redirects to /dashboard.
 */

import React, { useState } from "react";
import { useHistory } from "@docusaurus/router";
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
  const { signUpWithProfile, isLoading } = useAuth();
  const history = useHistory();

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

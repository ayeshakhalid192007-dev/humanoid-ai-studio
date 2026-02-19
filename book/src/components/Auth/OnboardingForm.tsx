/**
 * Onboarding Form Component
 *
 * Collects software background, hardware background, and
 * robotics knowledge level after signup.
 */

import React, { useState } from "react";
import { useAuth, UserProfile } from "../../context/AuthContext";
import styles from "./Auth.module.css";

const LEVELS = [
  {
    value: "none",
    label: "None",
    description: "No prior experience in this area.",
  },
  {
    value: "beginner",
    label: "Beginner",
    description: "Some exposure to basic concepts.",
  },
  {
    value: "intermediate",
    label: "Intermediate",
    description: "Comfortable with core topics; built small projects.",
  },
  {
    value: "advanced",
    label: "Advanced",
    description: "Deep experience; worked on production systems.",
  },
];

interface OnboardingFormProps {
  onComplete?: () => void;
}

export function OnboardingForm({ onComplete }: OnboardingFormProps) {
  const { saveProfile, isLoading } = useAuth();
  const [softwareBackground, setSoftwareBackground] = useState("none");
  const [hardwareBackground, setHardwareBackground] = useState("none");
  const [roboticsKnowledge, setRoboticsKnowledge] = useState("none");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSaving(true);

    const profileData: UserProfile = {
      softwareBackground,
      hardwareBackground,
      roboticsKnowledge,
    };

    const result = await saveProfile(profileData);

    if (result.success) {
      onComplete?.();
    } else {
      setError(result.error || "Failed to save profile");
    }

    setSaving(false);
  };

  return (
    <form onSubmit={handleSubmit} className={styles.authForm}>
      <div className={styles.onboardingHeader}>
        <h2 className={styles.authTitle}>Tell Us About Yourself</h2>
        <p className={styles.authSubtitle}>
          Help us personalize your learning experience.
        </p>
      </div>

      {error && <div className={styles.errorMessage}>{error}</div>}

      <div className={styles.inputGroup}>
        <label className={styles.label}>Software Development Background</label>
        <div className={styles.radioGroup}>
          {LEVELS.map((level) => (
            <label
              key={`sw-${level.value}`}
              className={`${styles.radioOption} ${
                softwareBackground === level.value ? styles.radioSelected : ""
              }`}
            >
              <input
                type="radio"
                name="softwareBackground"
                value={level.value}
                checked={softwareBackground === level.value}
                onChange={(e) => setSoftwareBackground(e.target.value)}
                className={styles.radioInput}
              />
              <span className={styles.radioLabel}>{level.label}</span>
              <span className={styles.radioDescription}>
                {level.description}
              </span>
            </label>
          ))}
        </div>
      </div>

      <div className={styles.inputGroup}>
        <label className={styles.label}>
          Hardware & Electronics Background
        </label>
        <div className={styles.radioGroup}>
          {LEVELS.map((level) => (
            <label
              key={`hw-${level.value}`}
              className={`${styles.radioOption} ${
                hardwareBackground === level.value ? styles.radioSelected : ""
              }`}
            >
              <input
                type="radio"
                name="hardwareBackground"
                value={level.value}
                checked={hardwareBackground === level.value}
                onChange={(e) => setHardwareBackground(e.target.value)}
                className={styles.radioInput}
              />
              <span className={styles.radioLabel}>{level.label}</span>
              <span className={styles.radioDescription}>
                {level.description}
              </span>
            </label>
          ))}
        </div>
      </div>

      <div className={styles.inputGroup}>
        <label className={styles.label}>Robotics Knowledge Level</label>
        <div className={styles.radioGroup}>
          {LEVELS.map((level) => (
            <label
              key={`rb-${level.value}`}
              className={`${styles.radioOption} ${
                roboticsKnowledge === level.value ? styles.radioSelected : ""
              }`}
            >
              <input
                type="radio"
                name="roboticsKnowledge"
                value={level.value}
                checked={roboticsKnowledge === level.value}
                onChange={(e) => setRoboticsKnowledge(e.target.value)}
                className={styles.radioInput}
              />
              <span className={styles.radioLabel}>{level.label}</span>
              <span className={styles.radioDescription}>
                {level.description}
              </span>
            </label>
          ))}
        </div>
      </div>

      <button
        type="submit"
        className={styles.submitButton}
        disabled={saving || isLoading}
      >
        {saving ? "Saving..." : "Complete Setup"}
      </button>
    </form>
  );
}

export default OnboardingForm;

/**
 * Dashboard Page
 *
 * Landing page for authenticated users.
 * Shows welcome message, course modules, and profile summary.
 */

import React from "react";
import Link from "@docusaurus/Link";
import BrowserOnly from "@docusaurus/BrowserOnly";
import { AppLayout } from "../components/Layout/AppLayout";
import ErrorBoundary from "../components/ErrorBoundary";
import styles from "./dashboard.module.css";

const modules = [
  {
    title: "Module 1: ROS 2 Middleware",
    description:
      "Build the communication backbone with ROS 2 Humble. Master nodes, topics, services, and URDF robot models.",
    link: "/docs/module1/intro",
    icon: "\u{1F916}",
  },
  {
    title: "Module 2: Simulation",
    description:
      "Simulate humanoid robots in Gazebo with physics engines, sensors, and optional NVIDIA Isaac Sim.",
    link: "/docs/module2/intro",
    icon: "\u{1F30D}",
  },
  {
    title: "Module 3: Perception & Navigation",
    description:
      "Implement VSLAM for mapping, Nav2 for path planning, and dynamic obstacle avoidance.",
    link: "/docs/module3/intro",
    icon: "\u{1F9ED}",
  },
  {
    title: "Module 4: Voice-Language-Action",
    description:
      "Build a complete VLA pipeline: speech transcription, LLM command parsing, safety validation, and action execution.",
    link: "/docs/module4/intro",
    icon: "\u{1F5E3}\u{FE0F}",
  },
];

function capitalize(str: string): string {
  return str ? str.charAt(0).toUpperCase() + str.slice(1) : "";
}

function DashboardContent() {
  const { useAuth } = require("../context/AuthContext");
  const { user, profile, fetchProfile } = useAuth();

  React.useEffect(() => {
    if (user && !profile) {
      fetchProfile();
    }
  }, [user, profile, fetchProfile]);

  const displayName = user?.name || user?.email?.split("@")[0] || "Student";

  return (
    <div className={styles.dashboard}>
      <div className={styles.welcome}>
        <h1 className={styles.welcomeTitle}>Welcome back, {displayName}</h1>
        <p className={styles.welcomeSubtitle}>
          Continue your Physical AI & Humanoid Robotics journey.
        </p>
      </div>

      <h2>Course Modules</h2>
      <div className={styles.grid}>
        {modules.map((mod, idx) => (
          <div key={idx} className={styles.card}>
            <div className={styles.cardIcon}>{mod.icon}</div>
            <div className={styles.cardTitle}>{mod.title}</div>
            <div className={styles.cardDescription}>{mod.description}</div>
            <Link to={mod.link} className={styles.cardLink}>
              Start Module &rarr;
            </Link>
          </div>
        ))}
      </div>

      {profile && (
        <div className={styles.profileSection}>
          <div className={styles.profileTitle}>Your Profile</div>
          <div className={styles.profileGrid}>
            <div className={styles.profileItem}>
              <div className={styles.profileLabel}>Software Background</div>
              <div className={styles.profileValue}>
                {profile.softwareBackground || "Not set"}
              </div>
            </div>
            <div className={styles.profileItem}>
              <div className={styles.profileLabel}>Hardware Background</div>
              <div className={styles.profileValue}>
                {profile.hardwareBackground || "Not set"}
              </div>
            </div>
            <div className={styles.profileItem}>
              <div className={styles.profileLabel}>Robotics Level</div>
              <div className={styles.profileValue}>
                {capitalize(profile.roboticsKnowledge) || "Not set"}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function DashboardPage(): JSX.Element {
  return (
    <AppLayout title="Dashboard" description="Your learning dashboard" background="default">
      <ErrorBoundary>
        <BrowserOnly
          fallback={
            <div className={styles.dashboard}>
              <p>Loading dashboard...</p>
            </div>
          }
        >
          {() => <DashboardContent />}
        </BrowserOnly>
      </ErrorBoundary>
    </AppLayout>
  );
}

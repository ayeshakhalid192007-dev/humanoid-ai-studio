import React from 'react';
import Layout from '@theme/Layout';
import styles from './features.module.css';

const features = [
  {
    title: 'ROS 2 Middleware',
    description:
      'Master the Robot Operating System 2 with hands-on projects. Learn nodes, topics, services, actions, and URDF robot models using the modern Humble distribution.',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="3" />
        <path d="M12 1v6M12 17v6M4.22 4.22l4.24 4.24M15.54 15.54l4.24 4.24M1 12h6M17 12h6M4.22 19.78l4.24-4.24M15.54 8.46l4.24-4.24" />
      </svg>
    ),
  },
  {
    title: 'Gazebo Simulation',
    description:
      'Build and test robots in photorealistic 3D environments. Configure physics engines, sensors, and controllers without risking real hardware.',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10" />
        <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
      </svg>
    ),
  },
  {
    title: 'VSLAM & Navigation',
    description:
      'Implement visual simultaneous localization and mapping. Use Nav2 for autonomous path planning and dynamic obstacle avoidance in complex environments.',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polygon points="3 11 22 2 13 21 11 13 3 11" />
      </svg>
    ),
  },
  {
    title: 'Voice-Language-Action',
    description:
      'Build end-to-end VLA pipelines: speech transcription with Whisper, LLM command parsing with GPT-4, safety validation, and robotic action execution.',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
        <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
        <line x1="12" y1="19" x2="12" y2="23" />
        <line x1="8" y1="23" x2="16" y2="23" />
      </svg>
    ),
  },
  {
    title: 'AI Learning Assistant',
    description:
      'Every page includes an AI chatbot trained on curriculum content. Highlight text and ask questions. Get instant answers with citations to specific lessons.',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        <circle cx="9" cy="10" r="1" fill="currentColor" />
        <circle cx="12" cy="10" r="1" fill="currentColor" />
        <circle cx="15" cy="10" r="1" fill="currentColor" />
      </svg>
    ),
  },
  {
    title: 'Predict-Execute-Reflect',
    description:
      'Our unique learning methodology builds deep intuition. Form hypotheses before running code, observe results, and analyze the gap to cement understanding.',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
        <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
      </svg>
    ),
  },
];

function FeatureCard({
  title,
  description,
  icon,
}: {
  title: string;
  description: string;
  icon: React.ReactNode;
}) {
  return (
    <div className={styles.featureCard}>
      <div className={styles.featureIcon}>{icon}</div>
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
}

export default function Features(): JSX.Element {
  return (
    <Layout title="Features" description="Explore the features of the Physical AI Platform">
      <header className={styles.hero}>
        <div className={styles.heroInner}>
          <h1>Platform Features</h1>
          <p className={styles.heroSubtitle}>
            Everything you need to build intelligent robots, from fundamentals to cutting-edge AI integration.
          </p>
        </div>
      </header>
      <main className={styles.main}>
        <section className={styles.featuresSection}>
          <div className={styles.featuresGrid}>
            {features.map((feature, idx) => (
              <FeatureCard key={idx} {...feature} />
            ))}
          </div>
        </section>
      </main>
    </Layout>
  );
}

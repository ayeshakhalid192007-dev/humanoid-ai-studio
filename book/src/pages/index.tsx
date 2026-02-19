import React, { useState } from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import BrowserOnly from '@docusaurus/BrowserOnly';
import styles from './index.module.css';

const modules = [
  {
    title: 'Module 1: ROS 2 Middleware',
    description: 'Build the communication backbone with ROS 2 Humble. Master nodes, topics, services, and URDF robot models.',
    link: '/docs/module1/intro',
    icon: '\u{1F916}',
  },
  {
    title: 'Module 2: Simulation',
    description: 'Simulate humanoid robots in Gazebo with physics engines, sensors, and optional NVIDIA Isaac Sim.',
    link: '/docs/module2/intro',
    icon: '\u{1F30D}',
  },
  {
    title: 'Module 3: Perception & Navigation',
    description: 'Implement VSLAM for mapping, Nav2 for path planning, and dynamic obstacle avoidance.',
    link: '/docs/module3/intro',
    icon: '\u{1F9ED}',
  },
  {
    title: 'Module 4: Voice-Language-Action',
    description: 'Build a complete VLA pipeline: speech transcription, LLM command parsing, safety validation, and action execution.',
    link: '/docs/module4/intro',
    icon: '\u{1F5E3}\u{FE0F}',
  },
];

function Hero() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={styles.hero}>
      <div className={styles.heroInner}>
        <h1 className={styles.heroTitle}>{siteConfig.title}</h1>
        <p className={styles.heroSubtitle}>{siteConfig.tagline}</p>
        <div className={styles.heroButtons}>
          <Link className={styles.heroButton} to="/docs/intro">
            Get Started
          </Link>
        </div>
      </div>
    </header>
  );
}

function ModuleCard({title, description, link, icon}: {
  title: string; description: string; link: string; icon: string;
}) {
  return (
    <div className={styles.moduleCard}>
      <div className={styles.moduleIcon}>{icon}</div>
      <h3>{title}</h3>
      <p>{description}</p>
      <Link to={link} className={styles.moduleLink}>
        Start Module &rarr;
      </Link>
    </div>
  );
}

function LearningApproach() {
  return (
    <section className={styles.section}>
      <h2>Learning Approach: Predict &rarr; Execute &rarr; Reflect</h2>
      <div className={styles.approachGrid}>
        <div className={styles.approachCard}>
          <h3>Predict</h3>
          <p>Form hypotheses about what will happen before running any code. Build intuition through deliberate prediction.</p>
        </div>
        <div className={styles.approachCard}>
          <h3>Execute</h3>
          <p>Run the code, observe the results, and compare with your predictions. Hands-on learning with real tools.</p>
        </div>
        <div className={styles.approachCard}>
          <h3>Reflect</h3>
          <p>Analyze the gap between prediction and reality. Deepen understanding through structured reflection.</p>
        </div>
      </div>
    </section>
  );
}

function AIAssistant() {
  return (
    <section className={styles.section} style={{textAlign: 'center'}}>
      <h2>AI-Powered Learning Assistant</h2>
      <p className={styles.sectionDescription}>
        Every page includes an embedded AI chatbot trained on the curriculum content.
        Highlight any text and ask questions. Get instant answers with citations to specific lessons.
      </p>
      <BrowserOnly>
        {() => {
          const { useAuth } = require('../context/AuthContext');
          const { AuthModal } = require('../components/Auth/AuthModal');
          const { isAuthenticated } = useAuth();
          const [showAuthModal, setShowAuthModal] = useState(false);

          if (isAuthenticated) {
            return (
              <div style={{marginTop: '1.5rem'}}>
                <Link className={styles.heroButton} to="/dashboard">
                  Go to Dashboard
                </Link>
              </div>
            );
          }

          return (
            <div style={{marginTop: '1.5rem'}}>
              <button
                className={styles.heroButton}
                onClick={() => setShowAuthModal(true)}
                style={{border: 'none', cursor: 'pointer'}}
              >
                Login to Unlock Advanced Features
              </button>
              <AuthModal
                isOpen={showAuthModal}
                onClose={() => setShowAuthModal(false)}
              />
            </div>
          );
        }}
      </BrowserOnly>
    </section>
  );
}

export default function Home(): JSX.Element {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout title={siteConfig.title} description={siteConfig.tagline}>
      <Hero />
      <main className={styles.main}>
        <section className={styles.section}>
          <h2>Course Modules</h2>
          <div className={styles.moduleGrid}>
            {modules.map((mod, idx) => (
              <ModuleCard key={idx} {...mod} />
            ))}
          </div>
        </section>
        <LearningApproach />
        <AIAssistant />
      </main>
    </Layout>
  );
}

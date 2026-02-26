import React, { useEffect, useRef, useState } from 'react';
import { motion, useScroll, useTransform, useInView } from 'framer-motion';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import { Button, Card } from '../components/ui';
import FuturisticNavbar from '../components/Navigation/FuturisticNavbar';

// Animated grid background component
const AnimatedGrid = () => {
  return (
    <div className="neon-grid-bg">
      <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(0, 255, 255, 0.1)" strokeWidth="1"/>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />
      </svg>
    </div>
  );
};

// Floating particles effect
const FloatingParticles = () => {
  const particles = Array.from({ length: 20 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    delay: Math.random() * 2,
    duration: 3 + Math.random() * 2,
  }));

  return (
    <div className="floating-particles">
      {particles.map((particle) => (
        <motion.div
          key={particle.id}
          className="particle"
          style={{
            left: `${particle.x}%`,
            top: `${particle.y}%`,
          }}
          animate={{
            y: [0, -30, 0],
            opacity: [0, 1, 0],
          }}
          transition={{
            duration: particle.duration,
            repeat: Infinity,
            delay: particle.delay,
          }}
        />
      ))}
    </div>
  );
};

// Hero Section with Neon Brutalism
const HeroSection = () => {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end start"]
  });

  const y = useTransform(scrollYProgress, [0, 1], ["0%", "50%"]);
  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);

  return (
    <section ref={ref} className="neon-hero">
      <AnimatedGrid />
      <FloatingParticles />

      <motion.div
        className="neon-hero__container"
        style={{ y, opacity }}
      >
        {/* Decorative brutalist shapes */}
        <div className="brutalist-shapes">
          <motion.div
            className="shape shape-1"
            animate={{ rotate: 360 }}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
          />
          <motion.div
            className="shape shape-2"
            animate={{ rotate: -360 }}
            transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
          />
        </div>

        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="hero-badge"
        >
          <span className="badge-text">🤖 AI-POWERED LEARNING</span>
        </motion.div>

        <motion.h1
          className="neon-hero__title"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
        >
          <span className="title-line">MASTER</span>
          <span className="title-line title-line--accent">PHYSICAL AI</span>
          <span className="title-line">& ROBOTICS</span>
        </motion.h1>

        <motion.p
          className="neon-hero__subtitle"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5 }}
        >
          Build humanoid robots with cutting-edge AI. Learn ROS 2, simulation,
          and vision-language-action systems through personalized, adaptive curriculum.
        </motion.p>

        <motion.div
          className="neon-hero__cta"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.7 }}
        >
          <Link to="/auth/signup" className="neon-button neon-button--primary">
            <span className="button-text">START LEARNING</span>
            <span className="button-arrow">→</span>
          </Link>
          <Link to="/chapters" className="neon-button neon-button--outline">
            <span className="button-text">EXPLORE CURRICULUM</span>
          </Link>
        </motion.div>

        <motion.div
          className="hero-stats"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 1 }}
        >
          <div className="stat">
            <div className="stat-number">8</div>
            <div className="stat-label">MODULES</div>
          </div>
          <div className="stat-divider" />
          <div className="stat">
            <div className="stat-number">50+</div>
            <div className="stat-label">LESSONS</div>
          </div>
          <div className="stat-divider" />
          <div className="stat">
            <div className="stat-number">AI</div>
            <div className="stat-label">POWERED</div>
          </div>
        </motion.div>
      </motion.div>
    </section>
  );
};

// Features with asymmetric layout
const FeaturesSection = () => {
  const features = [
    {
      icon: "🧠",
      title: "AI TUTOR",
      description: "Personalized learning that adapts to your pace. Get instant feedback and explanations powered by advanced language models.",
      color: "cyan"
    },
    {
      icon: "🎮",
      title: "SIMULATION",
      description: "Practice in physics-based environments. Master robotics without hardware constraints using Gazebo and Isaac Sim.",
      color: "magenta"
    },
    {
      icon: "📚",
      title: "STRUCTURED PATH",
      description: "From ROS 2 basics to humanoid systems. Follow a carefully designed curriculum that builds expertise progressively.",
      color: "yellow"
    },
    {
      icon: "🌐",
      title: "MULTILINGUAL",
      description: "Learn in your language. Full Urdu translation with more languages coming soon for global accessibility.",
      color: "green"
    }
  ];

  return (
    <section className="neon-features">
      <div className="neon-container">
        <motion.div
          className="section-header"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="section-title">
            <span className="title-accent">///</span> FEATURES
          </h2>
          <p className="section-subtitle">
            Everything you need to master physical AI and humanoid robotics
          </p>
        </motion.div>

        <div className="features-grid">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              className={`feature-card feature-card--${feature.color}`}
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              whileHover={{ y: -8, transition: { duration: 0.2 } }}
            >
              <div className="feature-icon">{feature.icon}</div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
              <div className="feature-corner" />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Curriculum with bold typography
const CurriculumSection = () => {
  const modules = [
    { num: "01", title: "ROS 2 FUNDAMENTALS", topics: "Nodes • Topics • Services • Actions" },
    { num: "02", title: "SIMULATION ENVIRONMENTS", topics: "Gazebo • URDF • Physics • Sensors" },
    { num: "03", title: "COMPUTER VISION", topics: "Perception • Object Detection • Tracking" },
    { num: "04", title: "VOICE-TO-ACTION", topics: "NLP • Speech • Command Execution" },
    { num: "05", title: "NVIDIA ISAAC", topics: "GPU Acceleration • Isaac Sim • Omniverse" },
    { num: "06", title: "VLA SYSTEMS", topics: "Vision • Language • Action Integration" },
    { num: "07", title: "REINFORCEMENT LEARNING", topics: "Policy Learning • Reward Design • Training" },
    { num: "08", title: "SIM-TO-REAL", topics: "Domain Transfer • Deployment • Testing" }
  ];

  return (
    <section className="neon-curriculum">
      <div className="neon-container">
        <motion.div
          className="section-header"
          initial={{ opacity: 0, x: -50 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="section-title section-title--large">
            COMPLETE<br />
            <span className="title-accent">CURRICULUM</span>
          </h2>
        </motion.div>

        <div className="curriculum-list">
          {modules.map((module, index) => (
            <motion.div
              key={index}
              className="curriculum-item"
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.05 }}
              whileHover={{ x: 10, transition: { duration: 0.2 } }}
            >
              <div className="curriculum-number">{module.num}</div>
              <div className="curriculum-content">
                <h3 className="curriculum-title">{module.title}</h3>
                <p className="curriculum-topics">{module.topics}</p>
              </div>
              <div className="curriculum-arrow">→</div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Tech stack with neon cards
const TechStackSection = () => {
  const technologies = [
    { name: "ROS 2", desc: "Robot Operating System", icon: "🔄" },
    { name: "GAZEBO", desc: "Physics Simulation", icon: "🎮" },
    { name: "NVIDIA ISAAC", desc: "GPU-Accelerated Robotics", icon: "⚡" },
    { name: "OPENAI", desc: "Language Models", icon: "🧠" },
    { name: "PYTHON", desc: "Primary Language", icon: "🐍" },
    { name: "PYTORCH", desc: "Deep Learning", icon: "🔥" }
  ];

  return (
    <section className="neon-tech">
      <div className="neon-container">
        <motion.div
          className="section-header section-header--center"
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="section-title">
            <span className="title-accent">///</span> TECH STACK
          </h2>
        </motion.div>

        <div className="tech-grid">
          {technologies.map((tech, index) => (
            <motion.div
              key={index}
              className="tech-card"
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: index * 0.1 }}
              whileHover={{ scale: 1.05, transition: { duration: 0.2 } }}
            >
              <div className="tech-icon">{tech.icon}</div>
              <div className="tech-name">{tech.name}</div>
              <div className="tech-desc">{tech.desc}</div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

// CTA Section with dramatic styling
const CTASection = () => {
  return (
    <section className="neon-cta">
      <div className="neon-container">
        <motion.div
          className="cta-content"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          <div className="cta-shapes">
            <div className="cta-shape cta-shape-1" />
            <div className="cta-shape cta-shape-2" />
          </div>

          <h2 className="cta-title">
            READY TO BUILD<br />
            <span className="title-accent">THE FUTURE?</span>
          </h2>

          <p className="cta-subtitle">
            Join hundreds of students mastering physical AI and humanoid robotics
          </p>

          <div className="cta-buttons">
            <Link to="/auth/signup" className="neon-button neon-button--primary neon-button--large">
              <span className="button-text">CREATE FREE ACCOUNT</span>
              <span className="button-arrow">→</span>
            </Link>
            <Link to="/auth/login" className="neon-button neon-button--outline neon-button--large">
              <span className="button-text">SIGN IN</span>
            </Link>
          </div>

          <div className="cta-note">
            No credit card required • Start learning immediately
          </div>
        </motion.div>
      </div>
    </section>
  );
};

// Footer with minimalist design
const Footer = () => {
  return (
    <footer className="neon-footer">
      <div className="neon-container">
        <div className="footer-content">
          <div className="footer-brand">
            <div className="footer-logo">PHYSICAL AI</div>
            <div className="footer-tagline">Master robotics with AI-powered learning</div>
          </div>

          <div className="footer-links">
            <Link to="/chapters" className="footer-link">Curriculum</Link>
            <Link to="/auth/signup" className="footer-link">Sign Up</Link>
            <Link to="/auth/login" className="footer-link">Login</Link>
          </div>
        </div>

        <div className="footer-bottom">
          <div className="footer-copyright">
            © {new Date().getFullYear()} Physical AI Platform
          </div>
          <div className="footer-tech">
            Built with React • Docusaurus • FastAPI
          </div>
        </div>
      </div>
    </footer>
  );
};

// Main page component
export default function Home(): JSX.Element {
  const { siteConfig } = useDocusaurusContext();

  return (
    <div className="neon-brutalism-page">
      <FuturisticNavbar />
      <HeroSection />
      <FeaturesSection />
      <CurriculumSection />
      <TechStackSection />
      <CTASection />
      <Footer />
    </div>
  );
}

import React from 'react';
import Layout from '@theme/Layout';
import { motion } from 'framer-motion';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';

// Inlined UI components
const Button: React.FC<{
  children: React.ReactNode;
  variant?: 'primary' | 'secondary';
  className?: string;
  href?: string;
}> = ({ children, variant = 'primary', className = '', href }) => {
  const baseClasses = 'px-6 py-3 rounded-full font-medium transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[#0f0f14] text-lg inline-block';

  const variantClasses = variant === 'primary'
    ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700 hover:scale-[1.03] hover:shadow-lg hover:shadow-blue-500/30'
    : 'glass-button glass-button--outline';

  const combinedClasses = `${baseClasses} ${variantClasses} ${className}`;

  if (href) {
    return (
      <Link to={href} className={combinedClasses}>
        {children}
      </Link>
    );
  }

  return (
    <motion.button
      whileHover={{ scale: 1.03 }}
      whileTap={{ scale: 0.98 }}
      className={combinedClasses}
    >
      {children}
    </motion.button>
  );
};

const GradientBackground: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div className={`absolute inset-0 -z-10 overflow-hidden ${className}`}>
      <div className="absolute inset-0 bg-[#0f0f14]"></div>
      <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-[150%] aspect-square rounded-full bg-gradient-radial from-blue-500/20 via-purple-500/10 to-transparent"></div>
    </div>
  );
};

// Inlined data
const homepageContent = {
  hero: {
    title: "Master Physical AI & Humanoid Robotics",
    subtitle: "The AI-powered learning platform that guides you through advanced robotics, AI systems, and humanoid development with personalized learning paths.",
    ctaButtons: {
      primary: "Get Started",
      secondary: "Explore Features"
    }
  },
  about: {
    title: "The Future of Robotics Education",
    description: "Our platform integrates cutting-edge technologies to deliver an unparalleled learning experience.",
    features: [
      {
        title: "AI-Powered Tutoring",
        description: "Personalized guidance tailored to your learning pace and style"
      },
      {
        title: "Simulation Environments",
        description: "Advanced physics-based simulators for safe robotics practice"
      },
      {
        title: "Structured Curriculum",
        description: "Comprehensive learning paths from basics to humanoid robotics"
      },
      {
        title: "Intelligent Personalization",
        description: "Real-time content adaptation based on your progress and goals"
      }
    ]
  },
  learningPillars: [
    {
      title: "AI Tutor",
      description: "Personalized learning with advanced AI that adapts to your pace and style."
    },
    {
      title: "Interactive Simulations",
      description: "State-of-the-art simulators to practice robotics without physical hardware."
    },
    {
      title: "Structured Curriculum",
      description: "Carefully designed learning paths from fundamentals to advanced robotics."
    },
    {
      title: "Personalized Chapters",
      description: "Content adjusted dynamically to match your learning needs and goals."
    },
    {
      title: "Urdu Translation",
      description: "Complete access to all content in multiple languages for global learning."
    },
    {
      title: "Intelligent RAG Chatbot",
      description: "Advanced conversational AI with access to all knowledge resources."
    }
  ],
  featuresOverview: {
    title: "Everything You Need to Master Robotics",
    subtitle: "Comprehensive technology stack designed to take you from beginner to advanced robotics practitioner with AI integration.",
    features: [
      {
        title: "ROS 2 Fundamentals",
        description: "Comprehensive coverage of Robot Operating System 2, the foundation for robotics applications."
      },
      {
        title: "Simulation Environments",
        description: "Advanced physics simulators that mirror real-world robotics challenges."
      },
      {
        title: "NVIDIA Isaac Integration",
        description: "Access to NVIDIA's robotics development platform and AI acceleration tools."
      },
      {
        title: "Vision-Language-Action Systems",
        description: "Learn to build robots that can see, understand, and interact with the physical world."
      },
      {
        title: "Reinforcement Learning",
        description: "State-of-the-art ML algorithms for robot learning and autonomous decision making."
      },
      {
        title: "Sim-to-Real Transfer",
        description: "Techniques for applying simulation-gained knowledge to real robots."
      },
      {
        title: "AI Orchestrator Architecture",
        description: "Advanced systems for coordinating complex AI capabilities in robotics applications."
      },
      {
        title: "Reusable Agent Skills",
        description: "Modular AI capabilities that can be combined and recombined for different tasks."
      },
      {
        title: "Modular AI System Design",
        description: "Building maintainable and scalable AI systems for robotics applications."
      },
      {
        title: "Authentication & Personalization",
        description: "Secure access with content tailored to your learning path and preferences."
      },
      {
        title: "Observability & Logging",
        description: "Advanced tools for monitoring, debugging, and improving AI robotics systems."
      }
    ]
  },
  footer: {
    title: "Master Physical AI & Humanoid Robotics",
    tagline: "The cutting-edge platform for AI-powered robotics education",
    links: {
      github: "https://github.com",
      contact: "mailto:contact@example.com",
      community: "/features"
    },
    copyright: "Physical AI Robotics"
  }
};

// Components
const HeroSection = () => {
  const { hero } = homepageContent;

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      <GradientBackground className="absolute inset-0 -z-10" />

      <div className="container mx-auto px-4 py-20 flex flex-col items-center justify-center text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-4xl mx-auto"
        >
          <motion.h1
            className="text-4xl md:text-6xl font-bold text-white mb-6 leading-tight"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            {hero.title}
          </motion.h1>

          <motion.p
            className="text-xl md:text-2xl text-gray-300 mb-10 max-w-3xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            {hero.subtitle}
          </motion.p>

          <motion.div
            className="flex flex-col sm:flex-row gap-4 justify-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            <Button variant="primary" href="/docs/intro">
              {hero.ctaButtons.primary}
            </Button>
            <Button variant="secondary" href="/features">
              {hero.ctaButtons.secondary}
            </Button>
          </motion.div>
        </motion.div>
      </div>

      {/* Floating elements for visual interest */}
      <motion.div
        className="absolute top-1/4 left-10 w-16 h-16 rounded-full bg-blue-500/20 blur-lg"
        animate={{
          y: [-10, 10, -10],
        }}
        transition={{
          duration: 6,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
      <motion.div
        className="absolute bottom-1/4 right-20 w-24 h-24 rounded-full bg-purple-500/20 blur-xl"
        animate={{
          y: [10, -10, 10],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 1,
        }}
      />
    </section>
  );
};

const AboutSection = () => {
  const { about } = homepageContent;

  return (
    <section className="py-20 bg-white/5 backdrop-blur-sm">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto text-center mb-16">
          <motion.h2
            className="text-3xl md:text-4xl font-bold text-white mb-4"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            {about.title}
          </motion.h2>
          <motion.p
            className="text-xl text-gray-300"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            {about.description}
          </motion.p>
        </div>

        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          {about.features.map((feature, index) => (
            <motion.div
              key={index}
              className="glass-card p-6 rounded-2xl"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
            >
              <h3 className="text-xl font-semibold text-white mb-3">{feature.title}</h3>
              <p className="text-gray-300">{feature.description}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

const PillarCard: React.FC<{
  title: string;
  description: string;
  index: number;
}> = ({ title, description, index }) => {
  return (
    <motion.div
      className="glass-card p-6 rounded-2xl hover:translate-y-[-8px] hover:shadow-2xl hover:shadow-purple-500/20 transition-all duration-300"
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6, delay: index * 0.1 }}
      whileHover={{ scale: 1.03 }}
    >
      <h3 className="text-xl font-semibold text-white mb-3">{title}</h3>
      <p className="text-gray-300">{description}</p>
    </motion.div>
  );
};

const LearningPillars = () => {
  return (
    <section className="py-20">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Core Learning Pillars</h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Six foundational components that will transform your approach to AI and robotics
          </p>
        </motion.div>

        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          {homepageContent.learningPillars.map((pillar, index) => (
            <PillarCard
              key={index}
              title={pillar.title}
              description={pillar.description}
              index={index}
            />
          ))}
        </motion.div>
      </div>
    </section>
  );
};

const FeaturesOverview = () => {
  return (
    <section className="py-20 bg-white/5 backdrop-blur-sm">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            {homepageContent.featuresOverview.title}
          </h2>
          <p className="text-xl text-gray-300 max-w-4xl mx-auto">
            {homepageContent.featuresOverview.subtitle}
          </p>
        </motion.div>

        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          {homepageContent.featuresOverview.features.map((feature, index) => (
            <motion.div
              key={index}
              className="glass-card p-6 rounded-2xl"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.05 }}
              whileHover={{ scale: 1.02 }}
            >
              <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
              <p className="text-gray-300 text-sm">{feature.description}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

const Footer = () => {
  const { footer } = homepageContent;

  return (
    <footer className="py-12 border-t border-white/10">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-6 md:mb-0">
            <h3 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              {footer.title}
            </h3>
            <p className="text-gray-400 mt-2">{footer.tagline}</p>
          </div>
          <div className="flex flex-col items-center md:items-end">
            <div className="flex space-x-6 mb-4">
              <Link to={footer.links.github} className="text-gray-400 hover:text-white transition-colors">
                GitHub
              </Link>
              <Link to={footer.links.contact} className="text-gray-400 hover:text-white transition-colors">
                Contact
              </Link>
              <Link to={footer.links.community} className="text-gray-400 hover:text-white transition-colors">
                Community
              </Link>
            </div>
            <p className="text-gray-500 text-sm">© {new Date().getFullYear()} {footer.copyright}. All rights reserved.</p>
          </div>
        </div>
      </div>
    </footer>
  );
};

// Main page component
export default function ModernHomepage(): JSX.Element {
  const { siteConfig } = useDocusaurusContext();

  return (
    <Layout
      title={homepageContent.hero.title}
      description={homepageContent.hero.subtitle}
    >
      <HeroSection />
      <AboutSection />
      <LearningPillars />
      <FeaturesOverview />
      <Footer />
    </Layout>
  );
}
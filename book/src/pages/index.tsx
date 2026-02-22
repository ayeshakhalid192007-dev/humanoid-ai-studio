import React from 'react';
import { motion } from 'framer-motion';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import { Button, Card } from '../components/ui';

// Data for the redesigned homepage
const homepageContent = {
  hero: {
    title: "Master Physical AI & Humanoid Robotics",
    subtitle: "The AI-powered learning platform that guides you through advanced robotics, AI systems, and humanoid development with personalized learning paths.",
    ctaButtons: {
      primary: "Get Started",
      secondary: "Explore Curriculum"
    }
  },
  features: [
    {
      icon: "🤖",
      title: "AI-Powered Tutoring",
      description: "Personalized guidance tailored to your learning pace and style with real-time feedback"
    },
    {
      icon: "🎮",
      title: "Simulation Environments",
      description: "Advanced physics-based simulators for safe practice in robotics and AI development"
    },
    {
      icon: "📚",
      title: "Structured Curriculum",
      description: "Comprehensive learning paths from basics to humanoid robotics engineering"
    },
    {
      icon: "🧠",
      title: "Smart Personalization",
      description: "Real-time content adjustment powered by AI to match your progress and goals"
    }
  ],
  pillars: [
    {
      icon: "👨‍💻",
      title: "AI Tutor",
      description: "Personalized learning experience with advanced AI that adapts to your learning style."
    },
    {
      icon: "🧪",
      title: "Interactive Simulations",
      description: "State-of-the-art simulators to practice robotics without physical hardware constraints."
    },
    {
      icon: "📋",
      title: "Structured Curriculum",
      description: "Carefully designed learning progressions from fundamentals to advanced robotics."
    },
    {
      icon: "🎯",
      title: "Personalized Chapters",
      description: "Dynamic content adjustment to match your learning needs and objectives."
    },
    {
      icon: "🌐",
      title: "Urdu Translation",
      description: "Complete access to curriculum content in multiple languages for global learners."
    },
    {
      icon: "💬",
      title: "Intelligent RAG Chatbot",
      description: "Advanced conversational AI with access to all knowledge resources instantly."
    }
  ],
  curriculum: {
    items: [
      {
        title: "ROS 2 Fundamentals",
        description: "Deep dive into the Robot Operating System 2 framework for robotics applications."
      },
      {
        title: "Simulation Environments",
        description: "Advanced simulators that mirror real-world robotics challenges safely."
      },
      {
        title: "NVIDIA Isaac Integration",
        description: "Hands-on experience with NVIDIA's robotics development platform and AI accelerators."
      },
      {
        title: "Vision-Language-Action Systems",
        description: "Build robots that perceive, understand, and interact with the physical world."
      },
      {
        title: "Reinforcement Learning",
        description: "Advanced ML algorithms for robot learning and autonomous decision making."
      },
      {
        title: "Sim-to-Real Transfer",
        description: "Techniques for applying simulation-knowledge to real robot deployment."
      },
      {
        title: "AI Orchestrator Architecture",
        description: "Advanced systems for coordinating complex AI capabilities in robotics."
      },
      {
        title: "Reusable Agent Skills",
        description: "Modular AI capabilities for combining and recombining for different tasks."
      }
    ]
  },
  testimonials: [
    {
      name: 'Sarah Chen',
      role: 'Robotics Engineer at Boston Dynamics',
      quote: 'The holistic approach changed how I learn robotics. After completing the curriculum, I advanced significantly in my career. The hands-on projects were transformative.',
    },
    {
      name: 'Marcus Johnson',
      role: 'AI Research Scientist',
      quote: 'As an ML professional exploring robotics, this platform perfectly bridged the gap. The Vision-Language-Action module showed me how to connect AI models to real robot actions.',
    },
    {
      name: 'Elena Rodriguez',
      role: 'Graduate Student, Stanford',
      quote: 'The AI assistant transforms learning by providing instant explanations with citations. I saved countless hours researching complex concepts and algorithms.',
    },
  ],
  footer: {
    title: "Master Physical AI & Humanoid Robotics",
    tagline: "The cutting-edge platform for AI-powered robotics education",
    copyright: "Physical AI Robotics"
  }
};

const HeroSection = () => {
  const { hero } = homepageContent;

  return (
    <section className="fm-hero">
      <div className="fm-hero__container relative">
        <motion.div
          className="fm-animated-element"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.1 }}
        >
          <h1 className="fm-h1">
            {hero.title}
          </h1>
        </motion.div>

        <motion.p
          className="fm-body-xl fm-lead fm-animated-element"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          {hero.subtitle}
        </motion.p>

        <motion.div
          className="fm-hero__cta fm-animated-element flex flex-col sm:flex-row items-center gap-4"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
        >
          <div className="flex flex-col sm:flex-row gap-4">
            <Button variant="primary" size="lg" href="/auth/signup">
              {hero.ctaButtons.primary}
            </Button>
            <Button variant="outline" size="lg" href="/chapters">
              {hero.ctaButtons.secondary}
            </Button>
          </div>
          <div className="text-center sm:text-left mt-2 sm:mt-0">
            <Link to="/auth/login" className="text-fm-accent-primary hover:underline inline-block">
              Already have an account? Sign in
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

const FeaturesSection = () => {
  return (
    <section id="features" className="fm-section fm-container">
      <motion.div
        className="text-center mb-16"
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
      >
        <h2 className="fm-h2">Advanced Learning Experience</h2>
        <p className="fm-body-lg fm-lead max-w-2xl mx-auto mt-4">
          Our platform integrates cutting-edge technologies to deliver an unparalleled learning experience that adapts to you.
        </p>
      </motion.div>

      <div className="fm-features-grid fm-features-grid--2">
        {homepageContent.features.map((feature, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: index * 0.1 }}
            className="fm-feature-card relative overflow-hidden group"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div className="fm-feature-card__icon relative z-10 group-hover:scale-110 transition-transform duration-300">
              {feature.icon}
            </div>
            <h3 className="fm-feature-card__title relative z-10">{feature.title}</h3>
            <p className="fm-feature-card__description relative z-10">{feature.description}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
};

const LearningPillars = () => {
  return (
    <section id="curriculum" className="fm-section fm-container">
      <motion.div
        className="text-center mb-16"
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
      >
        <h2 className="fm-h2">Core Learning Pillars</h2>
        <p className="fm-body-lg fm-lead max-w-3xl mx-auto mt-4">
          Six foundational components that will transform your approach to AI and robotics
        </p>
      </motion.div>

      <div className="fm-features-grid fm-features-grid--3">
        {homepageContent.pillars.map((pillar, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: index * 0.1 }}
          >
            <Card variant="elevated" hoverEffect={true}>
              <div className="fm-flex-center">
                <div className="fm-pillar-card__icon">{pillar.icon}</div>
              </div>
              <h3 className="fm-h4 text-center">{pillar.title}</h3>
              <p className="fm-body-md text-center mt-2">{pillar.description}</p>
            </Card>
          </motion.div>
        ))}
      </div>
    </section>
  );
};

const CurriculumOverview = () => {
  return (
    <section className="fm-section fm-container">
      <motion.div
        className="text-center mb-16"
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
      >
        <h2 className="fm-h2">Complete Learning Stack</h2>
        <p className="fm-body-lg fm-lead max-w-4xl mx-auto mt-4">
          Comprehensive technology curriculum designed to take you from beginner to advanced robotics practitioner with AI integration.
        </p>
      </motion.div>

      <div className="fm-features-grid fm-features-grid--2">
        {homepageContent.curriculum.items.map((item, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: index * 0.05 }}
          >
            <Card variant="solid" hoverEffect={true} className="h-full">
              <h3 className="fm-h4">{item.title}</h3>
              <p className="fm-body-md mt-2">{item.description}</p>
            </Card>
          </motion.div>
        ))}
      </div>
    </section>
  );
};

const TestimonialsSection = () => {
  return (
    <section id="testimonials" className="fm-section fm-container">
      <motion.div
        className="text-center mb-16"
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
      >
        <h2 className="fm-h2">Student Success Stories</h2>
        <p className="fm-body-lg fm-lead max-w-3xl mx-auto mt-4">
          Join hundreds of students and professionals advancing their robotics careers
        </p>
      </motion.div>

      <div className="fm-testimonial-grid">
        {homepageContent.testimonials.map((testimonial, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: index * 0.1 }}
          >
            <Card className="h-full">
              <div className="fm-testimonial-card">
                <p className="fm-testimonial-text">
                  "{testimonial.quote}"
                </p>
                <div className="fm-testimonial-author">
                  <span className="fm-testimonial-name">{testimonial.name}</span>
                  <span className="fm-testimonial-role">{testimonial.role}</span>
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

      <motion.div
        className="text-center mt-12 space-y-4 bg-gradient-to-r from-purple-900/20 to-blue-900/20 p-8 rounded-2xl border border-white/10"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6, delay: 0.3 }}
      >
        <h3 className="fm-h3 text-white">Ready to start your journey?</h3>
        <p className="fm-body-lg max-w-md mx-auto text-fm-gray-200">
          Join our community of robotics and AI pioneers today
        </p>

        <div className="flex flex-col sm:flex-row justify-center items-center gap-4 mt-6">
          <Link
            to="/auth/signup"
            className="inline-block"
          >
            <Button variant="primary" size="lg" className="shadow-lg">
              Create Your Account
            </Button>
          </Link>

          <div className="text-center">
            <Link to="/auth/login" className="text-fm-accent-primary hover:underline inline-block">
              Sign In to Existing Account →
            </Link>
          </div>
        </div>
      </motion.div>
    </section>
  );
};

const TechnologyStack = () => {
  const techStack = [
    {
      title: "ROS 2 Ecosystem",
      description: "Leverage the power of Robot Operating System 2 for distributed robotics applications.",
      icon: "🔄"
    },
    {
      title: "NVIDIA Isaac Sim",
      description: "High-fidelity simulation environment for testing and training robotic systems.",
      icon: "🎮"
    },
    {
      title: "OpenAI Integration",
      description: "Advanced language models for natural human-robot interaction and reasoning.",
      icon: "🧠"
    },
    {
      title: "Computer Vision",
      description: "State-of-the-art perception systems for real-world environment understanding.",
      icon: "👁️"
    }
  ];

  return (
    <section className="fm-section fm-container">
      <motion.div
        className="text-center mb-16"
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
      >
        <h2 className="fm-h2">Advanced Technology Stack</h2>
        <p className="fm-body-lg fm-lead max-w-3xl mx-auto mt-4">
          Cutting-edge tools and frameworks that power our robotics and AI education platform
        </p>
      </motion.div>

      <div className="fm-features-grid fm-features-grid--2">
        {techStack.map((tech, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: index * 0.1 }}
          >
            <Card variant="glass-3xl" hoverEffect={true} glowEffect={true}>
              <div className="fm-flex-center mb-4">
                <div className="text-3xl">{tech.icon}</div>
              </div>
              <h3 className="fm-h4 text-center">{tech.title}</h3>
              <p className="fm-body-md text-center mt-2">{tech.description}</p>
            </Card>
          </motion.div>
        ))}
      </div>
    </section>
  );
};

const Footer = () => {
  const { footer } = homepageContent;

  return (
    <footer className="fm-footer">
      <div className="fm-footer__container">
        <div className="fm-flex-between">
          <div>
            <h3 className="fm-footer__section-title">
              {footer.title}
            </h3>
            <p className="fm-body-sm">{footer.tagline}</p>
          </div>
          <div className="fm-footer__copyright">
            © {new Date().getFullYear()} {footer.copyright}. All rights reserved.
          </div>
        </div>
      </div>
    </footer>
  );
};

// Add a special sign-in CTA section
const SignInCTA = () => {
  return (
    <section className="fm-section bg-gradient-to-r from-blue-900/30 to-purple-900/30 border-y border-white/10 py-16">
      <div className="fm-container text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="max-w-3xl mx-auto"
        >
          <h2 className="fm-h2 text-white mb-4">Ready to Transform Your Learning?</h2>
          <p className="fm-body-lg text-fm-gray-200 mb-8 max-w-2xl mx-auto">
            Sign in to access personalized curriculum, track your progress, and engage with our AI-powered learning assistant.
          </p>

          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link to="/auth/signup">
              <Button variant="primary" size="lg" className="shadow-lg">
                Create Free Account
              </Button>
            </Link>
            <Link to="/auth/login">
              <Button variant="secondary" size="lg">
                Already Have an Account? Sign In
              </Button>
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

// Main page component
export default function Home(): JSX.Element {
  const { siteConfig } = useDocusaurusContext();

  return (
    <>
      <HeroSection />
      <FeaturesSection />
      <div className="fm-gradient-line"></div>
      <LearningPillars />
      <div className="fm-gradient-line"></div>
      <CurriculumOverview />
      <div className="fm-gradient-line"></div>
      <SignInCTA />
      <div className="fm-gradient-line"></div>
      <TestimonialsSection />
      <Footer />
    </>
  );
}
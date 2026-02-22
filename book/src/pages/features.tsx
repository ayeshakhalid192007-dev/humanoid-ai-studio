import React from 'react';
import { motion } from 'framer-motion';
import Link from '@docusaurus/Link';
import { Button, Card } from '../components/ui';
import { AppLayout } from '../components/Layout/AppLayout';
import ErrorBoundary from '../components/ErrorBoundary';


interface Feature {
  title: string;
  description: string;
  icon: JSX.Element;
}

const features: Feature[] = [
  {
    title: 'ROS 2 Fundamentals',
    description:
      'Master the Robot Operating System 2 with hands-on projects. Learn nodes, topics, services, actions, and URDF robot models using the modern Humble distribution.',
    icon: (
      <svg className="w-10 h-10 text-blue-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="3" />
        <path d="M12 1v6M12 17v6M4.22 4.22l4.24 4.24M15.54 15.54l4.24 4.24M1 12h6M17 12h6M4.22 19.78l4.24-4.24M15.54 8.46l4.24-4.24" />
      </svg>
    ),
  },
  {
    title: 'Simulation Environments',
    description:
      'Build and test robots in photorealistic 3D environments. Configure physics engines, sensors, and controllers using Gazebo, Unity, and NVIDIA Isaac Sim without risking real hardware.',
    icon: (
      <svg className="w-8 h-8 text-purple-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10" />
        <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
      </svg>
    ),
  },
  {
    title: 'NVIDIA Isaac Integration',
    description:
      'Access to NVIDIA Isaac ROS packages, Isaac Sim, and AI acceleration tools for advanced robotics applications in perception, navigation, and control.',
    icon: (
      <svg className="w-8 h-8 text-green-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
        <polyline points="22,6 12,13 2,6" />
      </svg>
    ),
  },
  {
    title: 'Vision-Language-Action Systems',
    description:
      'Learn to build robots that can see, understand, and interact with the physical world - from computer vision to language understanding to action execution.',
    icon: (
      <svg className="w-8 h-8 text-indigo-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polygon points="3 11 22 2 13 21 11 13 3 11" />
      </svg>
    ),
  },
  {
    title: 'Reinforcement Learning',
    description:
      'State-of-the-art ML algorithms for robot learning and autonomous decision making, including Q-learning, policy gradients, and other advanced techniques.',
    icon: (
      <svg className="w-8 h-8 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
        <circle cx="9" cy="7" r="4" />
        <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
        <path d="M16 3.13a4 4 0 0 1 0 7.75" />
      </svg>
    ),
  },
  {
    title: 'Sim-to-Real Transfer',
    description:
      'Techniques for applying simulation-gained knowledge to real robots, including domain randomization, sim-to-real gap minimization, and robustness validation.',
    icon: (
      <svg className="w-8 h-8 text-violet-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <line x1="12" y1="5" x2="12" y2="19" />
        <polyline points="19 12 12 19 5 12" />
      </svg>
    ),
  },
  {
    title: 'AI Orchestrator Architecture',
    description:
      'Advanced systems for coordinating complex AI capabilities in robotics applications, ensuring seamless integration and scalable design.',
    icon: (
      <svg className="w-8 h-8 text-cyan-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
        <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
      </svg>
    ),
  },
  {
    title: 'Reusable Agent Skills',
    description:
      'Modular AI capabilities that can be combined and recombined for different tasks, enabling rapid prototyping and robust system design.',
    icon: (
      <svg className="w-8 h-8 text-amber-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
        <line x1="3" y1="9" x2="21" y2="9" />
        <line x1="9" y1="21" x2="9" y2="9" />
      </svg>
    ),
  },
  {
    title: 'Modular AI System Design',
    description:
      'Building maintainable and scalable AI systems for robotics applications with clean interfaces, proper abstraction, and testable components.',
    icon: (
      <svg className="w-8 h-8 text-pink-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="11" cy="11" r="8" />
        <path d="M21 21l-4.35-4.35" />
      </svg>
    ),
  },
  {
    title: 'Authentication & Personalization',
    description:
      'Secure access with content tailored to your learning path and preferences, ensuring a focused and efficient learning experience. Sign up to unlock bonus features!',
    icon: (
      <svg className="w-8 h-8 text-rose-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
        <circle cx="8.5" cy="7" r="4" />
        <line x1="20" y1="8" x2="20" y2="14" />
        <line x1="23" y1="11" x2="17" y2="11" />
      </svg>
    ),
  },
  {
    title: 'Intelligent RAG Chatbot',
    description:
      'Advanced conversational AI with access to all knowledge resources - get instant answers, explanations, and guidance with citations to specific content.',
    icon: (
      <svg className="w-8 h-8 text-teal-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        <circle cx="9" cy="10" r="1" fill="currentColor" />
        <circle cx="12" cy="10" r="1" fill="currentColor" />
        <circle cx="15" cy="10" r="1" fill="currentColor" />
      </svg>
    ),
  },
  {
    title: 'Predict-Execute-Reflect Methodology',
    description:
      'Our unique learning approach that builds deep intuition. Form hypotheses before running code, observe results, and analyze the gap to cement understanding.',
    icon: (
      <svg className="w-8 h-8 text-lime-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M18 12h.01M12 12h.01M6 12h.01M18 6h.01M12 6h.01M6 6h.01M18 18h.01M12 18h.01M6 18h.01" />
      </svg>
    ),
  },
];

function FeatureCard({
  title,
  description,
  icon,
  index
}: Feature & { index: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6, delay: index * 0.05 }}
    >
      <Card variant="glass" className="p-6 h-full flex flex-col items-center text-center" hoverEffect={true}>
        <div className="flex items-center justify-center w-12 h-12 rounded-full bg-white/5 mb-5">
          {icon}
        </div>
        <h3 className="h4 font-semibold text-white mb-3">{title}</h3>
        <p className="body-md text-gray-300 mb-4 flex-grow">{description}</p>
        <Button variant="primary">
          Learn More
        </Button>
      </Card>
    </motion.div>
  );
}

export default function Features(): JSX.Element {
  return (
    <AppLayout title="Features" description="Explore the features of the Physical AI Platform" background="default">
      <ErrorBoundary>
        {/* Hero section */}
        <section className="py-24 relative overflow-hidden">
          <div className="container mx-auto px-4 relative z-10">
            <motion.div
              className="max-w-4xl mx-auto text-center"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <h1 className="h1 text-gradient-blue-purple mb-6">
                Platform Features
              </h1>
              <p className="body-lg text-gray-300 max-w-2xl mx-auto mb-8">
                Everything you need to build intelligent robots, from fundamentals to cutting-edge AI integration.
              </p>
            </motion.div>
          </div>
        </section>

        {/* Features grid section */}
        <section className="py-24">
          <div className="container mx-auto px-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {features.map((feature, index) => (
                <FeatureCard key={index} {...feature} index={index} />
              ))}
            </div>
          </div>
        </section>
      </ErrorBoundary>
    </AppLayout>
  );
}
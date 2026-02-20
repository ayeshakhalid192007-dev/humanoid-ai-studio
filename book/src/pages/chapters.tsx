import React from 'react';
import Layout from '@theme/Layout';
import { motion } from 'framer-motion';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import { Card, Badge } from '../components/ui';

// Define the chapter structure
interface ChapterCardProps {
  title: string;
  description: string;
  path: string;
  duration?: string;
  difficulty?: 'Beginner' | 'Intermediate' | 'Advanced' | 'Expert';
  module?: string;
  index: number;
}

const ChapterCard: React.FC<ChapterCardProps> = ({
  title,
  description,
  path,
  duration = '30-45 min',
  difficulty = 'Intermediate',
  module,
  index
}) => {
  // Difficulty-based styling
  const difficultyColors = {
    Beginner: 'bg-green-500/20 text-green-400 border-green-500/30',
    Intermediate: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    Advanced: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    Expert: 'bg-red-500/20 text-red-400 border-red-500/30',
  };

  return (
    <motion.div
      className="hover-lift flex flex-col h-full"
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6, delay: index * 0.1 }}
      whileHover={{ scale: 1.04 }}
    >
      <Card variant="glass-3xl" className="p-6 flex flex-col h-full hoverEffect={false}">
        <div className="flex-1">
          {module && (
            <Badge variant="secondary" className="text-xs mb-3">
              {module}
            </Badge>
          )}
          <h3 className="h4 font-semibold text-white mb-3">{title}</h3>
          <p className="body-md text-gray-300 mb-4">{description}</p>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-4 mt-4 pt-4 border-t border-white/10">
          <div className="flex items-center gap-2">
            <svg className="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <span className="text-sm text-gray-400">{duration}</span>
          </div>

          <div className="flex items-center gap-2">
            <Badge variant={difficulty.toLowerCase() as 'beginner' | 'intermediate' | 'advanced' | 'expert'}
                   className="text-xs">
              {difficulty}
            </Badge>
          </div>
        </div>

        <div className="mt-4">
          <Link to={path} className="glass-button--primary w-full text-center">
            Start Learning
          </Link>
        </div>
      </Card>
    </motion.div>
  );
};

const ChaptersPage = () => {
  const { siteConfig } = useDocusaurusContext();

  // Chapter data - based off the documentation structure from sidebars.js
  const allChapters = [
    {
      title: 'Getting Started',
      description: 'Introduction to the Physical AI & Humanoid Robotics platform and curriculum overview.',
      path: '/docs/intro',
      duration: '15 min',
      difficulty: 'Beginner' as const,
      module: 'Welcome',
    },
    {
      title: 'Lab Architecture',
      description: 'Understanding the architecture and components of the learning platform.',
      path: '/docs/lab-architecture/intro',
      duration: '25 min',
      difficulty: 'Beginner',
      module: 'Foundation',
    },
    {
      title: 'ROS 2 Middleware Introduction',
      description: 'Learn the fundamentals of Robot Operating System 2.',
      path: '/docs/module1/intro',
      duration: '30 min',
      difficulty: 'Beginner',
      module: 'Module 1',
    },
    {
      title: 'ROS 2 Basics',
      description: 'Core concepts of ROS 2 including packages, nodes, and basic architecture.',
      path: '/docs/module1/lesson1-ros2-basics',
      duration: '45 min',
      difficulty: 'Beginner',
      module: 'Module 1',
    },
    {
      title: 'Nodes & Topics',
      description: 'Understanding ROS 2 nodes, topics, and messaging system.',
      path: '/docs/module1/lesson2-nodes-topics',
      duration: '50 min',
      difficulty: 'Intermediate',
      module: 'Module 1',
    },
    {
      title: 'URDF Models',
      description: 'Creating and working with Unified Robot Description Format.',
      path: '/docs/module1/lesson2-urdf-models',
      duration: '55 min',
      difficulty: 'Intermediate',
      module: 'Module 1',
    },
    {
      title: 'Services & Actions',
      description: 'Learn how to implement synchronous and asynchronous communication.',
      path: '/docs/module1/lesson4-services',
      duration: '40 min',
      difficulty: 'Intermediate',
      module: 'Module 1',
    },
    {
      title: 'Visualization Tools',
      description: 'Using ROS 2 tools for data visualization and debugging.',
      path: '/docs/module1/lesson5-rqt-visualization',
      duration: '35 min',
      difficulty: 'Intermediate',
      module: 'Module 1',
    },
    {
      title: 'ROS 2 Exercises',
      description: 'Practical exercises to reinforce ROS 2 concepts.',
      path: '/docs/module1/exercises',
      duration: '60 min',
      difficulty: 'Intermediate',
      module: 'Module 1',
    },
    {
      title: 'Simulation Environments Introduction',
      description: 'Introduction to various simulation tools in robotics.',
      path: '/docs/module2/intro',
      duration: '20 min',
      difficulty: 'Beginner',
      module: 'Module 2',
    },
    {
      title: 'Gazebo Setup',
      description: 'Setting up and configuring Gazebo for robotics simulation.',
      path: '/docs/module2/lesson1-gazebo-setup',
      duration: '40 min',
      difficulty: 'Intermediate',
      module: 'Module 2',
    },
    {
      title: 'Physics Engines',
      description: 'Understanding physics simulation and different engines.',
      path: '/docs/module2/lesson2-physics-engines',
      duration: '45 min',
      difficulty: 'Intermediate',
      module: 'Module 2',
    },
    {
      title: 'Sensor Simulation',
      description: 'Implementing various sensors in simulation environments.',
      path: '/docs/module2/lesson3-sensor-simulation',
      duration: '55 min',
      difficulty: 'Advanced',
      module: 'Module 2',
    },
    {
      title: 'Unity & Isaac Sim',
      description: 'Advanced simulation with Unity and NVIDIA Isaac.',
      path: '/docs/module2/lesson4-unity-isaac-sim',
      duration: '60 min',
      difficulty: 'Advanced',
      module: 'Module 2',
    },
    {
      title: 'Simulation Debugging',
      description: 'Techniques for debugging simulation issues.',
      path: '/docs/module2/lesson5-debugging-simulation',
      duration: '40 min',
      difficulty: 'Advanced',
      module: 'Module 2',
    },
    {
      title: 'Simulation Exercises',
      description: 'Practical exercises to apply simulation concepts.',
      path: '/docs/module2/exercises',
      duration: '60 min',
      difficulty: 'Expert',
      module: 'Module 2',
    },
    {
      title: 'Perception & Navigation Introduction',
      description: 'Overview of perception and navigation systems.',
      path: '/docs/module3/intro',
      duration: '25 min',
      difficulty: 'Beginner',
      module: 'Module 3',
    },
    {
      title: 'Visual SLAM Fundamentals',
      description: 'Learn the fundamentals of Visual SLAM systems.',
      path: '/docs/module3/lesson1-vslam-fundamentals',
      duration: '50 min',
      difficulty: 'Advanced',
      module: 'Module 3',
    },
    {
      title: 'Isaac ROS vSLAM',
      description: 'Using NVIDIA Isaac ROS packages for visual SLAM.',
      path: '/docs/module3/lesson2-isaac-ros-vslam',
      duration: '60 min',
      difficulty: 'Expert',
      module: 'Module 3',
    },
    {
      title: 'CPU SLAM Fallback',
      description: 'Implementing CPU-based SLAM alternatives.',
      path: '/docs/module3/lesson3-cpu-slam-fallback',
      duration: '55 min',
      difficulty: 'Expert',
      module: 'Module 3',
    },
    {
      title: 'Navigation 2 Stack',
      description: 'Understanding and implementing the Navigation2 system.',
      path: '/docs/module3/lesson4-nav2-stack',
      duration: '65 min',
      difficulty: 'Expert',
      module: 'Module 3',
    },
    {
      title: 'Obstacle Avoidance',
      description: 'Implementing autonomous obstacle detection and avoidance.',
      path: '/docs/module3/lesson5-obstacle-avoidance',
      duration: '50 min',
      difficulty: 'Expert',
      module: 'Module 3',
    },
    {
      title: 'RViz Visualization',
      description: 'Advanced visualization with Robot Visualization (RViz).',
      path: '/docs/module3/lesson6-rviz-visualization',
      duration: '45 min',
      difficulty: 'Intermediate',
      module: 'Module 3',
    },
    {
      title: 'Perception Exercises',
      description: 'Applying perception and navigation concepts.',
      path: '/docs/module3/exercises',
      duration: '70 min',
      difficulty: 'Expert',
      module: 'Module 3',
    },
    {
      title: 'Voice-to-Action Introduction',
      description: 'Introduction to voice-controlled robot systems.',
      path: '/docs/module4/intro',
      duration: '30 min',
      difficulty: 'Intermediate',
      module: 'Module 4',
    },
    {
      title: 'VLA Architecture',
      description: 'Understanding Vision-Language-Action system architecture.',
      path: '/docs/module4/lesson1-vla-architecture',
      duration: '70 min',
      difficulty: 'Expert',
      module: 'Module 4',
    },
    {
      title: 'Speech Transcription',
      description: 'Implementing robust speech-to-text functionality.',
      path: '/docs/module4/lesson2-speech-transcription',
      duration: '55 min',
      difficulty: 'Advanced',
      module: 'Module 4',
    },
    {
      title: 'LLM Integration',
      description: 'Connecting large language models for robot instruction.',
      path: '/docs/module4/lesson3-llm-integration',
      duration: '60 min',
      difficulty: 'Expert',
      module: 'Module 4',
    },
    {
      title: 'Action Validation',
      description: 'Validating voice commands before execution.',
      path: '/docs/module4/lesson4-action-validation',
      duration: '50 min',
      difficulty: 'Advanced',
      module: 'Module 4',
    },
    {
      title: 'ROS 2 Action Servers',
      description: 'Implementing action servers for long-running tasks.',
      path: '/docs/module4/lesson5-ros2-action-servers',
      duration: '65 min',
      difficulty: 'Expert',
      module: 'Module 4',
    },
    {
      title: 'Latency Optimization',
      description: 'Optimizing response time for better UX.',
      path: '/docs/module4/lesson6-latency-optimization',
      duration: '45 min',
      difficulty: 'Advanced',
      module: 'Module 4',
    },
    {
      title: 'VLA Debugging',
      description: 'Debugging complex Voice-to-Action systems.',
      path: '/docs/module4/lesson7-debugging-vla',
      duration: '60 min',
      difficulty: 'Expert',
      module: 'Module 4',
    },
    {
      title: 'VLA Exercises',
      description: 'Practical exercises with voice-to-action systems.',
      path: '/docs/module4/exercises',
      duration: '90 min',
      difficulty: 'Expert',
      module: 'Module 4',
    },
    {
      title: 'Capstone Project Introduction',
      description: 'Overview of the final project combining all skills.',
      path: '/docs/capstone/intro',
      duration: '30 min',
      difficulty: 'Intermediate',
      module: 'Capstone',
    },
    {
      title: 'Project Requirements',
      description: 'Detailed requirements for the capstone project.',
      path: '/docs/capstone/project-requirements',
      duration: '40 min',
      difficulty: 'Intermediate',
      module: 'Capstone',
    },
    {
      title: 'Implementation Guide',
      description: 'Step-by-step guide for completing the project.',
      path: '/docs/capstone/implementation-guide',
      duration: '80 min',
      difficulty: 'Expert',
      module: 'Capstone',
    },
    {
      title: 'Project Debugging',
      description: 'Debugging strategies for complex robotics systems.',
      path: '/docs/capstone/debugging-checklist',
      duration: '50 min',
      difficulty: 'Expert',
      module: 'Capstone',
    },
  ];

  return (
    <Layout title="Chapters" description="All learning chapters in the Physical AI curriculum organized by difficulty and module">
      <div className="bg-[#0f0f14] min-h-screen">
        {/* Hero section */}
        <section className="py-20 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-futuristic"></div>
          <div className="absolute inset-0 bg-[#0f0f14]/80"></div>
          <div className="container mx-auto px-4 relative z-10">
            <motion.div
              className="max-w-4xl mx-auto text-center"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <h1 className="h1 text-gradient-blue-purple mb-6">
                Learning Chapters
              </h1>
              <p className="body-lg text-gray-300 max-w-2xl mx-auto">
                Explore our comprehensive curriculum designed to take you from ROS 2 fundamentals to advanced humanoid robotics
              </p>
            </motion.div>
          </div>
        </section>

        {/* Chapters grid */}
        <section className="py-20">
          <div className="container mx-auto px-4">
            <div className="mb-12 text-center">
              <h2 className="h2 text-white mb-4">Complete Curriculum</h2>
              <p className="body-lg text-gray-300 max-w-3xl mx-auto">
                All chapters organized by module with difficulty ratings and estimated completion times
              </p>
            </div>

            <motion.div
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6 }}
            >
              {allChapters.map((chapter, index) => (
                <ChapterCard
                  key={index}
                  title={chapter.title}
                  description={chapter.description}
                  path={chapter.path}
                  duration={chapter.duration}
                  difficulty={chapter.difficulty}
                  module={chapter.module}
                  index={index}
                />
              ))}
            </motion.div>
          </div>
        </section>
      </div>
    </Layout>
  );
};

export default ChaptersPage;
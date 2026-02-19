/**
 * Creating a sidebar enables you to:
 * - create an ordered group of docs
 * - render a sidebar for each doc of that group
 * - provide next/previous navigation
 *
 * The sidebars can be generated from the filesystem, or explicitly defined here.
 *
 * Create as many sidebars as you want.
 */

// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    {
      type: 'doc',
      id: 'intro',
      label: 'Getting Started',
    },
    {
      type: 'category',
      label: 'Lab Architecture',
      collapsed: false,
      items: [
        'lab-architecture/intro',
      ],
    },
    {
      type: 'category',
      label: 'Module 1: ROS 2 Middleware',
      collapsed: false,
      items: [
        'module1/intro',
        'module1/lesson1-ros2-basics',
        'module1/lesson2-nodes-topics',
        'module1/lesson2-urdf-models',
        'module1/lesson4-services',
        'module1/lesson5-rqt-visualization',
        'module1/exercises',
      ],
    },
    {
      type: 'category',
      label: 'Module 2: Simulation Environments',
      collapsed: true,
      items: [
        'module2/intro',
        'module2/lesson1-gazebo-setup',
        'module2/lesson2-physics-engines',
        'module2/lesson3-sensor-simulation',
        'module2/lesson4-unity-isaac-sim',
        'module2/lesson5-debugging-simulation',
        'module2/exercises',
      ],
    },
    {
      type: 'category',
      label: 'Module 3: Perception & Navigation',
      collapsed: true,
      items: [
        'module3/intro',
        'module3/lesson1-vslam-fundamentals',
        'module3/lesson2-isaac-ros-vslam',
        'module3/lesson3-cpu-slam-fallback',
        'module3/lesson4-nav2-stack',
        'module3/lesson5-obstacle-avoidance',
        'module3/lesson6-rviz-visualization',
        'module3/exercises',
      ],
    },
    {
      type: 'category',
      label: 'Module 4: Voice-to-Action Pipeline',
      collapsed: true,
      items: [
        'module4/intro',
        'module4/lesson1-vla-architecture',
        'module4/lesson2-speech-transcription',
        'module4/lesson3-llm-integration',
        'module4/lesson4-action-validation',
        'module4/lesson5-ros2-action-servers',
        'module4/lesson6-latency-optimization',
        'module4/lesson7-debugging-vla',
        'module4/exercises',
      ],
    },
    {
      type: 'category',
      label: 'Capstone Project',
      collapsed: true,
      items: [
        'capstone/intro',
        'capstone/project-requirements',
        'capstone/implementation-guide',
        'capstone/debugging-checklist',
      ],
    },
  ],
};

module.exports = sidebars;

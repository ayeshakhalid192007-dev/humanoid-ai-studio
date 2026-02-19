/**
 * SuggestedQuestions - Context-aware question prompts for ChatbotWidget
 *
 * Displays suggested questions based on current page metadata (module, lesson).
 * Helps students discover relevant questions without prior knowledge.
 *
 * Task: T035 (FR-056)
 */
import React from 'react';
import styles from './styles.module.css';

interface SuggestedQuestionsProps {
  onSelectQuestion: (question: string) => void;
  disabled?: boolean;
}

interface ModuleQuestions {
  general: string[];
  lessons: Record<string, string[]>;
}

// Context-aware questions organized by module and lesson
const QUESTIONS_BY_MODULE: Record<string, ModuleQuestions> = {
  module1: {
    general: [
      'What is ROS 2 and why is it used in robotics?',
      'How do I set up a ROS 2 workspace?',
      'What are the main differences between ROS 1 and ROS 2?',
    ],
    lessons: {
      'ros2-basics': [
        'How do I install ROS 2 Humble on Ubuntu?',
        'What is a ROS 2 package and how do I create one?',
        'How do talker and listener nodes communicate?',
      ],
      'nodes-topics': [
        'What is the difference between a node and a topic?',
        'How do I configure QoS policies for reliable communication?',
        'What ros2 topic commands are most useful for debugging?',
      ],
      'urdf-models': [
        'What are URDF joint types and when to use each?',
        'How do I define joint limits in URDF?',
        'What is the difference between visual and collision geometry?',
      ],
      services: [
        'When should I use services vs topics?',
        'How do I create a custom service definition?',
        'What is the request/response pattern in ROS 2 services?',
      ],
      'rqt-visualization': [
        'How do I visualize node connections with rqt_graph?',
        'What RQT plugins are useful for debugging?',
        'How do I monitor topic messages in real-time?',
      ],
    },
  },
  module2: {
    general: [
      'How do I set up Gazebo for robot simulation?',
      'What physics engines does Gazebo support?',
      'How do I spawn a robot model in Gazebo?',
    ],
    lessons: {
      'gazebo-setup': [
        'How do I install Gazebo and ros_gz_bridge?',
        'What is SDF and how does it relate to URDF?',
        'How do I configure physics parameters in Gazebo?',
      ],
      'physics-engines': [
        'How does gravity affect robot stability in simulation?',
        'What friction parameters should I set for realistic movement?',
        'How do I tune joint dynamics for stable control?',
      ],
      'sensor-simulation': [
        'How do I add a camera sensor to my robot in Gazebo?',
        'What is the difference between RGB and depth cameras?',
        'How do I configure lidar parameters in simulation?',
      ],
      'unity-isaac-sim': [
        'What are the benefits of using Isaac Sim over Gazebo?',
        'How do I set up Unity for ROS 2 integration?',
        'What GPU requirements does Isaac Sim have?',
      ],
      'debugging-simulation': [
        'Why is my robot exploding in simulation?',
        'How do I fix joint instability issues?',
        'What causes collision detection failures?',
      ],
    },
  },
  module3: {
    general: [
      'What is VSLAM and how does it work?',
      'How does Nav2 enable autonomous navigation?',
      'What sensors are needed for robot localization?',
    ],
    lessons: {
      'vslam-fundamentals': [
        'What is the difference between SLAM and localization?',
        'How do feature detection algorithms work in VSLAM?',
        'What is pose estimation and why is it important?',
      ],
      'isaac-ros-vslam': [
        'How do I set up Isaac ROS VSLAM on an NVIDIA GPU?',
        'What performance gains does GPU-accelerated VSLAM provide?',
        'How do I configure stereo camera input for Isaac ROS?',
      ],
      'cpu-slam-fallback': [
        'When should I use ORB-SLAM3 vs RTAB-Map?',
        'How do I optimize CPU-based SLAM performance?',
        'What are the tradeoffs between CPU and GPU SLAM?',
      ],
      'nav2-stack': [
        'What are the main components of the Nav2 stack?',
        'How do local and global planners work together?',
        'How do I configure costmap parameters?',
      ],
      'obstacle-avoidance': [
        'How do I tune Nav2 recovery behaviors?',
        'What causes the robot to get stuck during navigation?',
        'How do I configure obstacle inflation radius?',
      ],
      'rviz-visualization': [
        'How do I visualize costmaps in RViz?',
        'What topics should I subscribe to for navigation debugging?',
        'How do I display the planned path in RViz?',
      ],
    },
  },
  module4: {
    general: [
      'What is the Voice-Language-Action (VLA) pipeline?',
      'How do LLMs integrate with robot control?',
      'What safety measures are needed for voice-commanded robots?',
    ],
    lessons: {
      'vla-architecture': [
        'What are the components of a VLA system?',
        'How does speech-to-text feed into LLM reasoning?',
        'What is the latency breakdown in a VLA pipeline?',
      ],
      'speech-transcription': [
        'How do I integrate Whisper for speech recognition?',
        'What affects speech transcription accuracy?',
        'How do I handle background noise in transcription?',
      ],
      'llm-integration': [
        'How do I prompt an LLM for robot control tasks?',
        'What API parameters affect response quality?',
        'How do I handle LLM rate limits in production?',
      ],
      'action-validation': [
        'What safety checks should be applied to LLM outputs?',
        'How do I validate action parameters before execution?',
        'What is the role of simulation in action validation?',
      ],
      'ros2-action-servers': [
        'How do ROS 2 actions differ from services?',
        'How do I create an action server for robot commands?',
        'What feedback should action servers provide?',
      ],
      'latency-optimization': [
        'How do I achieve sub-10s voice-to-action latency?',
        'What components contribute most to VLA latency?',
        'How do I optimize LLM inference time?',
      ],
      'debugging-vla': [
        'How do I debug LLM output parsing errors?',
        'What causes invalid action commands?',
        'How do I handle ambiguous voice inputs?',
      ],
    },
  },
  capstone: {
    general: [
      'What are the capstone project requirements?',
      'How do I integrate all four modules?',
      'What deliverables are needed for the capstone?',
    ],
    lessons: {
      'project-requirements': [
        'What are the acceptance criteria for the capstone?',
        'How is the capstone project graded?',
        'What documentation is required?',
      ],
      'implementation-guide': [
        'What is the recommended implementation order?',
        'How do I structure my capstone codebase?',
        'What testing approach should I use?',
      ],
      'debugging-checklist': [
        'What are the most common integration issues?',
        'How do I diagnose communication failures between modules?',
        'What logs should I check when debugging?',
      ],
    },
  },
};

// Default questions when no module context is detected
const DEFAULT_QUESTIONS = [
  'What will I learn in this course?',
  'How do I get started with ROS 2?',
  'What are the prerequisites for this curriculum?',
  'How does the AI chatbot help me learn?',
];

/**
 * Extract module and lesson context from current URL
 */
function getPageContext(): { module: string | null; lesson: string | null } {
  if (typeof window === 'undefined') {
    return { module: null, lesson: null };
  }
  const path = window.location.pathname.toLowerCase();

  // Match module pattern: /docs/module1/, /docs/module2/, etc.
  const moduleMatch = path.match(/\/docs\/(module[1-4]|capstone)\//);
  const module = moduleMatch ? moduleMatch[1] : null;

  // Match lesson pattern: lesson1-ros2-basics, lesson2-nodes-topics, etc.
  const lessonMatch = path.match(/lesson\d+-([a-z0-9-]+)/);
  const lesson = lessonMatch ? lessonMatch[1] : null;

  // Also check for non-lesson pages like exercises, intro
  if (!lesson && module) {
    if (path.includes('exercises')) return { module, lesson: 'exercises' };
    if (path.includes('intro')) return { module, lesson: 'intro' };
  }

  return { module, lesson };
}

/**
 * Get suggested questions based on current page context
 */
function getSuggestedQuestions(module: string | null, lesson: string | null): string[] {
  if (!module || !QUESTIONS_BY_MODULE[module]) {
    return DEFAULT_QUESTIONS;
  }

  const moduleQuestions = QUESTIONS_BY_MODULE[module];

  // If we have a specific lesson, prioritize lesson-specific questions
  if (lesson && moduleQuestions.lessons[lesson]) {
    return moduleQuestions.lessons[lesson];
  }

  // Fall back to general module questions
  return moduleQuestions.general;
}

export default function SuggestedQuestions({
  onSelectQuestion,
  disabled = false
}: SuggestedQuestionsProps): JSX.Element {
  const { module, lesson } = getPageContext();
  const questions = getSuggestedQuestions(module, lesson);

  return (
    <div className={styles.suggestedQuestions} role="region" aria-label="Suggested questions">
      <div className={styles.suggestedHeader}>
        <span className={styles.suggestedIcon}>💡</span>
        <span>Try asking:</span>
      </div>
      <div className={styles.suggestedList}>
        {questions.map((question, idx) => (
          <button
            key={idx}
            onClick={() => onSelectQuestion(question)}
            disabled={disabled}
            className={styles.suggestedButton}
            aria-label={`Ask: ${question}`}
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  );
}

// Export for testing
export { getPageContext, getSuggestedQuestions, QUESTIONS_BY_MODULE, DEFAULT_QUESTIONS };

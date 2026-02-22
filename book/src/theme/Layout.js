import React from 'react';
import {useLocation} from '@docusaurus/router';
import {useColorMode} from '@docusaurus/theme-common';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import clsx from 'clsx';

// Import Framer Motion for animations
import { motion } from 'framer-motion';

// Import the default Docusaurus Layout
import OriginalLayout from '@theme-original/Layout';
import Footer from '@theme/Footer';
import FuturisticNavbar from '../components/Navigation/FuturisticNavbar';

// Background animation component (minimalist geometric pattern)
const AnimatedBackground = () => {
  return (
    <div className="fixed inset-0 -z-50 overflow-hidden pointer-events-none">
      <div className="absolute inset-0 fm-gradient-bg" />

      {/* Minimalist geometric overlay */}
      <div className="absolute inset-0 opacity-20">
        <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid slice">
          <defs>
            <pattern id="fm-grid" width="50" height="50" patternUnits="userSpaceOnUse">
              <path d="M 25 0 L 0 0 0 25" fill="none" stroke="rgba(0, 255, 255, 0.1)" strokeWidth="0.5" opacity="0.5"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#fm-grid)" />
        </svg>
      </div>

      {/* Subtle floating elements */}
      <motion.div
        className="absolute top-1/3 left-1/4 w-4 h-4 border border-fm-accent-primary opacity-30"
        animate={{
          y: [-10, 10, -10],
          x: [-10, 10, -10],
          rotate: [0, 90, 0]
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
      <motion.div
        className="absolute top-2/5 right-1/3 w-4 h-4 border border-fm-accent-secondary opacity-30"
        animate={{
          y: [10, -10, 10],
          x: [10, -10, 10],
          rotate: [0, -90, 0]
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
      <motion.div
        className="absolute bottom-1/3 left-1/2 w-4 h-4 border border-fm-accent-tertiary opacity-30"
        animate={{
          y: [-8, 8, -8],
          x: [8, -8, 8],
          rotate: [0, 45, 0]
        }}
        transition={{
          duration: 7,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
    </div>
  );
};

// Futuristic container component
const FuturisticContainer = ({ children, className = "" }) => {
  const { colorMode } = useColorMode();
  const isDark = colorMode !== 'light';

  return (
    <div className={clsx(
      "min-h-screen relative",
      className
    )}>
      {children}
    </div>
  );
};

// Staggered animation for content sections
const StaggeredContent = ({ children, delay = 0 }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay, ease: "easeOut" }}
    >
      {children}
    </motion.div>
  );
};

// Custom Layout wrapper
export default function Layout(props) {
  const { children, ...layoutProps } = props;
  const location = useLocation();
  const { isClient } = useDocusaurusContext();

  const layoutContent = (
    <FuturisticContainer>
      <StaggeredContent delay={0.1}>
        {children}
      </StaggeredContent>
    </FuturisticContainer>
  );

  // Only include the animated background since we have navbar in the swizzled theme
  return (
    <OriginalLayout {...layoutProps}>
      <AnimatedBackground />
      {layoutContent}
    </OriginalLayout>
  );
}
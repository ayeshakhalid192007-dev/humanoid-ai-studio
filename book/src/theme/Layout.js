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

// Background animation component (neural network style)
const AnimatedBackground = () => {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900" />

      {/* Animated neural network overlay */}
      <div className="absolute inset-0 opacity-20">
        <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid slice">
          <defs>
            <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
              <path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgb(16, 185, 129)" strokeWidth="0.5" opacity="0.3"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
        </svg>
      </div>

      {/* Floating animated elements */}
      <motion.div
        className="absolute top-1/4 left-1/4 w-64 h-64 bg-emerald-500 rounded-full mix-blend-multiply filter blur-xl opacity-20"
        animate={{
          y: [-20, 20, -20],
          x: [-20, 20, -20],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "linear",
        }}
      />
      <motion.div
        className="absolute top-3/4 right-1/4 w-72 h-72 bg-violet-500 rounded-full mix-blend-multiply filter blur-xl opacity-20"
        animate={{
          y: [20, -20, 20],
          x: [20, -20, 20],
        }}
        transition={{
          duration: 12,
          repeat: Infinity,
          ease: "linear",
        }}
      />
      <motion.div
        className="absolute bottom-1/4 left-1/2 w-60 h-60 bg-magenta-500 rounded-full mix-blend-multiply filter blur-xl opacity-20"
        animate={{
          y: [-15, 15, -15],
          x: [15, -15, 15],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "linear",
        }}
      />
    </div>
  );
};

// Glassmorphism container component
const GlassContainer = ({ children, className = "" }) => {
  const { colorMode } = useColorMode();
  const isDark = colorMode !== 'light';

  return (
    <div className={clsx(
      "glass-card min-h-screen relative",
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

  // Don't apply glassmorphism to certain pages that need full control
  const excludeGlassPages = ['/'];
  const isGlassPage = !excludeGlassPages.some(path => location.pathname.includes(path));

  const layoutContent = isGlassPage ? (
    <GlassContainer>
      <StaggeredContent delay={0.1}>
        {children}
      </StaggeredContent>
    </GlassContainer>
  ) : (
    <>{children}</>
  );

  return (
    <OriginalLayout {...layoutProps}>
      <AnimatedBackground />
      {layoutContent}
      <Footer />
    </OriginalLayout>
  );
}
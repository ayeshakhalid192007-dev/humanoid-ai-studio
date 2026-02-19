import React from 'react';
import { motion } from 'framer-motion';

interface MotionWrapperProps {
  children: React.ReactNode;
  variant?: 'fade' | 'slide' | 'stagger';
  delay?: number;
  duration?: number;
  direction?: 'up' | 'down' | 'left' | 'right';
}

const MotionWrapper: React.FC<MotionWrapperProps> = ({
  children,
  variant = 'fade',
  delay = 0,
  duration = 0.6,
  direction = 'up'
}) => {
  const animationVariants = {
    hidden: {
      opacity: 0,
      y: variant === 'slide' && (direction === 'up' ? 20 : direction === 'down' ? -20 : 0),
      x: variant === 'slide' && (direction === 'left' ? -20 : direction === 'right' ? 20 : 0),
    },
    visible: {
      opacity: 1,
      y: 0,
      x: 0,
      transition: {
        duration,
        delay,
        ease: "easeOut"
      }
    }
  };

  return (
    <motion.div
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, amount: 0.1 }}
      variants={variant === 'stagger' ? undefined : animationVariants}
    >
      {children}
    </motion.div>
  );
};

export { MotionWrapper };
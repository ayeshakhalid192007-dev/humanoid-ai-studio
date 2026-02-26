import React from 'react';
import { motion } from 'framer-motion';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'glass' | 'elevated' | 'solid' | 'accent';
  hoverEffect?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  variant = 'default',
  hoverEffect = true,
}) => {
  const baseClasses = 'fm-card';

  const variantClasses = {
    default: '',
    glass: 'fm-card--glass',
    elevated: 'fm-card--elevated',
    solid: 'fm-card--solid',
    accent: 'fm-card--accent',
  }[variant];

  const hoverClass = hoverEffect ? 'fm-hover-lift' : '';

  return (
    <motion.div
      className={`${baseClasses} ${variantClasses} ${hoverClass} ${className}`}
      whileHover={hoverEffect ? { y: -4, scale: 1.02 } : undefined}
      whileTap={{ scale: 0.98 }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
    >
      {children}
    </motion.div>
  );
};
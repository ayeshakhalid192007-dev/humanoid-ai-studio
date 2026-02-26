import React from 'react';
import { motion } from 'framer-motion';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'glass' | 'glass-3xl' | 'elevated' | 'solid' | 'accent';
  hoverEffect?: boolean;
  glowEffect?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  variant = 'default',
  hoverEffect = true,
  glowEffect = false,
}) => {
  const baseClasses = 'fm-card transition-all duration-300 overflow-hidden';

  const variantClasses = {
    default: 'fm-card',
    glass: 'fm-card--glass',
    'glass-3xl': 'fm-card--glass',
    elevated: 'fm-card--elevated',
    solid: 'fm-card--solid',
    accent: 'fm-card--accent'
  }[variant];

  const hoverClasses = hoverEffect ? 'fm-hover-lift' : '';

  const glowClasses = glowEffect ? 'fm-hover-glow' : '';

  return (
    <motion.div
      className={`${baseClasses} ${variantClasses} ${hoverClasses} ${glowClasses} ${className}`}
      whileHover={hoverEffect ? { y: -4 } : undefined}
      whileTap={{ scale: 0.98 }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
    >
      {children}
    </motion.div>
  );
};
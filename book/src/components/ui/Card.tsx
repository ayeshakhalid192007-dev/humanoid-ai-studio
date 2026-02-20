import React from 'react';
import { motion } from 'framer-motion';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'glass' | 'glass-3xl';
  hoverEffect?: boolean;
  glowEffect?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  variant = 'glass',
  hoverEffect = true,
  glowEffect = false,
}) => {
  const baseClasses = 'rounded-2xl shadow-xl transition-all duration-300 overflow-hidden';

  const variantClasses = {
    default: 'bg-white/10',
    glass: 'glass-card bg-white/10 backdrop-blur-sm border border-white/20',
    'glass-3xl': 'glass-card-3xl bg-white/10 backdrop-blur-3xl border border-white/20 rounded-3xl'
  }[variant];

  const hoverClasses = hoverEffect
    ? 'hover:translate-y-[-8px] hover:scale-[1.04] hover:shadow-2xl hover:border-white/30'
    : '';

  const glowClasses = glowEffect
    ? 'relative glow-border hover:glow-border'
    : '';

  return (
    <motion.div
      className={`${baseClasses} ${variantClasses} ${hoverClasses} ${glowClasses} ${className}`}
      whileHover={hoverEffect ? { y: -8, scale: 1.04 } : undefined}
      whileTap={{ scale: 0.98 }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
    >
      {children}
    </motion.div>
  );
};
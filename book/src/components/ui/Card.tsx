import React from 'react';
import { motion } from 'framer-motion';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'glass';
  hoverEffect?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  variant = 'default',
  hoverEffect = true,
}) => {
  const baseClasses = 'rounded-2xl shadow-xl transition-all duration-300';

  const variantClasses = variant === 'glass'
    ? 'bg-white/10 backdrop-blur-sm border border-white/20'
    : 'bg-white/10';

  const hoverClasses = hoverEffect
    ? 'hover:translate-y-[-8px] hover:scale-[1.03] hover:shadow-2xl hover:border-white/40'
    : '';

  return (
    <motion.div
      className={`${baseClasses} ${variantClasses} ${hoverClasses} ${className}`}
      whileHover={hoverEffect ? { y: -8, scale: 1.03 } : undefined}
      whileTap={{ scale: 0.98 }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
    >
      {children}
    </motion.div>
  );
};
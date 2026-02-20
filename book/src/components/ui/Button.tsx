import React from 'react';
import { motion } from 'framer-motion';

interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  onClick?: () => void;
  disabled?: boolean;
  fullWidth?: boolean;
  startIcon?: React.ReactNode;
  endIcon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  onClick,
  disabled = false,
  fullWidth = false,
  startIcon,
  endIcon,
}) => {
  const sizeClasses = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
  };

  const variantClasses = {
    primary: 'glass-button--primary hover:scale-[1.04]',
    secondary: 'glass-button text-white bg-gradient-to-r from-indigo-500 to-blue-600 hover:from-indigo-600 hover:to-blue-700 hover:scale-[1.04]',
    outline: 'glass-button glass-button--outline hover:scale-[1.04]',
    ghost: 'text-white hover:bg-white/10',
  };

  const hoverClasses = {
    primary: 'hover:scale-[1.03] hover:shadow-lg hover:shadow-blue-500/30',
    secondary: 'hover:scale-[1.03] hover:shadow-lg hover:shadow-indigo-500/30',
    outline: 'hover:scale-[1.03] hover:shadow-lg hover:shadow-white/20',
    ghost: '',
  };

  const disabledClasses = disabled ? 'opacity-50 cursor-not-allowed' : '';

  // If button type is not specified with the type attribute, provide a default
  const buttonProps: React.ButtonHTMLAttributes<HTMLButtonElement> = {
    onClick,
    disabled,
    className: [
      sizeClasses[size],
      variantClasses[variant],
      hoverClasses[variant],
      'font-medium transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2',
      'focus:ring-offset-[#0f0f14] rounded-full backdrop-blur-sm',
      disabled ? 'cursor-not-allowed' : '',
      fullWidth ? 'w-full' : '',
      disabledClasses,
      className
    ].join(' ')
  };

  return (
    <motion.button
      whileHover={disabled ? undefined : { scale: 1.03 }}
      whileTap={disabled ? undefined : { scale: 0.98 }}
      {...buttonProps}
    >
      <span className="flex items-center justify-center gap-2">
        {startIcon && <span>{startIcon}</span>}
        {children}
        {endIcon && <span>{endIcon}</span>}
      </span>
    </motion.button>
  );
};
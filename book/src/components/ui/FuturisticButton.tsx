import React from 'react';
import { motion } from 'framer-motion';

interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg' | 'block';
  className?: string;
  onClick?: () => void;
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
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
  type = 'button',
  startIcon,
  endIcon,
}) => {
  const sizeClasses = {
    sm: 'fm-button--small',
    md: '',
    lg: 'fm-button--large',
    block: 'fm-button--block',
  };

  const variantClasses = {
    primary: 'fm-button--primary',
    secondary: 'fm-button--secondary',
    outline: 'fm-button--outline',
    ghost: 'fm-button--ghost',
  };

  const disabledClass = disabled ? 'fm-button--disabled' : '';

  const buttonVariants = {
    primary: { scale: 1.02 },
    secondary: { scale: 1.02 },
    outline: { scale: 1.02 },
    ghost: { scale: 1.02 },
  };

  return (
    <motion.button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`fm-button ${variantClasses[variant]} ${sizeClasses[size]} ${disabledClass} ${className}`}
      whileHover={disabled ? undefined : { scale: 1.02 }}
      whileTap={disabled ? undefined : { scale: 0.98 }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
    >
      <span className="flex items-center justify-center gap-2">
        {startIcon && <span>{startIcon}</span>}
        {children}
        {endIcon && <span>{endIcon}</span>}
      </span>
    </motion.button>
  );
};
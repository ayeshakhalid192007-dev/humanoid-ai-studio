import React from 'react';
import { motion } from 'framer-motion';

export interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg' | 'block';
  className?: string;
  onClick?: () => void;
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
  startIcon?: React.ReactNode;
  endIcon?: React.ReactNode;
  href?: string;
  target?: string;
  rel?: string;
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
  href,
  target,
  rel,
}) => {
  const sizeClasses = {
    sm: 'fm-button--small',
    md: '', // Default size
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

  const baseClasses = [
    'fm-button',
    variantClasses[variant],
    sizeClasses[size],
    disabledClass,
    className
  ].join(' ');

  const motionProps = {
    whileHover: disabled ? undefined : { scale: 1.02 },
    whileTap: disabled ? undefined : { scale: 0.98 },
    transition: { type: "spring", stiffness: 300, damping: 20 }
  };

  if (href) {
    // Render as anchor for navigation
    return (
      <motion.a
        href={href}
        target={target}
        rel={rel}
        className={baseClasses}
        onClick={onClick as React.MouseEventHandler<HTMLAnchorElement>}
        {...motionProps}
      >
        <span className="flex items-center justify-center gap-2">
          {startIcon && <span>{startIcon}</span>}
          {children}
          {endIcon && <span>{endIcon}</span>}
        </span>
      </motion.a>
    );
  }

  // Render as button element
  return (
    <motion.button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={baseClasses}
      {...motionProps}
    >
      <span className="flex items-center justify-center gap-2">
        {startIcon && <span>{startIcon}</span>}
        {children}
        {endIcon && <span>{endIcon}</span>}
      </span>
    </motion.button>
  );
};
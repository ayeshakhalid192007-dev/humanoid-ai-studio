import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info' | 'beginner' | 'intermediate' | 'advanced' | 'expert';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
}) => {
  const variantClasses = {
    primary: 'bg-fm-accent-primary text-fm-bg-primary',
    secondary: 'bg-fm-bg-tertiary text-fm-text-secondary border border-fm-text-tertiary',
    success: 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30',
    warning: 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30',
    error: 'bg-red-500/20 text-red-400 border border-red-500/30',
    info: 'bg-blue-500/20 text-blue-400 border border-blue-500/30',
    beginner: 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30',
    intermediate: 'bg-blue-500/20 text-blue-400 border border-blue-500/30',
    advanced: 'bg-purple-500/20 text-purple-400 border border-purple-500/30',
    expert: 'bg-red-500/20 text-red-400 border border-red-500/30',
  };

  const sizeClasses = {
    sm: 'fm-body-sm px-2 py-0.5 rounded-full',
    md: 'fm-body-sm px-2.5 py-0.5 rounded-full',
    lg: 'fm-body-md px-3 py-1 rounded-full',
  };

  return (
    <span className={`
      inline-flex items-center justify-center font-medium
      ${variantClasses[variant]} ${sizeClasses[size]} ${className}
    `}>
      {children}
    </span>
  );
};
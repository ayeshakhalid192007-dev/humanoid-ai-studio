import React from 'react';

interface GlowBorderProps {
  children: React.ReactNode;
  className?: string;
  color?: 'blue' | 'purple' | 'indigo' | 'emerald' | 'violet';
  size?: 'sm' | 'md' | 'lg';
}

export const GlowBorder: React.FC<GlowBorderProps> = ({
  children,
  className = '',
  color = 'blue',
  size = 'md',
}) => {
  const colorClasses = {
    blue: 'from-blue-400 to-blue-600',
    purple: 'from-purple-400 to-purple-600',
    indigo: 'from-indigo-400 to-indigo-600',
    emerald: 'from-emerald-400 to-emerald-600',
    violet: 'from-violet-400 to-violet-600',
  };

  const sizeClasses = {
    sm: 'blur-sm',
    md: 'blur-md',
    lg: 'blur-lg',
  };

  return (
    <div className={`relative ${className}`}>
      <div className={`
        absolute -inset-0.5 bg-gradient-to-r ${colorClasses[color]}
        rounded-lg blur-${sizeClasses[size]} opacity-75
      `}></div>
      <div className="relative">
        {children}
      </div>
    </div>
  );
};
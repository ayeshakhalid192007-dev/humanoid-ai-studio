import React from 'react';

interface SectionProps {
  children: React.ReactNode;
  className?: string;
  paddingTop?: 'sm' | 'md' | 'lg' | 'xl' | 'none';
  paddingBottom?: 'sm' | 'md' | 'lg' | 'xl' | 'none';
  background?: 'default' | 'gradient' | 'glass' | 'dark';
}

export const Section: React.FC<SectionProps> = ({
  children,
  className = '',
  paddingTop = 'lg',
  paddingBottom = 'lg',
  background = 'default',
}) => {
  const paddingClasses = {
    sm: 'py-8',
    md: 'py-12',
    lg: 'py-20',
    xl: 'py-24',
    none: 'py-0',
  };

  const backgroundClasses = {
    default: 'bg-transparent',
    gradient: 'bg-gradient-futuristic',
    glass: 'bg-white/5 backdrop-blur-sm',
    dark: 'bg-[#0f0f14]',
  };

  return (
    <section
      className={`
        ${paddingClasses[paddingTop]} ${paddingClasses[paddingBottom]}
        ${backgroundClasses[background]} ${className}
      `}
    >
      {children}
    </section>
  );
};
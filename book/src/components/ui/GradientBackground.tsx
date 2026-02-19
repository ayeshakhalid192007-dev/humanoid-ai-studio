import React from 'react';
import { motion } from 'framer-motion';

interface GradientBackgroundProps {
  children?: React.ReactNode;
  className?: string;
}

export const GradientBackground: React.FC<GradientBackgroundProps> = ({
  children,
  className = '',
}) => {
  return (
    <div className={`relative w-full overflow-hidden ${className}`}>
      <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-purple-900/20 to-indigo-900/20" />
      <div className="absolute top-1/4 left-1/4 w-[800px] h-[600px] rounded-full bg-gradient-to-r from-blue-500/30 to-purple-600/20 blur-[100px] -z-10" />
      <div className="absolute top-1/3 right-1/4 w-[600px] h-[500px] rounded-full bg-gradient-to-r from-purple-500/20 to-indigo-600/30 blur-[80px] -z-10" />

      {children}
    </div>
  );
};
import React from 'react';

interface GridBackgroundProps {
  children?: React.ReactNode;
  className?: string;
}

export const GridBackground: React.FC<GridBackgroundProps> = ({
  children,
  className = '',
}) => {
  return (
    <div className={`fixed inset-0 w-full h-full -z-50 ${className}`}>
      {/* Minimal CSS Grid Background */}
      <div
        className="absolute inset-0 w-full h-full"
        style={{
          backgroundImage: `
            radial-gradient(circle at 15% 20%, rgba(59, 130, 246, 0.05) 1px, transparent 1px),
            radial-gradient(circle at 85% 30%, rgba(147, 51, 234, 0.03) 1px, transparent 1px)
          `,
          backgroundSize: '150px 150px',
          backgroundColor: 'transparent',
          backgroundPosition: '0 0, 0 0',
          backgroundRepeat: 'repeat',
        }}
      />
      {children}
    </div>
  );
};
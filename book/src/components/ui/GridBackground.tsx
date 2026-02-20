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
      {/* CSS Grid Background using radial gradients */}
      <div
        className="absolute inset-0 w-full h-full"
        style={{
          backgroundImage: `
            radial-gradient(circle at 15% 20%, rgba(59, 130, 246, 0.1) 1px, transparent 1px),
            radial-gradient(circle at 85% 30%, rgba(147, 51, 234, 0.08) 1px, transparent 1px),
            radial-gradient(circle at 30% 80%, rgba(99, 102, 241, 0.07) 1px, transparent 1px),
            radial-gradient(circle at 70% 75%, rgba(147, 51, 234, 0.05) 1px, transparent 1px),
            radial-gradient(circle at 20% 60%, rgba(59, 130, 246, 0.09) 1px, transparent 1px)
          `,
          backgroundColor: 'var(--ifm-background-color)',
          backgroundSize: '60px 60px',
          backgroundPosition: '0 0, 0 0, 0 0, 0 0, 0 0',
          backgroundRepeat: 'repeat',
        }}
      />
      {children}
    </div>
  );
};
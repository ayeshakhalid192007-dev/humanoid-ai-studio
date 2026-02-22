import React, { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { AuthStateIndicator } from '../Auth/AuthStateIndicator';
import Navbar from '@theme/Navbar';
import clsx from 'clsx';

interface DocsLayoutProps {
  children: ReactNode;
  title?: string;
  description?: string;
  className?: string;
  showAuthIndicator?: boolean;
  showNavbar?: boolean;
}

const DocsLayout: React.FC<DocsLayoutProps> = ({
  children,
  title,
  description,
  className = '',
  showAuthIndicator = false,
  showNavbar = true
}) => {
  React.useEffect(() => {
    if (title) {
      document.title = `${title} - Physical AI Platform`;
    }
  }, [title]);

  return (
    <div className={clsx('min-h-screen', className)}>
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-800" />
        <div
          className="absolute inset-0"
          style={{
            background: "radial-gradient(ellipse at center, rgba(120,119,198, 0.1), rgba(255,255,255, 0))"
          }}
        />
      </div>

      {showNavbar && <Navbar />}
      {showAuthIndicator && <AuthStateIndicator />}

      <motion.main
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="min-h-screen pt-0 pb-16 px-4 sm:px-6 lg:px-8"
      >
        <div className="max-w-7xl mx-auto">
          <div className="prose prose-invert max-w-none">
            {children}
          </div>
        </div>
      </motion.main>
    </div>
  );
};

export default DocsLayout;
export { DocsLayout };
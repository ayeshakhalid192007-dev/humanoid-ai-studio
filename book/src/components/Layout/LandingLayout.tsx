import React, { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { AuthStateIndicator } from '../Auth/AuthStateIndicator';
import clsx from 'clsx';

interface LandingLayoutProps {
  children: ReactNode;
  title?: string;
  description?: string;
  className?: string;
  showAuthIndicator?: boolean;
  showNavbar?: boolean; // This parameter exists for compatibility but Navbar is handled by Docusaurus
  fullBleed?: boolean;
}

const LandingLayout: React.FC<LandingLayoutProps> = ({
  children,
  title,
  description,
  className = '',
  showAuthIndicator = false, // Don't show auth indicator on landing by default
  showNavbar = true, // This parameter exists for compatibility but Navbar is handled by Docusaurus
  fullBleed = false
}) => {
  React.useEffect(() => {
    if (title) {
      document.title = `${title} - Physical AI Platform`;
    }
  }, [title]);

  return (
    <div className={clsx('min-h-screen', className)}>
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-blue-900 to-indigo-900" />
        <div
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage: "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")"
          }}
        />
      </div>

      {showAuthIndicator && <AuthStateIndicator />}

      <motion.main
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="min-h-screen pt-0 pb-16 px-4 sm:px-6 lg:px-8"
      >
        {fullBleed ? (
          <div className="w-full">
            {children}
          </div>
        ) : (
          <div className="max-w-7xl mx-auto">
            <div className="prose prose-invert max-w-none">
              {children}
            </div>
          </div>
        )}
      </motion.main>
    </div>
  );
};

export default LandingLayout;
export { LandingLayout };
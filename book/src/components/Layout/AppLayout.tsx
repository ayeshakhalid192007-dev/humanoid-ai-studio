import React, { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { AuthStateIndicator } from '../Auth/AuthStateIndicator';
import clsx from 'clsx';

interface AppLayoutProps {
  children: ReactNode;
  title?: string;
  description?: string;
  className?: string;
  showAuthIndicator?: boolean;
  showNavbar?: boolean;
  background?: 'default' | 'auth' | 'docs';
}

const AppLayout: React.FC<AppLayoutProps> = ({
  children,
  title,
  description,
  className = '',
  showAuthIndicator = true,
  showNavbar = true, // This parameter exists for compatibility but Navbar is handled by Docusaurus
  background = 'default'
}) => {
  React.useEffect(() => {
    if (title) {
      document.title = `${title} - Physical AI Platform`;
    }
  }, [title]);

  const renderBackground = () => {
    if (background === 'auth') {
      return (
        <div className="fixed inset-0 -z-10 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-800 opacity-90" />
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(120,119,198,0.3),rgba(255,255,255,0))]" />
        </div>
      );
    }

    if (background === 'docs') {
      return (
        <div className="fixed inset-0 -z-10 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-800" />
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(120,119,198,0.1),rgba(255,255,255,0))]" />
        </div>
      );
    }

    return (
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900" />
        <div
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage: "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")"
          }}
        />
      </div>
    );
  };

  return (
    <div className={clsx('min-h-screen', className)}>
      {renderBackground()}
      {showAuthIndicator && <AuthStateIndicator />}

      <motion.main
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 pb-16 px-4 sm:px-6 lg:px-8" /* Remove top padding since navbar is separate now */
      >
        {children}
      </motion.main>
    </div>
  );
};

export default AppLayout;
export { AppLayout };
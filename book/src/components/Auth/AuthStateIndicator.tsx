import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';
import clsx from 'clsx';

export interface AuthStateIndicatorProps {
  alwaysVisible?: boolean;
}

export const AuthStateIndicator: React.FC<AuthStateIndicatorProps> = ({
  alwaysVisible = false
}) => {
  const { isAuthenticated, isLoading, user, refreshSession, profile } = useAuth();
  const [showIndicator, setShowIndicator] = useState(false);

  // Only show indicator if it's explicitly requested
  useEffect(() => {
    if (alwaysVisible) {
      setShowIndicator(true);
    } else {
      setShowIndicator(false);
    }
  }, [alwaysVisible]);

  if (!showIndicator || isLoading) {
    return null;
  }

  if (!isAuthenticated) {
    return (
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className={clsx(
          'fixed top-4 right-4 z-50 px-4 py-2 rounded-lg shadow-lg',
          'bg-red-900/80 backdrop-blur-sm border border-red-500/30',
          'text-red-100 text-sm font-medium'
        )}
      >
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-red-400 rounded-full" />
          <span>Not Authenticated</span>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={clsx(
        'fixed top-4 right-4 z-50 px-4 py-2 rounded-lg shadow-lg',
        'bg-green-900/80 backdrop-blur-sm border border-green-500/30',
        'text-green-100 text-sm font-medium'
      )}
    >
      <div className="flex items-center gap-2">
        <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
        <span>Authenticated</span>
        {user?.email && (
          <span className="text-green-200/80 text-xs truncate max-w-[100px]">
            {user.email}
          </span>
        )}
        {user?.onboardingCompleted === false && (
          <span className="ml-2 text-yellow-300 text-xs">Onboarding</span>
        )}
      </div>
    </motion.div>
  );
};
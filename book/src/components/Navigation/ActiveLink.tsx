import React from 'react';
import Link from '@docusaurus/Link';
import { useLocation } from '@docusaurus/router';
import clsx from 'clsx';

interface ActiveLinkProps {
  to: string;
  children: React.ReactNode;
  className?: string;
  activeClassName?: string;
  alwaysActive?: boolean;
  external?: boolean;
  onClick?: () => void;
}

export const ActiveLink: React.FC<ActiveLinkProps> = ({
  to,
  children,
  className = '',
  activeClassName = 'text-blue-400',
  alwaysActive = false,
  external = false,
  onClick
}) => {
  const location = useLocation();
  const isActive = alwaysActive || location.pathname === to;

  if (external) {
    return (
      <a
        href={to}
        target="_blank"
        rel="noopener noreferrer"
        className={clsx(
          'transition-colors duration-200 hover:text-blue-400',
          className,
          isActive ? activeClassName : ''
        )}
        onClick={onClick}
      >
        {children}
      </a>
    );
  }

  return (
    <Link
      to={to}
      className={clsx(
        'transition-colors duration-200 hover:text-blue-400',
        className,
        isActive ? activeClassName : ''
      )}
      onClick={onClick}
    >
      {children}
    </Link>
  );
};
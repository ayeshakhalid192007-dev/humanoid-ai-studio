import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import { useLocation } from '@docusaurus/router';
import { Button } from '../ui/FuturisticButton';

const FuturisticNavbar = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const location = useLocation();
  const { siteConfig } = useDocusaurusContext();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { name: 'Features', href: '#features' },
    { name: 'Curriculum', href: '/chapters' },
    { name: 'Testimonials', href: '#testimonials' },
    { name: 'Dashboard', href: '/dashboard' },
  ];

  const isActive = (href: string) => {
    // For anchor links on the homepage, always return false for pathname matching
    if (href.startsWith('#') && location.pathname === '/') return false;

    // For non-anchor navigation
    if (!href.startsWith('#')) {
      // Check if it's the dashboard link
      if (href === '/dashboard' && location.pathname.startsWith('/dashboard')) {
        return true;
      }
      // Check if current location pathname matches href
      return location.pathname === href || location.pathname.startsWith(href + '/');
    }

    // For all other cases (shouldn't normally reach here for href matching)
    return false;
  };

  return (
    <motion.nav
      className={`fm-navbar ${isScrolled ? 'fm-navbar-scrolled' : ''}`}
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
    >
      <div className="fm-navbar__container">
        {/* Logo */}
        <Link href="/" className="fm-navbar__logo">
          <span className="fm-navbar__logo-text">PhysicalAI</span>
          <span className="fm-text-tertiary">.io</span>
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center space-x-8">
          {navLinks.map((link, index) => {
            const isAnchorLink = link.href.startsWith('#');
            const isActiveLink = isActive(link.href);

            return (
              <Link
                key={link.name}
                href={link.href}
                className={`fm-navbar__link ${isActiveLink ? 'fm-navbar__link--active' : ''}`}
                onClick={(e) => {
                  if (isAnchorLink && location.pathname === '/') {
                    e.preventDefault();
                    const targetElement = document.querySelector(link.href);
                    if (targetElement) {
                      targetElement.scrollIntoView({
                        behavior: 'smooth'
                      });
                    }
                  }
                }}
                style={{ transitionDelay: `${index * 0.05}s` }}
              >
                {link.name}
              </Link>
            );
          })}
        </div>

        {/* Desktop Auth Buttons */}
        <div className="hidden md:flex items-center space-x-4">
          <Link
            href="/auth/login"
            className="fm-text-secondary hover:fm-text-primary transition-colors duration-200"
          >
            Sign In
          </Link>
          <Button variant="primary" href="/auth/signup">
            Create Account
          </Button>
        </div>

        {/* Mobile Menu Button */}
        <div className="md:hidden">
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="fm-text-secondary hover:fm-text-primary focus:outline-none fm-text-2xl"
            aria-label="Toggle menu"
          >
            {isMobileMenuOpen ? (
              <span>✕</span>
            ) : (
              <span>☰</span>
            )}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="md:hidden fm-bg-secondary border-t border-fm-text-tertiary/20"
          >
            <div className="px-4 py-4 space-y-4">
              {navLinks.map((link) => {
                const isAnchorLink = link.href.startsWith('#');
                const isActiveLink = isActive(link.href);

                return (
                  <Link
                    key={link.name}
                    href={link.href}
                    className={`block py-2 text-fm-text-secondary hover:text-fm-accent-primary ${isActiveLink ? 'text-fm-accent-primary' : ''}`}
                    onClick={(e) => {
                      if (isAnchorLink && location.pathname === '/') {
                        e.preventDefault();
                        const targetElement = document.querySelector(link.href);
                        if (targetElement) {
                          targetElement.scrollIntoView({
                            behavior: 'smooth'
                          });
                        }
                      }
                      setIsMobileMenuOpen(false);
                    }}
                  >
                    {link.name}
                  </Link>
                );
              })}
              <div className="pt-4 border-t border-fm-text-tertiary/20">
                <div className="flex flex-col space-y-3">
                  <Link
                    href="/auth/login"
                    className="text-fm-text-secondary hover:text-fm-accent-primary text-center"
                  >
                    Sign In
                  </Link>
                  <Button variant="primary" href="/auth/signup" className="w-full">
                    Create Account
                  </Button>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  );
};

export default FuturisticNavbar;
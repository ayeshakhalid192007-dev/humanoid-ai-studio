import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import { useLocation } from '@docusaurus/router';
import { Button } from '../ui/Button'; // Use unified button component
import ChatbotWidget from '../ChatbotWidget/FuturisticChatbotWidget';
import { useAuth } from '../../context/AuthContext';
import { UserMenu } from '../Auth/UserMenu';
import BrowserOnly from '@docusaurus/BrowserOnly';

const FuturisticNavbar = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const location = useLocation();
  const { siteConfig } = useDocusaurusContext();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };

    // Use passive event listener for better performance
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { name: 'Home', href: '/' },
    { name: 'Curriculum', href: '/chapters' },
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
      className={`fm-navbar navbar navbar--fixed-top ${isScrolled ? 'fm-navbar-scrolled' : ''}`}
      id="navbar"  // Add navbar ID that Docusaurus expects
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

        {/* Desktop Navigation with boxes */}
        <div className="hidden md:flex items-center gap-2">
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
                    try {
                      const targetElement = document.querySelector(link.href);
                      if (targetElement) {
                        const elementPosition = targetElement.getBoundingClientRect().top;
                        const offsetPosition = elementPosition + window.pageYOffset - 100; // Account for fixed navbar
                        window.scrollTo({
                          top: offsetPosition,
                          behavior: 'smooth'
                        });
                      }
                    } catch (error) {
                      console.warn('Error scrolling to element:', error);
                      // Fallback to regular navigation if smooth scrolling fails
                      window.location.hash = link.href;
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

        {/* Desktop Chatbot and Auth Buttons */}
        <div className="hidden md:flex fm-navbar__auth-container">
          <div className="fm-navbar__auth-inner">
            <div className="fm-chatbot-upper-container">
              <ChatbotWidget position="upper" />
            </div>
            <BrowserOnly fallback={<div>Loading...</div>}>
              {() => {
                const { isAuthenticated, signOut, isLoading } = useAuth();

                if (isAuthenticated) {
                  return <UserMenu />;
                }

                return (
                  <>
                    <Link
                      href="/auth/login"
                      className="fm-navbar__link--auth"
                    >
                      Sign In
                    </Link>
                    <Button variant="primary" href="/auth/signup">
                      Create Account
                    </Button>
                  </>
                );
              }}
            </BrowserOnly>
          </div>
        </div>

        {/* Mobile Menu Button */}
        <div className="md:hidden flex items-center">
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="fm-text-secondary hover:fm-text-primary focus:outline-none fm-text-2xl transition-all duration-200"
            aria-label="Toggle menu"
          >
            {isMobileMenuOpen ? (
              <span className="fm-text-accent-primary">✕</span>
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
                    className={`block py-3 text-fm-text-secondary hover:text-fm-accent-primary rounded-lg transition-all duration-200 ${isActiveLink ? 'text-fm-accent-primary' : ''}`}
                    onClick={(e) => {
                      if (isAnchorLink && location.pathname === '/') {
                        e.preventDefault();
                        try {
                          const targetElement = document.querySelector(link.href);
                          if (targetElement) {
                            const elementPosition = targetElement.getBoundingClientRect().top;
                            const offsetPosition = elementPosition + window.pageYOffset - 100; // Account for fixed navbar
                            window.scrollTo({
                              top: offsetPosition,
                              behavior: 'smooth'
                            });
                          }
                        } catch (error) {
                          console.warn('Error scrolling to element:', error);
                          // Fallback to regular navigation if smooth scrolling fails
                          window.location.hash = link.href;
                        }
                      }
                      // Close mobile menu after any click
                      setIsMobileMenuOpen(false);
                    }}
                  >
                    {link.name}
                  </Link>
                );
              })}
              <div className="pt-4 border-t border-fm-text-tertiary/20">
                <BrowserOnly fallback={<div>Loading...</div>}>
                  {() => {
                    const { isAuthenticated, signOut, user } = useAuth();

                    if (isAuthenticated) {
                      return (
                        <div className="flex flex-col space-y-3">
                          <div className="text-fm-text-secondary text-center py-2">
                            {user?.name || user?.email}
                          </div>
                          <Button
                            variant="secondary"
                            onClick={async () => {
                              await signOut();
                              setIsMobileMenuOpen(false);
                            }}
                            className="w-full"
                          >
                            Sign Out
                          </Button>
                        </div>
                      );
                    }

                    return (
                      <div className="flex flex-col space-y-3">
                        <Link
                          href="/auth/login"
                          className="text-fm-text-secondary hover:text-fm-accent-primary text-center py-2 transition-all duration-200"
                        >
                          Sign In
                        </Link>
                        <Button variant="primary" href="/auth/signup" className="w-full">
                          Create Account
                        </Button>
                      </div>
                    );
                  }}
                </BrowserOnly>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  );
};

export default FuturisticNavbar;
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import { useLocation } from '@docusaurus/router';
import BrowserOnly from '@docusaurus/BrowserOnly';
import { Button } from '../ui/Button';

/**
 * Inner navbar that has access to auth context (client-only).
 * Hooks are called at the top level of this component — no violations.
 */
function FuturisticNavbarInner() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const location = useLocation();

  // Auth hook called at top-level — no hooks-in-callbacks violation
  const { useAuth } = require('../../context/AuthContext') as typeof import('../../context/AuthContext');
  const { isAuthenticated, user, signOut } = useAuth();
  const { siteConfig } = useDocusaurusContext();
  const baseUrl = siteConfig.baseUrl.replace(/\/$/, ''); // e.g. '/humanoid-ai-studio'

  // Lazy import UserMenu to keep it client-only
  const { UserMenu } = require('../Auth/UserMenu') as typeof import('../Auth/UserMenu');

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 10);
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { name: 'Home', href: '/' },
    { name: 'Curriculum', href: '/chapters' },
    { name: 'Dashboard', href: '/dashboard' },
  ];

  const isActive = (href: string) => {
    if (href.startsWith('#')) return false;
    if (href === '/') return location.pathname === baseUrl + '/' || location.pathname === '/';
    const fullPath = baseUrl + href;
    return location.pathname === fullPath || location.pathname.startsWith(fullPath + '/');
  };

  const scrollToSection = (href: string) => {
    try {
      const el = document.querySelector(href);
      if (el) {
        const top = el.getBoundingClientRect().top + window.pageYOffset - 100;
        window.scrollTo({ top, behavior: 'smooth' });
      }
    } catch {
      window.location.hash = href;
    }
  };

  return (
    <motion.nav
      className={`fm-navbar navbar navbar--fixed-top ${isScrolled ? 'fm-navbar-scrolled' : ''}`}
      id="navbar"
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
    >
      <div className="fm-navbar__container">
        {/* Logo */}
        <Link href="/" className="fm-navbar__logo">
          <span className="fm-navbar__logo-text">PhysicalAI</span>
          <span className="fm-text-tertiary">.io</span>
        </Link>

        {/* Desktop nav links */}
        <div className="fm-navbar__nav">
          {navLinks.map((link, index) => {
            const isAnchorLink = link.href.startsWith('#');
            const active = isActive(link.href);
            return (
              <Link
                key={link.name}
                href={link.href}
                className={`fm-navbar__link ${active ? 'fm-navbar__link--active' : ''}`}
                style={{ transitionDelay: `${index * 0.05}s` }}
                onClick={(e) => {
                  if (isAnchorLink && location.pathname === '/') {
                    e.preventDefault();
                    scrollToSection(link.href);
                  }
                }}
              >
                {link.name}
              </Link>
            );
          })}
        </div>

        {/* Desktop auth area */}
        <div className="fm-navbar__auth-container">
          <div className="fm-navbar__auth-inner">
            {isAuthenticated ? (
              <UserMenu />
            ) : (
              <>
                <Link href="/auth/login" className="fm-navbar__link--auth">
                  Sign In
                </Link>
                <Button variant="primary" href="/auth/signup">
                  Create Account
                </Button>
              </>
            )}
          </div>
        </div>

        {/* Mobile toggle */}
        <div className="fm-navbar__mobile-toggle">
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="fm-text-secondary hover:fm-text-primary focus:outline-none transition-all duration-200 text-2xl"
            aria-label="Toggle menu"
            aria-expanded={isMobileMenuOpen}
          >
            {isMobileMenuOpen ? (
              <span className="fm-text-accent-primary">✕</span>
            ) : (
              <span>☰</span>
            )}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.25 }}
            className="fm-navbar__mobile-menu"
          >
            <div className="fm-navbar__mobile-menu-inner">
              {navLinks.map((link) => {
                const isAnchorLink = link.href.startsWith('#');
                const active = isActive(link.href);
                return (
                  <Link
                    key={link.name}
                    href={link.href}
                    className={active ? 'fm-navbar__link-mobile fm-navbar__link-mobile--active' : 'fm-navbar__link-mobile'}
                    onClick={(e) => {
                      if (isAnchorLink && location.pathname === '/') {
                        e.preventDefault();
                        scrollToSection(link.href);
                      }
                      setIsMobileMenuOpen(false);
                    }}
                  >
                    {link.name}
                  </Link>
                );
              })}

              <div className="fm-navbar__mobile-menu-auth">
                {isAuthenticated ? (
                  <div className="fm-navbar__mobile-auth-stack">
                    <div className="fm-navbar__mobile-user">
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
                ) : (
                  <div className="fm-navbar__mobile-auth-stack">
                    <Link
                      href="/auth/login"
                      className="fm-navbar__mobile-auth-link"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      Sign In
                    </Link>
                    <Button
                      variant="primary"
                      href="/auth/signup"
                      className="w-full"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      Create Account
                    </Button>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  );
}

/**
 * FuturisticNavbar — server-safe shell.
 * Renders a static placeholder during SSR, real navbar on client.
 */
const FuturisticNavbar = () => {
  return (
    <BrowserOnly
      fallback={
        <nav className="fm-navbar navbar navbar--fixed-top" id="navbar">
          <div className="fm-navbar__container">
            <span className="fm-navbar__logo">
              <span className="fm-navbar__logo-text">PhysicalAI</span>
              <span className="fm-text-tertiary">.io</span>
            </span>
          </div>
        </nav>
      }
    >
      {() => <FuturisticNavbarInner />}
    </BrowserOnly>
  );
};

export default FuturisticNavbar;

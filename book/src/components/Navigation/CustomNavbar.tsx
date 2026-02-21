import React, { useState, useEffect } from 'react';
import Link from '@docusaurus/Link';
import { useLocation } from '@docusaurus/router';
import { NavbarAuth } from '../Auth';
import { motion, AnimatePresence } from 'framer-motion';

// Custom Navbar component that doesn't rely on Docusaurus internal context
const CustomNavbar = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Define navigation items - different set for home vs other pages
  const isHomePage = location.pathname === '/';

  const navLinks = isHomePage
    ? [
        { name: 'Features', href: '#features' },
        { name: 'Curriculum', href: '#curriculum' },
        { name: 'Testimonials', href: '#testimonials' },
      ]
    : [
        { name: 'Curriculum', href: '/docs/intro' },
        { name: 'Features', href: '/features' },
        { name: 'Testimonials', href: '/testimonials' },
        { name: 'Chapters', href: '/chapters' },
      ];

  const isActive = (href: string) => {
    const section = href.split('#')[1];
    if (!section || !isHomePage) return false;
    return false; // We'll handle active state differently for anchor links
  };

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? 'bg-gray-900/90 backdrop-blur-md shadow-lg'
          : 'bg-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            <Link href="/" className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
              PhysicalAI
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:block">
            <div className="flex items-center space-x-8">
              {navLinks.map((link) => {
                const isAnchorLink = link.href.startsWith('#');

                return (
                  <Link
                    key={link.name}
                    href={link.href}
                    className="text-gray-300 hover:text-white transition-colors duration-200"
                    onClick={(e) => {
                      if (isAnchorLink && isHomePage) {
                        e.preventDefault();
                        const targetElement = document.querySelector(link.href);
                        if (targetElement) {
                          targetElement.scrollIntoView({
                            behavior: 'smooth'
                          });
                        }
                      }
                    }}
                  >
                    {link.name}
                  </Link>
                );
              })}
            </div>
          </div>

          {/* Desktop Auth Buttons */}
          <div className="hidden md:flex items-center space-x-4">
            <Link
              href="/auth/login"
              className="px-4 py-2 text-gray-300 hover:text-white border border-gray-600 hover:border-gray-400 rounded-lg transition-all duration-200"
            >
              Sign In
            </Link>
            <Link
              href="/auth/signup"
              className="px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white rounded-lg transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              Create Account
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-gray-300 hover:text-white focus:outline-none"
            >
              <svg
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                {isMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="md:hidden bg-gray-900/95 backdrop-blur-md"
          >
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
              {navLinks.map((link) => {
                const isAnchorLink = link.href.startsWith('#');

                return (
                  <Link
                    key={link.name}
                    href={link.href}
                    className="block px-3 py-2 text-gray-300 hover:text-white hover:bg-gray-800 rounded-md"
                    onClick={(e) => {
                      if (isAnchorLink && isHomePage) {
                        e.preventDefault();
                        const targetElement = document.querySelector(link.href);
                        if (targetElement) {
                          targetElement.scrollIntoView({
                            behavior: 'smooth'
                          });
                        }
                      }
                      setIsMenuOpen(false);
                    }}
                  >
                    {link.name}
                  </Link>
                );
              })}
              <div className="pt-4 pb-3 border-t border-gray-700">
                <div className="flex flex-col space-y-3 px-3">
                  <Link
                    href="/auth/login"
                    className="px-4 py-2 text-gray-300 border border-gray-600 hover:border-gray-400 rounded-lg transition-all duration-200 text-center"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Sign In
                  </Link>
                  <Link
                    href="/auth/signup"
                    className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg transition-all duration-200 text-center"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Create Account
                  </Link>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
};

export default CustomNavbar;
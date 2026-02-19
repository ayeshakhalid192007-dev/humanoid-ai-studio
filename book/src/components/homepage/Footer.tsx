import React from 'react';
import { motion } from 'framer-motion';
import { homepageContent } from '@/data/homepage-content';

const Footer = () => {
  const { footer } = homepageContent;
  const currentYear = new Date().getFullYear();

  return (
    <footer className="py-12 border-t border-white/10">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="mb-6 md:mb-0"
          >
            <h3 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
              {footer.title}
            </h3>
            <p className="text-gray-400 mt-2 text-sm">
              {footer.tagline}
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="flex space-x-6"
          >
            <a
              href={footer.links.github}
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-white transition-colors text-sm"
            >
              GitHub
            </a>
            <a
              href={footer.links.contact}
              className="text-gray-400 hover:text-white transition-colors text-sm"
            >
              Contact
            </a>
            <a
              href={footer.links.community}
              className="text-gray-400 hover:text-white transition-colors text-sm"
            >
              Community
            </a>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-8 pt-8 border-t border-white/5 text-center text-gray-500 text-sm"
        >
          © {currentYear} {footer.copyright}. All rights reserved.
        </motion.div>
      </div>
    </footer>
  );
};

export { Footer };
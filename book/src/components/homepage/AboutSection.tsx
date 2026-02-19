import React from 'react';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/Card';
import { homepageContent } from '@/data/homepage-content';

const AboutSection = () => {
  const { about } = homepageContent;

  return (
    <section className="py-20">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="max-w-3xl mx-auto"
        >
          <Card variant="glass" className="p-8 md:p-12 text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
              {about.title}
            </h2>
            <p className="text-lg text-gray-300 mb-4">
              {about.description}
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6 text-left">
              {about.features.map((feature, index) => (
                <div key={index} className="text-gray-200">
                  <h3 className="font-semibold text-white mb-2">{feature.title}</h3>
                  <p className="text-sm">{feature.description}</p>
                </div>
              ))}
            </div>
          </Card>
        </motion.div>
      </div>
    </section>
  );
};

export { AboutSection };
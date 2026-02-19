import React from 'react';
import { motion } from 'framer-motion';
import { FeatureCard } from '@/components/homepage/FeatureCard';
import { homepageContent } from '@/data/homepage-content';

const FeaturesOverview = () => {
  const { featuresOverview } = homepageContent;

  return (
    <section className="py-20 bg-[#0f0f14]/50">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            {featuresOverview.title}
          </h2>
          <p className="text-lg text-gray-300 max-w-3xl mx-auto">
            {featuresOverview.subtitle}
          </p>
        </motion.div>

        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          variants={{
            hidden: { opacity: 0 },
            visible: {
              opacity: 1,
              transition: {
                staggerChildren: 0.1
              }
            }
          }}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          {featuresOverview.features.map((feature, index) => (
            <FeatureCard
              key={index}
              title={feature.title}
              description={feature.description}
              delay={index * 0.05}
            />
          ))}
        </motion.div>
      </div>
    </section>
  );
};

export { FeaturesOverview };
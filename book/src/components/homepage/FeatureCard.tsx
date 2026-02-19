import React from 'react';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/Card';

interface FeatureCardProps {
  title: string;
  description: string;
  icon?: React.ReactNode;
  delay?: number;
}

const FeatureCard: React.FC<FeatureCardProps> = ({
  title,
  description,
  icon,
  delay = 0
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.5 }}
      transition={{ duration: 0.5, delay }}
    >
      <Card className="p-5 hover:bg-white/15 transition-colors">
        <div className="flex items-start">
          <div className="mr-4 mt-1 text-blue-400">
            {icon || (
              <div className="w-6 h-6 rounded-full bg-blue-500"></div>
            )}
          </div>
          <div>
            <h3 className="text-lg font-bold text-white mb-2">{title}</h3>
            <p className="text-gray-300 text-sm">{description}</p>
          </div>
        </div>
      </Card>
    </motion.div>
  );
};

export { FeatureCard };
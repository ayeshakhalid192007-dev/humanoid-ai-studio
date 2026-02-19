import React from 'react';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/Card';

interface PillarCardProps {
  title: string;
  description: string;
  icon?: React.ReactNode;
  delay?: number;
}

const PillarCard: React.FC<PillarCardProps> = ({
  title,
  description,
  icon,
  delay = 0
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.3 }}
      transition={{ duration: 0.6, delay }}
    >
      <Card variant="glass" className="h-full p-6 flex flex-col items-center text-center">
        <div className="mb-4 text-blue-400">
          {icon || (
            <div className="w-12 h-12 rounded-full bg-blue-500/20 flex items-center justify-center mx-auto">
              <div className="w-6 h-6 rounded-full bg-blue-500"></div>
            </div>
          )}
        </div>
        <h3 className="text-xl font-bold text-white mb-3">{title}</h3>
        <p className="text-gray-300 text-sm">{description}</p>
      </Card>
    </motion.div>
  );
};

export { PillarCard };
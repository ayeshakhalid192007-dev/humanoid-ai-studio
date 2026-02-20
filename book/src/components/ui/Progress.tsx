import React from 'react';

interface ProgressProps {
  value: number;
  max?: number;
  label?: string;
  showPercentage?: boolean;
  className?: string;
}

export const Progress: React.FC<ProgressProps> = ({
  value,
  max = 100,
  label,
  showPercentage = false,
  className = '',
}) => {
  const percentage = Math.round((value / max) * 100);

  return (
    <div className={className}>
      {label && (
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-300">{label}</span>
          {showPercentage && (
            <span className="text-sm font-medium text-gray-400">{percentage}%</span>
          )}
        </div>
      )}

      <div className="w-full bg-white/10 rounded-full h-2.5">
        <div
          className="bg-gradient-to-r from-blue-500 to-purple-600 h-2.5 rounded-full transition-all duration-300 ease-out"
          style={{ width: `${percentage}%` }}
        ></div>
      </div>

      {!label && showPercentage && (
        <div className="mt-1 text-right">
          <span className="text-xs text-gray-400">{percentage}%</span>
        </div>
      )}
    </div>
  );
};
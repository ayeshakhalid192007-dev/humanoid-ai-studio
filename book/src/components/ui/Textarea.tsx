import React from 'react';

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Textarea: React.FC<TextareaProps> = ({
  label,
  error,
  helperText,
  className = '',
  ...props
}) => {
  const hasError = !!error;

  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-300 mb-2">
          {label}
        </label>
      )}

      <textarea
        {...props}
        className={`
          w-full rounded-lg py-3 px-4 bg-white/10 backdrop-blur-sm
          border ${hasError ? 'border-red-500' : 'border-white/20'}
          text-white placeholder-gray-400
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
          resize-y min-h-[100px]
          ${className}
        `}
      />

      {error && (
        <p className="mt-1 text-sm text-red-400">{error}</p>
      )}

      {!error && helperText && (
        <p className="mt-1 text-sm text-gray-400">{helperText}</p>
      )}
    </div>
  );
};
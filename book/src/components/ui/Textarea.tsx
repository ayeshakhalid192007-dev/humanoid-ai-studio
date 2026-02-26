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
        <label className="fm-body-sm text-fm-text-secondary mb-2 block">
          {label}
        </label>
      )}

      <textarea
        {...props}
        className={`
          w-full py-3 px-4 fm-bg-tertiary border
          ${hasError ? 'border-red-500' : 'border-fm-text-tertiary'}
          text-fm-text-primary rounded-lg
          placeholder:text-fm-text-tertiary
          focus:outline-none focus:ring-2 focus:ring-fm-accent-primary focus:border-transparent
          resize-y min-h-[100px]
          transition-all duration-200
          ${className}
        `}
      />

      {error && (
        <p className="mt-2 fm-body-sm text-red-400">{error}</p>
      )}

      {!error && helperText && (
        <p className="mt-2 fm-body-sm text-fm-text-tertiary">{helperText}</p>
      )}
    </div>
  );
};
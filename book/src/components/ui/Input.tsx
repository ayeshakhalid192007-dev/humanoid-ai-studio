import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  helperText,
  leftIcon,
  rightIcon,
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

      <div className="relative">
        {leftIcon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-fm-text-tertiary">
            {leftIcon}
          </div>
        )}

        <input
          {...props}
          className={`
            w-full py-3 px-4 fm-bg-tertiary border
            ${hasError ? 'border-red-500' : 'border-fm-text-tertiary'}
            text-fm-text-primary rounded-lg
            placeholder:text-fm-text-tertiary
            focus:outline-none focus:ring-2 focus:ring-fm-accent-primary focus:border-transparent
            ${leftIcon ? 'pl-10' : ''} ${rightIcon ? 'pr-10' : ''}
            transition-all duration-200
            ${className}
          `}
        />

        {rightIcon && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center text-fm-text-tertiary">
            {rightIcon}
          </div>
        )}
      </div>

      {error && (
        <p className="mt-2 fm-body-sm text-red-400">{error}</p>
      )}

      {!error && helperText && (
        <p className="mt-2 fm-body-sm text-fm-text-tertiary">{helperText}</p>
      )}
    </div>
  );
};
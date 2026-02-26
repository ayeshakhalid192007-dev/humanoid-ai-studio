import React from 'react';

interface SelectOption {
  label: string;
  value: string;
}

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  helperText?: string;
  options: SelectOption[];
}

export const Select: React.FC<SelectProps> = ({
  label,
  error,
  helperText,
  options,
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

      <select
        {...props}
        className={`
          w-full py-3 px-4 fm-bg-tertiary border
          ${hasError ? 'border-red-500' : 'border-fm-text-tertiary'}
          text-fm-text-primary rounded-lg
          focus:outline-none focus:ring-2 focus:ring-fm-accent-primary focus:border-transparent
          appearance-none
          transition-all duration-200
          ${className}
        `}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>

      {error && (
        <p className="mt-2 fm-body-sm text-red-400">{error}</p>
      )}

      {!error && helperText && (
        <p className="mt-2 fm-body-sm text-fm-text-tertiary">{helperText}</p>
      )}
    </div>
  );
};
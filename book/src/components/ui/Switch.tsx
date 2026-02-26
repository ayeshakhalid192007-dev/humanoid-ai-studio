import React from 'react';

interface SwitchProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
  disabled?: boolean;
  className?: string;
}

export const Switch: React.FC<SwitchProps> = ({
  checked,
  onChange,
  label,
  disabled = false,
  className = '',
}) => {
  const toggleSwitch = () => {
    if (!disabled) {
      onChange(!checked);
    }
  };

  return (
    <div className={`fm-flex-align-center ${className}`}>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        disabled={disabled}
        onClick={toggleSwitch}
        className={`
          relative inline-flex h-6 w-11 items-center rounded-full
          transition-colors focus:outline-none focus:ring-2 focus:ring-fm-accent-primary focus:ring-offset-2
          ${checked ? 'bg-fm-accent-primary' : 'bg-fm-bg-tertiary'}
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
      >
        <span
          className={`
            inline-block h-4 w-4 transform rounded-full bg-fm-text-primary transition-transform
            ${checked ? 'translate-x-6' : 'translate-x-1'}
          `}
        />
      </button>
      {label && (
        <span className={`ml-3 fm-body-sm ${disabled ? 'text-fm-text-tertiary' : 'text-fm-text-secondary'}`}>
          {label}
        </span>
      )}
    </div>
  );
};
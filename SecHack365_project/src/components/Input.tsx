import React from 'react';
import { InputProps } from '../types';

const Input: React.FC<InputProps> = ({
  value,
  onChange,
  placeholder,
  type = 'text',
  required = false,
  disabled = false,
  className = '',
  ...props
}) => {
  const baseClasses = 'form-control';
  const classes = [baseClasses, className].filter(Boolean).join(' ');

  if (type === 'textarea') {
    return (
      <textarea
        className={classes}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        required={required}
        disabled={disabled}
        rows={3}
        {...props}
      />
    );
  }

  return (
    <input
      type={type}
      className={classes}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      required={required}
      disabled={disabled}
      {...props}
    />
  );
};

export default Input;

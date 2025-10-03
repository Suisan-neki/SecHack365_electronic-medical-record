import React from 'react';
import { useAppStore } from '../store/useAppStore';

const ErrorMessage: React.FC<{ message: string }> = ({ message }) => {
  const { setError } = useAppStore();

  const handleClose = () => {
    setError(null);
  };

  if (!message) return null;

  return (
    <div className="alert alert-error">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>{message}</span>
        <button 
          onClick={handleClose}
          style={{ 
            background: 'none', 
            border: 'none', 
            fontSize: '18px', 
            cursor: 'pointer',
            color: '#721c24'
          }}
        >
          ×
        </button>
      </div>
    </div>
  );
};

export default ErrorMessage;

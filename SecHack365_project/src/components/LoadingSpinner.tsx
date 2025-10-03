import React from 'react';

const LoadingSpinner: React.FC = () => {
  return (
    <div className="loading">
      <div className="spinner"></div>
      <p>読み込み中...</p>
    </div>
  );
};

export default LoadingSpinner;

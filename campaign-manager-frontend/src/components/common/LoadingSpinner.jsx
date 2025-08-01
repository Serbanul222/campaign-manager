import React from 'react';

const LoadingSpinner = () => (
  <div className="flex justify-center items-center p-4">
    <div className="animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent" />
  </div>
);

export default LoadingSpinner;

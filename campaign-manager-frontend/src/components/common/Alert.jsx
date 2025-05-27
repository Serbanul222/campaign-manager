import React from 'react';
import PropTypes from 'prop-types';

const Alert = ({ type = 'info', message, onClose }) => {
  if (!message) {
    return null;
  }

  const baseClass = 'p-4 rounded mb-4';
  const typeClass = {
    info: 'bg-blue-100 text-blue-700',
    success: 'bg-green-100 text-green-700',
    error: 'bg-red-100 text-red-700',
    warning: 'bg-yellow-100 text-yellow-700',
  }[type];

  return (
    <div className={`${baseClass} ${typeClass}`}> 
      <div className="flex justify-between items-center">
        <span>{message}</span>
        {onClose && (
          <button
            type="button"
            className="text-xl font-bold focus:outline-none"
            onClick={onClose}
            aria-label="Close"
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
};

Alert.propTypes = {
  type: PropTypes.oneOf(['info', 'success', 'error', 'warning']),
  message: PropTypes.string,
  onClose: PropTypes.func,
};

export default Alert;

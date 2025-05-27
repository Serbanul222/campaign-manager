import React from 'react';
import PropTypes from 'prop-types';

const variants = {
  primary: 'bg-blue-600 text-white hover:bg-blue-700',
  secondary: 'bg-gray-200 text-gray-700 hover:bg-gray-300',
  danger: 'bg-red-600 text-white hover:bg-red-700',
};

const Button = ({
  children,
  type = 'button',
  variant = 'primary',
  className = '',
  disabled = false,
  ...rest
}) => (
  <button
    type={type}
    disabled={disabled}
    className={`px-4 py-2 rounded ${variants[variant]} ${className}`}
    {...rest}
  >
    {children}
  </button>
);

Button.propTypes = {
  children: PropTypes.node.isRequired,
  type: PropTypes.oneOf(['button', 'submit', 'reset']),
  variant: PropTypes.oneOf(['primary', 'secondary', 'danger']),
  className: PropTypes.string,
  disabled: PropTypes.bool,
};

export default Button;

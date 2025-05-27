import React from 'react';
import PropTypes from 'prop-types';

const Input = ({
  label,
  id,
  type = 'text',
  className = '',
  value,
  onChange,
  ...rest
}) => (
  <div className="mb-4">
    {label && (
      <label htmlFor={id} className="block text-sm font-medium mb-1">
        {label}
      </label>
    )}
    <input
      id={id}
      type={type}
      value={value}
      onChange={onChange}
      className={`border rounded px-3 py-2 w-full ${className}`}
      {...rest}
    />
  </div>
);

Input.propTypes = {
  label: PropTypes.string,
  id: PropTypes.string,
  type: PropTypes.string,
  className: PropTypes.string,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  onChange: PropTypes.func,
};

export default Input;

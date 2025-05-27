import React from 'react';
import PropTypes from 'prop-types';
import { NavLink } from 'react-router-dom';

const Navigation = ({ links }) => (
  <nav className="flex space-x-4">
    {links.map(({ to, label }) => (
      <NavLink
        key={to}
        to={to}
        className={({ isActive }) =>
          `text-gray-700 hover:text-blue-600 ${isActive ? 'font-semibold' : ''}`
        }
      >
        {label}
      </NavLink>
    ))}
  </nav>
);

Navigation.propTypes = {
  links: PropTypes.arrayOf(
    PropTypes.shape({
      to: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
    })
  ).isRequired,
};

export default Navigation;

import React from 'react';
import PropTypes from 'prop-types';
import { NavLink } from 'react-router-dom';

const Sidebar = ({ links, onClose }) => (
  <aside className="w-64 bg-gray-800 text-white min-h-screen">
    <div className="p-4 flex justify-between items-center">
      <span className="text-lg font-semibold">Campaign Manager</span>
      {onClose && (
        <button
          type="button"
          onClick={onClose}
          className="text-white lg:hidden"
          aria-label="Close sidebar"
        >
          ×
        </button>
      )}
    </div>
    <nav className="p-4 space-y-2">
      {links.map(({ to, label }) => (
        <NavLink
          key={to}
          to={to}
          className={({ isActive }) =>
            `block p-2 rounded hover:bg-gray-700 ${isActive ? 'bg-gray-700' : ''}`
          }
        >
          {label}
        </NavLink>
      ))}
    </nav>
  </aside>
);

Sidebar.propTypes = {
  links: PropTypes.arrayOf(
    PropTypes.shape({
      to: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
    })
  ).isRequired,
  onClose: PropTypes.func,
};

export default Sidebar;

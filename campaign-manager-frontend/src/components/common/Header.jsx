import React from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';

const Header = ({ title }) => (
  <header className="bg-gray-800 text-white p-4 flex justify-between">
    <h1 className="text-xl font-semibold">{title}</h1>
    <nav className="space-x-4">
      <Link to="/campaigns" className="hover:underline">
        Campaigns
      </Link>
      <Link to="/users" className="hover:underline">
        Users
      </Link>
      <Link to="/logs" className="hover:underline">
        Logs
      </Link>
    </nav>
  </header>
);

Header.propTypes = {
  title: PropTypes.string.isRequired,
};

export default Header;

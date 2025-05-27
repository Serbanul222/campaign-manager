import React from 'react';
import PropTypes from 'prop-types';

const Pagination = ({ currentPage, totalPages, onChange }) => {
  if (totalPages <= 1) {
    return null;
  }

  const pages = Array.from({ length: totalPages }, (_, i) => i + 1);

  return (
    <ul className="flex space-x-1">
      {pages.map((page) => (
        <li key={page}>
          <button
            type="button"
            className={`px-3 py-1 rounded ${
              page === currentPage ? 'bg-blue-600 text-white' : 'bg-gray-200'
            }`}
            onClick={() => onChange(page)}
          >
            {page}
          </button>
        </li>
      ))}
    </ul>
  );
};

Pagination.propTypes = {
  currentPage: PropTypes.number.isRequired,
  totalPages: PropTypes.number.isRequired,
  onChange: PropTypes.func.isRequired,
};

export default Pagination;

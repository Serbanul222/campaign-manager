 
import React from 'react';

const LogsFilter = ({ onRefresh }) => (
  <button onClick={onRefresh} className="mb-2">
    Refresh
  </button>
);

export default LogsFilter;


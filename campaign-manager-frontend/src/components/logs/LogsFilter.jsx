// components/logs/LogsFilter.jsx - Enhanced filtering component
import React from 'react';
import { X, Calendar, User, Activity, AlertTriangle } from 'lucide-react';

const LogsFilter = ({ filters, filterOptions, onFilterChange, onReset }) => {
  const handleFilterChange = (key, value) => {
    onFilterChange({ [key]: value });
  };

  const formatDateForInput = (dateString) => {
    if (!dateString) return '';
    return dateString.split('T')[0]; // Extract YYYY-MM-DD part
  };

  const handleDateChange = (key, value) => {
    // Convert to ISO string for API
    const isoDate = value ? new Date(value).toISOString() : '';
    onFilterChange({ [key]: isoDate });
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900">Filter Activity Logs</h3>
        <button
          onClick={onReset}
          className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1"
        >
          <X size={16} />
          Clear All
        </button>
      </div>

      {/* Filter Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {/* User Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            <User size={16} className="inline mr-1" />
            User
          </label>
          <select
            value={filters.user_id}
            onChange={(e) => handleFilterChange('user_id', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Users</option>
            {filterOptions.users?.map(user => (
              <option key={user.id} value={user.id}>
                {user.email}
              </option>
            ))}
          </select>
        </div>

        {/* Action Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            <Activity size={16} className="inline mr-1" />
            Action
          </label>
          <select
            value={filters.action}
            onChange={(e) => handleFilterChange('action', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Actions</option>
            {filterOptions.actions?.map(action => (
              <option key={action} value={action}>
                {action.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </option>
            ))}
          </select>
        </div>

        {/* Status Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            <AlertTriangle size={16} className="inline mr-1" />
            Status
          </label>
          <select
            value={filters.status}
            onChange={(e) => handleFilterChange('status', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Statuses</option>
            {filterOptions.statuses?.map(status => (
              <option key={status} value={status}>
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </option>
            ))}
          </select>
        </div>

        {/* Resource Type Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Resource Type
          </label>
          <select
            value={filters.resource_type}
            onChange={(e) => handleFilterChange('resource_type', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Types</option>
            {filterOptions.resource_types?.map(type => (
              <option key={type} value={type}>
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </option>
            ))}
          </select>
        </div>

        {/* Start Date Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            <Calendar size={16} className="inline mr-1" />
            Start Date
          </label>
          <input
            type="date"
            value={formatDateForInput(filters.start_date)}
            onChange={(e) => handleDateChange('start_date', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* End Date Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            <Calendar size={16} className="inline mr-1" />
            End Date
          </label>
          <input
            type="date"
            value={formatDateForInput(filters.end_date)}
            onChange={(e) => handleDateChange('end_date', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Active Filters Display */}
      <div className="flex flex-wrap gap-2">
        {Object.entries(filters).map(([key, value]) => {
          if (!value || key === 'page' || key === 'per_page') return null;
          
          let displayValue = value;
          if (key === 'user_id') {
            const user = filterOptions.users?.find(u => u.id.toString() === value);
            displayValue = user?.email || value;
          } else if (key === 'start_date' || key === 'end_date') {
            displayValue = formatDateForInput(value);
          } else if (key === 'action') {
            displayValue = value.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
          }
          
          return (
            <span
              key={key}
              className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
            >
              {key.replace(/_/g, ' ')}: {displayValue}
              <button
                onClick={() => handleFilterChange(key, '')}
                className="ml-2 text-blue-600 hover:text-blue-800"
              >
                <X size={14} />
              </button>
            </span>
          );
        })}
      </div>
    </div>
  );
};

export default LogsFilter;
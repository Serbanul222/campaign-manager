// components/logs/LogEntry.jsx - Enhanced log entry component
import React from 'react';

const LogEntry = ({ log, onClick, formatDate, getStatusIcon, getActionColor }) => {
  const truncateText = (text, maxLength = 50) => {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };

  const formatDuration = (durationMs) => {
    if (!durationMs) return '';
    if (durationMs < 1000) return `${durationMs}ms`;
    return `${(durationMs / 1000).toFixed(1)}s`;
  };

  return (
    <tr 
      className="hover:bg-gray-50 cursor-pointer transition-colors"
      onClick={() => onClick && onClick()}
    >
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
        <div className="flex flex-col">
          <span>{formatDate(log.created_at)}</span>
          {log.duration_ms && (
            <span className="text-xs text-gray-500">
              {formatDuration(log.duration_ms)}
            </span>
          )}
        </div>
      </td>
      
      <td className="px-6 py-4 whitespace-nowrap">
        <div className="flex items-center">
          <div className="text-sm font-medium text-gray-900">
            {log.user_email || `User #${log.user_id}`}
          </div>
        </div>
      </td>
      
      <td className="px-6 py-4 whitespace-nowrap">
        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getActionColor(log.action)}`}>
          {log.action.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
        </span>
      </td>
      
      <td className="px-6 py-4 whitespace-nowrap">
        <div className="flex items-center">
          {getStatusIcon(log.status)}
          <span className="ml-2 text-sm text-gray-900 capitalize">
            {log.status}
          </span>
        </div>
      </td>
      
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
        {log.resource_type && log.resource_id ? (
          <div>
            <div className="font-medium">{log.resource_type}</div>
            <div className="text-gray-500">#{log.resource_id}</div>
          </div>
        ) : (
          <span className="text-gray-400">-</span>
        )}
      </td>
      
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        {log.ip_address || '-'}
      </td>
      
      <td className="px-6 py-4 text-sm text-gray-900 max-w-xs">
        {log.details ? (
          <div className="truncate" title={log.details}>
            {truncateText(log.details, 100)}
          </div>
        ) : (
          <span className="text-gray-400">-</span>
        )}
      </td>
    </tr>
  );
};

export default LogEntry;
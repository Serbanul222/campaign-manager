// components/logs/LogDetailModal.jsx - Detailed log view modal
import React, { useState } from 'react';
import { X, Copy, CheckCircle, User, Clock, Globe, Database, FileText } from 'lucide-react';

const LogDetailModal = ({ log, onClose, formatDate, getStatusIcon, getActionColor }) => {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const formatDetails = (details) => {
    if (!details) return 'No additional details';
    
    try {
      const parsed = JSON.parse(details);
      return JSON.stringify(parsed, null, 2);
    } catch {
      return details;
    }
  };

  const getDetailsSummary = (details) => {
    if (!details) return null;
    
    try {
      const parsed = JSON.parse(details);
      return parsed;
    } catch {
      return { raw: details };
    }
  };

  const detailsObj = getDetailsSummary(log.details);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-screen overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            {getStatusIcon(log.status)}
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                Activity Log Details
              </h2>
              <p className="text-sm text-gray-600">
                {formatDate(log.created_at)}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-96">
          {/* Basic Information Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <User className="h-5 w-5 text-gray-400" />
                <div>
                  <div className="text-sm font-medium text-gray-700">User</div>
                  <div className="text-gray-900">
                    {log.user_email || `User #${log.user_id}`}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <Database className="h-5 w-5 text-gray-400" />
                <div>
                  <div className="text-sm font-medium text-gray-700">Action</div>
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getActionColor(log.action)}`}>
                    {log.action.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </span>
                </div>
              </div>

                              <div className="flex items-center gap-3">
                <Globe className="h-5 w-5 text-gray-400" />
                <div>
                  <div className="text-sm font-medium text-gray-700">IP Address</div>
                  <div className="text-gray-900">{log.ip_address || 'Unknown'}</div>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              {log.resource_type && (
                <div className="flex items-center gap-3">
                  <FileText className="h-5 w-5 text-gray-400" />
                  <div>
                    <div className="text-sm font-medium text-gray-700">Resource</div>
                    <div className="text-gray-900">
                      {log.resource_type} #{log.resource_id}
                    </div>
                  </div>
                </div>
              )}

              {log.duration_ms && (
                <div className="flex items-center gap-3">
                  <Clock className="h-5 w-5 text-gray-400" />
                  <div>
                    <div className="text-sm font-medium text-gray-700">Duration</div>
                    <div className="text-gray-900">
                      {log.duration_ms < 1000 ? `${log.duration_ms}ms` : `${(log.duration_ms / 1000).toFixed(1)}s`}
                    </div>
                  </div>
                </div>
              )}

              <div className="flex items-center gap-3">
                <div className="h-5 w-5 flex items-center justify-center">
                  {getStatusIcon(log.status)}
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-700">Status</div>
                  <div className="text-gray-900 capitalize">{log.status}</div>
                </div>
              </div>
            </div>
          </div>

          {/* Details Section */}
          {log.details && (
            <div className="border-t border-gray-200 pt-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Additional Details</h3>
                <button
                  onClick={() => copyToClipboard(formatDetails(log.details))}
                  className="flex items-center gap-2 px-3 py-1 text-sm text-gray-600 hover:text-gray-800 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                >
                  {copied ? <CheckCircle size={16} /> : <Copy size={16} />}
                  {copied ? 'Copied!' : 'Copy'}
                </button>
              </div>

              {/* Formatted Details */}
              {detailsObj && typeof detailsObj === 'object' && !detailsObj.raw && (
                <div className="mb-4 space-y-3">
                  {Object.entries(detailsObj).map(([key, value]) => (
                    <div key={key} className="flex flex-col sm:flex-row sm:items-start gap-2">
                      <div className="text-sm font-medium text-gray-700 sm:w-32 flex-shrink-0 capitalize">
                        {key.replace(/_/g, ' ')}:
                      </div>
                      <div className="text-sm text-gray-900 flex-1">
                        {typeof value === 'object' ? (
                          <pre className="bg-gray-50 p-2 rounded text-xs overflow-x-auto">
                            {JSON.stringify(value, null, 2)}
                          </pre>
                        ) : (
                          <span>{String(value)}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Raw Details */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Raw Details</h4>
                <pre className="text-xs text-gray-600 whitespace-pre-wrap overflow-x-auto">
                  {formatDetails(log.details)}
                </pre>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 p-6 border-t border-gray-200">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default LogDetailModal;
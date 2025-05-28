// components/logs/ActivityLogViewer.jsx - Main logs component
import React, { useState, useEffect } from 'react';
import { 
  Search, Filter, Download, RefreshCw, Calendar, 
  User, Activity, AlertCircle, CheckCircle, 
  XCircle, Clock, ChevronLeft, ChevronRight 
} from 'lucide-react';
import { fetchLogs, exportLogs, getLogStats } from '../../services/logs';
import LogsFilter from './LogsFilter';
import LogEntry from './LogEntry';
import LogStats from './LogStats';
import LogDetailModal from './LogDetailModal';

const ActivityLogViewer = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    user_id: '',
    action: '',
    status: '',
    resource_type: '',
    start_date: '',
    end_date: '',
    page: 1,
    per_page: 50
  });
  
  const [pagination, setPagination] = useState({});
  const [filterOptions, setFilterOptions] = useState({
    users: [],
    actions: [],
    statuses: [],
    resource_types: []
  });
  const [showFilters, setShowFilters] = useState(false);
  const [stats, setStats] = useState(null);
  const [selectedLog, setSelectedLog] = useState(null);

  const loadLogs = async (newFilters = filters) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetchLogs(newFilters);
      const data = response.data;
      
      setLogs(data.logs || []);
      setPagination(data.pagination || {});
      setFilterOptions(data.filters || {});
      
      // Load stats if no specific filters are applied
      if (!newFilters.user_id && !newFilters.action && !newFilters.status) {
        try {
          const statsResponse = await getLogStats({
            start_date: newFilters.start_date,
            end_date: newFilters.end_date
          });
          setStats(statsResponse.data);
        } catch (statsError) {
          console.warn('Failed to load stats:', statsError);
        }
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load activity logs');
      console.error('Load logs error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (newFilters) => {
    const updatedFilters = { ...filters, ...newFilters, page: 1 };
    setFilters(updatedFilters);
    loadLogs(updatedFilters);
  };

  const handlePageChange = (newPage) => {
    const updatedFilters = { ...filters, page: newPage };
    setFilters(updatedFilters);
    loadLogs(updatedFilters);
  };

  const handleExport = async () => {
    try {
      setLoading(true);
      const response = await exportLogs(filters);
      const data = response.data;
      
      // Create and download CSV file
      const blob = new Blob([data.csv_data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = data.filename || 'activity_logs.csv';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to export logs');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'warning':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getActionColor = (action) => {
    if (action.includes('create')) return 'bg-green-100 text-green-800';
    if (action.includes('update')) return 'bg-blue-100 text-blue-800';
    if (action.includes('delete')) return 'bg-red-100 text-red-800';
    if (action.includes('login')) return 'bg-purple-100 text-purple-800';
    if (action.includes('logout')) return 'bg-gray-100 text-gray-800';
    return 'bg-gray-100 text-gray-800';
  };

  useEffect(() => {
    loadLogs();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Activity Logs</h1>
              <p className="text-gray-600 mt-1">Monitor all system activities and user actions</p>
            </div>
            
            <div className="flex gap-3">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${
                  showFilters 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <Filter size={18} />
                Filters
              </button>
              
              <button
                onClick={() => loadLogs()}
                disabled={loading}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center gap-2 transition-colors disabled:opacity-50"
              >
                <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
                Refresh
              </button>
              
              <button
                onClick={handleExport}
                disabled={loading}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2 transition-colors disabled:opacity-50"
              >
                <Download size={18} />
                Export CSV
              </button>
            </div>
          </div>

          {/* Stats */}
          {stats && <LogStats stats={stats} />}
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <LogsFilter
              filters={filters}
              filterOptions={filterOptions}
              onFilterChange={handleFilterChange}
              onReset={() => {
                const resetFilters = {
                  user_id: '',
                  action: '',
                  status: '',
                  resource_type: '',
                  start_date: '',
                  end_date: '',
                  page: 1,
                  per_page: 50
                };
                setFilters(resetFilters);
                loadLogs(resetFilters);
              }}
            />
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 flex items-center">
            <AlertCircle className="h-4 w-4 mr-2 flex-shrink-0" />
            <span>{error}</span>
            <button 
              onClick={() => setError('')}
              className="ml-auto text-red-500 hover:text-red-700 text-xl font-bold"
            >
              ×
            </button>
          </div>
        )}

        {/* Logs Table */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
              <span className="ml-3 text-gray-600">Loading activity logs...</span>
            </div>
          ) : logs.length === 0 ? (
            <div className="text-center py-12">
              <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No activity logs found</h3>
              <p className="text-gray-600">Try adjusting your filters or check back later.</p>
            </div>
          ) : (
            <>
              {/* Desktop Table */}
              <div className="hidden md:block overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Date/Time
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        User
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Action
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Resource
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        IP Address
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Details
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {logs.map((log) => (
                      <LogEntry 
                        key={log.id} 
                        log={log} 
                        onClick={() => setSelectedLog(log)}
                        formatDate={formatDate}
                        getStatusIcon={getStatusIcon}
                        getActionColor={getActionColor}
                      />
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Mobile Cards */}
              <div className="md:hidden space-y-4 p-4">
                {logs.map((log) => (
                  <div 
                    key={log.id} 
                    className="bg-white border rounded-lg p-4 cursor-pointer hover:shadow-md transition-shadow"
                    onClick={() => setSelectedLog(log)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(log.status)}
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getActionColor(log.action)}`}>
                          {log.action}
                        </span>
                      </div>
                      <span className="text-xs text-gray-500">
                        {formatDate(log.created_at)}
                      </span>
                    </div>
                    <div className="text-sm text-gray-900 mb-1">
                      {log.user_email}
                    </div>
                    {log.resource_type && (
                      <div className="text-xs text-gray-500">
                        {log.resource_type} #{log.resource_id}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* Pagination */}
              {pagination.pages > 1 && (
                <div className="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
                  <div className="flex items-center justify-between">
                    <div className="flex-1 flex justify-between sm:hidden">
                      <button
                        onClick={() => handlePageChange(pagination.page - 1)}
                        disabled={!pagination.has_prev}
                        className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Previous
                      </button>
                      <button
                        onClick={() => handlePageChange(pagination.page + 1)}
                        disabled={!pagination.has_next}
                        className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Next
                      </button>
                    </div>
                    
                    <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                      <div>
                        <p className="text-sm text-gray-700">
                          Showing page <span className="font-medium">{pagination.page}</span> of{' '}
                          <span className="font-medium">{pagination.pages}</span>
                          {' '}({pagination.total} total records)
                        </p>
                      </div>
                      <div>
                        <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                          <button
                            onClick={() => handlePageChange(pagination.page - 1)}
                            disabled={!pagination.has_prev}
                            className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            <ChevronLeft className="h-5 w-5" />
                          </button>
                          
                          {/* Page numbers */}
                          {Array.from({ length: Math.min(5, pagination.pages) }, (_, i) => {
                            const pageNum = Math.max(1, pagination.page - 2) + i;
                            if (pageNum > pagination.pages) return null;
                            
                            return (
                              <button
                                key={pageNum}
                                onClick={() => handlePageChange(pageNum)}
                                className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                                  pageNum === pagination.page
                                    ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                                    : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                                }`}
                              >
                                {pageNum}
                              </button>
                            );
                          })}
                          
                          <button
                            onClick={() => handlePageChange(pagination.page + 1)}
                            disabled={!pagination.has_next}
                            className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            <ChevronRight className="h-5 w-5" />
                          </button>
                        </nav>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Log Detail Modal */}
        {selectedLog && (
          <LogDetailModal 
            log={selectedLog} 
            onClose={() => setSelectedLog(null)}
            formatDate={formatDate}
            getStatusIcon={getStatusIcon}
            getActionColor={getActionColor}
          />
        )}
      </div>
    </div>
  );
};

export default ActivityLogViewer;

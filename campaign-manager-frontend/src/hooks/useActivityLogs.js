// hooks/useActivityLogs.js - Custom hook for activity logs management
import { useState, useEffect, useCallback } from 'react';
import { fetchLogs, exportLogs, getLogStats } from '../services/logs';

const useActivityLogs = (initialFilters = {}) => {
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
    per_page: 50,
    ...initialFilters
  });
  
  const [pagination, setPagination] = useState({});
  const [filterOptions, setFilterOptions] = useState({
    users: [],
    actions: [],
    statuses: [],
    resource_types: []
  });
  const [stats, setStats] = useState(null);

  const loadLogs = useCallback(async (newFilters = filters) => {
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
  }, [filters]);

  const updateFilters = useCallback((newFilters) => {
    const updatedFilters = { ...filters, ...newFilters, page: 1 };
    setFilters(updatedFilters);
    loadLogs(updatedFilters);
  }, [filters, loadLogs]);

  const changePage = useCallback((newPage) => {
    const updatedFilters = { ...filters, page: newPage };
    setFilters(updatedFilters);
    loadLogs(updatedFilters);
  }, [filters, loadLogs]);

  const resetFilters = useCallback(() => {
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
  }, [loadLogs]);

  const exportLogsData = useCallback(async () => {
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
      
      return true;
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to export logs');
      return false;
    } finally {
      setLoading(false);
    }
  }, [filters]);

  const refreshLogs = useCallback(() => {
    loadLogs(filters);
  }, [filters, loadLogs]);

  const clearError = useCallback(() => {
    setError('');
  }, []);

  useEffect(() => {
    loadLogs();
  }, []);

  return {
    logs,
    loading,
    error,
    filters,
    pagination,
    filterOptions,
    stats,
    updateFilters,
    changePage,
    resetFilters,
    exportLogsData,
    refreshLogs,
    clearError
  };
};

export default useActivityLogs;
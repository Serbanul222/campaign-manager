// services/logs.js - Enhanced logs service with admin checks
import api from './api';

export const fetchLogs = async (filters = {}) => {
  try {
    const params = new URLSearchParams();
    
    // Add filter parameters
    if (filters.user_id) params.append('user_id', filters.user_id);
    if (filters.action) params.append('action', filters.action);
    if (filters.status) params.append('status', filters.status);
    if (filters.resource_type) params.append('resource_type', filters.resource_type);
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    if (filters.page) params.append('page', filters.page);
    if (filters.per_page) params.append('per_page', filters.per_page);
    
    const response = await api.get(`/logs?${params.toString()}`);
    return response;
  } catch (error) {
    // Handle admin-only access errors
    if (error.response?.status === 403) {
      throw new Error('Admin access required to view activity logs');
    }
    throw error;
  }
};

export const exportLogs = async (filters = {}) => {
  try {
    const params = new URLSearchParams();
    
    // Add same filter parameters for export
    if (filters.user_id) params.append('user_id', filters.user_id);
    if (filters.action) params.append('action', filters.action);
    if (filters.status) params.append('status', filters.status);
    if (filters.resource_type) params.append('resource_type', filters.resource_type);
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    
    const response = await api.get(`/logs/export?${params.toString()}`);
    return response;
  } catch (error) {
    if (error.response?.status === 403) {
      throw new Error('Admin access required to export activity logs');
    }
    throw error;
  }
};

export const getLogStats = async (filters = {}) => {
  try {
    const params = new URLSearchParams();
    
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    
    const response = await api.get(`/logs/stats?${params.toString()}`);
    return response;
  } catch (error) {
    if (error.response?.status === 403) {
      throw new Error('Admin access required to view activity statistics');
    }
    throw error;
  }
};
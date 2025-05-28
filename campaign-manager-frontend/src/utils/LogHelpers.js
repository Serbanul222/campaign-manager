// utils/logHelpers.js - Utility functions for log processing
export const formatLogAction = (action) => {
  return action
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (l) => l.toUpperCase());
};

export const getActionCategory = (action) => {
  if (action.includes('create')) return 'create';
  if (action.includes('update') || action.includes('edit')) return 'update';
  if (action.includes('delete')) return 'delete';
  if (action.includes('login') || action.includes('logout')) return 'auth';
  if (action.includes('view') || action.includes('list')) return 'view';
  return 'other';
};

export const getActionColor = (action) => {
  const category = getActionCategory(action);
  
  switch (category) {
    case 'create':
      return 'bg-green-100 text-green-800';
    case 'update':
      return 'bg-blue-100 text-blue-800';
    case 'delete':
      return 'bg-red-100 text-red-800';
    case 'auth':
      return 'bg-purple-100 text-purple-800';
    case 'view':
      return 'bg-gray-100 text-gray-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

export const getStatusIcon = (status) => {
  // This would typically import from lucide-react
  // Placeholder for the actual implementation
  return null;
};

export const formatDuration = (durationMs) => {
  if (!durationMs) return '';
  if (durationMs < 1000) return `${durationMs}ms`;
  return `${(durationMs / 1000).toFixed(1)}s`;
};

export const formatTimestamp = (timestamp) => {
  return new Date(timestamp).toLocaleString();
};

export const parseLogDetails = (details) => {
  if (!details) return null;
  
  try {
    return JSON.parse(details);
  } catch {
    return { raw: details };
  }
};

export const extractLogSummary = (log) => {
  const details = parseLogDetails(log.details);
  
  if (!details) return null;
  
  // Extract key information based on action type
  const summary = {};
  
  if (log.action.includes('campaign')) {
    summary.campaign_name = details.campaign_name;
    summary.campaign_id = details.campaign_id;
  }
  
  if (log.action.includes('user')) {
    summary.user_email = details.created_user_email || details.deleted_user?.email;
  }
  
  if (details.changes) {
    summary.changes = Object.keys(details.changes);
  }
  
  return summary;
};
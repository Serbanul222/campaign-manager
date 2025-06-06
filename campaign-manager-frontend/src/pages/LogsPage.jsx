// pages/LogsPage.jsx - Admin-protected logs page
import React from 'react';
import { Navigate } from 'react-router-dom';
import { Shield, AlertTriangle } from 'lucide-react';
import useAuth from '../hooks/useAuth.js';
import ActivityLogViewer from '../components/logs/ActivityLogViewer';

const LogsPage = () => {
  const { user, loading } = useAuth();

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
        <span className="ml-2 text-gray-600">Loading...</span>
      </div>
    );
  }

  // Redirect non-admin users to dashboard
  if (!user?.is_admin) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="min-h-screen">
      <ActivityLogViewer />
    </div>
  );
};

// Alternative component for when non-admin users somehow access this page
export const AdminOnlyMessage = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
      <div className="max-w-md w-full bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
        <div className="mx-auto h-16 w-16 bg-red-100 rounded-full flex items-center justify-center mb-6">
          <Shield className="h-8 w-8 text-red-600" />
        </div>
        
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          Admin Access Required
        </h1>
        
        <p className="text-gray-600 mb-6">
          Activity logs are only accessible to administrators. Please contact your system administrator if you need access to this feature.
        </p>
        
        <div className="space-y-3">
          <a
            href="/dashboard"
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-blue-700 transition-colors inline-block"
          >
            Return to Dashboard
          </a>
          
          <p className="text-xs text-gray-500">
            Only users with administrator privileges can view system activity logs
          </p>
        </div>
      </div>
    </div>
  );
};

export default LogsPage;
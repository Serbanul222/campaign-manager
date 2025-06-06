import React from 'react';
import { Link } from 'react-router-dom';
import { Calendar, Users, Activity, Plus } from 'lucide-react';
import useAuth from '../hooks/useAuth.js';

const DashboardPage = () => {
  const { user } = useAuth();

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Welcome back, {user?.email}!
        </h1>
        <p className="text-gray-600">
          Manage your promotional campaigns from this dashboard.
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <Link 
          to="/campaigns" 
          className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
        >
          <div className="flex items-center">
            <div className="bg-blue-100 p-3 rounded-lg">
              <Calendar className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-gray-900">Campaigns</h3>
              <p className="text-gray-600 text-sm">Manage promotional campaigns</p>
            </div>
          </div>
        </Link>

        {user?.is_admin && (
          <>
            <Link 
              to="/users" 
              className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center">
                <div className="bg-green-100 p-3 rounded-lg">
                  <Users className="h-6 w-6 text-green-600" />
                </div>
                <div className="ml-4">
                  <h3 className="text-lg font-semibold text-gray-900">Users</h3>
                  <p className="text-gray-600 text-sm">Manage user access</p>
                </div>
              </div>
            </Link>

            <Link 
              to="/logs" 
              className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center">
                <div className="bg-purple-100 p-3 rounded-lg">
                  <Activity className="h-6 w-6 text-purple-600" />
                </div>
                <div className="ml-4">
                  <h3 className="text-lg font-semibold text-gray-900">Activity Logs</h3>
                  <p className="text-gray-600 text-sm">View system activity (Admin only)</p>
                </div>
              </div>
            </Link>
          </>
        )}
      </div>

      {/* Admin notice */}
      {user?.is_admin && (
        <div className="bg-gradient-to-r from-purple-500 to-indigo-600 rounded-lg p-6 text-white mb-6">
          <div className="flex items-center">
            <div className="bg-white bg-opacity-20 p-2 rounded-lg">
              <Activity className="h-6 w-6" />
            </div>
            <div className="ml-4">
              <h2 className="text-lg font-semibold mb-1">Administrator Access</h2>
              <p className="text-purple-100 text-sm">
                You have access to user management and system activity logs
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Quick Create Campaign */}
      <div className="bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold mb-2">Ready to create a campaign?</h2>
            <p className="text-blue-100">Upload images and schedule your next promotion</p>
          </div>
          <Link 
            to="/campaigns"
            className="bg-white text-blue-600 px-4 py-2 rounded-lg font-medium hover:bg-blue-50 transition-colors flex items-center"
          >
            <Plus className="h-4 w-4 mr-2" />
            New Campaign
          </Link>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
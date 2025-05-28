// components/logs/LogStats.jsx - Statistics dashboard for logs
import React from 'react';
import { TrendingUp, Users, Activity, AlertTriangle } from 'lucide-react';

const LogStats = ({ stats }) => {
  if (!stats) return null;

  const formatPercent = (value) => `${value}%`;

  return (
    <div className="border-t pt-6 mt-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Activity Statistics</h3>
      
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="flex items-center">
            <Activity className="h-8 w-8 text-blue-600" />
            <div className="ml-3">
              <div className="text-2xl font-bold text-blue-600">
                {stats.summary?.total_actions || 0}
              </div>
              <div className="text-sm text-blue-600">Total Actions</div>
            </div>
          </div>
        </div>

        <div className="bg-red-50 p-4 rounded-lg">
          <div className="flex items-center">
            <AlertTriangle className="h-8 w-8 text-red-600" />
            <div className="ml-3">
              <div className="text-2xl font-bold text-red-600">
                {stats.summary?.error_actions || 0}
              </div>
              <div className="text-sm text-red-600">Errors</div>
            </div>
          </div>
        </div>

        <div className="bg-green-50 p-4 rounded-lg">
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <div className="text-2xl font-bold text-green-600">
                {formatPercent(100 - (stats.summary?.error_rate || 0))}
              </div>
              <div className="text-sm text-green-600">Success Rate</div>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Daily Activity Chart */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="font-medium text-gray-900 mb-3">Daily Activity</h4>
          <div className="space-y-2">
            {stats.daily_activity?.slice(-7).map((day, index) => (
              <div key={day.date} className="flex items-center justify-between">
                <span className="text-sm text-gray-600">
                  {new Date(day.date).toLocaleDateString('en-US', { 
                    month: 'short', 
                    day: 'numeric' 
                  })}
                </span>
                <div className="flex items-center">
                  <div 
                    className="bg-blue-200 h-2 rounded mr-2"
                    style={{ 
                      width: `${Math.max(10, (day.count / Math.max(...stats.daily_activity.map(d => d.count))) * 100)}px` 
                    }}
                  ></div>
                  <span className="text-sm font-medium text-gray-900">
                    {day.count}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Users */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="font-medium text-gray-900 mb-3">Most Active Users</h4>
          <div className="space-y-2">
            {stats.top_users?.slice(0, 5).map((user, index) => (
              <div key={user.email} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white mr-2 ${
                    index === 0 ? 'bg-yellow-500' : 
                    index === 1 ? 'bg-gray-400' : 
                    index === 2 ? 'bg-orange-600' : 'bg-blue-500'
                  }`}>
                    {index + 1}
                  </div>
                  <span className="text-sm text-gray-600 truncate" title={user.email}>
                    {user.email.length > 20 ? user.email.substring(0, 20) + '...' : user.email}
                  </span>
                </div>
                <span className="text-sm font-medium text-gray-900">
                  {user.count}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Top Actions */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="font-medium text-gray-900 mb-3">Most Common Actions</h4>
          <div className="space-y-2">
            {stats.top_actions?.slice(0, 5).map((action, index) => (
              <div key={action.action} className="flex items-center justify-between">
                <span className="text-sm text-gray-600 capitalize">
                  {action.action.replace(/_/g, ' ')}
                </span>
                <div className="flex items-center">
                  <div 
                    className="bg-green-200 h-2 rounded mr-2"
                    style={{ 
                      width: `${Math.max(10, (action.count / Math.max(...stats.top_actions.map(a => a.count))) * 60)}px` 
                    }}
                  ></div>
                  <span className="text-sm font-medium text-gray-900">
                    {action.count}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LogStats;
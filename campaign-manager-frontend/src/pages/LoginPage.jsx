import React from 'react';
import Login from '../components/auth/Login.jsx';

const LoginPage = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Campaign Manager</h1>
          <p className="text-gray-600">Sign in to manage your promotional campaigns</p>
        </div>

        {/* Login Form */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <Login />
        </div>

        {/* Footer */}
        <div className="text-center mt-6">
          <p className="text-xs text-gray-500">
            Secure access for authorized users only
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
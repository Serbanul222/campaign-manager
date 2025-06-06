import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext.jsx';

// Auth components
import LoginPage from './pages/LoginPage.jsx';
import SetPasswordPage from './pages/SetPasswordPage.jsx';
import ProtectedRoute from './components/auth/ProtectedRoute.jsx';

// Main app pages
import DashboardPage from './pages/DashboardPage.jsx';
import CampaignsPage from './pages/CampaignsPage.jsx';
import UsersPage from './pages/UsersPage.jsx';
import LogsPage from './pages/LogsPage.jsx';

// Layout
import MainLayout from './components/layout/MainLayout.jsx';

// CSS
import './index.css';

// Import useAuth hook
import useAuth from './hooks/useAuth.js';

// Admin-only route component
const AdminRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
        <span className="ml-2 text-gray-600">Loading...</span>
      </div>
    );
  }
  
  if (!user?.is_admin) {
    return <Navigate to="/dashboard" replace />;
  }
  
  return children;
};

const App = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/set-password" element={<SetPasswordPage />} />
          
          {/* Protected routes with layout */}
          <Route path="/" element={
            <ProtectedRoute>
              <MainLayout>
                <Navigate to="/dashboard" replace />
              </MainLayout>
            </ProtectedRoute>
          } />
          
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <MainLayout>
                <DashboardPage />
              </MainLayout>
            </ProtectedRoute>
          } />
          
          <Route path="/campaigns" element={
            <ProtectedRoute>
              <MainLayout>
                <CampaignsPage />
              </MainLayout>
            </ProtectedRoute>
          } />
          
          {/* Admin-only routes */}
          <Route path="/users" element={
            <ProtectedRoute>
              <AdminRoute>
                <MainLayout>
                  <UsersPage />
                </MainLayout>
              </AdminRoute>
            </ProtectedRoute>
          } />
          
          <Route path="/logs" element={
            <ProtectedRoute>
              <AdminRoute>
                <MainLayout>
                  <LogsPage />
                </MainLayout>
              </AdminRoute>
            </ProtectedRoute>
          } />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
import React, { createContext, useContext, useState, useEffect } from 'react';
import { login, setPassword, logout, getCurrentUser } from '../services/auth';
import { isTokenExpired } from '../utils/jwt';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // Function to fetch current user details from backend
  const fetchCurrentUser = async () => {
    try {
      console.log('Fetching current user...');
      const response = await getCurrentUser();
      console.log('Current user response:', response.data);
      setUser(response.data.user);
      return response.data.user;
    } catch (error) {
      console.error('Error fetching current user:', error);
      // If we can't fetch user details, clear the token
      localStorage.removeItem('token');
      setToken(null);
      setUser(null);
      return null;
    }
  };

  // Check for existing token on app start
  useEffect(() => {
    const initializeAuth = async () => {
      console.log('Initializing auth...');
      const storedToken = localStorage.getItem('token');
      
      if (storedToken) {
        console.log('Found stored token:', storedToken.substring(0, 20) + '...');
        
        // Check if token is expired
        if (isTokenExpired(storedToken)) {
          console.log('Token expired, clearing storage');
          localStorage.removeItem('token');
          setLoading(false);
          return;
        }

        // Token is valid, set it and try to fetch user details
        setToken(storedToken);
        const fetchedUser = await fetchCurrentUser();
        console.log('Fetched user:', fetchedUser);
      } else {
        console.log('No stored token found');
      }
      
      setLoading(false);
    };

    initializeAuth();
  }, []);

  const handleLogin = async (email, password) => {
    try {
      console.log('AuthContext: Attempting login with:', email);
      const response = await login(email, password);
      console.log('AuthContext: Login response:', response);
      
      // Check if this is a first-time login requiring password setup
      if (response.requires_password_setup) {
        console.log('AuthContext: Password setup required');
        return response;
      }
      
      // Normal login success
      if (response && response.token) {
        console.log('AuthContext: Setting token and user');
        setToken(response.token);
        
        // Set user from response if available
        if (response.user) {
          setUser(response.user);
        } else {
          // Fetch user details from backend
          await fetchCurrentUser();
        }
        
        console.log('AuthContext: Login successful');
        return response;
      }
      
      return response;
    } catch (error) {
      console.error('AuthContext: Login error:', error);
      if (error.response?.status === 200 && error.response?.data?.requires_password_setup) {
        return error.response.data;
      }
      throw error;
    }
  };

  const handleSetPassword = async (email, password) => {
    try {
      console.log('AuthContext: Setting password for:', email);
      const response = await setPassword(email, password);
      
      if (response && response.token) {
        setToken(response.token);
        
        // Set user from response if available
        if (response.user) {
          setUser(response.user);
        } else {
          // Fetch user details from backend
          await fetchCurrentUser();
        }
        
        console.log('AuthContext: Password set, user logged in');
      }
      
      return response;
    } catch (error) {
      console.error('AuthContext: Set password error:', error);
      throw error;
    }
  };

  const handleLogout = async () => {
    try {
      console.log('AuthContext: Logging out...');
      await logout();
    } catch (error) {
      console.warn('AuthContext: Logout request failed:', error);
    }
    
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    console.log('AuthContext: Logout complete, redirecting...');
    window.location.href = '/login';
  };

  const value = {
    user,
    token,
    loading,
    login: handleLogin,
    logout: handleLogout,
    setPassword: handleSetPassword,
    isAuthenticated: !!token && !!user
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
        <span className="ml-2 text-gray-600">Loading...</span>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export { AuthContext };
export const useAuth = () => useContext(AuthContext);
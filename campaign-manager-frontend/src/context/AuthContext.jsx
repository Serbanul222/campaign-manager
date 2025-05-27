 
import React, { createContext, useContext, useState } from 'react';
import * as authService from '../services/auth';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null); // Could be enhanced to store full user object or token

  const login = async (email, password) => {
    const response = await authService.login(email, password);
    // Assuming login service stores token in localStorage/sessionStorage
    // and returns user info or confirmation
    if (response && response.token) { // or based on actual response structure
        // Potentially fetch user details here or decode token if it contains user info
        setUser({ email }); // Placeholder for user state
    }
  };
  
  // setPassword might need a token if it's a protected route, 
  // or email if it's for password reset.
  // The current `vzu7ti-codex` auth.py doesn't require JWT for set-password
  // but uses email to find the user.
  const setPassword = async (email, password) => {
    await authService.setPassword(email, password);
    // No specific user state change here unless re-authentication or UI update is needed
  };

  const logout = async () => {
    await authService.logout();
    // Auth service should handle token removal from storage
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, setPassword }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
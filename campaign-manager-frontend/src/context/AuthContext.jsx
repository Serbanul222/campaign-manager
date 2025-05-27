import React, { createContext, useState, useContext } from 'react';
import * as authService from '../services/auth.js';
import { getToken } from '../services/storage.js';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(getToken());

  const login = async (email, password) => {
    const data = await authService.login(email, password);
    setToken(data.access_token);
  };

  const setPassword = async (authToken, password) => {
    const data = await authService.setPassword(authToken, password);
    setToken(data.access_token);
  };

  const logout = async () => {
    await authService.logout();
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ token, login, logout, setPassword }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuthContext = () => useContext(AuthContext);

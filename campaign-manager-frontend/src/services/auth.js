import api from './api';

export const login = async (email, password) => {
  try {
    const response = await api.post('/auth/login', { email, password });
    const data = response.data;
    
    if (data.token) {
      localStorage.setItem('token', data.token);
    }
    
    return data;
  } catch (error) {
    console.error('Login service error:', error);
    throw error;
  }
};

export const setPassword = async (email, password) => {
  try {
    const response = await api.post('/auth/set-password', { email, password });
    const data = response.data;
    
    if (data.token) {
      localStorage.setItem('token', data.token);
    }
    
    return data;
  } catch (error) {
    console.error('Set password service error:', error);
    throw error;
  }
};

export const logout = async () => {
  try {
    localStorage.removeItem('token');
    const response = await api.post('/auth/logout');
    return response.data;
  } catch (error) {
    console.error('Logout service error:', error);
    // Don't throw on logout errors, just log them
    return null;
  }
};

export const getCurrentUser = async () => {
  try {
    const response = await api.get('/auth/me');
    return response;
  } catch (error) {
    console.error('Get current user service error:', error);
    throw error;
  }
};

// Default export for backward compatibility
const authService = {
  login,
  setPassword,
  logout,
  getCurrentUser
};

export default authService;
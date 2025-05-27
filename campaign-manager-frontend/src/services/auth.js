 
import api from './api';

export const login = async (email, password) => {
  const { data } = await api.post('/auth/login', { email, password });
  localStorage.setItem('token', data.token); // Store token upon successful login
  return data;
};

// The setPassword in `vzu7ti-codex` backend takes email and new password.
// It does not require JWT for this specific endpoint as per its definition.
export const setPassword = (email, password) =>
  api.post('/auth/set-password', { email, password });

export const logout = () => {
  // Client-side token removal
  localStorage.removeItem('token');
  // Server-side logout (e.g., token blacklisting if implemented)
  // The `vzu7ti-codex` backend's /auth/logout is a placeholder but still called.
  return api.post('/auth/logout');
};
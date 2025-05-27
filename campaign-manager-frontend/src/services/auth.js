 
import api from './api';

export const login = async (email, password) => {
  const { data } = await api.post('/auth/login', { email, password });
  localStorage.setItem('token', data.token);
  return data;
};

export const setPassword = (email, password) =>
  api.post('/auth/set-password', { email, password });

export const logout = () => {
  localStorage.removeItem('token');
  return api.post('/auth/logout');
};


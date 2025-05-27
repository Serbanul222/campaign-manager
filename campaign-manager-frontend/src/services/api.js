import axios from 'axios';

/**
 * Axios instance with JWT authorization header.
 * The token is retrieved from localStorage for each request.
 */
const api = axios.create({
  baseURL: '/api',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
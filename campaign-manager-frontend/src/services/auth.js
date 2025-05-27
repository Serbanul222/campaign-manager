import api from './api.js';
import { saveToken, clearToken } from './storage.js';

export async function login(email, password) {
  const { data } = await api.post('/auth/login', { email, password });
  saveToken(data.access_token);
  return data;
}

export async function setPassword(token, password) {
  const { data } = await api.post('/auth/set-password', { token, password });
  saveToken(data.access_token);
  return data;
}

export function logout() {
  clearToken();
  return api.post('/auth/logout');
}

 
import api from './api';

export const fetchUsers = () => api.get('/users');

export const createUser = (email, isAdmin = false) =>
  api.post('/users', { email, is_admin: isAdmin });

export const deleteUser = (id) => api.delete(`/users/${id}`);


import api from './api';

export const fetchLogs = () => api.get('/logs');


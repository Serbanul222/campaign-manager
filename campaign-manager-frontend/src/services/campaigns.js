import api from './api';

/**
 * Campaign API service.
 * Provides CRUD operations for campaigns and image upload handling.
 */
export const fetchCampaigns = () => api.get('/campaigns');

export const createCampaign = (payload) => api.post('/campaigns', payload);

export const updateCampaign = (id, payload) => api.put(`/campaigns/${id}`, payload);

export const deleteCampaign = (id) => api.delete(`/campaigns/${id}`);

export const uploadImages = (id, files) => {
  const formData = new FormData();
  formData.append('background', files.background);
  formData.append('logo', files.logo);
  formData.append('screensaver', files.screensaver);
  return api.post(`/campaigns/${id}/images`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

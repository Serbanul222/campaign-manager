// Filename: services/campaigns.js
import api from './api'; // Assuming './api' is your configured axios instance or similar

/**
 * Campaign API service.
 * Provides CRUD operations for campaigns and image upload handling.
 */

export const fetchCampaigns = () => {
  return api.get('/campaigns');
};

export const createCampaign = (campaignData) => {
  // If campaignData is FormData, send it directly (for campaigns with images)
  if (campaignData instanceof FormData) {
    return api.post('/campaigns', campaignData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  }
  
  // Otherwise, send as JSON (for campaigns without initial images, or if backend handles base64/URLs)
  return api.post('/campaigns', campaignData);
};

export const updateCampaign = (id, payload) => {
  // Current frontend implementation sends JSON payload for metadata updates.
  // If you intend to update files via this endpoint as well,
  // payload might need to be FormData and this function would need to detect it.
  // e.g. if (payload instanceof FormData) { /* set headers */ }
  return api.put(`/campaigns/${id}`, payload);
};

export const deleteCampaign = (id) => {
  return api.delete(`/campaigns/${id}`);
};

/**
 * Fetches image information for a specific campaign.
 * @param {string|number} campaignId - The ID of the campaign.
 * @returns {Promise} - The API response promise.
 */
export const getCampaignImages = (campaignId) => {
  return api.get(`/campaigns/${campaignId}/images`);
};

/**
 * Uploads images for a specific campaign.
 * @param {string|number} id - The ID of the campaign.
 * @param {FormData|Object} files - The files to upload. Can be a FormData instance
 *                                  or an object mapping keys to File objects (e.g., { background: File, logo: File }).
 * @returns {Promise} - The API response promise.
 */
export const uploadImages = (id, files) => {
  let formDataToSubmit;

  // If files is already FormData, use it directly.
  // This is the primary path used by your React component.
  if (files instanceof FormData) {
    formDataToSubmit = files;
  } 
  // Handle object with file properties, e.g., { background: file1, logo: file2 }
  else if (typeof files === 'object' && files !== null && !(files instanceof File) && !Array.isArray(files)) {
    const newFormData = new FormData();
    let hasFiles = false;
    for (const key in files) {
      if (Object.prototype.hasOwnProperty.call(files, key)) {
        const file = files[key];
        if (file instanceof File) {
          newFormData.append(key, file);
          hasFiles = true;
        }
        // You could add logic here if you want to signify to the backend
        // that an image should be removed, e.g., by appending an empty string
        // or a special marker if `file` is null. For now, we only append actual files.
      }
    }

    if (!hasFiles) {
      // console.log('uploadImages: No actual File instances found in the provided object to upload.');
      // Resolve with a message; the calling code can decide if this is an issue.
      return Promise.resolve({ data: { message: "No new files to upload." } });
    }
    formDataToSubmit = newFormData;
  } 
  // If it's neither FormData nor a processable object of files
  else {
    console.error('uploadImages: files argument must be FormData or an object of {key: File} pairs. Received:', files);
    return Promise.reject(new Error('Invalid files argument for uploadImages.'));
  }

  // Final check to ensure FormData is not empty before sending.
  // This is a safeguard; prior logic should mostly prevent empty FormData.
  let hasEntries = false;
  if (formDataToSubmit instanceof FormData) {
    for (const _ of formDataToSubmit.entries()) {
      hasEntries = true;
      break; 
    }
  }

  if (!hasEntries) {
    // console.log('uploadImages: FormData is empty. No API call will be made.');
    return Promise.resolve({ data: { message: "No files to upload (FormData is empty)." } });
  }
  
  return api.post(`/uploads/${id}`, formDataToSubmit, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};
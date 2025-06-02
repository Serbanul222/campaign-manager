import { useState, useEffect } from 'react';
import { fetchCampaigns, deleteCampaign as deleteCampaignAPI, getCampaignImages } from '../services/campaigns';

/**
 * Enhanced custom hook to manage campaign data with image loading.
 * Extends the existing useCampaigns hook with additional functionality.
 */
const useCampaigns = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [campaignImages, setCampaignImages] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadCampaigns = async () => {
    setLoading(true);
    try {
      const { data } = await fetchCampaigns();
      setCampaigns(data);
      
      // Load images for each campaign
      const imagesPromises = data.map(async (campaign) => {
        try {
          const imageResponse = await getCampaignImages(campaign.id);
          return { campaignId: campaign.id, images: imageResponse.data.images };
        } catch (err) {
          console.warn(`Failed to load images for campaign ${campaign.id}:`, err);
          return { campaignId: campaign.id, images: {} };
        }
      });
      
      const imagesResults = await Promise.all(imagesPromises);
      const imagesMap = {};
      imagesResults.forEach(({ campaignId, images }) => {
        imagesMap[campaignId] = images;
      });
      setCampaignImages(imagesMap);
      
      setError(null);
    } catch (err) {
      setError(err.response?.data?.message || err.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteCampaign = async (id) => {
    if (!confirm('Are you sure you want to delete this campaign?')) {
      return;
    }

    try {
      await deleteCampaignAPI(id);
      await loadCampaigns(); // Reload after deletion
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to delete campaign');
      console.error('Delete campaign error:', err);
    }
  };

 const getImageUrl = (campaignId, imageType) => {
  const images = campaignImages[campaignId];
  if (images && images[imageType] && images[imageType].url) {
    const url = images[imageType].url;
    
    // If backend returns full URL (starts with http), use it directly
    if (url.startsWith('http://') || url.startsWith('https://')) {
      return url;
    }
    
    // Otherwise it's a relative URL, prepend VM IP
    return `http://192.168.103.111:5000${url}`;
  }
  return null;
};

  const clearError = () => setError(null);

  useEffect(() => {
    loadCampaigns();
  }, []);

  return { 
    campaigns, 
    campaignImages,
    loading, 
    error, 
    reload: loadCampaigns,
    deleteCampaign,
    getImageUrl,
    clearError
  };
};

export default useCampaigns;
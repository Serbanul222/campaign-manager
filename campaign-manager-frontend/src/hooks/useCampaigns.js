import { useState, useEffect } from 'react';
import { fetchCampaigns } from '../services/campaigns';

/**
 * Custom hook to manage campaign data.
 */
const useCampaigns = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadCampaigns = async () => {
    setLoading(true);
    try {
      const { data } = await fetchCampaigns();
      setCampaigns(data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.message || err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCampaigns();
  }, []);

  return { campaigns, loading, error, reload: loadCampaigns };
};

export default useCampaigns;

import React, { useState } from 'react';
import useCampaigns from '../../hooks/useCampaigns';
import {
  createCampaign,
  updateCampaign,
  deleteCampaign,
  uploadImages,
} from '../../services/campaigns';
import CampaignCard from './CampaignCard';
import CampaignForm from './CampaignForm';

/**
 * Display list of campaigns with create/edit functionality.
 */
const CampaignList = () => {
  const { campaigns, loading, error, reload } = useCampaigns();
  const [editing, setEditing] = useState(null);

  const handleSave = async (data) => {
    try {
      let campaign;
      if (editing) {
        const res = await updateCampaign(editing.id, data);
        campaign = res.data;
      } else {
        const res = await createCampaign(data);
        campaign = res.data;
      }
      if (data.images.background) {
        await uploadImages(campaign.id, data.images);
      }
      setEditing(null);
      reload();
    } catch (err) {
      // TODO: display error message
      console.error(err);
    }
  };

  const handleDelete = async (id) => {
    await deleteCampaign(id);
    reload();
  };

  if (loading) return <p>Loading...</p>;
  if (error) return <p className="text-red-600">{error}</p>;

  return (
    <div className="space-y-4">
      <button
        onClick={() => setEditing({})}
        className="bg-green-600 text-white px-3 py-1"
      >
        New Campaign
      </button>
      {editing && (
        <CampaignForm
          initialData={editing}
          onSubmit={handleSave}
        />
      )}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {campaigns.map((c) => (
          <CampaignCard
            key={c.id}
            campaign={c}
            onEdit={setEditing}
            onDelete={handleDelete}
          />
        ))}
      </div>
    </div>
  );
};

export default CampaignList;

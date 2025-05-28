import React, { useState } from 'react';
import { Plus, AlertCircle } from 'lucide-react';
import useCampaigns from '../hooks/useCampaigns';
import CampaignList from '../components/campaigns/CampaignList';
import CampaignForm from '../components/campaigns/CampaignForm';
import Modal from '../components/common/Modal';



/**
 * Refactored CampaignsPage using existing components.
 * Main orchestrator component that coordinates all campaign operations.
 */
const CampaignsPage = () => {
  const {
    campaigns,
    loading,
    error,
    reload,
    deleteCampaign,
    getImageUrl,
    clearError
  } = useCampaigns();

  const [showModal, setShowModal] = useState(false);
  const [editingCampaign, setEditingCampaign] = useState(null);

  const handleEdit = (campaign) => {
    setEditingCampaign({
      id: campaign.id,
      name: campaign.name,
      startDate: campaign.start_date,
      endDate: campaign.end_date
    });
    setShowModal(true);
    clearError();
  };

  const handleCreateNew = () => {
    setEditingCampaign(null);
    setShowModal(true);
    clearError();
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingCampaign(null);
    clearError();
  };

  const handleFormSubmit = async (campaignData) => {
    // Form component handles the API calls
    // Just close modal and reload data
    handleCloseModal();
    await reload();
  };

  const handleDelete = async (id) => {
    await deleteCampaign(id);
    // The useCampaigns hook handles reloading after deletion
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
        <span className="ml-3 text-gray-600">Loading campaigns...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm p-6">
          {/* Page Header */}
          <div className="flex justify-between items-center mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Campaign Manager</h1>
              <p className="text-gray-600 mt-1">Manage your promotional campaigns</p>
            </div>
            <button
              onClick={handleCreateNew}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700 transition-colors shadow-sm hover:shadow-md"
            >
              <Plus size={20} />
              New Campaign
            </button>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center">
              <AlertCircle className="h-4 w-4 mr-2 flex-shrink-0" />
              <span>{error}</span>
              <button 
                onClick={clearError}
                className="ml-auto text-red-500 hover:text-red-700 text-xl font-bold"
              >
                ×
              </button>
            </div>
          )}

          {/* Campaign Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{campaigns.length}</div>
              <div className="text-sm text-blue-600">Total Campaigns</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {campaigns.filter(c => c.status === 'active').length}
              </div>
              <div className="text-sm text-green-600">Active Campaigns</div>
            </div>
            <div className="bg-yellow-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">
                {campaigns.filter(c => c.status === 'scheduled').length}
              </div>
              <div className="text-sm text-yellow-600">Scheduled Campaigns</div>
            </div>
          </div>

          {/* Campaign List */}
          <CampaignList
            campaigns={campaigns}
            onEdit={handleEdit}
            onDelete={handleDelete}
            getImageUrl={getImageUrl}
          />
        </div>

        {/* Form Modal */}
        <Modal
          isOpen={showModal}
          title={editingCampaign ? 'Edit Campaign' : 'Create New Campaign'}
          onClose={handleCloseModal}
        >
          <CampaignForm
            initialData={editingCampaign}
            onSubmit={handleFormSubmit}
            onCancel={handleCloseModal}
            campaigns={campaigns}
          />
        </Modal>
      </div>
    </div>
  );
};

export default CampaignsPage;
import React, { useState, useEffect } from 'react';
import { Calendar, Upload, Eye, Edit2, Trash2, Plus, Save, X, AlertCircle } from 'lucide-react';
import * as campaignService from '../services/campaigns';

const CampaignsPage = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [campaignImages, setCampaignImages] = useState({}); // Store images by campaign ID
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingCampaign, setEditingCampaign] = useState(null);
  const [saving, setSaving] = useState(false);
  
  const [previewImages, setPreviewImages] = useState({
    background: null,
    logo: null,
    screensaver: null
  });
  
  const [formData, setFormData] = useState({
    name: '',
    startDate: '',
    endDate: ''
  });

  // Load campaigns and their images
  const loadCampaigns = async () => {
    try {
      setLoading(true);
      const response = await campaignService.fetchCampaigns();
      const campaignsData = response.data || [];
      setCampaigns(campaignsData);
      
      // Load images for each campaign
      const imagesPromises = campaignsData.map(async (campaign) => {
        try {
          const imageResponse = await campaignService.getCampaignImages(campaign.id);
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
      
    } catch (err) {
      setError('Failed to load campaigns');
      console.error('Load campaigns error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCampaigns();
  }, []);

  const handleImageUpload = (type, event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.size > 16 * 1024 * 1024) {
        alert('File size must be less than 16MB');
        return;
      }

      if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        setPreviewImages(prev => ({
          ...prev,
          [type]: { file, preview: e.target.result }
        }));
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async () => {
    if (!formData.name || !formData.startDate || !formData.endDate) {
      alert('Please fill all required fields');
      return;
    }

    if (new Date(formData.startDate) >= new Date(formData.endDate)) {
      alert('End date must be after start date');
      return;
    }

    setSaving(true);
    setError('');

    try {
      let campaign;
      
      if (editingCampaign) {
        const response = await campaignService.updateCampaign(editingCampaign.id, {
          name: formData.name,
          start_date: formData.startDate,
          end_date: formData.endDate
        });
        campaign = response.data;
      } else {
        const campaignData = new FormData();
        campaignData.append('name', formData.name);
        campaignData.append('start_date', formData.startDate);
        campaignData.append('end_date', formData.endDate);

        if (previewImages.background?.file) {
          campaignData.append('background', previewImages.background.file);
        }
        if (previewImages.logo?.file) {
          campaignData.append('logo', previewImages.logo.file);
        }
        if (previewImages.screensaver?.file) {
          campaignData.append('screensaver', previewImages.screensaver.file);
        }

        const response = await campaignService.createCampaign(campaignData);
        campaign = response.data;
      }

      if (editingCampaign && (previewImages.background?.file || previewImages.logo?.file || previewImages.screensaver?.file)) {
        const imageData = new FormData();
        if (previewImages.background?.file) imageData.append('background', previewImages.background.file);
        if (previewImages.logo?.file) imageData.append('logo', previewImages.logo.file);
        if (previewImages.screensaver?.file) imageData.append('screensaver', previewImages.screensaver.file);
        
        await campaignService.uploadImages(campaign.id, imageData);
      }

      resetForm();
      await loadCampaigns();
      
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to save campaign');
      console.error('Save campaign error:', err);
    } finally {
      setSaving(false);
    }
  };

  const resetForm = () => {
    setShowCreateForm(false);
    setEditingCampaign(null);
    setFormData({ name: '', startDate: '', endDate: '' });
    setPreviewImages({ background: null, logo: null, screensaver: null });
    setError('');
  };

  const handleEdit = (campaign) => {
    setEditingCampaign(campaign);
    setFormData({
      name: campaign.name,
      startDate: campaign.start_date,
      endDate: campaign.end_date
    });
    setShowCreateForm(true);
  };

  const deleteCampaign = async (id) => {
    if (!confirm('Are you sure you want to delete this campaign?')) {
      return;
    }

    try {
      await campaignService.deleteCampaign(id);
      await loadCampaigns();
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to delete campaign');
      console.error('Delete campaign error:', err);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'scheduled': return 'bg-blue-100 text-blue-800';
      case 'expired': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getImageUrl = (campaignId, imageType) => {
    const images = campaignImages[campaignId];
    if (images && images[imageType] && images[imageType].url) {
      return `http://localhost:5000${images[imageType].url}`;
    }
    return null;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-gray-900">Campaign Manager</h1>
            <button
              onClick={() => setShowCreateForm(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700 transition-colors"
            >
              <Plus size={20} />
              New Campaign
            </button>
          </div>

          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center">
              <AlertCircle className="h-4 w-4 mr-2 flex-shrink-0" />
              {error}
            </div>
          )}

          <div className="grid gap-4">
            {campaigns.length === 0 ? (
              <div className="text-center py-12">
                <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No campaigns yet</h3>
                <p className="text-gray-600 mb-4">Create your first promotional campaign to get started.</p>
                <button
                  onClick={() => setShowCreateForm(true)}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Create Campaign
                </button>
              </div>
            ) : (
              campaigns.map(campaign => (
                <div key={campaign.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900">{campaign.name}</h3>
                      <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                        <span className="flex items-center gap-1">
                          <Calendar size={16} />
                          {campaign.start_date} to {campaign.end_date}
                        </span>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(campaign.status)}`}>
                          {campaign.status.charAt(0).toUpperCase() + campaign.status.slice(1)}
                        </span>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button className="p-2 text-gray-500 hover:text-blue-600 transition-colors" title="Preview Campaign">
                        <Eye size={18} />
                      </button>
                      <button 
                        onClick={() => handleEdit(campaign)}
                        className="p-2 text-gray-500 hover:text-yellow-600 transition-colors"
                        title="Edit Campaign"
                      >
                        <Edit2 size={18} />
                      </button>
                      <button 
                        onClick={() => deleteCampaign(campaign.id)}
                        className="p-2 text-gray-500 hover:text-red-600 transition-colors"
                        title="Delete Campaign"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </div>

                  {/* Campaign Images */}
                  <div className="grid grid-cols-3 gap-4">
                    {['background', 'logo', 'screensaver'].map(imageType => {
                      const imageUrl = getImageUrl(campaign.id, imageType);
                      return (
                        <div key={imageType} className="text-center">
                          <p className="text-sm font-medium text-gray-700 mb-2 capitalize">
                            {imageType === 'screensaver' ? 'Screen Saver' : imageType}
                          </p>
                          {imageUrl ? (
                            <img 
                              src={imageUrl} 
                              alt={`${imageType} for ${campaign.name}`}
                              className="w-full h-24 object-cover rounded border"
                              onError={(e) => {
                                console.error(`Failed to load image: ${imageUrl}`);
                                e.target.style.display = 'none';
                                e.target.nextSibling.style.display = 'flex';
                              }}
                            />
                          ) : null}
                          <div 
                            className="w-full h-24 bg-gray-100 rounded border flex items-center justify-center"
                            style={{ display: imageUrl ? 'none' : 'flex' }}
                          >
                            <span className="text-gray-400 text-sm">
                              {imageType === 'screensaver' ? 'Screen Saver' : imageType} Image
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Form Modal - keeping existing form code */}
        {(showCreateForm || editingCampaign) && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">
                  {editingCampaign ? 'Edit Campaign' : 'Create New Campaign'}
                </h2>
                <button onClick={resetForm} className="text-gray-500 hover:text-gray-700">
                  <X size={24} />
                </button>
              </div>

              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Campaign Name *
                    </label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter campaign name"
                      disabled={saving}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Start Date *
                    </label>
                    <input
                      type="date"
                      value={formData.startDate}
                      onChange={(e) => setFormData(prev => ({ ...prev, startDate: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      disabled={saving}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      End Date *
                    </label>
                    <input
                      type="date"
                      value={formData.endDate}
                      onChange={(e) => setFormData(prev => ({ ...prev, endDate: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      disabled={saving}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {['background', 'logo', 'screensaver'].map(type => (
                    <div key={type} className="space-y-3">
                      <label className="block text-sm font-medium text-gray-700 capitalize">
                        {type === 'screensaver' ? 'Screen Saver' : type} Image
                      </label>
                      
                      <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:border-gray-400 transition-colors">
                        <input
                          type="file"
                          accept="image/*"
                          onChange={(e) => handleImageUpload(type, e)}
                          className="hidden"
                          id={`upload-${type}`}
                          disabled={saving}
                        />
                        <label htmlFor={`upload-${type}`} className="cursor-pointer block">
                          {previewImages[type]?.preview ? (
                            <img 
                              src={previewImages[type].preview} 
                              alt={`${type} preview`}
                              className="w-full h-32 object-cover rounded"
                            />
                          ) : (
                            <div className="flex flex-col items-center justify-center h-32">
                              <Upload size={32} className="text-gray-400 mb-2" />
                              <p className="text-sm text-gray-500">Click to upload</p>
                              <p className="text-xs text-gray-400 mt-1">Max 16MB</p>
                            </div>
                          )}
                        </label>
                      </div>
                      
                      {previewImages[type] && (
                        <button
                          type="button"
                          onClick={() => setPreviewImages(prev => ({ ...prev, [type]: null }))}
                          className="w-full text-sm text-red-600 hover:text-red-800"
                          disabled={saving}
                        >
                          Remove Image
                        </button>
                      )}
                    </div>
                  ))}
                </div>

                <div className="flex justify-end gap-3 pt-4 border-t">
                  <button
                    type="button"
                    onClick={resetForm}
                    className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                    disabled={saving}
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    onClick={handleSubmit}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2 disabled:opacity-50 transition-colors"
                    disabled={saving}
                  >
                    {saving ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save size={18} />
                        {editingCampaign ? 'Update Campaign' : 'Create Campaign'}
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CampaignsPage;
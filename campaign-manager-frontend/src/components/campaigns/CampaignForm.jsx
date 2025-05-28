import React, { useState, useEffect } from 'react';
import { Save, AlertCircle } from 'lucide-react';
import PropTypes from 'prop-types';
import ImageUpload from './ImageUpload';
import { createCampaign, updateCampaign, uploadImages } from '../../services/campaigns';

/**
 * Enhanced form for creating or editing campaigns.
 * Includes validation, date conflict checking, and error handling.
 */
const CampaignForm = ({ initialData, onSubmit, onCancel, campaigns = [] }) => {
  const [name, setName] = useState(initialData?.name || '');
  const [startDate, setStartDate] = useState(initialData?.startDate || '');
  const [endDate, setEndDate] = useState(initialData?.endDate || '');
  const [images, setImages] = useState({
    background: null,
    logo: null,
    screensaver: null,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  // Reset form when initialData changes
  useEffect(() => {
    setName(initialData?.name || '');
    setStartDate(initialData?.startDate || '');
    setEndDate(initialData?.endDate || '');
    setImages({ background: null, logo: null, screensaver: null });
    setError('');
  }, [initialData]);

  const handleImageSelect = (key) => (file) => {
    if (file && file.size > 16 * 1024 * 1024) {
      setError('File size must be less than 16MB');
      return;
    }
    
    if (file && !file.type.startsWith('image/')) {
      setError('Please select an image file');
      return;
    }

    setImages((prev) => ({ ...prev, [key]: file }));
    setError(''); // Clear error when valid file is selected
  };

  // Check for date conflicts with existing campaigns
  const isDateConflict = (start, end) => {
    const startDate = new Date(start);
    const endDate = new Date(end);
    
    return campaigns.some(campaign => {
      // Don't check against itself when editing
      if (initialData && campaign.id === initialData.id) {
        return false;
      }
      
      // Only check against active campaigns
      if (campaign.status !== 'active') {
        return false;
      }
      
      const campaignStart = new Date(campaign.start_date);
      const campaignEnd = new Date(campaign.end_date);
      
      // Check for overlap
      return startDate <= campaignEnd && endDate >= campaignStart;
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!name || !startDate || !endDate) {
      setError('Please fill all required fields');
      return;
    }

    if (new Date(startDate) >= new Date(endDate)) {
      setError('End date must be after start date');
      return;
    }

    // Check for date conflicts (only for new campaigns)
    if (!initialData && isDateConflict(startDate, endDate)) {
      setError('Date range conflicts with an existing active campaign. Please choose different dates.');
      return;
    }

    setSaving(true);

    try {
      let campaign;
      
      if (initialData) {
        // Update existing campaign
        const response = await updateCampaign(initialData.id, {
          name,
          start_date: startDate,
          end_date: endDate
        });
        campaign = response.data;

        // Upload new images if any were selected
        const hasNewImages = images.background || images.logo || images.screensaver;
        if (hasNewImages) {
          const formData = new FormData();
          if (images.background) formData.append('background', images.background);
          if (images.logo) formData.append('logo', images.logo);
          if (images.screensaver) formData.append('screensaver', images.screensaver);
          
          await uploadImages(campaign.id, formData);
        }
      } else {
        // Create new campaign
        const formData = new FormData();
        formData.append('name', name);
        formData.append('start_date', startDate);
        formData.append('end_date', endDate);

        if (images.background) formData.append('background', images.background);
        if (images.logo) formData.append('logo', images.logo);
        if (images.screensaver) formData.append('screensaver', images.screensaver);

        const response = await createCampaign(formData);
        campaign = response.data;
      }

      // Call the parent's onSubmit callback
      if (onSubmit) {
        await onSubmit(campaign);
      }
    } catch (err) {
      if (err.response?.status === 409) {
        setError(err.response.data.error);
      } else {
        setError(err.response?.data?.error || err.response?.data?.message || 'Failed to save campaign');
      }
      console.error('Save campaign error:', err);
    } finally {
      setSaving(false);
    }
  };

  const hasDateConflict = startDate && endDate && !initialData && isDateConflict(startDate, endDate);

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Error Alert */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center">
          <AlertCircle className="h-4 w-4 mr-2 flex-shrink-0" />
          {error}
        </div>
      )}

      {/* Basic Fields */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Campaign Name *</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter campaign name"
            required
            disabled={saving}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Start Date *</label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              hasDateConflict ? 'border-red-300 bg-red-50' : 'border-gray-300'
            }`}
            required
            disabled={saving}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">End Date *</label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              hasDateConflict ? 'border-red-300 bg-red-50' : 'border-gray-300'
            }`}
            required
            disabled={saving}
          />
        </div>
      </div>

      {/* Date Conflict Warning */}
      {hasDateConflict && (
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-3 rounded-lg flex items-center">
          <AlertCircle className="h-4 w-4 mr-2 flex-shrink-0" />
          Warning: This date range conflicts with an existing active campaign. Please choose different dates.
        </div>
      )}

      {/* Image Uploads */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <ImageUpload 
          label="Background Image" 
          onSelect={handleImageSelect('background')} 
        />
        <ImageUpload 
          label="Logo" 
          onSelect={handleImageSelect('logo')} 
        />
        <ImageUpload 
          label="Screensaver" 
          onSelect={handleImageSelect('screensaver')} 
        />
      </div>

      {/* Action Buttons */}
      <div className="flex justify-end gap-3 pt-4 border-t">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            disabled={saving}
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2 disabled:opacity-50 transition-colors"
          disabled={saving || hasDateConflict}
        >
          {saving ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              Saving...
            </>
          ) : (
            <>
              <Save size={18} />
              {initialData ? 'Update Campaign' : 'Create Campaign'}
            </>
          )}
        </button>
      </div>
    </form>
  );
};

CampaignForm.propTypes = {
  initialData: PropTypes.shape({
    id: PropTypes.number,
    name: PropTypes.string,
    startDate: PropTypes.string,
    endDate: PropTypes.string,
  }),
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func,
  campaigns: PropTypes.array,
};

export default CampaignForm;
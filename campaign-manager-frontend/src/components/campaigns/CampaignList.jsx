import React from 'react';
import { Calendar, Eye, Edit2, Trash2 } from 'lucide-react';
import PropTypes from 'prop-types';

/**
 * Enhanced campaign list component with image display and better styling.
 * Extends the existing CampaignList with additional functionality.
 */
const CampaignList = ({ campaigns, onEdit, onDelete, getImageUrl }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'scheduled': return 'bg-blue-100 text-blue-800';
      case 'expired': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (!campaigns || campaigns.length === 0) {
    return (
      <div className="text-center py-12">
        <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No campaigns yet</h3>
        <p className="text-gray-600">Create your first promotional campaign to get started.</p>
      </div>
    );
  }

  return (
    <div className="grid gap-4">
      {campaigns.map(campaign => (
        <div key={campaign.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow bg-white">
          {/* Campaign Header */}
          <div className="flex justify-between items-start mb-4">
            <div className="flex-1">
              <h3 className="text-xl font-semibold text-gray-900 mb-2">{campaign.name}</h3>
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <span className="flex items-center gap-1">
                  <Calendar size={16} />
                  {formatDate(campaign.start_date)} to {formatDate(campaign.end_date)}
                </span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(campaign.status)}`}>
                  {campaign.status.charAt(0).toUpperCase() + campaign.status.slice(1)}
                </span>
              </div>
            </div>
            
            {/* Action Buttons */}
            <div className="flex gap-2">
              <button 
                className="p-2 text-gray-500 hover:text-blue-600 transition-colors rounded-md hover:bg-blue-50" 
                title="Preview Campaign"
                onClick={() => console.log('Preview not implemented yet')}
              >
                <Eye size={18} />
              </button>
              <button 
                onClick={() => onEdit(campaign)}
                className="p-2 text-gray-500 hover:text-yellow-600 transition-colors rounded-md hover:bg-yellow-50"
                title="Edit Campaign"
              >
                <Edit2 size={18} />
              </button>
              <button 
                onClick={() => onDelete(campaign.id)}
                className="p-2 text-gray-500 hover:text-red-600 transition-colors rounded-md hover:bg-red-50"
                title="Delete Campaign"
              >
                <Trash2 size={18} />
              </button>
            </div>
          </div>

          {/* Campaign Images */}
          <div className="grid grid-cols-3 gap-4">
            {['background', 'logo', 'screensaver'].map(imageType => {
              const imageUrl = getImageUrl ? getImageUrl(campaign.id, imageType) : null;
              return (
                <div key={imageType} className="text-center">
                  <p className="text-sm font-medium text-gray-700 mb-2 capitalize">
                    {imageType === 'screensaver' ? 'Screen Saver' : imageType}
                  </p>
                  
                  {imageUrl ? (
                    <img 
                      src={imageUrl} 
                      alt={`${imageType} for ${campaign.name}`}
                      className="w-full h-24 object-cover rounded border shadow-sm"
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
      ))}
    </div>
  );
};

CampaignList.propTypes = {
  campaigns: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      name: PropTypes.string.isRequired,
      start_date: PropTypes.string.isRequired,
      end_date: PropTypes.string.isRequired,
      status: PropTypes.string.isRequired,
    })
  ).isRequired,
  onEdit: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
  getImageUrl: PropTypes.func,
};

export default CampaignList;
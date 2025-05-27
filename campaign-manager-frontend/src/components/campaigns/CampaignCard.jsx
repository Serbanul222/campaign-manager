import React from 'react';
import PropTypes from 'prop-types';

/**
 * Display a single campaign summary.
 */
const CampaignCard = ({ campaign, onEdit, onDelete }) => {
  const { id, name, startDate, endDate } = campaign;

  const status = (() => {
    const now = new Date();
    if (new Date(startDate) > now) return 'Scheduled';
    if (new Date(endDate) < now) return 'Expired';
    return 'Active';
  })();

  return (
    <div className="border p-4 rounded">
      <h3 className="font-bold text-lg">{name}</h3>
      <p className="text-sm">
        {startDate} - {endDate} ({status})
      </p>
      <div className="space-x-2 mt-2">
        <button onClick={() => onEdit(campaign)} className="text-blue-600">
          Edit
        </button>
        <button onClick={() => onDelete(id)} className="text-red-600">
          Delete
        </button>
      </div>
    </div>
  );
};

CampaignCard.propTypes = {
  campaign: PropTypes.shape({
    id: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired,
    startDate: PropTypes.string.isRequired,
    endDate: PropTypes.string.isRequired,
  }).isRequired,
  onEdit: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
};

export default CampaignCard;

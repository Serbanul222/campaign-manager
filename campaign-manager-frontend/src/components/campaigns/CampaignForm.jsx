import React, { useState } from 'react';
import PropTypes from 'prop-types';
import ImageUpload from './ImageUpload';

/**
 * Form for creating or editing campaigns.
 */
const CampaignForm = ({ initialData, onSubmit }) => {
  const [name, setName] = useState(initialData?.name || '');
  const [startDate, setStartDate] = useState(initialData?.startDate || '');
  const [endDate, setEndDate] = useState(initialData?.endDate || '');
  const [images, setImages] = useState({
    background: null,
    logo: null,
    screensaver: null,
  });

  const handleImage = (key) => (file) => {
    setImages((prev) => ({ ...prev, [key]: file }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ name, startDate, endDate, images });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block">Name</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="border p-2 w-full"
          required
        />
      </div>
      <div>
        <label className="block">Start Date</label>
        <input
          type="date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
          className="border p-2 w-full"
          required
        />
      </div>
      <div>
        <label className="block">End Date</label>
        <input
          type="date"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
          className="border p-2 w-full"
          required
        />
      </div>
      <div className="grid grid-cols-3 gap-4">
        <ImageUpload label="Background" onSelect={handleImage('background')} />
        <ImageUpload label="Logo" onSelect={handleImage('logo')} />
        <ImageUpload label="Screensaver" onSelect={handleImage('screensaver')} />
      </div>
      <button type="submit" className="bg-blue-600 text-white px-4 py-2">
        Save
      </button>
    </form>
  );
};

CampaignForm.propTypes = {
  initialData: PropTypes.shape({
    name: PropTypes.string,
    startDate: PropTypes.string,
    endDate: PropTypes.string,
  }),
  onSubmit: PropTypes.func.isRequired,
};

CampaignForm.defaultProps = {
  initialData: null,
};

export default CampaignForm;

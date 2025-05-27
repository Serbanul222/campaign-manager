import React from 'react';
import PropTypes from 'prop-types';

/**
 * Preview component showing how a campaign will appear.
 */
const CampaignPreview = ({ images }) => (
  <div className="border p-4 flex flex-col items-center space-y-2">
    {images.background && (
      <img src={images.background} alt="Background" className="w-48" />
    )}
    {images.logo && <img src={images.logo} alt="Logo" className="w-24" />}
    {images.screensaver && (
      <img src={images.screensaver} alt="Screensaver" className="w-48" />
    )}
  </div>
);

CampaignPreview.propTypes = {
  images: PropTypes.shape({
    background: PropTypes.string,
    logo: PropTypes.string,
    screensaver: PropTypes.string,
  }).isRequired,
};

export default CampaignPreview;

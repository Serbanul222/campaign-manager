import React, { useCallback, useState } from 'react';
import PropTypes from 'prop-types';

/**
 * Drag-and-drop file input for campaign images.
 */
const ImageUpload = ({ label, accept, onSelect }) => {
  const [preview, setPreview] = useState(null);

  const handleFiles = useCallback(
    (files) => {
      const file = files[0];
      if (!file) return;
      setPreview(URL.createObjectURL(file));
      onSelect(file);
    },
    [onSelect],
  );

  const onChange = (e) => handleFiles(e.target.files);

  const onDrop = (e) => {
    e.preventDefault();
    handleFiles(e.dataTransfer.files);
  };

  const onDragOver = (e) => e.preventDefault();

  return (
    <div
      className="border rounded p-4 text-center"
      onDrop={onDrop}
      onDragOver={onDragOver}
    >
      <p>{label}</p>
      {preview && (
        <img src={preview} alt="preview" className="mx-auto h-24 my-2" />
      )}
      <input type="file" accept={accept} onChange={onChange} />
    </div>
  );
};

ImageUpload.propTypes = {
  label: PropTypes.string.isRequired,
  accept: PropTypes.string,
  onSelect: PropTypes.func.isRequired,
};

ImageUpload.defaultProps = {
  accept: 'image/*',
};

export default ImageUpload;

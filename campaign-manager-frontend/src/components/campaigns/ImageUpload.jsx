import React, { useCallback, useState } from 'react';
import { Upload, X } from 'lucide-react';
import PropTypes from 'prop-types';

/**
 * Enhanced drag-and-drop file input for campaign images with better styling.
 */
const ImageUpload = ({ label, accept = 'image/*', onSelect }) => {
  const [preview, setPreview] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleFiles = useCallback(
    (files) => {
      const file = files[0];
      if (!file) return;
      
      // Validate file size (16MB limit)
      if (file.size > 16 * 1024 * 1024) {
        alert('File size must be less than 16MB');
        return;
      }

      // Validate file type
      if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
      }

      setPreview(URL.createObjectURL(file));
      onSelect(file);
    },
    [onSelect],
  );

  const onChange = (e) => {
    handleFiles(e.target.files);
    // Reset input value to allow selecting the same file again
    e.target.value = '';
  };

  const onDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    handleFiles(e.dataTransfer.files);
  };

  const onDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const onDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const removeImage = () => {
    setPreview(null);
    onSelect(null); // Notify parent that image was removed
  };

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700">
        {label}
      </label>
      
      <div
        className={`relative border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer ${
          isDragOver
            ? 'border-blue-400 bg-blue-50'
            : preview
            ? 'border-green-300 bg-green-50'
            : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
        }`}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
      >
        <input
          type="file"
          accept={accept}
          onChange={onChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          id={`upload-${label.replace(/\s+/g, '-').toLowerCase()}`}
        />
        
        {preview ? (
          <div className="relative">
            <img 
              src={preview} 
              alt="Preview" 
              className="mx-auto h-32 w-full object-cover rounded-md"
            />
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                removeImage();
              }}
              className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition-colors"
              title="Remove image"
            >
              <X size={16} />
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-6">
            <Upload 
              size={32} 
              className={`mb-3 ${isDragOver ? 'text-blue-500' : 'text-gray-400'}`} 
            />
            <p className="text-sm font-medium text-gray-700 mb-1">
              {isDragOver ? 'Drop image here' : 'Click to upload or drag and drop'}
            </p>
            <p className="text-xs text-gray-500">
              PNG, JPG, GIF up to 16MB
            </p>
          </div>
        )}
      </div>
      
      {preview && (
        <button
          type="button"
          onClick={removeImage}
          className="w-full text-sm text-red-600 hover:text-red-800 font-medium"
        >
          Remove Image
        </button>
      )}
    </div>
  );
};

ImageUpload.propTypes = {
  label: PropTypes.string.isRequired,
  accept: PropTypes.string,
  onSelect: PropTypes.func.isRequired,
};

export default ImageUpload;
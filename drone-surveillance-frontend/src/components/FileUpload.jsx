import React, { useState, useRef } from 'react';
import { Upload, Image, Video as VideoIcon, X, CheckCircle, AlertCircle, Loader } from 'lucide-react';

function FileUpload({ apiBaseUrl, onUploadSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null); // 'success', 'error', null
  const [message, setMessage] = useState('');
  const fileInputRef = useRef(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Check file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'video/mp4', 'video/avi', 'video/quicktime', 'video/x-matroska'];
    if (!validTypes.includes(file.type)) {
      setUploadStatus('error');
      setMessage('Invalid file type. Please upload an image (JPG, PNG, BMP) or video (MP4, AVI, MOV, MKV)');
      return;
    }

    // Check file size (500MB max)
    if (file.size > 500 * 1024 * 1024) {
      setUploadStatus('error');
      setMessage('File size exceeds 500MB limit');
      return;
    }

    setSelectedFile(file);
    setUploadStatus(null);
    setMessage('');

    // Create preview for images
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target.result);
      reader.readAsDataURL(file);
    } else {
      setPreview(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setUploadStatus(null);
    setMessage('');

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch(`${apiBaseUrl}/upload`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setUploadStatus('success');
        setMessage(`File uploaded successfully: ${data.filename}`);
        
        // Notify parent component
        if (onUploadSuccess) {
          onUploadSuccess(data);
        }

        // Clear after 3 seconds
        setTimeout(() => {
          handleClear();
        }, 3000);
      } else {
        setUploadStatus('error');
        setMessage(data.error || 'Upload failed');
      }
    } catch (error) {
      setUploadStatus('error');
      setMessage(`Upload error: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
    setPreview(null);
    setUploadStatus(null);
    setMessage('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleResetSource = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/reset-source`, {
        method: 'POST',
      });

      if (response.ok) {
        setUploadStatus('success');
        setMessage('Switched back to live camera feed');
        handleClear();
        
        if (onUploadSuccess) {
          onUploadSuccess({ reset: true });
        }
      }
    } catch (error) {
      setUploadStatus('error');
      setMessage(`Error: ${error.message}`);
    }
  };

  const fileType = selectedFile?.type.startsWith('image/') ? 'image' : 'video';

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold flex items-center space-x-2">
          <Upload className="w-5 h-5 text-primary-500" />
          <span>Upload Image or Video</span>
        </h2>
        <button
          onClick={handleResetSource}
          className="text-sm text-gray-400 hover:text-primary-400 transition-colors"
        >
          Switch to Live Camera
        </button>
      </div>

      {/* Upload Area */}
      <div className="space-y-4">
        {/* File Input */}
        <div 
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            selectedFile 
              ? 'border-primary-500 bg-primary-500/5' 
              : 'border-dark-600 hover:border-primary-500/50 bg-dark-800'
          }`}
          onClick={() => !selectedFile && fileInputRef.current?.click()}
        >
          {!selectedFile ? (
            <>
              <Upload className="w-12 h-12 text-gray-500 mx-auto mb-4" />
              <p className="text-gray-300 mb-2">
                Click to upload or drag and drop
              </p>
              <p className="text-sm text-gray-500">
                Images: JPG, PNG, BMP • Videos: MP4, AVI, MOV, MKV
              </p>
              <p className="text-xs text-gray-600 mt-2">
                Max size: 500MB
              </p>
            </>
          ) : (
            <div className="space-y-4">
              {/* Preview */}
              {preview ? (
                <img 
                  src={preview} 
                  alt="Preview" 
                  className="max-h-48 mx-auto rounded-lg object-contain"
                />
              ) : (
                <VideoIcon className="w-16 h-16 text-primary-500 mx-auto" />
              )}
              
              {/* File Info */}
              <div className="flex items-center justify-center space-x-2">
                {fileType === 'image' ? (
                  <Image className="w-5 h-5 text-primary-500" />
                ) : (
                  <VideoIcon className="w-5 h-5 text-primary-500" />
                )}
                <span className="text-gray-300 font-medium">
                  {selectedFile.name}
                </span>
                <span className="text-sm text-gray-500">
                  ({(selectedFile.size / (1024 * 1024)).toFixed(2)} MB)
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Hidden File Input */}
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept="image/jpeg,image/jpg,image/png,image/bmp,video/mp4,video/avi,video/quicktime,video/x-matroska"
          onChange={handleFileSelect}
        />

        {/* Action Buttons */}
        {selectedFile && (
          <div className="flex space-x-3">
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="flex-1 btn-primary flex items-center justify-center space-x-2"
            >
              {uploading ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  <span>Uploading...</span>
                </>
              ) : (
                <>
                  <Upload className="w-5 h-5" />
                  <span>Upload & Process</span>
                </>
              )}
            </button>
            <button
              onClick={handleClear}
              disabled={uploading}
              className="btn-secondary flex items-center justify-center space-x-2"
            >
              <X className="w-5 h-5" />
              <span>Clear</span>
            </button>
          </div>
        )}

        {/* Status Message */}
        {message && (
          <div className={`p-4 rounded-lg flex items-start space-x-3 ${
            uploadStatus === 'success' 
              ? 'bg-green-500/10 border border-green-500/20' 
              : 'bg-red-500/10 border border-red-500/20'
          }`}>
            {uploadStatus === 'success' ? (
              <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
            ) : (
              <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            )}
            <p className={`text-sm ${
              uploadStatus === 'success' ? 'text-green-400' : 'text-red-400'
            }`}>
              {message}
            </p>
          </div>
        )}

        {/* Instructions */}
        <div className="bg-dark-800 rounded-lg p-4 border border-dark-600">
          <h3 className="text-sm font-semibold text-gray-300 mb-2">How it works:</h3>
          <ol className="text-xs text-gray-400 space-y-1 list-decimal list-inside">
            <li>Upload an image or video file using the button above</li>
            <li>AI will automatically detect objects (people, vehicles, etc.)</li>
            <li>View processed results in the live feed section</li>
            <li>Check the detection table for detailed information</li>
            <li>Receive alerts if restricted zones are breached</li>
          </ol>
        </div>
      </div>
    </div>
  );
}

export default FileUpload;

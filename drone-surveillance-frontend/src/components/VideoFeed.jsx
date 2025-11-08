import React, { useState, useEffect } from 'react';
import { Video, VideoOff, Maximize2, RefreshCw } from 'lucide-react';

const VideoFeed = React.memo(function VideoFeed({ apiBaseUrl, fullScreen = false }) {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(false);
  const [key, setKey] = useState(Date.now()); // Used to force reload
  const imgRef = React.useRef(null);

  const videoUrl = `${apiBaseUrl}/video_feed?t=${key}`; // Add timestamp to prevent caching

  useEffect(() => {
    setIsLoading(true);
    setError(false);
  }, [key]);

  const handleImageLoad = () => {
    setIsLoading(false);
    setError(false);
  };

  const handleImageError = () => {
    setIsLoading(false);
    setError(true);
  };

  const handleReload = () => {
    setKey(Date.now());
  };

  return (
    <div className={`card p-4 ${fullScreen ? 'h-[500px]' : 'h-[400px]'}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Video className="w-5 h-5 text-primary-500" />
          <h2 className="text-lg font-bold">Live Video Feed</h2>
          {!error && !isLoading && (
            <span className="flex items-center space-x-1">
              <span className="status-dot bg-red-500"></span>
              <span className="text-xs text-red-400 font-medium">LIVE</span>
            </span>
          )}
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={handleReload}
            className="p-2 hover:bg-dark-700 rounded-lg transition-colors"
            title="Reload feed"
          >
            <RefreshCw className="w-4 h-4 text-gray-400" />
          </button>
          <button
            className="p-2 hover:bg-dark-700 rounded-lg transition-colors"
            title="Fullscreen"
          >
            <Maximize2 className="w-4 h-4 text-gray-400" />
          </button>
        </div>
      </div>

      {/* Video Container */}
      <div className="relative bg-dark-900 rounded-lg overflow-hidden h-[calc(100%-60px)] flex items-center justify-center">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-dark-900">
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-4 border-b-4 border-primary-500 mb-4"></div>
              <p className="text-gray-400 text-sm">Loading video stream...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="absolute inset-0 flex items-center justify-center bg-dark-900">
            <div className="text-center">
              <VideoOff className="w-16 h-16 text-red-500 mx-auto mb-4" />
              <p className="text-gray-400 text-sm mb-2">
                Unable to connect to video stream
              </p>
              <p className="text-gray-500 text-xs mb-4">
                Check backend connection
              </p>
              <button
                onClick={handleReload}
                className="btn-primary text-sm"
              >
                Retry Connection
              </button>
            </div>
          </div>
        )}

        {!error && (
          <img
            ref={imgRef}
            key={key}
            src={videoUrl}
            alt="Live Video Feed"
            className="max-w-full max-h-full object-contain"
            onLoad={handleImageLoad}
            onError={handleImageError}
            loading="eager"
            decoding="async"
            style={{ imageRendering: 'auto' }}
          />
        )}

        {/* Video Overlay Info */}
        {!error && !isLoading && (
          <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between">
            <div className="bg-dark-900/80 backdrop-blur-sm px-3 py-2 rounded-lg">
              <p className="text-xs text-gray-300">
                YOLOv8 + DeepSORT Active
              </p>
            </div>
            <div className="bg-dark-900/80 backdrop-blur-sm px-3 py-2 rounded-lg">
              <p className="text-xs text-gray-300">
                {new Date().toLocaleTimeString()}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
});

export default VideoFeed;

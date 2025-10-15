import React, { useEffect, useState } from 'react';
import { AlertTriangle, Shield, Download, Database } from 'lucide-react';

const GeofenceAlerts = React.memo(function GeofenceAlerts({ apiBaseUrl }) {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const res = await fetch(`${apiBaseUrl}/api/geofence/alerts`);
        const data = await res.json();
        setAlerts(data.alerts || []);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching geofence alerts:', error);
        setLoading(false);
      }
    };

    fetchAlerts();
    const interval = setInterval(fetchAlerts, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, [apiBaseUrl]);

  if (loading) {
    return (
      <div className="card p-6">
        <h2 className="text-xl font-bold mb-4 flex items-center space-x-2">
          <Shield className="w-6 h-6 text-red-500" />
          <span>Geofence Alerts</span>
        </h2>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-b-4 border-red-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="card p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold flex items-center space-x-2">
          <Shield className="w-6 h-6 text-red-500" />
          <span>Geofence Alerts</span>
        </h2>
        {alerts.length > 0 && (
          <span className="bg-red-500 text-white text-xs font-bold rounded-full px-3 py-1">
            {alerts.length} Active
          </span>
        )}
      </div>

      {/* Alerts List */}
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {alerts.length === 0 ? (
          <div className="text-center py-8">
            <Shield className="w-12 h-12 text-green-500 mx-auto mb-3" />
            <p className="text-green-400 font-semibold">No Violations Detected</p>
            <p className="text-gray-500 text-sm mt-2">All drones within safe zones</p>
          </div>
        ) : (
          alerts.map((alert, index) => (
            <AlertCard key={alert.id || index} alert={alert} />
          ))
        )}
      </div>
    </div>
  );
});

const AlertCard = React.memo(function AlertCard({ alert }) {
  return (
    <div className="bg-red-900/20 border-2 border-red-500/50 rounded-lg p-4 animate-pulse-slow">
      <div className="flex items-start space-x-3">
        <AlertTriangle className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5" />
        
        <div className="flex-1">
          {/* Message */}
          <div className="font-bold text-red-400 mb-2">
            {alert.message || `Drone ${alert.drone_id} breached geofence`}
          </div>

          {/* Location */}
          {alert.location && (
            <div className="text-xs text-gray-400 mb-2 space-y-1">
              <div className="flex items-center space-x-4">
                <span>📍 Lat: {alert.location.lat?.toFixed(6)}</span>
                <span>Lon: {alert.location.lon?.toFixed(6)}</span>
              </div>
              <div>
                ⬆️ Alt: {alert.location.altitude?.toFixed(1)}m
                {alert.distance_to_center_m && (
                  <span className="ml-4">
                    📏 Distance: {alert.distance_to_center_m.toFixed(0)}m from center
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Violations */}
          {alert.violations && alert.violations.length > 0 && (
            <div className="mt-2 pt-2 border-t border-red-500/30">
              <div className="text-xs font-semibold text-red-400 mb-1">Violations:</div>
              <div className="flex flex-wrap gap-1">
                {alert.violations.map((violation, idx) => (
                  <span 
                    key={idx}
                    className="bg-red-500/20 text-red-300 px-2 py-1 rounded text-xs border border-red-500/40"
                  >
                    {violation}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Timestamp */}
          {alert.timestamp && (
            <div className="text-xs text-gray-500 mt-2">
              🕒 {new Date(alert.timestamp).toLocaleString()}
            </div>
          )}
        </div>
      </div>
    </div>
  );
});

const DatasetInfo = React.memo(function DatasetInfo({ apiBaseUrl }) {
  const [stats, setStats] = useState(null);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    fetchStats();
  }, [apiBaseUrl]);

  const fetchStats = async () => {
    try {
      const res = await fetch(`${apiBaseUrl}/api/dataset/stats`);
      const data = await res.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching dataset stats:', error);
    }
  };

  const handleDownload = async () => {
    setDownloading(true);
    try {
      const res = await fetch(`${apiBaseUrl}/api/dataset/download`, {
        method: 'POST'
      });
      const data = await res.json();
      
      if (data.success) {
        alert('Dataset downloaded successfully!');
        fetchStats();
      } else {
        alert('Failed to download dataset. Check Kaggle API credentials.');
      }
    } catch (error) {
      alert('Error downloading dataset: ' + error.message);
    } finally {
      setDownloading(false);
    }
  };

  if (!stats) {
    return null;
  }

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold flex items-center space-x-2">
          <Database className="w-5 h-5 text-blue-500" />
          <span>Kaggle Dataset</span>
        </h3>
      </div>

      <div className="space-y-3">
        {stats.total_records > 0 ? (
          <>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="bg-dark-800 rounded-lg p-3">
                <div className="text-gray-400 text-xs mb-1">Total Records</div>
                <div className="text-2xl font-bold text-primary-400">
                  {stats.total_records.toLocaleString()}
                </div>
              </div>
              <div className="bg-dark-800 rounded-lg p-3">
                <div className="text-gray-400 text-xs mb-1">File Size</div>
                <div className="text-2xl font-bold text-green-400">
                  {stats.file_size_mb} MB
                </div>
              </div>
            </div>
            <div className="text-xs text-gray-500">
              📂 {stats.dataset_path}
            </div>
          </>
        ) : (
          <div className="text-center py-4">
            <Database className="w-12 h-12 text-gray-600 mx-auto mb-2" />
            <p className="text-gray-500 text-sm mb-3">Dataset not downloaded</p>
            <button
              onClick={handleDownload}
              disabled={downloading}
              className="btn-primary text-sm flex items-center space-x-2 mx-auto"
            >
              {downloading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white"></div>
                  <span>Downloading...</span>
                </>
              ) : (
                <>
                  <Download className="w-4 h-4" />
                  <span>Download Dataset</span>
                </>
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
});

export { GeofenceAlerts, DatasetInfo };

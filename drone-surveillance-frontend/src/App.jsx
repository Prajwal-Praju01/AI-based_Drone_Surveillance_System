import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import VideoFeed from './components/VideoFeed';
import DetectionTable from './components/DetectionTable';
import AlertPanel from './components/AlertPanel';
import FileUpload from './components/FileUpload';
import DroneMap from './components/DroneMap';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import HistoryViewer from './components/HistoryViewer';
import HeatmapViewer from './components/HeatmapViewer';
import Login from './components/Login';
import { GeofenceAlerts, DatasetInfo } from './components/GeofenceComponents';

// Base URL for API - uses environment variable or defaults to localhost
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

function App() {
  const [detections, setDetections] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [activeView, setActiveView] = useState('dashboard');
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Fetch detections from backend
  const fetchDetections = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/detections`);
      setDetections(response.data);
      setIsConnected(true);
    } catch (error) {
      console.error('Error fetching detections:', error);
      setIsConnected(false);
    }
  };

  // Fetch alerts from backend
  const fetchAlerts = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/alerts`);
      setAlerts(response.data);
    } catch (error) {
      console.error('Error fetching alerts:', error);
    }
  };

  // Handle file upload success
  const handleUploadSuccess = (data) => {
    console.log('File uploaded:', data);
    // Force refresh of detection data
    fetchDetections();
    fetchAlerts();
  };

  // Check if user is already logged in
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    const token = localStorage.getItem('access_token');
    
    if (storedUser && token) {
      setUser(JSON.parse(storedUser));
      setIsAuthenticated(true);
    }
  }, []);

  // Initial load
  useEffect(() => {
    if (!isAuthenticated) return;
    
    const loadInitialData = async () => {
      setLoading(true);
      await Promise.all([fetchDetections(), fetchAlerts()]);
      setLoading(false);
    };
    
    loadInitialData();
  }, [isAuthenticated]);

  // Auto-refresh detection data every 2 seconds (optimized with dependency array)
  useEffect(() => {
    if (!isAuthenticated || loading) return;
    
    const interval = setInterval(() => {
      fetchDetections();
      fetchAlerts();
    }, 2000);

    return () => clearInterval(interval);
  }, [isAuthenticated, loading]); // Only re-create interval if loading or auth changes

  // Handle login
  const handleLogin = (userData) => {
    setUser(userData);
    setIsAuthenticated(true);
  };

  // Handle logout
  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    setUser(null);
    setIsAuthenticated(false);
    setActiveView('dashboard');
  };

  // If not authenticated, show login page
  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />;
  }

  // Get unread alerts count
  const unreadAlertsCount = alerts.filter(alert => !alert.read).length;

  return (
    <div className="flex h-screen bg-dark-950 overflow-hidden relative">
      {/* HAL Logo Background */}
      <div className="absolute inset-0 flex items-center justify-center opacity-5 pointer-events-none">
        <img 
          src="/hal-logo.svg" 
          alt="HAL Logo" 
          className="w-full h-full object-contain"
          style={{ maxWidth: '1200px' }}
        />
      </div>
      
      {/* Subtle Background Pattern */}
      <div className="absolute inset-0 opacity-5 pointer-events-none">
        <div className="absolute inset-0" style={{
          backgroundImage: `repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255,255,255,0.02) 2px, rgba(255,255,255,0.02) 4px),
                           repeating-linear-gradient(90deg, transparent, transparent 2px, rgba(255,255,255,0.02) 2px, rgba(255,255,255,0.02) 4px)`
        }}></div>
      </div>
      
      {/* Sidebar */}
      <Sidebar 
        activeView={activeView} 
        setActiveView={setActiveView}
        alertsCount={unreadAlertsCount}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <Header 
          isConnected={isConnected} 
          alertsCount={unreadAlertsCount}
          user={user}
          onLogout={handleLogout}
        />

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto p-6 space-y-6">
          {loading ? (
            <LoadingSpinner />
          ) : (
            <>
              {/* Dashboard View */}
              {activeView === 'dashboard' && (
                <>
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Stats Cards */}
                    <StatsCard 
                      title="Active Detections" 
                      value={detections.length} 
                      color="blue"
                      icon="📊"
                    />
                    <StatsCard 
                      title="Active Alerts" 
                      value={alerts.length} 
                      color="red"
                      icon="🚨"
                    />
                    <StatsCard 
                      title="System Status" 
                      value={isConnected ? "Online" : "Offline"} 
                      color={isConnected ? "green" : "red"}
                      icon="📡"
                    />
                  </div>

                  {/* Video Feed and Alerts */}
                  <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                    <div className="xl:col-span-2 space-y-6">
                      <FileUpload 
                        apiBaseUrl={API_BASE_URL}
                        onUploadSuccess={handleUploadSuccess}
                      />
                      <VideoFeed apiBaseUrl={API_BASE_URL} />
                    </div>
                    <div className="space-y-6">
                      <AlertPanel alerts={alerts} />
                      <DatasetInfo apiBaseUrl={API_BASE_URL} />
                    </div>
                  </div>

                  {/* Geofence Monitoring Row */}
                  <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                    <DroneMap apiBaseUrl={API_BASE_URL} />
                    <GeofenceAlerts apiBaseUrl={API_BASE_URL} />
                  </div>

                  {/* Detection Table */}
                  <DetectionTable detections={detections} />
                </>
              )}

              {/* Live Feed View */}
              {activeView === 'live-feed' && (
                <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                  <div className="xl:col-span-2 space-y-6">
                    <FileUpload 
                      apiBaseUrl={API_BASE_URL}
                      onUploadSuccess={handleUploadSuccess}
                    />
                    <VideoFeed apiBaseUrl={API_BASE_URL} fullScreen />
                  </div>
                  <div className="space-y-6">
                    <AlertPanel alerts={alerts} />
                    <DatasetInfo apiBaseUrl={API_BASE_URL} />
                  </div>
                  <div className="xl:col-span-3">
                    <DetectionTable detections={detections} />
                  </div>
                </div>
              )}

              {/* Alerts View */}
              {activeView === 'alerts' && (
                <div className="grid grid-cols-1 gap-6">
                  <AlertPanel alerts={alerts} fullPage />
                  <DetectionTable detections={detections.filter(d => d.zone_status === 'BREACH')} />
                </div>
              )}

              {/* Analytics View */}
              {activeView === 'analytics' && (
                <AnalyticsDashboard apiBaseUrl={API_BASE_URL} />
              )}

              {/* History View */}
              {activeView === 'history' && (
                <HistoryViewer apiBaseUrl={API_BASE_URL} />
              )}

              {/* Heatmap View */}
              {activeView === 'heatmap' && (
                <HeatmapViewer apiBaseUrl={API_BASE_URL} />
              )}

              {/* Settings View */}
              {activeView === 'settings' && (
                <div className="card p-6">
                  <h2 className="text-2xl font-bold mb-4">Settings</h2>
                  <div className="space-y-4">
                    <div className="border-b border-dark-700 pb-4">
                      <h3 className="text-lg font-semibold mb-2">API Configuration</h3>
                      <p className="text-gray-400 text-sm">Backend URL: {API_BASE_URL}</p>
                    </div>
                    <div className="border-b border-dark-700 pb-4">
                      <h3 className="text-lg font-semibold mb-2">Refresh Rate</h3>
                      <p className="text-gray-400 text-sm">Auto-refresh every 2 seconds</p>
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold mb-2">Theme</h3>
                      <p className="text-gray-400 text-sm">Dark Mode (Default)</p>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </main>

        {/* Footer */}
        <footer className="bg-dark-900 border-t border-dark-700 py-3 px-6">
          <p className="text-center text-gray-500 text-sm">
            © HAL Defense AI Division 2025 | AI-Based Drone Surveillance System
          </p>
        </footer>
      </div>
    </div>
  );
}

// Stats Card Component
function StatsCard({ title, value, color, icon }) {
  const colorClasses = {
    blue: 'border-blue-500/50 bg-blue-900/20',
    red: 'border-red-500/50 bg-red-900/20',
    green: 'border-green-500/50 bg-green-900/20',
  };

  return (
    <div className={`card p-6 border-l-4 ${colorClasses[color]}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-400 text-sm font-medium">{title}</p>
          <p className="text-3xl font-bold mt-2">{value}</p>
        </div>
        <div className="text-4xl">{icon}</div>
      </div>
    </div>
  );
}

// Loading Spinner Component
function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center h-full">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-primary-500"></div>
        <p className="mt-4 text-gray-400">Loading surveillance data...</p>
      </div>
    </div>
  );
}

export default App;

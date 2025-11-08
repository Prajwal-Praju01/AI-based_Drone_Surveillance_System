import React, { useEffect, useRef, useState } from 'react';
import { MapPin, Flame, Filter, Calendar, Search } from 'lucide-react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import applyLeafletHeatPatch from '../utils/leaflet-heat-patch';
import 'leaflet.heat';

// Apply canvas performance patch before using leaflet.heat
applyLeafletHeatPatch();

const DEFAULT_CENTER = [37.7749, -122.4194]; // San Francisco
const DEFAULT_ZOOM = 13;

const HeatmapViewer = ({ apiBaseUrl }) => {
  const mapRef = useRef(null);
  const heatLayerRef = useRef(null);
  const [heatmapData, setHeatmapData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dataInfo, setDataInfo] = useState({ count: 0, type: 'detections' });
  const [filters, setFilters] = useState({
    startDate: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // Last 7 days
    endDate: new Date().toISOString().split('T')[0],
    className: '',
    zoneName: '',
    threatLevel: '',
    type: 'detections', // 'detections' or 'breaches'
  });

  useEffect(() => {
    if (!mapRef.current) {
      mapRef.current = L.map('heatmap-map', {
        center: DEFAULT_CENTER,
        zoom: DEFAULT_ZOOM,
        layers: [L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '© OpenStreetMap contributors',
        })],
      });
    }
    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []);

  // Fetch heatmap data
  const fetchHeatmapData = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({
        start_time: filters.startDate + 'T00:00:00',
        end_time: filters.endDate + 'T23:59:59',
        class_name: filters.className,
        zone_name: filters.zoneName,
        threat_level: filters.threatLevel,
        type: filters.type,
      });
      const response = await fetch(`${apiBaseUrl}/api/heatmap?${params}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      const points = data.points || [];
      
      setHeatmapData(points);
      setDataInfo({ count: points.length, type: filters.type });
      
      // Render heatmap and auto-center on data
      setTimeout(() => {
        renderHeatmap(points);
        if (points.length > 0) {
          centerMapOnData(points);
        }
      }, 100);
      
      if (points.length === 0) {
        setError(`No ${filters.type} found for the selected filters. Try expanding the date range or clearing filters.`);
      }
    } catch (err) {
      setError(`Failed to fetch heatmap data: ${err.message}`);
      console.error('Heatmap fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Render heatmap layer
  const renderHeatmap = (points) => {
    if (!mapRef.current || !L.heatLayer) return;
    if (heatLayerRef.current) {
      mapRef.current.removeLayer(heatLayerRef.current);
    }
    
    if (points.length === 0) return;
    
    heatLayerRef.current = L.heatLayer(points, {
      radius: 25,
      blur: 15,
      maxZoom: 17,
      gradient: {
        0.2: 'blue',
        0.4: 'lime',
        0.6: 'yellow',
        0.8: 'orange',
        1.0: 'red',
      },
    }).addTo(mapRef.current);
  };

  // Center map on data points
  const centerMapOnData = (points) => {
    if (!mapRef.current || points.length === 0) return;
    
    try {
      // Calculate bounds from all points
      const bounds = L.latLngBounds(points.map(p => [p[0], p[1]]));
      
      // Fit map to bounds with padding
      mapRef.current.fitBounds(bounds, {
        padding: [50, 50],
        maxZoom: 15
      });
    } catch (err) {
      console.error('Error centering map:', err);
    }
  };

  useEffect(() => {
    fetchHeatmapData();
    // eslint-disable-next-line
  }, [filters.startDate, filters.endDate, filters.className, filters.zoneName, filters.threatLevel, filters.type]);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Flame size={28} className="text-orange-500" />
            Heatmap Visualization
          </h2>
          <p className="text-gray-400">
            View {filters.type === 'detections' ? 'detection' : 'breach'} hotspots over time
            {dataInfo.count > 0 && (
              <span className="ml-2 text-primary-400 font-semibold">
                ({dataInfo.count} points plotted)
              </span>
            )}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setFilters({ ...filters, type: filters.type === 'detections' ? 'breaches' : 'detections' })}
            className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${
              filters.type === 'detections'
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-red-600 text-white hover:bg-red-700'
            }`}
          >
            {filters.type === 'detections' ? 'Show Breaches' : 'Show Detections'}
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-gray-800 rounded-lg p-4 mb-4">
        <div className="flex items-center gap-2 mb-4">
          <Filter size={20} className="text-gray-400" />
          <span className="text-white font-medium">Filters</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Start Date</label>
            <input
              type="date"
              value={filters.startDate}
              onChange={(e) => setFilters({ ...filters, startDate: e.target.value })}
              className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">End Date</label>
            <input
              type="date"
              value={filters.endDate}
              onChange={(e) => setFilters({ ...filters, endDate: e.target.value })}
              className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Object Class</label>
            <select
              value={filters.className}
              onChange={(e) => setFilters({ ...filters, className: e.target.value })}
              className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
            >
              <option value="">All Classes</option>
              <option value="person">Person</option>
              <option value="car">Car</option>
              <option value="truck">Truck</option>
              <option value="bicycle">Bicycle</option>
              <option value="motorcycle">Motorcycle</option>
              <option value="bird">Bird</option>
              <option value="drone">Drone</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Zone</label>
            <select
              value={filters.zoneName}
              onChange={(e) => setFilters({ ...filters, zoneName: e.target.value })}
              className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
            >
              <option value="">All Zones</option>
              <option value="Restricted Area Alpha">Restricted Area Alpha</option>
              <option value="Perimeter Zone Beta">Perimeter Zone Beta</option>
              <option value="No-Fly Zone Gamma">No-Fly Zone Gamma</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Threat Level</label>
            <select
              value={filters.threatLevel}
              onChange={(e) => setFilters({ ...filters, threatLevel: e.target.value })}
              className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
            >
              <option value="">All Levels</option>
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
            </select>
          </div>
        </div>
        <div className="flex justify-end gap-2 mt-4">
          <button
            onClick={fetchHeatmapData}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center gap-2"
          >
            <Search size={16} />
            Apply Filters
          </button>
        </div>
      </div>

      {/* Status Messages */}
      {loading && (
        <div className="bg-blue-900/20 border border-blue-500/50 rounded-lg p-4 text-center">
          <div className="flex items-center justify-center gap-3">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
            <span className="text-blue-400">Loading heatmap data...</span>
          </div>
        </div>
      )}
      
      {error && !loading && (
        <div className="bg-yellow-900/20 border border-yellow-500/50 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <span className="text-yellow-500 text-xl">⚠️</span>
            <span className="text-yellow-400">{error}</span>
          </div>
        </div>
      )}

      {/* Map Container */}
      <div className="rounded-lg overflow-hidden border border-gray-700 relative" style={{ height: '600px' }}>
        <div id="heatmap-map" style={{ height: '100%', width: '100%' }}></div>
        
        {/* Heatmap Legend */}
        {heatmapData.length > 0 && (
          <div className="absolute top-4 right-4 bg-gray-900/90 backdrop-blur-sm rounded-lg p-4 border border-gray-700 shadow-lg z-[1000]">
            <div className="text-sm font-semibold text-white mb-2">Intensity</div>
            <div className="flex flex-col gap-1">
              <div className="flex items-center gap-2">
                <div className="w-6 h-3 bg-gradient-to-r from-blue-500 to-blue-600 rounded"></div>
                <span className="text-xs text-gray-300">Low</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-6 h-3 bg-gradient-to-r from-lime-500 to-lime-600 rounded"></div>
                <span className="text-xs text-gray-300">Medium</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-6 h-3 bg-gradient-to-r from-yellow-500 to-orange-500 rounded"></div>
                <span className="text-xs text-gray-300">High</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-6 h-3 bg-gradient-to-r from-red-500 to-red-600 rounded"></div>
                <span className="text-xs text-gray-300">Very High</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default HeatmapViewer;

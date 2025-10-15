import React, { useState, useEffect } from 'react';
import { Clock, Search, Filter, Download, Play, Pause, Calendar, MapPin, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

const HistoryViewer = ({ apiBaseUrl }) => {
  const [detections, setDetections] = useState([]);
  const [breaches, setBreaches] = useState([]);
  const [activeTab, setActiveTab] = useState('detections'); // 'detections' or 'breaches'
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Filters
  const [filters, setFilters] = useState({
    startDate: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString().split('T')[0], // Last 24h
    endDate: new Date().toISOString().split('T')[0],
    className: '',
    zoneName: '',
    threatLevel: '',
    resolved: 'all',
    searchQuery: '',
  });
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(50);
  const [totalItems, setTotalItems] = useState(0);
  
  // Replay mode
  const [replayMode, setReplayMode] = useState(false);
  const [replaySpeed, setReplaySpeed] = useState(1); // 1x, 2x, 5x, 10x
  const [currentReplayIndex, setCurrentReplayIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  
  // Statistics
  const [stats, setStats] = useState(null);

  // Fetch detections
  const fetchDetections = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams({
        start_time: filters.startDate + 'T00:00:00',
        end_time: filters.endDate + 'T23:59:59',
        limit: itemsPerPage,
        offset: (currentPage - 1) * itemsPerPage,
      });
      
      if (filters.className) params.append('class_name', filters.className);
      if (filters.searchQuery) params.append('search', filters.searchQuery);
      
      const response = await fetch(`${apiBaseUrl}/api/history/detections?${params}`);
      const data = await response.json();
      
      setDetections(data.detections || []);
      setTotalItems(data.total || 0);
      setStats(data.statistics || null);
    } catch (err) {
      setError('Failed to fetch detection history');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch breaches
  const fetchBreaches = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams({
        start_time: filters.startDate + 'T00:00:00',
        end_time: filters.endDate + 'T23:59:59',
        limit: itemsPerPage,
        offset: (currentPage - 1) * itemsPerPage,
      });
      
      if (filters.zoneName) params.append('zone_name', filters.zoneName);
      if (filters.threatLevel) params.append('threat_level', filters.threatLevel);
      if (filters.resolved !== 'all') params.append('resolved', filters.resolved === 'true');
      
      const response = await fetch(`${apiBaseUrl}/api/history/breaches?${params}`);
      const data = await response.json();
      
      setBreaches(data.breaches || []);
      setTotalItems(data.total || 0);
      setStats(data.statistics || null);
    } catch (err) {
      setError('Failed to fetch breach history');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Resolve breach
  const resolveBreach = async (breachId) => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/history/breaches/${breachId}/resolve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resolved_by: 'system_operator',
          notes: 'Resolved via web interface'
        })
      });
      
      if (response.ok) {
        fetchBreaches(); // Refresh list
      }
    } catch (err) {
      console.error('Failed to resolve breach:', err);
    }
  };

  // Export data
  const exportData = async (format = 'csv') => {
    try {
      const params = new URLSearchParams({
        format,
        start_time: filters.startDate + 'T00:00:00',
        end_time: filters.endDate + 'T23:59:59',
      });
      
      if (activeTab === 'detections' && filters.className) {
        params.append('class_name', filters.className);
      }
      if (activeTab === 'breaches' && filters.zoneName) {
        params.append('zone_name', filters.zoneName);
      }
      if (activeTab === 'breaches' && filters.threatLevel) {
        params.append('threat_level', filters.threatLevel);
      }
      
      const endpoint = activeTab === 'detections' ? 'detections' : 'breaches';
      const response = await fetch(`${apiBaseUrl}/api/history/${endpoint}/export?${params}`);
      const blob = await response.blob();
      
      // Download file
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${endpoint}_${filters.startDate}_to_${filters.endDate}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Export failed:', err);
    }
  };

  // Export PDF report
  const exportPDF = async () => {
    try {
      const params = new URLSearchParams({
        start_time: filters.startDate + 'T00:00:00',
        end_time: filters.endDate + 'T23:59:59',
      });
      
      if (activeTab === 'detections' && filters.className) {
        params.append('class_name', filters.className);
      }
      if (activeTab === 'breaches' && filters.zoneName) {
        params.append('zone_name', filters.zoneName);
      }
      if (activeTab === 'breaches' && filters.threatLevel) {
        params.append('threat_level', filters.threatLevel);
      }
      
      const endpoint = activeTab === 'detections' ? 'detections' : 'breaches';
      const response = await fetch(`${apiBaseUrl}/api/reports/${endpoint}/pdf?${params}`);
      const blob = await response.blob();
      
      // Download file
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${endpoint}_report_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('PDF export failed:', err);
    }
  };

  // Replay functionality
  useEffect(() => {
    if (!replayMode || !isPlaying) return;
    
    const data = activeTab === 'detections' ? detections : breaches;
    if (currentReplayIndex >= data.length) {
      setIsPlaying(false);
      setCurrentReplayIndex(0);
      return;
    }
    
    const interval = setInterval(() => {
      setCurrentReplayIndex(prev => prev + 1);
    }, 1000 / replaySpeed);
    
    return () => clearInterval(interval);
  }, [replayMode, isPlaying, currentReplayIndex, replaySpeed, detections, breaches, activeTab]);

  // Fetch data when filters change
  useEffect(() => {
    if (activeTab === 'detections') {
      fetchDetections();
    } else {
      fetchBreaches();
    }
  }, [activeTab, currentPage, filters.startDate, filters.endDate]);

  const totalPages = Math.ceil(totalItems / itemsPerPage);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">History & Replay</h2>
          <p className="text-gray-400">Browse and replay historical detection and breach events</p>
        </div>
        
        <div className="flex gap-2">
          <button
            onClick={() => setReplayMode(!replayMode)}
            className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${
              replayMode
                ? 'bg-purple-600 text-white hover:bg-purple-700'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            {replayMode ? <Pause size={16} /> : <Play size={16} />}
            {replayMode ? 'Stop Replay' : 'Replay Mode'}
          </button>
          
          <button
            onClick={() => exportPDF()}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2"
          >
            <Download size={16} />
            Export PDF
          </button>
          
          <button
            onClick={() => exportData('csv')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <Download size={16} />
            Export CSV
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-700">
        <button
          onClick={() => setActiveTab('detections')}
          className={`px-6 py-3 font-medium transition-colors ${
            activeTab === 'detections'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-gray-400 hover:text-gray-300'
          }`}
        >
          Detections ({totalItems})
        </button>
        <button
          onClick={() => setActiveTab('breaches')}
          className={`px-6 py-3 font-medium transition-colors ${
            activeTab === 'breaches'
              ? 'text-red-400 border-b-2 border-red-400'
              : 'text-gray-400 hover:text-gray-300'
          }`}
        >
          Breaches ({totalItems})
        </button>
      </div>

      {/* Filters */}
      <div className="bg-gray-800 rounded-lg p-4">
        <div className="flex items-center gap-2 mb-4">
          <Filter size={20} className="text-gray-400" />
          <span className="text-white font-medium">Filters</span>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Date Range */}
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
          
          {/* Detection-specific filters */}
          {activeTab === 'detections' && (
            <>
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
                <label className="block text-sm text-gray-400 mb-1">Search</label>
                <input
                  type="text"
                  placeholder="Object ID, operator..."
                  value={filters.searchQuery}
                  onChange={(e) => setFilters({ ...filters, searchQuery: e.target.value })}
                  className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
                />
              </div>
            </>
          )}
          
          {/* Breach-specific filters */}
          {activeTab === 'breaches' && (
            <>
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
              
              <div>
                <label className="block text-sm text-gray-400 mb-1">Status</label>
                <select
                  value={filters.resolved}
                  onChange={(e) => setFilters({ ...filters, resolved: e.target.value })}
                  className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
                >
                  <option value="all">All</option>
                  <option value="false">Unresolved</option>
                  <option value="true">Resolved</option>
                </select>
              </div>
            </>
          )}
        </div>
        
        <div className="flex justify-end gap-2 mt-4">
          <button
            onClick={() => activeTab === 'detections' ? fetchDetections() : fetchBreaches()}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center gap-2"
          >
            <Search size={16} />
            Apply Filters
          </button>
          <button
            onClick={() => {
              setFilters({
                startDate: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                endDate: new Date().toISOString().split('T')[0],
                className: '',
                zoneName: '',
                threatLevel: '',
                resolved: 'all',
                searchQuery: '',
              });
              setCurrentPage(1);
            }}
            className="px-4 py-2 bg-gray-700 text-gray-300 rounded hover:bg-gray-600"
          >
            Reset
          </button>
        </div>
      </div>

      {/* Statistics Summary */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="text-gray-400 text-sm mb-1">Total Records</div>
            <div className="text-2xl font-bold text-white">{totalItems}</div>
          </div>
          
          {activeTab === 'detections' && (
            <>
              <div className="bg-gray-800 rounded-lg p-4">
                <div className="text-gray-400 text-sm mb-1">Unique Objects</div>
                <div className="text-2xl font-bold text-blue-400">{stats.unique_objects || 0}</div>
              </div>
              <div className="bg-gray-800 rounded-lg p-4">
                <div className="text-gray-400 text-sm mb-1">Most Common</div>
                <div className="text-lg font-bold text-green-400 capitalize">
                  {stats.most_common_class || 'N/A'}
                </div>
              </div>
            </>
          )}
          
          {activeTab === 'breaches' && (
            <>
              <div className="bg-gray-800 rounded-lg p-4">
                <div className="text-gray-400 text-sm mb-1">Resolved</div>
                <div className="text-2xl font-bold text-green-400">{stats.resolved_count || 0}</div>
              </div>
              <div className="bg-gray-800 rounded-lg p-4">
                <div className="text-gray-400 text-sm mb-1">Unresolved</div>
                <div className="text-2xl font-bold text-red-400">{stats.unresolved_count || 0}</div>
              </div>
            </>
          )}
          
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="text-gray-400 text-sm mb-1">Date Range</div>
            <div className="text-sm font-medium text-gray-300">
              {filters.startDate} to {filters.endDate}
            </div>
          </div>
        </div>
      )}

      {/* Replay Controls */}
      {replayMode && (
        <div className="bg-purple-900/30 border border-purple-500/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="p-2 bg-purple-600 text-white rounded hover:bg-purple-700"
              >
                {isPlaying ? <Pause size={20} /> : <Play size={20} />}
              </button>
              
              <div className="text-white">
                Event {currentReplayIndex + 1} of {activeTab === 'detections' ? detections.length : breaches.length}
              </div>
              
              <select
                value={replaySpeed}
                onChange={(e) => setReplaySpeed(Number(e.target.value))}
                className="bg-gray-700 text-white px-3 py-1 rounded border border-gray-600"
              >
                <option value="1">1x Speed</option>
                <option value="2">2x Speed</option>
                <option value="5">5x Speed</option>
                <option value="10">10x Speed</option>
              </select>
            </div>
            
            <button
              onClick={() => setCurrentReplayIndex(0)}
              className="px-3 py-1 bg-gray-700 text-gray-300 rounded hover:bg-gray-600"
            >
              Reset
            </button>
          </div>
          
          {/* Progress bar */}
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div
              className="bg-purple-500 h-2 rounded-full transition-all"
              style={{
                width: `${((currentReplayIndex + 1) / (activeTab === 'detections' ? detections.length : breaches.length)) * 100}%`
              }}
            />
          </div>
        </div>
      )}

      {/* Data Table */}
      <div className="bg-gray-800 rounded-lg overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-gray-400">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            Loading data...
          </div>
        ) : error ? (
          <div className="p-12 text-center text-red-400">{error}</div>
        ) : activeTab === 'detections' ? (
          <DetectionsTable 
            detections={detections} 
            replayMode={replayMode}
            highlightIndex={replayMode ? currentReplayIndex : -1}
          />
        ) : (
          <BreachesTable 
            breaches={breaches}
            onResolve={resolveBreach}
            replayMode={replayMode}
            highlightIndex={replayMode ? currentReplayIndex : -1}
          />
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && !replayMode && (
        <div className="flex items-center justify-between">
          <div className="text-gray-400 text-sm">
            Showing {(currentPage - 1) * itemsPerPage + 1} to {Math.min(currentPage * itemsPerPage, totalItems)} of {totalItems} records
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              disabled={currentPage === 1}
              className="px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            
            <div className="flex gap-1">
              {[...Array(Math.min(5, totalPages))].map((_, i) => {
                const page = i + 1;
                return (
                  <button
                    key={page}
                    onClick={() => setCurrentPage(page)}
                    className={`px-4 py-2 rounded ${
                      currentPage === page
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    {page}
                  </button>
                );
              })}
            </div>
            
            <button
              onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
              disabled={currentPage === totalPages}
              className="px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

// Detections Table Component
const DetectionsTable = ({ detections, replayMode, highlightIndex }) => (
  <div className="overflow-x-auto">
    <table className="w-full">
      <thead className="bg-gray-700">
        <tr>
          <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Time</th>
          <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Object ID</th>
          <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Class</th>
          <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Confidence</th>
          <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Location</th>
          <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Operator</th>
          <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Details</th>
        </tr>
      </thead>
      <tbody className="divide-y divide-gray-700">
        {detections.map((detection, index) => (
          <tr 
            key={detection.id}
            className={`hover:bg-gray-700/50 transition-colors ${
              replayMode && index === highlightIndex ? 'bg-purple-900/30 border-l-4 border-purple-500' : ''
            }`}
          >
            <td className="px-4 py-3 text-sm text-gray-300">
              <div className="flex items-center gap-2">
                <Clock size={14} className="text-gray-500" />
                {new Date(detection.timestamp).toLocaleString()}
              </div>
            </td>
            <td className="px-4 py-3 text-sm font-mono text-blue-400">{detection.object_id}</td>
            <td className="px-4 py-3">
              <span className="px-2 py-1 bg-blue-900/50 text-blue-300 rounded text-xs font-medium capitalize">
                {detection.class_name}
              </span>
            </td>
            <td className="px-4 py-3 text-sm text-gray-300">{(detection.confidence * 100).toFixed(1)}%</td>
            <td className="px-4 py-3 text-sm text-gray-400">
              <div className="flex items-center gap-1">
                <MapPin size={12} />
                {detection.latitude.toFixed(6)}, {detection.longitude.toFixed(6)}
              </div>
            </td>
            <td className="px-4 py-3 text-sm text-gray-300">{detection.operator_name || 'Unknown'}</td>
            <td className="px-4 py-3 text-sm text-gray-400">{detection.description || '-'}</td>
          </tr>
        ))}
      </tbody>
    </table>
    
    {detections.length === 0 && (
      <div className="p-12 text-center text-gray-400">No detections found for the selected filters</div>
    )}
  </div>
);

// Breaches Table Component
const BreachesTable = ({ breaches, onResolve, replayMode, highlightIndex }) => (
  <div className="overflow-x-auto">
    <table className="w-full">
      <thead className="bg-gray-700">
        <tr>
          <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Time</th>
          <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Object</th>
          <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Zone</th>
          <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Threat</th>
          <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Location</th>
          <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Violations</th>
          <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Status</th>
          <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Actions</th>
        </tr>
      </thead>
      <tbody className="divide-y divide-gray-700">
        {breaches.map((breach, index) => (
          <tr 
            key={breach.id}
            className={`hover:bg-gray-700/50 transition-colors ${
              replayMode && index === highlightIndex ? 'bg-purple-900/30 border-l-4 border-purple-500' : ''
            }`}
          >
            <td className="px-4 py-3 text-sm text-gray-300">
              <div className="flex items-center gap-2">
                <Clock size={14} className="text-gray-500" />
                {new Date(breach.timestamp).toLocaleString()}
              </div>
            </td>
            <td className="px-4 py-3">
              <div className="text-sm font-mono text-blue-400">{breach.object_id}</div>
              <div className="text-xs text-gray-500 capitalize">{breach.class_name}</div>
            </td>
            <td className="px-4 py-3 text-sm text-gray-300">{breach.zone_name}</td>
            <td className="px-4 py-3">
              <span className={`px-2 py-1 rounded text-xs font-medium ${
                breach.threat_level === 'HIGH' ? 'bg-red-900/50 text-red-300' :
                breach.threat_level === 'MEDIUM' ? 'bg-yellow-900/50 text-yellow-300' :
                'bg-green-900/50 text-green-300'
              }`}>
                {breach.threat_level}
              </span>
            </td>
            <td className="px-4 py-3 text-sm text-gray-400">
              <div className="flex items-center gap-1">
                <MapPin size={12} />
                {breach.latitude.toFixed(6)}, {breach.longitude.toFixed(6)}
              </div>
            </td>
            <td className="px-4 py-3 text-xs text-gray-400">
              {breach.violations ? (
                typeof breach.violations === 'string' && breach.violations.startsWith('[') 
                  ? JSON.parse(breach.violations).join(', ') 
                  : breach.violations
              ) : '-'}
            </td>
            <td className="px-4 py-3">
              {breach.resolved ? (
                <div className="flex items-center gap-1 text-green-400">
                  <CheckCircle size={16} />
                  <span className="text-xs">Resolved</span>
                </div>
              ) : (
                <div className="flex items-center gap-1 text-red-400">
                  <XCircle size={16} />
                  <span className="text-xs">Active</span>
                </div>
              )}
            </td>
            <td className="px-4 py-3">
              {!breach.resolved && (
                <button
                  onClick={() => onResolve(breach.id)}
                  className="px-3 py-1 bg-green-600 text-white rounded text-xs hover:bg-green-700"
                >
                  Resolve
                </button>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
    
    {breaches.length === 0 && (
      <div className="p-12 text-center text-gray-400">No breaches found for the selected filters</div>
    )}
  </div>
);

export default HistoryViewer;

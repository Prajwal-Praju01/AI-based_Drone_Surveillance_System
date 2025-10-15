import React, { useState, useMemo } from 'react';
import { Search, ChevronDown, ChevronUp } from 'lucide-react';

const DetectionTable = React.memo(function DetectionTable({ detections }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState('object_id');
  const [sortDirection, setSortDirection] = useState('asc');

  // Memoize filtered detections to avoid recalculation on every render
  const filteredDetections = useMemo(() => {
    if (!searchTerm) return detections;
    
    const search = searchTerm.toLowerCase();
    return detections.filter(
      (detection) =>
        detection.class_name?.toLowerCase().includes(search) ||
        detection.object_id?.toString().includes(search) ||
        detection.zone_status?.toLowerCase().includes(search)
    );
  }, [detections, searchTerm]);

  // Memoize sorted detections
  const sortedDetections = useMemo(() => {
    return [...filteredDetections].sort((a, b) => {
      const aValue = a[sortField] ?? '';
      const bValue = b[sortField] ?? '';
      
      if (sortDirection === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });
  }, [filteredDetections, sortField, sortDirection]);

  // Handle column header click for sorting
  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const SortIcon = ({ field }) => {
    if (sortField !== field) return null;
    return sortDirection === 'asc' ? (
      <ChevronUp className="w-4 h-4 inline ml-1" />
    ) : (
      <ChevronDown className="w-4 h-4 inline ml-1" />
    );
  };

  return (
    <div className="card p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold">Detection Log</h2>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search detections..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 pr-4 py-2 bg-dark-900 border border-dark-700 rounded-lg text-sm focus:outline-none focus:border-primary-500 w-64"
          />
        </div>
      </div>

      {/* Stats */}
      <div className="mb-4 flex items-center space-x-4 text-sm">
        <span className="text-gray-400">
          Total Detections: <span className="text-white font-medium">{detections.length}</span>
        </span>
        <span className="text-gray-400">
          Showing: <span className="text-white font-medium">{sortedDetections.length}</span>
        </span>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-dark-700">
              <th
                className="text-left py-3 px-4 text-sm font-semibold text-gray-400 cursor-pointer hover:text-white"
                onClick={() => handleSort('object_id')}
              >
                Object ID <SortIcon field="object_id" />
              </th>
              <th
                className="text-left py-3 px-4 text-sm font-semibold text-gray-400 cursor-pointer hover:text-white"
                onClick={() => handleSort('class_name')}
              >
                Class <SortIcon field="class_name" />
              </th>
              <th
                className="text-left py-3 px-4 text-sm font-semibold text-gray-400 cursor-pointer hover:text-white"
                onClick={() => handleSort('confidence')}
              >
                Confidence <SortIcon field="confidence" />
              </th>
              <th
                className="text-left py-3 px-4 text-sm font-semibold text-gray-400 cursor-pointer hover:text-white"
                onClick={() => handleSort('zone_status')}
              >
                Zone Status <SortIcon field="zone_status" />
              </th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">
                Timestamp
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedDetections.length === 0 ? (
              <tr>
                <td colSpan="5" className="text-center py-8 text-gray-500">
                  No detections found
                </td>
              </tr>
            ) : (
              sortedDetections.map((detection, index) => (
                <tr
                  key={`${detection.object_id}-${index}`}
                  className="border-b border-dark-700 hover:bg-dark-800 transition-colors"
                >
                  <td className="py-3 px-4 text-sm">
                    <span className="font-mono text-primary-400">
                      #{detection.object_id || 'N/A'}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-sm">
                    <span className="bg-dark-700 px-2 py-1 rounded text-xs font-medium">
                      {detection.class_name || 'Unknown'}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-sm">
                    <div className="flex items-center space-x-2">
                      <div className="w-20 bg-dark-700 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            (detection.confidence || 0) > 0.8
                              ? 'bg-green-500'
                              : (detection.confidence || 0) > 0.6
                              ? 'bg-yellow-500'
                              : 'bg-red-500'
                          }`}
                          style={{ width: `${(detection.confidence || 0) * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-xs text-gray-400">
                        {((detection.confidence || 0) * 100).toFixed(1)}%
                      </span>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-sm">
                    <ZoneStatusBadge status={detection.zone_status} />
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-400">
                    {detection.timestamp || new Date().toLocaleTimeString()}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
});

// Memoize ZoneStatusBadge component
const ZoneStatusBadge = React.memo(function ZoneStatusBadge({ status }) {
  const statusConfig = {
    SAFE: { color: 'bg-green-500/20 text-green-400 border-green-500/50', label: 'SAFE' },
    BREACH: { color: 'bg-red-500/20 text-red-400 border-red-500/50', label: 'BREACH' },
    WARNING: { color: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50', label: 'WARNING' },
  };

  const config = statusConfig[status] || statusConfig.SAFE;

  return (
    <span className={`px-2 py-1 rounded text-xs font-bold border ${config.color}`}>
      {config.label}
    </span>
  );
});

export default DetectionTable;

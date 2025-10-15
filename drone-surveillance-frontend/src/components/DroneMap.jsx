import React, { useEffect, useState } from 'react';
import { MapPin, AlertTriangle, CheckCircle, Navigation } from 'lucide-react';

const DroneMap = React.memo(function DroneMap({ apiBaseUrl }) {
  const [drones, setDrones] = useState([]);
  const [zones, setZones] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch drones from Kaggle dataset with geofence info
        const dronesRes = await fetch(`${apiBaseUrl}/api/drones`);
        const dronesData = await dronesRes.json();
        setDrones(dronesData);

        // Fetch geofence zones
        const zonesRes = await fetch(`${apiBaseUrl}/api/geofence/zones`);
        const zonesData = await zonesRes.json();
        setZones(zonesData.zones || {});
        
        setLoading(false);
      } catch (error) {
        console.error('Error fetching drone map data:', error);
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, [apiBaseUrl]);

  if (loading) {
    return (
      <div className="card p-6">
        <h2 className="text-xl font-bold mb-4 flex items-center space-x-2">
          <MapPin className="w-6 h-6 text-primary-500" />
          <span>Live Drone Map</span>
        </h2>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-b-4 border-primary-500"></div>
        </div>
      </div>
    );
  }

  const safeDrones = drones.filter(d => d.in_safe_zone);
  const breachedDrones = drones.filter(d => !d.in_safe_zone);

  return (
    <div className="card p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold flex items-center space-x-2">
          <MapPin className="w-6 h-6 text-primary-500" />
          <span>Live Drone Map</span>
        </h2>
        <div className="flex items-center space-x-4 text-sm">
          <span className="flex items-center space-x-1">
            <CheckCircle className="w-4 h-4 text-green-500" />
            <span className="text-green-400">{safeDrones.length} Safe</span>
          </span>
          <span className="flex items-center space-x-1">
            <AlertTriangle className="w-4 h-4 text-red-500" />
            <span className="text-red-400">{breachedDrones.length} Breach</span>
          </span>
        </div>
      </div>

      {/* Drones List */}
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {drones.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <MapPin className="w-12 h-12 mx-auto mb-2 text-gray-600" />
            <p>No drones detected</p>
          </div>
        ) : (
          drones.map((drone, index) => (
            <DroneCard key={drone.id || index} drone={drone} index={index} />
          ))
        )}
      </div>

      {/* Zone Information */}
      {Object.keys(zones).length > 0 && (
        <div className="mt-4 pt-4 border-t border-dark-700">
          <h3 className="text-sm font-semibold text-gray-400 mb-2">Geofence Zones</h3>
          <div className="grid grid-cols-1 gap-2">
            {Object.entries(zones).slice(0, 2).map(([key, zone]) => (
              <div key={key} className="bg-dark-800 rounded-lg p-3 text-xs">
                <div className="font-semibold text-primary-400 mb-1">{zone.name}</div>
                <div className="text-gray-400 space-y-0.5">
                  <div>N: {zone.north}°, S: {zone.south}°</div>
                  <div>E: {zone.east}°, W: {zone.west}°</div>
                  <div>Max Alt: {zone.max_altitude}m</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
});

const DroneCard = React.memo(function DroneCard({ drone, index }) {
  const breach_info = drone.breach_info || {};
  const location = breach_info.location || { lat: drone.lat, lon: drone.lon, altitude: drone.altitude || 0 };
  const isBreached = !drone.in_safe_zone;

  return (
    <div className={`
      border-2 rounded-lg p-4 transition-all
      ${isBreached 
        ? 'border-red-500/50 bg-red-900/10' 
        : 'border-green-500/30 bg-dark-800'
      }
    `}>
      <div className="flex items-start justify-between">
        {/* Drone Info */}
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <Navigation className={`w-5 h-5 ${isBreached ? 'text-red-500' : 'text-green-500'}`} />
            <div>
              <div className="font-bold text-white">
                {drone.name || drone.id || `Object ${index + 1}`}
              </div>
              <div className="text-xs text-gray-500">
                ID: {drone.id || `Unknown-${index + 1}`}
              </div>
            </div>
            {isBreached && (
              <span className="px-2 py-0.5 bg-red-500 text-white text-xs rounded-full font-bold">
                BREACH
              </span>
            )}
          </div>

          {/* Description */}
          {drone.description && (
            <div className="text-xs text-gray-400 mb-2 italic">
              "{drone.description}"
            </div>
          )}

          {/* Object Details */}
          <div className="grid grid-cols-2 gap-2 text-xs mb-2">
            <div className="bg-dark-700 rounded px-2 py-1">
              <span className="text-gray-500">Type:</span>{' '}
              <span className="text-primary-400 font-semibold">{drone.class_name || 'Unknown'}</span>
            </div>
            <div className="bg-dark-700 rounded px-2 py-1">
              <span className="text-gray-500">Confidence:</span>{' '}
              <span className="text-green-400 font-semibold">
                {drone.confidence ? `${(drone.confidence * 100).toFixed(1)}%` : 'N/A'}
              </span>
            </div>
          </div>

          {/* Operator/Registration Info */}
          {(drone.operator || drone.registration) && (
            <div className="bg-dark-700 rounded px-2 py-1.5 mb-2 text-xs">
              {drone.operator && (
                <div className="text-gray-400">
                  <span className="text-gray-500">Operator:</span>{' '}
                  <span className="text-blue-400">{drone.operator}</span>
                </div>
              )}
              {drone.registration && drone.registration !== 'N/A' && (
                <div className="text-gray-400">
                  <span className="text-gray-500">Registration:</span>{' '}
                  <span className="text-yellow-400">{drone.registration}</span>
                </div>
              )}
            </div>
          )}

          {/* Location Data */}
          <div className="grid grid-cols-2 gap-2 text-xs text-gray-400 mb-2">
            <div>
              <span className="text-gray-500">Latitude:</span> {location.lat?.toFixed(6)}
            </div>
            <div>
              <span className="text-gray-500">Longitude:</span> {location.lon?.toFixed(6)}
            </div>
            <div>
              <span className="text-gray-500">Altitude:</span> {location.altitude?.toFixed(1)}m
            </div>
            <div>
              <span className="text-gray-500">Speed:</span> {drone.speed?.toFixed(1)} km/h
            </div>
            {drone.heading !== undefined && (
              <div>
                <span className="text-gray-500">Heading:</span> {drone.heading}°
              </div>
            )}
            {breach_info.distance_to_center_m && (
              <div>
                <span className="text-gray-500">Distance:</span> {breach_info.distance_to_center_m?.toFixed(0)}m
              </div>
            )}
          </div>

          {/* Threat Level */}
          {drone.threat_level && (
            <div className="mb-2">
              <span className={`text-xs font-bold px-2 py-0.5 rounded ${
                drone.threat_level === 'HIGH' ? 'bg-red-500/20 text-red-400' :
                drone.threat_level === 'MEDIUM' ? 'bg-yellow-500/20 text-yellow-400' :
                'bg-green-500/20 text-green-400'
              }`}>
                Threat: {drone.threat_level}
              </span>
            </div>
          )}

          {/* Violations */}
          {isBreached && breach_info.violations && breach_info.violations.length > 0 && (
            <div className="mt-2 pt-2 border-t border-red-500/30">
              <div className="text-xs text-red-400">
                <span className="font-semibold">⚠️ Violations:</span>
                <div className="mt-1 space-y-1">
                  {breach_info.violations.map((violation, idx) => (
                    <div key={idx} className="flex items-center space-x-1">
                      <AlertTriangle className="w-3 h-3" />
                      <span>{violation}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Status Indicator */}
        <div className="ml-4">
          {isBreached ? (
            <AlertTriangle className="w-8 h-8 text-red-500 animate-pulse" />
          ) : (
            <CheckCircle className="w-8 h-8 text-green-500" />
          )}
        </div>
      </div>
    </div>
  );
});

export default DroneMap;

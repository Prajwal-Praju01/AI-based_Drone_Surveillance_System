import React, { useState, useEffect, useMemo } from 'react';
import { AlertTriangle, X, Clock, MapPin } from 'lucide-react';

const AlertPanel = React.memo(function AlertPanel({ alerts, fullPage = false }) {
  const [visibleAlerts, setVisibleAlerts] = useState([]);

  useEffect(() => {
    setVisibleAlerts(alerts);
  }, [alerts]);

  // Handle dismiss alert
  const handleDismiss = (alertId) => {
    setVisibleAlerts(prev => 
      prev.map(alert => 
        alert.id === alertId ? { ...alert, dismissed: true } : alert
      )
    );
  };

  // Memoize filtered alerts for better performance
  const activeAlerts = useMemo(() => 
    visibleAlerts.filter((alert) => !alert.dismissed),
    [visibleAlerts]
  );
  
  const breachAlerts = useMemo(() => 
    activeAlerts.filter((alert) => alert.severity === 'high' || alert.type === 'breach'),
    [activeAlerts]
  );

  return (
    <div className={`card p-4 ${fullPage ? 'min-h-[600px]' : 'h-full'}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <AlertTriangle className="w-5 h-5 text-red-500" />
          <h2 className="text-lg font-bold">Active Alerts</h2>
          {breachAlerts.length > 0 && (
            <span className="bg-red-500 text-white text-xs font-bold rounded-full px-2 py-1">
              {breachAlerts.length}
            </span>
          )}
        </div>
      </div>

      {/* Alert Stats */}
      <div className="grid grid-cols-3 gap-2 mb-4">
        <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-3 text-center">
          <p className="text-2xl font-bold text-red-400">{breachAlerts.length}</p>
          <p className="text-xs text-gray-400 mt-1">Critical</p>
        </div>
        <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-lg p-3 text-center">
          <p className="text-2xl font-bold text-yellow-400">
            {activeAlerts.filter((a) => a.severity === 'medium').length}
          </p>
          <p className="text-xs text-gray-400 mt-1">Warning</p>
        </div>
        <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-3 text-center">
          <p className="text-2xl font-bold text-blue-400">
            {activeAlerts.filter((a) => a.severity === 'low').length}
          </p>
          <p className="text-xs text-gray-400 mt-1">Info</p>
        </div>
      </div>

      {/* Alerts List */}
      <div className={`space-y-3 ${fullPage ? '' : 'max-h-[400px]'} overflow-y-auto`}>
        {activeAlerts.length === 0 ? (
          <div className="text-center py-8">
            <AlertTriangle className="w-12 h-12 text-gray-600 mx-auto mb-3" />
            <p className="text-gray-500 text-sm">No active alerts</p>
            <p className="text-gray-600 text-xs mt-1">System operating normally</p>
          </div>
        ) : (
          activeAlerts.map((alert) => (
            <AlertCard
              key={alert.id}
              alert={alert}
              onDismiss={handleDismiss}
            />
          ))
        )}
      </div>

      {/* Alert History Summary */}
      {fullPage && (
        <div className="mt-6 pt-4 border-t border-dark-700">
          <h3 className="text-sm font-semibold text-gray-400 mb-3">
            Alert History (Last 24h)
          </h3>
          <div className="space-y-2">
            <HistoryItem label="Total Alerts" value={alerts.length} />
            <HistoryItem label="Breach Incidents" value={breachAlerts.length} />
            <HistoryItem label="Average Response Time" value="2.3 min" />
          </div>
        </div>
      )}    </div>
  );
});

const AlertCard = React.memo(function AlertCard({ alert, onDismiss }) {
  const severityConfig = {
    high: {
      bg: 'bg-red-900/20',
      border: 'border-red-500/50',
      icon: 'text-red-500',
      pulse: 'animate-pulse',
    },
    medium: {
      bg: 'bg-yellow-900/20',
      border: 'border-yellow-500/50',
      icon: 'text-yellow-500',
      pulse: '',
    },
    low: {
      bg: 'bg-blue-900/20',
      border: 'border-blue-500/50',
      icon: 'text-blue-500',
      pulse: '',
    },
  };

  const config = severityConfig[alert.severity || 'low'];

  return (
    <div
      className={`alert-card ${config.bg} border-2 ${config.border} rounded-lg p-4 relative`}
    >
      {/* Dismiss Button */}
      <button
        onClick={() => onDismiss(alert.id)}
        className="absolute top-2 right-2 p-1 hover:bg-dark-700 rounded transition-colors"
        title="Dismiss alert"
      >
        <X className="w-4 h-4 text-gray-400" />
      </button>

      {/* Alert Icon */}
      <div className="flex items-start space-x-3">
        <AlertTriangle className={`w-5 h-5 ${config.icon} ${config.pulse} mt-0.5`} />
        <div className="flex-1">
          {/* Alert Title */}
          <h4 className="font-bold text-white mb-1">
            {alert.title || 'Security Alert'}
          </h4>

          {/* Alert Message */}
          <p className="text-sm text-gray-300 mb-3">
            {alert.message || 'Unauthorized object detected in restricted zone'}
          </p>

          {/* Alert Metadata */}
          <div className="flex flex-wrap gap-3 text-xs text-gray-400">
            {alert.zone && (
              <div className="flex items-center space-x-1">
                <MapPin className="w-3 h-3" />
                <span>Zone: {alert.zone}</span>
              </div>
            )}
            {alert.timestamp && (
              <div className="flex items-center space-x-1">
                <Clock className="w-3 h-3" />
                <span>{new Date(alert.timestamp).toLocaleString()}</span>
              </div>
            )}
            {alert.object_class && (
              <div className="bg-dark-700 px-2 py-0.5 rounded">
                <span>Object: {alert.object_class}</span>
              </div>
            )}
          </div>

          {/* Alert Actions */}
          {alert.severity === 'high' && (
            <div className="mt-3 pt-3 border-t border-red-500/30">
              <button className="btn-primary text-xs py-1.5 px-3">
                View Details
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
});

const HistoryItem = React.memo(function HistoryItem({ label, value }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-dark-700">
      <span className="text-sm text-gray-400">{label}</span>
      <span className="text-sm font-semibold text-white">{value}</span>
    </div>
  );
});

export default AlertPanel;

import React, { useState, useEffect, useMemo } from 'react';
import { BarChart3, TrendingUp, Clock, AlertTriangle, Target, Activity, Download } from 'lucide-react';

const AnalyticsDashboard = React.memo(function AnalyticsDashboard({ apiBaseUrl }) {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('24h');

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const response = await fetch(`${apiBaseUrl}/api/analytics?range=${timeRange}`);
        const data = await response.json();
        setAnalytics(data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching analytics:', error);
        setLoading(false);
      }
    };

    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 10000); // Update every 10s
    return () => clearInterval(interval);
  }, [apiBaseUrl, timeRange]);

  const exportPDF = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/reports/analytics/pdf?range=${timeRange}`);
      const blob = await response.blob();
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analytics_report_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('PDF export failed:', error);
    }
  };

  if (loading || !analytics) {
    return (
      <div className="card p-6">
        <h2 className="text-xl font-bold mb-4 flex items-center space-x-2">
          <BarChart3 className="w-6 h-6 text-primary-500" />
          <span>Analytics Dashboard</span>
        </h2>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-b-4 border-primary-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Time Range Selector */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold flex items-center space-x-2">
            <BarChart3 className="w-7 h-7 text-primary-500" />
            <span>Analytics Dashboard</span>
          </h2>
          <div className="flex items-center space-x-2">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="bg-dark-800 border border-dark-600 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="1h">Last Hour</option>
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
            </select>
            <button className="btn-primary flex items-center space-x-2" onClick={exportPDF}>
              <Download className="w-4 h-4" />
              <span>Export PDF Report</span>
            </button>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <MetricCard
            icon={<Target className="w-6 h-6" />}
            label="Total Detections"
            value={analytics.total_detections || 0}
            trend={analytics.detection_trend || 0}
            color="blue"
          />
          <MetricCard
            icon={<AlertTriangle className="w-6 h-6" />}
            label="Breach Incidents"
            value={analytics.total_breaches || 0}
            trend={analytics.breach_trend || 0}
            color="red"
          />
          <MetricCard
            icon={<Activity className="w-6 h-6" />}
            label="Active Objects"
            value={analytics.active_objects || 0}
            trend={analytics.active_trend || 0}
            color="green"
          />
          <MetricCard
            icon={<Clock className="w-6 h-6" />}
            label="Avg Response Time"
            value={`${analytics.avg_response_time || 0}s`}
            trend={analytics.response_trend || 0}
            color="yellow"
          />
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Detection by Class */}
        <DetectionByClassChart data={analytics.detection_by_class || {}} />

        {/* Hourly Activity */}
        <HourlyActivityChart data={analytics.hourly_activity || []} />

        {/* Threat Distribution */}
        <ThreatDistributionChart data={analytics.threat_distribution || {}} />

        {/* Zone Status */}
        <ZoneStatusChart data={analytics.zone_status || {}} />
      </div>

      {/* Detection Timeline */}
      <DetectionTimeline data={analytics.recent_events || []} />
    </div>
  );
});

const MetricCard = React.memo(function MetricCard({ icon, label, value, trend, color }) {
  const colorClasses = {
    blue: 'border-blue-500/50 bg-blue-900/20 text-blue-400',
    red: 'border-red-500/50 bg-red-900/20 text-red-400',
    green: 'border-green-500/50 bg-green-900/20 text-green-400',
    yellow: 'border-yellow-500/50 bg-yellow-900/20 text-yellow-400',
  };

  const trendColor = trend > 0 ? 'text-red-400' : trend < 0 ? 'text-green-400' : 'text-gray-400';
  const trendIcon = trend > 0 ? '↑' : trend < 0 ? '↓' : '→';

  return (
    <div className={`card p-4 border-l-4 ${colorClasses[color]}`}>
      <div className="flex items-center justify-between mb-2">
        <div className={colorClasses[color]}>{icon}</div>
        <span className={`text-xs font-semibold ${trendColor}`}>
          {trendIcon} {Math.abs(trend)}%
        </span>
      </div>
      <p className="text-sm text-gray-400 mb-1">{label}</p>
      <p className="text-2xl font-bold text-white">{value}</p>
    </div>
  );
});

const DetectionByClassChart = React.memo(function DetectionByClassChart({ data }) {
  const maxValue = Math.max(...Object.values(data), 1);
  
  return (
    <div className="card p-6">
      <h3 className="text-lg font-bold mb-4">Detection by Object Type</h3>
      <div className="space-y-3">
        {Object.entries(data).map(([className, count]) => (
          <div key={className} className="space-y-1">
            <div className="flex items-center justify-between text-sm">
              <span className="capitalize text-gray-300">{className}</span>
              <span className="font-bold text-primary-400">{count}</span>
            </div>
            <div className="w-full bg-dark-700 rounded-full h-2 overflow-hidden">
              <div
                className="bg-primary-500 h-full rounded-full transition-all duration-500"
                style={{ width: `${(count / maxValue) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
});

const HourlyActivityChart = React.memo(function HourlyActivityChart({ data }) {
  const maxValue = Math.max(...data, 1);
  
  return (
    <div className="card p-6">
      <h3 className="text-lg font-bold mb-4">Hourly Detection Activity</h3>
      <div className="flex items-end justify-between h-48 space-x-1">
        {data.map((value, index) => (
          <div key={index} className="flex-1 flex flex-col items-center">
            <div
              className="w-full bg-gradient-to-t from-primary-500 to-primary-300 rounded-t-lg transition-all duration-500 hover:opacity-80"
              style={{ height: `${(value / maxValue) * 100}%` }}
              title={`Hour ${index}: ${value} detections`}
            />
            <span className="text-xs text-gray-500 mt-2">{index}</span>
          </div>
        ))}
      </div>
      <p className="text-xs text-gray-400 text-center mt-4">Hour of Day (24h format)</p>
    </div>
  );
});

const ThreatDistributionChart = React.memo(function ThreatDistributionChart({ data }) {
  const total = Object.values(data).reduce((sum, val) => sum + val, 0);
  const colors = {
    LOW: { bg: 'bg-green-500', border: 'border-green-400' },
    MEDIUM: { bg: 'bg-yellow-500', border: 'border-yellow-400' },
    HIGH: { bg: 'bg-red-500', border: 'border-red-400' },
  };

  return (
    <div className="card p-6">
      <h3 className="text-lg font-bold mb-4">Threat Level Distribution</h3>
      <div className="flex items-center justify-center mb-6">
        <div className="relative w-48 h-48">
          {/* Simple pie chart representation */}
          <div className="absolute inset-0 rounded-full overflow-hidden">
            {Object.entries(data).map(([level, count], index) => {
              const percentage = (count / total) * 100;
              return (
                <div
                  key={level}
                  className={`absolute inset-0 ${colors[level]?.bg || 'bg-gray-500'}`}
                  style={{
                    clipPath: `polygon(50% 50%, 50% 0%, ${50 + 50 * Math.sin((percentage / 100) * 2 * Math.PI)}% ${50 - 50 * Math.cos((percentage / 100) * 2 * Math.PI)}%, 50% 50%)`,
                    transform: `rotate(${(Object.values(data).slice(0, index).reduce((sum, val) => sum + val, 0) / total) * 360}deg)`,
                  }}
                />
              );
            })}
          </div>
          <div className="absolute inset-4 bg-dark-900 rounded-full flex items-center justify-center">
            <div className="text-center">
              <p className="text-3xl font-bold text-white">{total}</p>
              <p className="text-xs text-gray-400">Total</p>
            </div>
          </div>
        </div>
      </div>
      <div className="space-y-2">
        {Object.entries(data).map(([level, count]) => (
          <div key={level} className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${colors[level]?.bg || 'bg-gray-500'}`} />
              <span className="text-sm text-gray-300">{level}</span>
            </div>
            <span className="text-sm font-bold text-white">
              {count} ({total > 0 ? ((count / total) * 100).toFixed(1) : 0}%)
            </span>
          </div>
        ))}
      </div>
    </div>
  );
});

const ZoneStatusChart = React.memo(function ZoneStatusChart({ data }) {
  return (
    <div className="card p-6">
      <h3 className="text-lg font-bold mb-4">Geofence Zone Status</h3>
      <div className="space-y-4">
        {Object.entries(data).map(([zoneName, status]) => (
          <div key={zoneName} className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-300">{zoneName}</span>
              <span className={`text-xs font-bold px-2 py-1 rounded ${
                status.breaches > 0 ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'
              }`}>
                {status.breaches > 0 ? `${status.breaches} Breaches` : 'Secure'}
              </span>
            </div>
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div className="bg-dark-700 rounded p-2 text-center">
                <p className="text-gray-400">Active</p>
                <p className="font-bold text-blue-400">{status.active || 0}</p>
              </div>
              <div className="bg-dark-700 rounded p-2 text-center">
                <p className="text-gray-400">Safe</p>
                <p className="font-bold text-green-400">{status.safe || 0}</p>
              </div>
              <div className="bg-dark-700 rounded p-2 text-center">
                <p className="text-gray-400">Breach</p>
                <p className="font-bold text-red-400">{status.breaches || 0}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
});

const DetectionTimeline = React.memo(function DetectionTimeline({ data }) {
  return (
    <div className="card p-6">
      <h3 className="text-lg font-bold mb-4">Recent Detection Events</h3>
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {data.length === 0 ? (
          <p className="text-center text-gray-500 py-8">No recent events</p>
        ) : (
          data.map((event, index) => (
            <div
              key={index}
              className={`flex items-start space-x-3 p-3 rounded-lg border-l-4 ${
                event.type === 'breach'
                  ? 'border-red-500 bg-red-900/10'
                  : 'border-blue-500 bg-blue-900/10'
              }`}
            >
              <div className="flex-shrink-0 mt-1">
                {event.type === 'breach' ? (
                  <AlertTriangle className="w-5 h-5 text-red-500" />
                ) : (
                  <Target className="w-5 h-5 text-blue-500" />
                )}
              </div>
              <div className="flex-1">
                <p className="text-sm font-semibold text-white">{event.title}</p>
                <p className="text-xs text-gray-400 mt-1">{event.description}</p>
                <div className="flex items-center space-x-3 mt-2 text-xs text-gray-500">
                  <span>{event.class_name}</span>
                  <span>•</span>
                  <span>{new Date(event.timestamp).toLocaleString()}</span>
                  <span>•</span>
                  <span className="text-primary-400">{event.location}</span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
});

export default AnalyticsDashboard;

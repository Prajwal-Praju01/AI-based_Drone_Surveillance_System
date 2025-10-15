import React from 'react';
import { Bell, Shield, Activity, User, LogOut } from 'lucide-react';

function Header({ isConnected, alertsCount, user, onLogout }) {
  const getRoleBadgeColor = (role) => {
    switch(role) {
      case 'admin': return 'bg-red-500/20 text-red-400 border-red-500/50';
      case 'operator': return 'bg-green-500/20 text-green-400 border-green-500/50';
      case 'viewer': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/50';
    }
  };

  return (
    <header className="bg-dark-900 border-b border-dark-700 shadow-lg">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Left: Logo and Title */}
          <div className="flex items-center space-x-4">
            <div className="bg-primary-600 p-2 rounded-lg">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">
                AI Drone Surveillance System
              </h1>
              <p className="text-xs text-gray-400">HAL Defense AI Division</p>
            </div>
          </div>

          {/* Right: Status, User, and Alerts */}
          <div className="flex items-center space-x-6">
            {/* Connection Status */}
            <div className="flex items-center space-x-2">
              <Activity className="w-5 h-5 text-gray-400" />
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-300">Status:</span>
                <div className="flex items-center space-x-1">
                  <span
                    className={`status-dot ${
                      isConnected ? 'bg-green-500' : 'bg-red-500'
                    }`}
                  />
                  <span
                    className={`text-sm font-medium ${
                      isConnected ? 'text-green-400' : 'text-red-400'
                    }`}
                  >
                    {isConnected ? 'Connected' : 'Disconnected'}
                  </span>
                </div>
              </div>
            </div>

            {/* Alerts Indicator */}
            <div className="relative">
              <button className="relative p-2 hover:bg-dark-800 rounded-lg transition-colors">
                <Bell className="w-6 h-6 text-gray-400" />
                {alertsCount > 0 && (
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center animate-pulse">
                    {alertsCount}
                  </span>
                )}
              </button>
            </div>

            {/* User Info */}
            {user && (
              <div className="flex items-center gap-3 px-3 py-2 bg-dark-800/50 rounded-lg border border-dark-700">
                <div className="flex items-center gap-2">
                  <div className="bg-blue-500/20 p-1.5 rounded-full">
                    <User size={16} className="text-blue-400" />
                  </div>
                  <div className="text-left">
                    <div className="text-sm font-medium text-white">{user.username}</div>
                    <div className={`text-xs px-2 py-0.5 rounded border ${getRoleBadgeColor(user.role)}`}>
                      {user.role}
                    </div>
                  </div>
                </div>
                <button
                  onClick={onLogout}
                  className="p-1.5 hover:bg-red-500/20 rounded text-gray-400 hover:text-red-400 transition"
                  title="Logout"
                >
                  <LogOut size={16} />
                </button>
              </div>
            )}

            {/* Time Display */}
            <div className="text-sm text-gray-400 hidden md:block">
              {new Date().toLocaleString()}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;

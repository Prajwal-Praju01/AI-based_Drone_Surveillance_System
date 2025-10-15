# 🚁 AI-Based Drone Surveillance System - Frontend

A modern, real-time surveillance dashboard built with **React + Tailwind CSS** for monitoring drone video feeds with AI-powered object detection.

## ✨ Features

- **Live Video Stream**: Real-time MJPEG video feed from drone
- **Object Detection Table**: Live table displaying all detected objects with YOLOv8 + DeepSORT
- **Alert System**: Real-time alerts for restricted zone breaches
- **Responsive Design**: Professional dark theme optimized for desktop and tablet
- **Auto-Refresh**: Detection data updates every 2 seconds
- **Modern UI Components**:
  - Dynamic sidebar navigation
  - Stats dashboard with cards
  - Sortable and searchable detection table
  - Animated alert notifications
  - Connection status indicator

## 🛠️ Tech Stack

- **React 18** - UI framework
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API calls
- **Lucide React** - Beautiful icon set

## 📦 Installation

### Prerequisites
- Node.js 18+ and npm/yarn
- Python backend running on `http://localhost:5000`

### Steps

1. **Install Dependencies**
```bash
cd drone-surveillance-frontend
npm install
```

2. **Configure Backend URL** (if different from localhost:5000)
Edit `src/App.jsx`:
```javascript
const API_BASE_URL = 'http://your-backend-url:port';
```

3. **Start Development Server**
```bash
npm run dev
```

The app will open at `http://localhost:3000`

4. **Build for Production**
```bash
npm run build
```

## 🎯 API Integration

The frontend expects the following backend endpoints:

### GET `/video_feed`
Returns MJPEG video stream from drone

### GET `/detections`
Returns JSON array of current detections:
```json
[
  {
    "object_id": 1,
    "class_name": "person",
    "confidence": 0.95,
    "zone_status": "SAFE",
    "timestamp": "2025-10-06T10:30:45"
  }
]
```

### GET `/alerts`
Returns JSON array of active alerts:
```json
[
  {
    "id": 1,
    "title": "Restricted Zone Breach",
    "message": "Person detected in Zone A",
    "severity": "high",
    "zone": "Zone A",
    "object_class": "person",
    "timestamp": "2025-10-06T10:30:45",
    "read": false,
    "dismissed": false
  }
]
```

## 🎨 UI Components

### Header
- Project title and branding
- Connection status indicator (green/red)
- Alert notification bell with badge count
- Real-time clock

### Sidebar
- Navigation menu (Dashboard, Live Feed, Alerts, Settings)
- System load indicator
- Alert counter badges

### VideoFeed
- Live MJPEG stream display
- Loading spinner
- Error handling with retry
- Fullscreen toggle
- Timestamp overlay

### DetectionTable
- Sortable columns (ID, Class, Confidence, Zone Status)
- Search/filter functionality
- Confidence progress bars
- Zone status badges (SAFE/BREACH/WARNING)
- Responsive design

### AlertPanel
- Real-time alert cards
- Severity-based color coding (Critical/Warning/Info)
- Alert statistics
- Dismissible notifications
- Animated slide-in effects

## 🎭 Views

1. **Dashboard** - Overview with video feed, alerts, and detection table
2. **Live Feed** - Full-screen video feed with detection data
3. **Alerts** - Dedicated alerts view with history
4. **Settings** - Configuration panel (API URLs, refresh rate, etc.)

## 🔧 Configuration

### Update Refresh Rate
In `src/App.jsx`, modify the interval:
```javascript
const interval = setInterval(() => {
  fetchDetections();
  fetchAlerts();
}, 2000); // Change to desired milliseconds
```

### Customize Theme Colors
Edit `tailwind.config.js` to modify color schemes.

### Proxy Configuration
If running backend on different port, update `vite.config.js`:
```javascript
proxy: {
  '/video_feed': 'http://localhost:YOUR_PORT',
  '/detections': 'http://localhost:YOUR_PORT',
  '/alerts': 'http://localhost:YOUR_PORT'
}
```

## 📱 Responsive Design

- Desktop: Full sidebar + multi-column layout
- Tablet: Adaptive layout with collapsible sidebar
- Mobile: Stacked layout (in development)

## 🎨 Color Scheme

- **Primary**: Blue (`#0ea5e9`)
- **Background**: Dark (`#020617`, `#0f172a`, `#1e293b`)
- **Success**: Green (`#22c55e`)
- **Warning**: Yellow (`#eab308`)
- **Danger**: Red (`#ef4444`)

## 🚀 Production Deployment

1. Build the project:
```bash
npm run build
```

2. Deploy the `dist/` folder to your web server (Nginx, Apache, etc.)

3. Configure reverse proxy for API calls:
```nginx
location /api/ {
    proxy_pass http://backend-server:5000/;
}
```

## 📝 Sample Backend Response Format

For testing, your backend should return data in this format:

**Detections:**
```json
[
  {
    "object_id": 1,
    "class_name": "person",
    "confidence": 0.95,
    "zone_status": "SAFE"
  },
  {
    "object_id": 2,
    "class_name": "vehicle",
    "confidence": 0.87,
    "zone_status": "BREACH"
  }
]
```

**Alerts:**
```json
[
  {
    "id": 1,
    "title": "Security Breach",
    "message": "Unauthorized person detected in Zone A",
    "severity": "high",
    "zone": "Zone A",
    "object_class": "person",
    "timestamp": "2025-10-06T10:30:45",
    "read": false
  }
]
```

## 🤝 Integration Guide

1. Start your Python backend (Flask/FastAPI) on port 5000
2. Ensure CORS is enabled in backend
3. Start the React frontend
4. The frontend will automatically connect and start polling

## 📄 License

© HAL Defense AI Division 2025

## 🐛 Troubleshooting

**Video not loading?**
- Check backend is running
- Verify `/video_feed` endpoint is accessible
- Check browser console for CORS errors

**No detections showing?**
- Verify `/detections` endpoint returns valid JSON
- Check network tab in browser DevTools
- Ensure backend is sending data every 2 seconds

**Build errors?**
- Delete `node_modules` and run `npm install` again
- Clear npm cache: `npm cache clean --force`

## 📞 Support

For issues or questions, contact the HAL Defense AI Division team.

---

**Built with ❤️ by HAL Defense AI Division**

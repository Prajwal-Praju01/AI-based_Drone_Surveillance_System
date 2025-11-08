# 📘 AI-Based Drone Surveillance System - User Manual

**Version:** 1.0.0  
**Date:** November 2025  
**Organization:** HAL Defense AI Division

---

## 📑 Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture & Data Flow](#2-architecture--data-flow)
3. [Installation Guide](#3-installation-guide)
4. [Getting Started](#4-getting-started)
5. [User Interface Guide](#5-user-interface-guide)
6. [Features & Functionality](#6-features--functionality)
7. [API Reference](#7-api-reference)
8. [Configuration](#8-configuration)
9. [Troubleshooting](#9-troubleshooting)
10. [Best Practices](#10-best-practices)
11. [FAQs](#11-faqs)

---

## 1. System Overview

### 1.1 What is This System?

The AI-Based Drone Surveillance System is a complete, production-ready solution for real-time monitoring and tracking of objects using advanced computer vision. It combines:

- **YOLOv8** (You Only Look Once) - State-of-the-art object detection
- **DeepSORT** - Multi-object tracking with ID persistence
- **Geofencing** - Automatic zone breach detection
- **Real-time Dashboard** - Modern React-based user interface
- **Analytics** - Historical data analysis and reporting

### 1.2 Key Capabilities

✅ **Real-time Object Detection** - Detects persons, vehicles, drones, and more  
✅ **Multi-object Tracking** - Maintains consistent IDs across frames  
✅ **Geofence Monitoring** - Alerts when objects enter restricted zones  
✅ **Live Video Streaming** - MJPEG stream with bounding boxes  
✅ **Historical Analysis** - Review past detections and breaches  
✅ **Export & Reporting** - CSV/PDF export for analysis  
✅ **Replay Mode** - Playback historical events  
✅ **Heatmap Visualization** - Identify hotspots  

### 1.3 System Requirements

#### Minimum Requirements (CPU Only)
- **OS:** Windows 10/11, Ubuntu 20.04+, macOS 11+
- **CPU:** Intel i5 or AMD Ryzen 5 (4 cores)
- **RAM:** 8 GB
- **Storage:** 10 GB free space
- **Performance:** 5-10 FPS

#### Recommended Requirements (GPU)
- **OS:** Windows 10/11, Ubuntu 20.04+
- **CPU:** Intel i7 or AMD Ryzen 7
- **RAM:** 16 GB
- **GPU:** NVIDIA RTX 3060 (8GB VRAM) or better
- **Storage:** 20 GB free space
- **Performance:** 30+ FPS

#### For Training
- **GPU:** NVIDIA RTX 3060 or better (6GB+ VRAM)
- **RAM:** 16 GB minimum
- **Storage:** 50 GB for datasets and models
- **Training Time:** 2-8 hours depending on model size

---

## 2. Architecture & Data Flow

### 2.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     AI DRONE SURVEILLANCE SYSTEM                         │
└─────────────────────────────────────────────────────────────────────────┘

┌────────────────────┐                           ┌───────────────────────┐
│   VIDEO INPUT      │                           │   TRAINING PIPELINE   │
│                    │                           │                       │
│ • Webcam (0,1,2..) │                           │ 1. Kaggle Dataset     │
│ • Video File       │                           │ 2. Data Preparation   │
│ • RTSP Stream      │                           │ 3. YOLOv8 Training    │
│ • Drone Feed       │                           │ 4. Model Export       │
└──────────┬─────────┘                           └──────────┬────────────┘
           │                                                │
           │ Video Frames (30 FPS)                         │ Trained Model
           ↓                                                ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                         INFERENCE ENGINE                                 │
│                         (backend/inference.py)                           │
│                                                                          │
│  ┌──────────────┐        ┌──────────────┐        ┌──────────────────┐  │
│  │  YOLOv8      │──────→ │  DeepSORT    │──────→ │  Geofence        │  │
│  │  Detection   │        │  Tracking    │        │  Checking        │  │
│  │              │        │              │        │                  │  │
│  │ • Bounding   │        │ • ID         │        │ • Zone Breach    │  │
│  │   Boxes      │        │   Assignment │        │ • Alert          │  │
│  │ • Classes    │        │ • Tracking   │        │   Generation     │  │
│  │ • Confidence │        │ • History    │        │ • Logging        │  │
│  └──────────────┘        └──────────────┘        └──────────────────┘  │
│         │                        │                        │             │
│         └────────────────────────┴────────────────────────┘             │
│                                  │                                       │
└──────────────────────────────────┼───────────────────────────────────────┘
                                   │
                                   │ Real-time Data
                                   ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                         FLASK REST API                                   │
│                         (backend/app.py)                                 │
│                                                                          │
│  GET /video_feed      → MJPEG stream with bounding boxes               │
│  GET /detections      → Current detections (JSON)                       │
│  GET /alerts          → Active alerts (JSON)                            │
│  GET /api/history/*   → Historical data                                 │
│  GET /api/heatmap     → Heatmap data                                    │
│  GET /api/analytics   → Statistics                                      │
│                                                                          │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
                                   │ HTTP/REST
                                   │
                                   ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                         REACT FRONTEND                                   │
│                         (localhost:3000)                                 │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Navigation: Dashboard | Live Feed | Analytics | History | Alerts│  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐    │
│  │  Live Video     │  │  Detection      │  │  Alert Panel        │    │
│  │  Stream         │  │  Table          │  │                     │    │
│  │                 │  │                 │  │  🚨 Zone Breach     │    │
│  │  [Bounding Boxes]  │  ID | Class | Zone │  🚨 Unauthorized    │    │
│  │                 │  │  ──────────────  │  │                     │    │
│  │                 │  │  1  | person| ✓ │  │                     │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘    │
│                                                                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐    │
│  │  Heatmap        │  │  History &      │  │  Analytics          │    │
│  │  Visualization  │  │  Replay         │  │  Dashboard          │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                        REAL-TIME PROCESSING FLOW                      │
└──────────────────────────────────────────────────────────────────────┘

Video Frame (1280x720)
       │
       ↓
┌──────────────────┐
│ Pre-processing   │  • Resize to 640x640
│                  │  • Normalize pixels
│                  │  • BGR → RGB
└────────┬─────────┘
         │
         ↓
┌──────────────────┐
│ YOLOv8 Inference │  • Forward pass through neural network
│ (~30-50ms)       │  • Non-Maximum Suppression (NMS)
│                  │  • Output: [bbox, class, confidence]
└────────┬─────────┘
         │
         ↓
[Detection Results: N objects]
{bbox: [x,y,w,h], class: "person", conf: 0.95}
         │
         ↓
┌──────────────────┐
│ DeepSORT Tracker │  • Match detections to existing tracks
│ (~8ms)           │  • Kalman filter prediction
│                  │  • Hungarian algorithm matching
│                  │  • Assign/create track IDs
└────────┬─────────┘
         │
         ↓
[Tracked Objects: N objects]
{id: 1, bbox: [x,y,w,h], class: "person", conf: 0.95}
         │
         ↓
┌──────────────────┐
│ Geofence Check   │  • Compare position with zone polygons
│ (~5ms)           │  • Calculate distance to zone center
│                  │  • Generate alerts if breached
└────────┬─────────┘
         │
         ├──→ Alerts: [{zone: "A", object_id: 1, type: "breach"}]
         │
         ↓
┌──────────────────┐
│ Visualization    │  • Draw bounding boxes
│ (~5ms)           │  • Add labels and IDs
│                  │  • Draw zone boundaries
└────────┬─────────┘
         │
         ↓
┌──────────────────┐
│ JPEG Encoding    │  • Compress frame to JPEG
│                  │  • Stream via MJPEG protocol
└────────┬─────────┘
         │
         ↓
  Browser Display (Frontend)

Total Latency: ~50-70ms per frame (15-20 FPS)
```

### 2.3 Training Pipeline Flow

```
┌────────────────────────────────────────────────────────────────────────┐
│                         MODEL TRAINING PIPELINE                         │
└────────────────────────────────────────────────────────────────────────┘

Step 1: Dataset Acquisition
┌──────────────────────────┐
│  Kaggle API              │
│  • Download dataset      │
│  • Extract archives      │
└────────┬─────────────────┘
         │
         ↓
Step 2: Data Preparation
┌──────────────────────────┐
│  data_preparation.py     │
│  • Parse annotations     │
│  • Convert to YOLO format│
│  • Train/Val split (80/20)│
│  • Generate data.yaml    │
└────────┬─────────────────┘
         │
         ↓
Step 3: Model Initialization
┌──────────────────────────┐
│  Load YOLOv8 Pretrained  │
│  • YOLOv8n (fastest)     │
│  • YOLOv8m (recommended) │
│  • YOLOv8x (most accurate)│
└────────┬─────────────────┘
         │
         ↓
Step 4: Training Loop (100 epochs)
┌──────────────────────────────────────────┐
│  For each epoch:                         │
│  1. Load batch (16 images)               │
│  2. Forward pass                         │
│  3. Calculate loss (bbox + class + obj)  │
│  4. Backward propagation                 │
│  5. Update weights (AdamW optimizer)     │
│  6. Validate on val set                  │
│  7. Save checkpoint if best              │
│  8. Early stopping if no improvement     │
└────────┬─────────────────────────────────┘
         │
         ↓
Step 5: Model Evaluation
┌──────────────────────────┐
│  Metrics Calculation     │
│  • mAP@50-95: 0.52       │
│  • Precision: 0.71       │
│  • Recall: 0.68          │
│  • Confusion matrix      │
└────────┬─────────────────┘
         │
         ↓
Step 6: Model Export
┌──────────────────────────┐
│  Save Trained Model      │
│  • best.pt (PyTorch)     │
│  • best.onnx (ONNX)      │
│  • results.png (plots)   │
└──────────────────────────┘

Training Time: 2-8 hours (depending on GPU)
Output: models/drone_surveillance_YYYYMMDD_HHMMSS/weights/best.pt
```

---

## 3. Installation Guide

### 3.1 Prerequisites Checklist

Before starting installation, ensure you have:

- [ ] Python 3.8 or higher installed
- [ ] Node.js 16+ and npm installed
- [ ] Git installed (optional, for cloning)
- [ ] 10-50 GB free disk space
- [ ] Internet connection (for downloading dependencies and datasets)
- [ ] (Optional) NVIDIA GPU with CUDA support for faster performance

### 3.2 Step-by-Step Installation

#### For Your Friend Receiving the ZIP File

**Step 1: Extract the ZIP**

```bash
# Extract to a folder (e.g., C:\Projects\)
# You should see: AI-based_Drone_Surveillance_System/
```

**Step 2: Navigate to Project**

```bash
cd AI-based_Drone_Surveillance_System
```

**Step 3: Create Python Virtual Environment (Recommended)**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

**Step 4: Install Backend Dependencies**

```bash
cd backend
pip install -r requirements.txt
```

This will install:
- ✅ YOLOv8 (ultralytics)
- ✅ PyTorch and torchvision
- ✅ OpenCV
- ✅ DeepSORT
- ✅ Flask
- ✅ All other dependencies

**Step 5: Install Frontend Dependencies**

```bash
cd ../drone-surveillance-frontend
npm install
```

This will install:
- ✅ React and React DOM
- ✅ Vite (build tool)
- ✅ Tailwind CSS
- ✅ Axios (HTTP client)
- ✅ Lucide React (icons)
- ✅ Leaflet (maps)

**Step 6: Verify Installation**

```bash
# Check Python packages
pip list | grep -E "ultralytics|torch|opencv|flask"

# Check Node packages
npm list --depth=0
```

### 3.3 Quick Start Scripts

The project includes automated setup scripts:

**Windows:**
```bash
# Start both servers automatically
start_servers.bat
```

**Manual Start:**
```bash
# Terminal 1: Backend
cd backend
python app.py

# Terminal 2: Frontend
cd drone-surveillance-frontend
npm run dev
```

### 3.4 Optional: Kaggle API Setup (For Real Data)

If you want to use real datasets instead of mock data:

**Step 1: Get Kaggle API Credentials**
1. Go to https://www.kaggle.com/account
2. Scroll to "API" section
3. Click "Create New API Token"
4. Download `kaggle.json`

**Step 2: Install Credentials**

```bash
# Windows
mkdir %USERPROFILE%\.kaggle
copy kaggle.json %USERPROFILE%\.kaggle\

# Linux/Mac
mkdir ~/.kaggle
mv kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

**Step 3: Download Dataset**

```bash
cd backend
python data_preparation.py
```

---

## 4. Getting Started

### 4.1 First Time Setup

After installation, follow these steps to get the system running:

**1. Start the Backend Server**

```bash
cd backend
python app.py
```

Expected output:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
[INFO] YOLOv8 model loaded successfully
[INFO] DeepSORT tracker initialized
[INFO] Database initialized
```

**2. Start the Frontend Server**

```bash
cd drone-surveillance-frontend
npm run dev
```

Expected output:
```
VITE v5.0.7  ready in 234 ms
➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

**3. Access the Dashboard**

Open your browser and navigate to:
```
http://localhost:3000
```

**4. Login (Default Credentials)**

```
Username: admin
Password: admin123
```

Or:
```
Username: operator
Password: operator123
```

### 4.2 First Detection Test

Once logged in, you should see:

1. ✅ **Video Feed** - Live camera feed or test video
2. ✅ **Detection Table** - Real-time object detections
3. ✅ **Alert Panel** - Zone breach notifications
4. ✅ **System Statistics** - Active detections count

**Test Video Feed:**

If no camera is detected, the system will use test video or mock data.

To use a specific camera:
```python
# Edit backend/config.py
VIDEO_CONFIG = {
    "source": 0,  # Change to 1, 2, etc. for other cameras
}
```

### 4.3 Understanding the Dashboard

The main dashboard shows:

```
┌────────────────────────────────────────────────────────────────┐
│ [Logo] AI Drone Surveillance    [●] Online    [🚨] 3 Alerts   │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────┐    │
│  │  LIVE VIDEO FEED                                      │    │
│  │                                                        │    │
│  │  [Video stream with bounding boxes around detected   │    │
│  │   objects, showing class labels and confidence]       │    │
│  │                                                        │    │
│  └───────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌───────────────────────────────────────────────────────┐    │
│  │  DETECTION TABLE                                      │    │
│  ├─────┬──────────┬────────┬──────────┬─────────────────┤    │
│  │ ID  │ Class    │ Conf   │ Zone     │ Status          │    │
│  ├─────┼──────────┼────────┼──────────┼─────────────────┤    │
│  │ 1   │ person   │ 95%    │ Zone A   │ ✓ Safe          │    │
│  │ 2   │ car      │ 87%    │ Zone B   │ ⚠️  Breach       │    │
│  │ 3   │ truck    │ 92%    │ -        │ ✓ Safe          │    │
│  └─────┴──────────┴────────┴──────────┴─────────────────┘    │
│                                                                 │
│  ┌───────────────────────────────────────────────────────┐    │
│  │  ALERT PANEL                                          │    │
│  │                                                        │    │
│  │  🚨 Zone A Breach - Unauthorized Person Detected      │    │
│  │     Time: 14:23:45  |  Distance: 45m from center     │    │
│  │                                                        │    │
│  │  🚨 Zone B Altitude Violation - Drone Exceeded 120m  │    │
│  │     Time: 14:22:10  |  Altitude: 145m                │    │
│  └───────────────────────────────────────────────────────┘    │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## 5. User Interface Guide

### 5.1 Navigation Menu

The sidebar provides access to all features:

| Icon | Menu Item | Description |
|------|-----------|-------------|
| 📊 | **Dashboard** | Main overview with live feed and statistics |
| 🎥 | **Live Feed** | Full-screen video feed view |
| 📈 | **Analytics** | Charts and statistics |
| 🗺️ | **Heatmap** | Visual hotspot analysis |
| 📚 | **History** | Historical data browser with replay |
| 🚨 | **Alerts** | Alert management and review |
| ⚙️ | **Settings** | System configuration |

### 5.2 Dashboard View

**Components:**

1. **Stats Cards (Top)**
   - Active Detections count
   - Active Alerts count
   - System Status (Online/Offline)

2. **Video Feed (Center-Left)**
   - Live MJPEG stream
   - Bounding boxes with labels
   - Auto-refresh every frame

3. **Alert Panel (Right)**
   - Real-time alerts
   - Severity indicators (High/Medium/Low)
   - Time stamps
   - Auto-dismiss after 5 minutes

4. **Detection Table (Bottom)**
   - Object ID (persistent tracking)
   - Class name
   - Confidence score
   - Zone status
   - Coordinates

### 5.3 Live Feed View

Full-screen video feed with:
- Larger video display
- Detection overlay
- Real-time FPS counter
- Frame timestamp

**Controls:**
- Click to pause/resume
- Scroll to zoom (if supported)

### 5.4 Analytics Dashboard

Displays comprehensive statistics:

**Time-based Charts:**
- Detections per hour (last 24h)
- Detections by class (pie chart)
- Breach frequency timeline

**Summary Cards:**
- Total detections
- Unique objects tracked
- Total breaches
- Resolution rate

**Top Statistics:**
- Most detected class
- Most breached zone
- Peak detection hour

### 5.5 Heatmap Visualization

Interactive map showing:

**Detection Heatmap:**
- Red zones = High detection density
- Yellow zones = Medium density
- Green zones = Low density

**Breach Heatmap:**
- Red zones = Frequent breaches
- Purple zones = Occasional breaches

**Controls:**
- Toggle between detection/breach heatmaps
- Adjust intensity slider
- Filter by time range
- Export heatmap image

### 5.6 History & Replay

Browse and replay historical events:

**Tabs:**
1. **Detections Tab**
   - Search by object class
   - Filter by date range
   - Search by object ID
   - Export to CSV

2. **Breaches Tab**
   - Filter by zone
   - Filter by threat level (High/Medium/Low)
   - Filter by resolution status
   - Resolve breaches inline

**Replay Mode:**
- Play/pause controls
- Speed selector (1x, 2x, 5x, 10x)
- Progress bar
- Highlighted current event
- Auto-advance through events

**Export Options:**
- CSV export
- PDF report generation
- Filtered exports

### 5.7 Alerts View

Comprehensive alert management:

**Alert Cards:**
- Severity indicator (colored dot)
- Alert message
- Timestamp
- Location details
- "NEW" badge for recent alerts

**Filters:**
- By severity
- By time range
- By zone
- By status (active/resolved)

**Actions:**
- Mark as read
- Resolve breach
- Export alert log

---

## 6. Features & Functionality

### 6.1 Object Detection

**Supported Classes:**
- person
- car
- truck
- bus
- motorcycle
- bicycle
- bird
- drone
- (And more from COCO dataset)

**Detection Process:**
1. Frame captured from video source
2. Preprocessed and fed to YOLOv8
3. Objects detected with bounding boxes
4. Confidence threshold applied (default: 25%)
5. Results displayed in real-time

**Adjusting Detection:**
```python
# Edit backend/config.py
MODEL_CONFIG = {
    "conf_threshold": 0.25,  # Increase to reduce false positives
    "iou_threshold": 0.45,   # Adjust overlap threshold
}
```

### 6.2 Object Tracking

**Features:**
- Persistent ID assignment across frames
- Handles occlusions and re-appearances
- Tracks up to 50 objects simultaneously
- Maintains track history

**Tracking States:**
- **Confirmed** - Track established (green box)
- **Tentative** - New detection (yellow box)
- **Deleted** - Lost track (removed after 30 frames)

**Track Information:**
- Unique ID (e.g., person_001)
- Position history (last 30 frames)
- Velocity estimation
- Time on screen

### 6.3 Geofence Monitoring

**Zone Types:**

1. **Restricted Areas** - No entry allowed
2. **Perimeter Zones** - Boundary monitoring
3. **No-Fly Zones** - Altitude + boundary restrictions

**Default Zones:**

```python
# Restricted Area Alpha
{
    "name": "Restricted Area Alpha",
    "polygon": [[100, 100], [500, 100], [500, 400], [100, 400]],
    "alert_classes": ["person", "vehicle"],
    "threat_level": "HIGH"
}

# Perimeter Zone Beta
{
    "name": "Perimeter Zone Beta",
    "polygon": [[50, 50], [600, 50], [600, 450], [50, 450]],
    "alert_classes": ["person"],
    "threat_level": "MEDIUM"
}

# No-Fly Zone Gamma
{
    "name": "No-Fly Zone Gamma",
    "type": "3D",  # Includes altitude
    "polygon": [[200, 200], [400, 200], [400, 400], [200, 400]],
    "max_altitude": 120.0,  # meters
    "alert_classes": ["drone", "bird"],
    "threat_level": "HIGH"
}
```

**Breach Detection:**
- Point-in-polygon algorithm
- Distance from zone center calculation
- Violation type identification
- Alert generation with deduplication

**Alert Deduplication:**
- 30-second cooldown per (zone, object_id) pair
- Prevents alert flooding
- 5-minute alert expiration

### 6.4 Alert System

**Alert Levels:**

| Level | Color | Conditions | Actions |
|-------|-------|------------|---------|
| 🔴 **HIGH** | Red | Restricted zone breach, unauthorized drone | Immediate notification |
| 🟡 **MEDIUM** | Yellow | Perimeter breach, altitude warning | Standard alert |
| 🟢 **LOW** | Green | Minor boundary proximity | Log only |

**Alert Structure:**
```json
{
  "id": 1,
  "type": "geofence_breach",
  "severity": "high",
  "title": "Restricted Area Breach",
  "message": "Person detected in Restricted Area Alpha",
  "zone": "Restricted Area Alpha",
  "object_id": "person_001",
  "class": "person",
  "timestamp": "2025-11-05T14:23:45Z",
  "location": {
    "lat": 12.9716,
    "lon": 77.5946,
    "altitude": 85.0
  },
  "violations": ["unauthorized_entry"],
  "distance_to_center": 45.2,
  "new": true
}
```

**Alert Actions:**
- Visual notification in UI
- Log to database
- (Optional) Email/SMS notification
- (Optional) Webhook trigger

### 6.5 Video Streaming

**Stream Configuration:**

```python
# backend/config.py
VIDEO_CONFIG = {
    "source": 0,              # Camera index or video path
    "resolution": (1280, 720),
    "fps": 30,
    "stream_quality": 85,     # JPEG quality (0-100)
}
```

**Supported Sources:**
1. **Webcam:** `source: 0` (or 1, 2 for multiple cameras)
2. **Video File:** `source: "video.mp4"`
3. **RTSP Stream:** `source: "rtsp://192.168.1.100:554/stream"`
4. **IP Camera:** `source: "http://192.168.1.100/video"`

**Stream Optimization:**
- Dynamic frame skipping on CPU
- Adaptive JPEG compression
- Frame caching
- Reduced resolution for slower systems

### 6.6 Data Export

**Export Formats:**

1. **CSV Export**
   - Detection history
   - Breach log
   - Alert log
   - Customizable columns

2. **PDF Reports**
   - Summary statistics
   - Charts and graphs
   - Detailed tables
   - Company branding

**Export Process:**

1. Navigate to History view
2. Apply desired filters
3. Click "Export CSV" or "Export PDF"
4. File downloads automatically

**Example CSV Structure:**
```csv
id,object_id,class_name,confidence,latitude,longitude,altitude,timestamp
1,person_001,person,0.95,12.9716,77.5946,85.0,2025-11-05T14:23:45Z
2,car_002,car,0.87,12.9720,77.5950,85.5,2025-11-05T14:23:46Z
```

### 6.7 Replay Mode

**Features:**
- Playback historical events
- Variable speed (1x, 2x, 5x, 10x)
- Pause and resume
- Event highlighting
- Progress tracking

**Usage:**

1. Go to History view
2. Apply filters for desired events
3. Click "Replay Mode" button
4. Use playback controls:
   - ▶️ Play
   - ⏸️ Pause
   - ⏩ Speed up
   - ⏪ Slow down
   - ⏭️ Reset

**Replay Display:**
- Current event highlighted in purple
- Event counter (e.g., Event 5/50)
- Progress bar showing completion
- Time elapsed

---

## 7. API Reference

### 7.1 Video Streaming Endpoint

**GET /video_feed**

Returns MJPEG video stream with detections.

**Request:**
```http
GET http://localhost:5000/video_feed HTTP/1.1
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: multipart/x-mixed-replace; boundary=frame

--frame
Content-Type: image/jpeg

[JPEG image data]
--frame
Content-Type: image/jpeg

[JPEG image data]
...
```

**Usage in HTML:**
```html
<img src="http://localhost:5000/video_feed" alt="Live Feed" />
```

### 7.2 Detection Endpoints

**GET /detections**

Returns current active detections.

**Request:**
```http
GET http://localhost:5000/detections HTTP/1.1
```

**Response:**
```json
[
  {
    "id": 1,
    "object_id": "person_001",
    "class_name": "person",
    "confidence": 0.95,
    "bbox": [120, 80, 200, 350],
    "zone_status": "SAFE",
    "timestamp": "2025-11-05T14:23:45Z"
  },
  {
    "id": 2,
    "object_id": "car_002",
    "class_name": "car",
    "confidence": 0.87,
    "bbox": [450, 120, 180, 120],
    "zone_status": "BREACH",
    "zone_name": "Restricted Area Alpha",
    "timestamp": "2025-11-05T14:23:45Z"
  }
]
```

**GET /api/history/detections**

Returns historical detection data with pagination.

**Request:**
```http
GET http://localhost:5000/api/history/detections?
    start_time=2025-11-01T00:00:00&
    end_time=2025-11-05T23:59:59&
    class_name=person&
    limit=50&
    offset=0
```

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| start_time | ISO datetime | Start of time range | - |
| end_time | ISO datetime | End of time range | - |
| class_name | string | Filter by object class | - |
| object_id | string | Filter by object ID | - |
| search | string | Search query | - |
| limit | integer | Results per page | 50 |
| offset | integer | Pagination offset | 0 |

**Response:**
```json
{
  "detections": [...],
  "total": 700,
  "statistics": {
    "total_detections": 700,
    "unique_objects": 145,
    "most_common_class": "person",
    "by_class": {
      "person": 320,
      "car": 215,
      "truck": 165
    }
  },
  "page": {
    "limit": 50,
    "offset": 0
  }
}
```

### 7.3 Alert Endpoints

**GET /alerts**

Returns current active alerts (last 5 minutes).

**Request:**
```http
GET http://localhost:5000/alerts HTTP/1.1
```

**Response:**
```json
[
  {
    "id": 1,
    "type": "geofence_breach",
    "severity": "high",
    "title": "Restricted Area Breach",
    "message": "Person detected in Restricted Area Alpha",
    "zone": "Restricted Area Alpha",
    "object_id": "person_001",
    "timestamp": "2025-11-05T14:23:45Z",
    "new": true
  }
]
```

**GET /api/history/breaches**

Returns historical breach data.

**Request:**
```http
GET http://localhost:5000/api/history/breaches?
    zone_name=Restricted Area Alpha&
    threat_level=HIGH&
    resolved=false&
    limit=50&
    offset=0
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| start_time | ISO datetime | Start of time range |
| end_time | ISO datetime | End of time range |
| zone_name | string | Filter by zone |
| threat_level | string | HIGH, MEDIUM, or LOW |
| resolved | boolean | Filter by resolution status |
| limit | integer | Results per page |
| offset | integer | Pagination offset |

**Response:**
```json
{
  "breaches": [
    {
      "id": 1,
      "object_id": "person_001",
      "class_name": "person",
      "zone_name": "Restricted Area Alpha",
      "threat_level": "HIGH",
      "latitude": 12.9716,
      "longitude": 77.5946,
      "violations": ["unauthorized_entry"],
      "distance_to_center": 45.2,
      "resolved": false,
      "timestamp": "2025-11-05T14:23:45Z"
    }
  ],
  "total": 114,
  "statistics": {
    "total_breaches": 114,
    "resolved_count": 68,
    "unresolved_count": 46,
    "by_threat_level": {
      "HIGH": 14,
      "MEDIUM": 31,
      "LOW": 69
    }
  }
}
```

**POST /api/history/breaches/:id/resolve**

Mark a breach as resolved.

**Request:**
```http
POST http://localhost:5000/api/history/breaches/1/resolve HTTP/1.1
Content-Type: application/json

{
  "resolved_by": "operator_01",
  "notes": "Authorized personnel confirmed"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Breach resolved"
}
```

### 7.4 Analytics Endpoints

**GET /api/analytics**

Returns system analytics and statistics.

**Request:**
```http
GET http://localhost:5000/api/analytics?hours=24
```

**Response:**
```json
{
  "time_period_hours": 24,
  "total_detections": 700,
  "unique_objects": 145,
  "total_breaches": 114,
  "detection_by_class": {
    "person": 320,
    "car": 215,
    "truck": 165
  },
  "breach_by_zone": {
    "Restricted Area Alpha": 45,
    "Perimeter Zone Beta": 39,
    "No-Fly Zone Gamma": 30
  },
  "hourly_detections": [
    {"hour": 0, "count": 15},
    {"hour": 1, "count": 12},
    ...
  ]
}
```

**GET /api/heatmap**

Returns heatmap data for visualization.

**Request:**
```http
GET http://localhost:5000/api/heatmap?type=detections
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| type | string | "detections" or "breaches" |
| hours | integer | Time range in hours |

**Response:**
```json
{
  "type": "detections",
  "points": [
    {
      "lat": 12.9716,
      "lon": 77.5946,
      "intensity": 15
    },
    {
      "lat": 12.9720,
      "lon": 77.5950,
      "intensity": 8
    }
  ],
  "total_points": 700,
  "time_range_hours": 24
}
```

### 7.5 Export Endpoints

**GET /api/history/detections/export**

Export detection data as CSV or JSON.

**Request:**
```http
GET http://localhost:5000/api/history/detections/export?
    format=csv&
    start_time=2025-11-01T00:00:00&
    end_time=2025-11-05T23:59:59&
    class_name=person
```

**Response:**
```
Content-Type: text/csv
Content-Disposition: attachment; filename=detections_2025-11-01_to_2025-11-05.csv

id,object_id,class_name,confidence,latitude,longitude,altitude,timestamp
1,person_001,person,0.95,12.9716,77.5946,85.0,2025-11-05T14:23:45Z
...
```

**GET /api/reports/detections/pdf**

Generate PDF report.

**Request:**
```http
GET http://localhost:5000/api/reports/detections/pdf?
    start_time=2025-11-01T00:00:00&
    end_time=2025-11-05T23:59:59
```

**Response:**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename=detections_report_2025-11-05.pdf

[PDF binary data]
```

---

## 8. Configuration

### 8.1 Backend Configuration

All backend configuration is in `backend/config.py`.

**Video Source:**
```python
VIDEO_CONFIG = {
    "source": 0,                    # 0 = Webcam, or path to video file
    "resolution": (1280, 720),      # Camera resolution
    "fps": 30,                      # Target FPS
    "stream_quality": 85,           # JPEG quality (0-100)
}
```

**Model Configuration:**
```python
MODEL_CONFIG = {
    "model_path": "yolov8m.pt",     # Path to trained model
    "conf_threshold": 0.25,         # Confidence threshold (0-1)
    "iou_threshold": 0.45,          # IOU threshold for NMS
    "device": "cuda",               # "cuda" or "cpu"
}
```

**Tracking Configuration:**
```python
TRACKING_CONFIG = {
    "max_age": 30,                  # Frames to keep lost tracks
    "n_init": 3,                    # Frames to confirm track
    "max_iou_distance": 0.7,        # Maximum IOU distance
}
```

**Geofence Zones:**
```python
RESTRICTED_ZONES = [
    {
        "name": "Restricted Area Alpha",
        "polygon": [[100, 100], [500, 100], [500, 400], [100, 400]],
        "alert_classes": ["person", "vehicle"],
        "threat_level": "HIGH",
    },
    # Add more zones...
]
```

**Database Configuration:**
```python
DATABASE_CONFIG = {
    "path": "surveillance_data.db",  # SQLite database path
    "enabled": True,                 # Enable database logging
}
```

### 8.2 Frontend Configuration

Configuration is in `drone-surveillance-frontend/src/App.jsx`.

**API Base URL:**
```javascript
const API_BASE_URL = 'http://localhost:5000';
```

**Auto-refresh Interval:**
```javascript
// In App.jsx useEffect
const interval = setInterval(() => {
  fetchDetections();
  fetchAlerts();
}, 2000);  // 2 seconds
```

**Map Configuration:**

In `DroneMap.jsx`:
```javascript
const defaultCenter = [12.9716, 77.5946];  // Bangalore coordinates
const defaultZoom = 13;
```

### 8.3 Environment Variables

Create `.env` file in backend directory:

```bash
# backend/.env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# Database
DATABASE_PATH=surveillance_data.db

# Kaggle API (optional)
KAGGLE_USERNAME=your-username
KAGGLE_KEY=your-api-key

# Video Source
VIDEO_SOURCE=0

# Model
MODEL_PATH=yolov8m.pt
CONFIDENCE_THRESHOLD=0.25
```

Create `.env` file in frontend directory:

```bash
# drone-surveillance-frontend/.env
VITE_API_BASE_URL=http://localhost:5000
VITE_REFRESH_INTERVAL=2000
```

### 8.4 Performance Tuning

**For CPU-only Systems:**

```python
# backend/config.py
MODEL_CONFIG = {
    "model_path": "yolov8n.pt",     # Use nano model for speed
    "device": "cpu",
}

VIDEO_CONFIG = {
    "resolution": (640, 480),       # Lower resolution
    "fps": 15,                      # Reduce FPS
    "frame_skip": 2,                # Process every 2nd frame
}
```

**For GPU Systems:**

```python
MODEL_CONFIG = {
    "model_path": "yolov8m.pt",     # Or yolov8l/yolov8x
    "device": "cuda",
    "batch_size": 1,
}

VIDEO_CONFIG = {
    "resolution": (1920, 1080),     # Higher resolution
    "fps": 30,
    "frame_skip": 1,                # Process every frame
}
```

---

## 9. Troubleshooting

### 9.1 Common Issues

#### Issue: Backend won't start

**Error:** `ModuleNotFoundError: No module named 'ultralytics'`

**Solution:**
```bash
pip install -r requirements.txt
```

#### Issue: No video feed displayed

**Symptoms:** Black screen or "Loading..." message persists

**Solutions:**

1. **Check camera availability:**
```python
# Test camera
python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"
```

2. **Try different camera index:**
```python
# In backend/config.py
VIDEO_CONFIG = {"source": 1}  # or 2, 3...
```

3. **Check CORS:**
```bash
# Ensure Flask-CORS is installed
pip install flask-cors
```

4. **Browser console errors:**
- Open DevTools (F12)
- Check Console for errors
- Look for CORS or network errors

#### Issue: Low FPS / Slow performance

**CPU System:**
```python
# backend/config.py
MODEL_CONFIG = {
    "model_path": "yolov8n.pt",  # Smallest/fastest model
}

VIDEO_CONFIG = {
    "resolution": (640, 480),
    "fps": 10,
    "frame_skip": 3,  # Process every 3rd frame
}
```

**GPU Not Detected:**
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# If False, reinstall PyTorch with CUDA:
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

#### Issue: Out of Memory (GPU)

**Error:** `CUDA out of memory`

**Solution:**
```python
# Reduce image size
MODEL_CONFIG = {
    "image_size": 416,  # Down from 640
}

# Or use smaller model
MODEL_CONFIG = {
    "model_path": "yolov8n.pt",
}
```

#### Issue: Frontend won't connect to backend

**Symptoms:** "Failed to fetch" errors

**Solutions:**

1. **Check backend is running:**
```bash
curl http://localhost:5000/health
```

2. **Check firewall:**
- Allow port 5000 in Windows Firewall
- Or temporarily disable firewall

3. **CORS configuration:**
```python
# In backend/app.py
from flask_cors import CORS
CORS(app, origins=["http://localhost:3000"])
```

#### Issue: Database errors

**Error:** `sqlite3.OperationalError: database is locked`

**Solution:**
```bash
# Close all connections and restart
pkill -f "python app.py"
python app.py
```

### 9.2 Log Files

**Backend Logs:**
```bash
# Location: backend/logs/
tail -f backend/logs/app.log
```

**Check for errors:**
```bash
grep ERROR backend/logs/app.log
```

**Frontend Console:**
- Open browser DevTools (F12)
- Check Console tab for errors
- Check Network tab for failed requests

### 9.3 Performance Diagnostics

**Backend FPS:**
```bash
# Check terminal output for FPS counter
# Should show: "FPS: 25.3"
```

**GPU Utilization:**
```bash
# NVIDIA
nvidia-smi

# Should show VRAM usage and GPU utilization
```

**CPU Usage:**
```bash
# Windows
taskmgr

# Linux
htop
```

### 9.4 Reset and Clean Installation

**Full Reset:**

```bash
# 1. Delete virtual environment
rm -rf venv  # or: rmdir /s venv (Windows)

# 2. Delete node modules
rm -rf drone-surveillance-frontend/node_modules

# 3. Delete database
rm backend/surveillance_data.db

# 4. Delete model cache
rm -rf backend/models/*

# 5. Reinstall
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate (Windows)
pip install -r backend/requirements.txt
cd drone-surveillance-frontend
npm install
```

---

## 10. Best Practices

### 10.1 System Operation

**Daily Checklist:**
- [ ] Check system status (green indicator)
- [ ] Verify video feed is active
- [ ] Review overnight alerts
- [ ] Check detection counts are reasonable
- [ ] Verify database size (should grow steadily)

**Weekly Tasks:**
- [ ] Export weekly report (CSV/PDF)
- [ ] Review breach statistics
- [ ] Check disk space
- [ ] Backup database
- [ ] Update trained model if needed

**Monthly Tasks:**
- [ ] Full system backup
- [ ] Review and adjust geofence zones
- [ ] Analyze heatmaps for pattern changes
- [ ] Update software dependencies
- [ ] Performance optimization review

### 10.2 Geofence Configuration

**Best Practices:**

1. **Start with larger zones** - Easier to adjust inward than outward
2. **Test thoroughly** - Walk through zones with detection active
3. **Use appropriate threat levels** - Reserve HIGH for critical areas
4. **Document zone purposes** - Add descriptions in config
5. **Regular review** - Adjust based on actual breach patterns

**Zone Design Tips:**

```python
# Bad: Too small, too many false positives
{
    "polygon": [[100, 100], [110, 100], [110, 110], [100, 110]],  # 10x10 pixels
}

# Good: Reasonable size with buffer
{
    "polygon": [[50, 50], [300, 50], [300, 200], [50, 200]],  # 250x150 pixels
}
```

### 10.3 Alert Management

**Avoid Alert Fatigue:**

1. **Set appropriate thresholds** - Don't alert on minor events
2. **Use deduplication** - System already implements 30-second cooldown
3. **Regular review** - Mark false positives and adjust
4. **Prioritize** - Focus on HIGH severity alerts first
5. **Resolve promptly** - Mark resolved to clear alert queue

**Alert Response SOP:**

1. **Receive alert** → Note time and details
2. **Review video feed** → Verify actual breach
3. **Assess threat** → Is it legitimate concern?
4. **Take action** → Respond as needed
5. **Document** → Add notes to breach record
6. **Resolve** → Mark as resolved in system

### 10.4 Model Training

**When to Retrain:**

- Detection accuracy drops below 70%
- New object classes needed
- Significant environment changes
- False positive rate > 20%

**Training Tips:**

1. **Use sufficient data** - 1000+ images minimum
2. **Balance classes** - Equal representation if possible
3. **Augmentation** - Use built-in augmentation
4. **Validation** - Always validate on separate set
5. **Checkpoint** - Save best model, not last

**Training Command:**
```bash
cd backend
python train_model.py
```

### 10.5 Database Maintenance

**Backup Schedule:**

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
cp backend/surveillance_data.db backups/surveillance_$DATE.db

# Keep last 30 days
find backups/ -name "surveillance_*.db" -mtime +30 -delete
```

**Cleanup Old Data:**

```sql
-- Delete detections older than 90 days
DELETE FROM detections WHERE timestamp < datetime('now', '-90 days');

-- Delete resolved breaches older than 180 days
DELETE FROM breaches WHERE resolved = 1 AND resolved_at < datetime('now', '-180 days');

-- Vacuum to reclaim space
VACUUM;
```

### 10.6 Security Best Practices

**Authentication:**

1. **Change default passwords** immediately
2. **Use strong passwords** (12+ characters)
3. **Enable JWT tokens** for API access
4. **Regular password rotation** (every 90 days)

**Network Security:**

1. **Use HTTPS** in production
2. **Restrict API access** to known IPs
3. **Enable firewall** rules
4. **VPN for remote access**

**Data Privacy:**

1. **Blur faces** if required by policy
2. **Limit data retention** to necessary period
3. **Secure database** file permissions
4. **Encrypted backups** for sensitive data

---

## 11. FAQs

### General Questions

**Q: Can I use this without a GPU?**

A: Yes! The system works on CPU, but at reduced FPS (5-10 instead of 30+). Use YOLOv8n model for better CPU performance.

**Q: What cameras are supported?**

A: Any USB webcam, IP camera (RTSP), or video file. Just configure the source in `backend/config.py`.

**Q: Can I add custom object classes?**

A: Yes! Train YOLOv8 on your custom dataset using `train_model.py`. See TRAINING_GUIDE.md for details.

**Q: Does it work offline?**

A: Yes! After initial setup and training, the system runs completely offline. Internet is only needed for downloading datasets/models.

**Q: How many objects can it detect simultaneously?**

A: Up to 100 objects per frame, but tracking is optimized for 20-30 simultaneous tracks for best performance.

### Technical Questions

**Q: What's the detection latency?**

A: Approximately 30-50ms per frame on GPU, 200-500ms on CPU. End-to-end latency including display: 100-600ms.

**Q: Can I integrate this with other systems?**

A: Yes! The REST API allows integration. You can call the API endpoints from any system.

**Q: How accurate is the geofencing?**

A: Very accurate for 2D zones (pixel-perfect). For GPS-based 3D zones, accuracy depends on GPS precision (~5-10 meters).

**Q: Can I export data automatically?**

A: Yes! Use the API endpoints in a cron job or scheduled task:
```bash
# Daily export at midnight
0 0 * * * curl "http://localhost:5000/api/history/detections/export?format=csv" > /backups/detections_$(date +%Y%m%d).csv
```

**Q: What database is used?**

A: SQLite for simplicity. For production with high volume, migrate to PostgreSQL or MySQL.

### Performance Questions

**Q: My FPS is low, how to improve?**

A:
1. Use smaller model (YOLOv8n instead of YOLOv8m)
2. Reduce resolution (`VIDEO_CONFIG["resolution"]`)
3. Enable frame skipping (`VIDEO_CONFIG["frame_skip"]`)
4. Close other applications
5. Use GPU if available

**Q: How much disk space is needed?**

A:
- Base installation: ~2 GB
- Dataset: 5-20 GB
- Trained model: 50-200 MB
- Database (1 month): 500 MB - 2 GB
- **Total:** 10-30 GB recommended

**Q: How much RAM is needed?**

A:
- CPU inference: 4-8 GB
- GPU inference: 8-16 GB
- Training: 16-32 GB

### Deployment Questions

**Q: Can I deploy this to cloud?**

A: Yes! Deployable to AWS, Azure, GCP, or any cloud provider. See RENDER_DEPLOYMENT.md for guide.

**Q: Is Docker supported?**

A: Yes! Dockerfile is included. Build and run:
```bash
docker build -t drone-surveillance .
docker run -p 5000:5000 -p 3000:3000 drone-surveillance
```

**Q: Can multiple users access simultaneously?**

A: Yes! The web interface supports multiple concurrent users viewing the same feed.

**Q: How to run 24/7?**

A: Use a process manager like PM2 or systemd:
```bash
# PM2 example
pm2 start backend/app.py --name drone-backend
pm2 start "npm run dev" --name drone-frontend
pm2 save
pm2 startup
```

### Troubleshooting FAQs

**Q: "CUDA out of memory" error?**

A: Use smaller model, reduce batch size, or lower image resolution.

**Q: Video feed shows "Loading..." forever?**

A: Check backend logs, verify camera access, try different camera index.

**Q: Detections are inaccurate?**

A: Retrain model on your specific environment, or adjust confidence threshold.

**Q: System uses too much CPU?**

A: Enable frame skipping, use GPU, or reduce FPS.

**Q: How to add more zones?**

A: Edit `backend/config.py` RESTRICTED_ZONES array, restart backend.

---

## Appendix A: Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + R` | Refresh dashboard |
| `Ctrl + E` | Export current view |
| `Space` | Pause/Resume video feed |
| `Ctrl + F` | Open search/filter |
| `Esc` | Close modals/overlays |
| `Ctrl + S` | Open settings |

---

## Appendix B: System Specifications

### Supported Operating Systems

| OS | Version | Status |
|----|---------|--------|
| Windows | 10, 11 | ✅ Tested |
| Ubuntu | 20.04, 22.04 | ✅ Tested |
| macOS | 11+ (Big Sur+) | ✅ Compatible |
| Raspberry Pi OS | Bullseye | ⚠️ Limited (CPU only) |

### Browser Compatibility

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 90+ | ✅ Recommended |
| Edge | 90+ | ✅ Supported |
| Firefox | 88+ | ✅ Supported |
| Safari | 14+ | ✅ Supported |

---

## Appendix C: File Locations

| Item | Location |
|------|----------|
| Backend code | `backend/` |
| Frontend code | `drone-surveillance-frontend/` |
| Configuration | `backend/config.py` |
| Database | `backend/surveillance_data.db` |
| Trained models | `backend/models/` |
| Logs | `backend/logs/` |
| Datasets | `backend/data/` |
| Checkpoints | `backend/checkpoints/` |

---

## Appendix D: Default Credentials

**Admin Account:**
- Username: `admin`
- Password: `admin123`
- Role: Administrator

**Operator Account:**
- Username: `operator`
- Password: `operator123`
- Role: Operator

**⚠️ IMPORTANT: Change these passwords immediately in production!**

---

## Appendix E: Support & Contact

**Documentation:**
- User Manual: `USER_MANUAL.md` (this file)
- Architecture: `ARCHITECTURE.md`
- Training Guide: `TRAINING_GUIDE.md`
- API Reference: See Section 7

**Community:**
- GitHub Issues: Report bugs and feature requests
- Discussions: Community support and questions

**Commercial Support:**
- Contact: HAL Defense AI Division
- Email: support@example.com

---

## Appendix F: Version History

### Version 1.0.0 (November 2025)
- ✅ Initial production release
- ✅ YOLOv8 + DeepSORT integration
- ✅ Real-time detection and tracking
- ✅ Geofence monitoring
- ✅ React dashboard
- ✅ Historical analysis
- ✅ Export functionality

---

**© HAL Defense AI Division 2025**

**License:** Proprietary

**Documentation Version:** 1.0.0

**Last Updated:** November 5, 2025

---

**END OF USER MANUAL**

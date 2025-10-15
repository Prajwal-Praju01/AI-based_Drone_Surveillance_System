# 📊 Project Architecture & Data Flow

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AI Drone Surveillance System                      │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────────┐         ┌──────────────────────────┐
│   VIDEO INPUT SOURCE     │         │    KAGGLE DATASETS       │
│                          │         │                          │
│  • Webcam (0, 1, 2...)  │         │  • Drone Detection       │
│  • Video File (.mp4)    │         │  • Aerial Imagery        │
│  • RTSP Stream          │         │  • Human Detection       │
│  • Drone Feed           │         │                          │
└──────────┬───────────────┘         └─────────┬────────────────┘
           │                                   │
           │                                   │ Download & Prepare
           │                                   ↓
           │                         ┌─────────────────────────┐
           │                         │  DATA PREPARATION       │
           │                         │  (data_preparation.py)  │
           │                         │                         │
           │                         │  • Download from Kaggle │
           │                         │  • Convert to YOLO     │
           │                         │  • Train/Val Split     │
           │                         │  • Generate data.yaml  │
           │                         └─────────┬───────────────┘
           │                                   │
           │                                   │ Prepared Dataset
           │                                   ↓
           │                         ┌─────────────────────────┐
           │                         │   MODEL TRAINING        │
           │                         │   (train_model.py)      │
           │                         │                         │
           │                         │  • Load YOLOv8         │
           │                         │  • Train on Dataset    │
           │                         │  • Validate & Export   │
           │                         │                         │
           │                         │  ┌──────────────────┐  │
           │                         │  │ YOLOv8n (3.2M)  │  │
           │                         │  │ YOLOv8s (11M)   │  │
           │                         │  │ YOLOv8m (26M)⭐ │  │
           │                         │  │ YOLOv8l (44M)   │  │
           │                         │  │ YOLOv8x (68M)   │  │
           │                         │  └──────────────────┘  │
           │                         └─────────┬───────────────┘
           │                                   │
           │                                   │ Trained Model
           ↓                                   ↓
┌──────────────────────────────────────────────────────────────┐
│                    INFERENCE ENGINE                           │
│                    (inference.py)                             │
│                                                               │
│  ┌─────────────────┐      ┌──────────────┐                  │
│  │  YOLOv8 Model   │─────→│  Detection   │                  │
│  │  • Load weights │      │  • Bounding  │                  │
│  │  • Process frame│      │  • Classes   │                  │
│  │  • Get detections│     │  • Confidence│                  │
│  └─────────────────┘      └──────┬───────┘                  │
│                                   │                           │
│                                   ↓                           │
│  ┌─────────────────────────────────────────┐                │
│  │         DeepSORT Tracker                 │                │
│  │  • Track objects across frames          │                │
│  │  • Assign unique IDs                    │                │
│  │  • Handle occlusions                    │                │
│  └─────────────────┬───────────────────────┘                │
│                    │                                          │
│                    ↓                                          │
│  ┌─────────────────────────────────────────┐                │
│  │      Zone Breach Detection               │                │
│  │  • Check restricted zones                │                │
│  │  • Generate alerts                       │                │
│  │  • Log violations                        │                │
│  └─────────────────┬───────────────────────┘                │
└────────────────────┼─────────────────────────────────────────┘
                     │
                     │ Real-time Data
                     ↓
┌──────────────────────────────────────────────────────────────┐
│                    FLASK REST API                             │
│                    (app.py)                                   │
│                                                               │
│  Endpoints:                                                   │
│  • GET /video_feed    → MJPEG stream                         │
│  • GET /detections    → JSON detection data                  │
│  • GET /alerts        → JSON alerts                          │
│  • GET /stats         → System statistics                    │
│  • GET /health        → Health check                         │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        │ HTTP/REST
                        │
                        ↓
┌──────────────────────────────────────────────────────────────┐
│              REACT FRONTEND (Port 3000)                       │
│              (drone-surveillance-frontend/)                   │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                    HEADER                               │  │
│  │  [Logo] AI Drone Surveillance  [Status: ●] [Alerts: 3] │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────┐  ┌───────────────────────────────────────┐    │
│  │ SIDEBAR  │  │         MAIN CONTENT                   │    │
│  │          │  │                                        │    │
│  │ Dashboard│  │  ┌─────────────────────────────────┐  │    │
│  │ Live Feed│  │  │      VIDEO FEED COMPONENT       │  │    │
│  │ Alerts   │  │  │  • Live MJPEG stream            │  │    │
│  │ Settings │  │  │  • Bounding boxes               │  │    │
│  │          │  │  │  • Object IDs                   │  │    │
│  │ [Stats]  │  │  └─────────────────────────────────┘  │    │
│  │          │  │                                        │    │
│  │          │  │  ┌─────────────────────────────────┐  │    │
│  └──────────┘  │  │   DETECTION TABLE COMPONENT     │  │    │
│                │  │  ID | Class | Conf | Zone       │  │    │
│                │  │  ──────────────────────────────  │  │    │
│                │  │  1  | person| 95%  | BREACH ⚠️   │  │    │
│                │  │  2  | car   | 87%  | SAFE ✓     │  │    │
│                │  └─────────────────────────────────┘  │    │
│                │                                        │    │
│                │  ┌─────────────────────────────────┐  │    │
│                │  │    ALERT PANEL COMPONENT        │  │    │
│                │  │  🚨 Zone A Breach Detected      │  │    │
│                │  │  🚨 Unauthorized Person - Zone B│  │    │
│                │  └─────────────────────────────────┘  │    │
│                └────────────────────────────────────────┘    │
│                                                               │
│  └────────────────────────────────────────────────────────┘  │
│  │              FOOTER                                     │  │
│  │  © HAL Defense AI Division 2025                        │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌──────────┐
│  Camera  │
└────┬─────┘
     │ Video Frames (30 FPS)
     ↓
┌─────────────────┐
│  Inference      │
│  • YOLOv8       │──→ Detections [bbox, class, conf]
│  • 30-50ms/frame│
└────┬────────────┘
     │
     ↓
┌─────────────────┐
│  DeepSORT       │──→ Tracked Objects [id, bbox, class]
│  • ID Assignment│
└────┬────────────┘
     │
     ↓
┌─────────────────┐
│ Zone Checker    │──→ Alerts [zone, object, timestamp]
└────┬────────────┘
     │
     ├──→ /video_feed  (MJPEG Stream)
     ├──→ /detections  (JSON every 2s)
     └──→ /alerts      (JSON events)
          │
          ↓
     ┌─────────────┐
     │  Frontend   │
     │  React App  │──→ User Interface
     └─────────────┘
```

## File Structure

```
AI-based_Drone_Surveillance_System/
│
├── 📁 backend/                          # Python Backend
│   │
│   ├── 📄 config.py                     # Configuration (datasets, models, zones)
│   ├── 📄 data_preparation.py          # Download & prepare Kaggle datasets
│   ├── 📄 train_model.py               # Train YOLOv8 model
│   ├── 📄 inference.py                 # Real-time detection & tracking
│   ├── 📄 app.py                       # Flask REST API server
│   ├── 📄 setup_and_train.py          # Interactive setup script
│   ├── 📄 requirements.txt             # Python dependencies
│   │
│   ├── 📁 data/                        # Dataset storage
│   │   ├── 📁 raw/                     # Downloaded datasets
│   │   └── 📁 yolo_format/            # Prepared YOLO format
│   │
│   ├── 📁 models/                      # Trained model weights
│   │   └── 📁 drone_surveillance_*/   # Training run outputs
│   │       ├── 📁 weights/
│   │       │   ├── best.pt            # Best model checkpoint
│   │       │   └── last.pt            # Last epoch checkpoint
│   │       ├── results.png            # Training curves
│   │       └── confusion_matrix.png   # Confusion matrix
│   │
│   ├── 📁 checkpoints/                # Training checkpoints
│   └── 📁 logs/                       # Training logs
│
├── 📁 drone-surveillance-frontend/    # React Frontend
│   │
│   ├── 📁 src/
│   │   ├── 📁 components/
│   │   │   ├── Header.jsx             # Top navigation bar
│   │   │   ├── Sidebar.jsx            # Side navigation menu
│   │   │   ├── VideoFeed.jsx          # Live video display
│   │   │   ├── DetectionTable.jsx     # Detection data table
│   │   │   └── AlertPanel.jsx         # Alert notifications
│   │   │
│   │   ├── App.jsx                    # Main application
│   │   ├── main.jsx                   # React entry point
│   │   └── index.css                  # Tailwind + custom styles
│   │
│   ├── package.json                   # Node dependencies
│   ├── vite.config.js                 # Vite build config
│   └── tailwind.config.js             # Tailwind theme config
│
├── 📄 README.md                        # Main documentation
├── 📄 TRAINING_GUIDE.md               # Complete training guide
├── 📄 ARCHITECTURE.md                 # This file
├── 📄 quick_start.bat                 # Windows quick setup
└── 📄 start_servers.bat               # Start both servers
```

## Component Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                       PYTHON BACKEND                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ultralytics (YOLOv8)  ─────────┐                          │
│  torch, torchvision            │                           │
│  opencv-python                 ├──→  inference.py          │
│  deep-sort-realtime            │                           │
│  numpy, scipy                  │                           │
│                                │                           │
│  flask, flask-cors      ───────┼──→  app.py               │
│                                │                           │
│  kaggle                 ───────┴──→  data_preparation.py  │
│  pandas, pyyaml                                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     REACT FRONTEND                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  react, react-dom       ───────┐                           │
│                                ├──→  All Components         │
│  axios                  ───────┤     (API calls)            │
│                                │                           │
│  lucide-react          ────────┘     (Icons)               │
│                                                              │
│  tailwindcss           ───────────→  Styling               │
│  postcss, autoprefixer                                      │
│                                                              │
│  vite                  ───────────→  Build & Dev Server    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Training Pipeline

```
┌──────────────┐
│ Raw Dataset  │
│ (Kaggle)     │
└──────┬───────┘
       │
       ↓
┌──────────────────────────────┐
│  Data Preprocessing          │
│  • Download from Kaggle      │
│  • Extract annotations       │
│  • Convert to YOLO format    │
│  • Normalize coordinates     │
│  • Train/Val/Test split      │
│  • Create data.yaml          │
└──────┬───────────────────────┘
       │
       ↓
┌──────────────────────────────┐
│  Model Initialization        │
│  • Load pretrained YOLOv8    │
│  • Set hyperparameters       │
│  • Configure augmentation    │
└──────┬───────────────────────┘
       │
       ↓
┌──────────────────────────────┐
│  Training Loop (100 epochs)  │
│  ┌─────────────────────────┐ │
│  │ Epoch 1                 │ │
│  │ • Forward pass          │ │
│  │ • Calculate loss        │ │
│  │ • Backward pass         │ │
│  │ • Update weights        │ │
│  │ • Validate              │ │
│  └─────────────────────────┘ │
│  ...                         │
│  ┌─────────────────────────┐ │
│  │ Epoch 100               │ │
│  └─────────────────────────┘ │
└──────┬───────────────────────┘
       │
       ↓
┌──────────────────────────────┐
│  Model Evaluation            │
│  • Calculate mAP             │
│  • Precision/Recall          │
│  • Confusion Matrix          │
│  • Per-class metrics         │
└──────┬───────────────────────┘
       │
       ↓
┌──────────────────────────────┐
│  Model Export                │
│  • Save best.pt              │
│  • Export to ONNX            │
│  • Optimize for inference    │
└──────┬───────────────────────┘
       │
       ↓
┌──────────────┐
│ Deployed     │
│ Model        │
└──────────────┘
```

## Real-time Inference Pipeline

```
Video Frame (1280x720 RGB)
        ↓
┌───────────────────┐
│ Preprocessing     │
│ • Resize to 640   │
│ • Normalize       │
│ • BGR → RGB       │
└────────┬──────────┘
         ↓
┌───────────────────┐
│ YOLOv8 Inference  │
│ • Forward pass    │
│ • NMS filtering   │
│ • ~30-50ms        │
└────────┬──────────┘
         ↓
[Detections: N objects]
[bbox, class, conf]
         ↓
┌───────────────────┐
│ DeepSORT Tracker  │
│ • Match to tracks │
│ • Update Kalman   │
│ • Assign IDs      │
└────────┬──────────┘
         ↓
[Tracked Objects: N objects]
[id, bbox, class, conf]
         ↓
┌───────────────────┐
│ Zone Checker      │
│ • Check polygon   │
│ • Generate alerts │
└────────┬──────────┘
         ↓
┌───────────────────┐
│ Visualization     │
│ • Draw boxes      │
│ • Draw labels     │
│ • Draw zones      │
└────────┬──────────┘
         ↓
Annotated Frame
         ↓
[Encode to JPEG]
         ↓
Stream to Frontend
```

## API Request Flow

```
┌─────────────┐
│  Browser    │
│  (React)    │
└──────┬──────┘
       │
       │ HTTP GET /video_feed
       ├────────────────────────────→ Flask Server
       │                              • generate_frames()
       │                              • Process frame
       │                              • Encode JPEG
       │ ←──────────────────────────  MJPEG Stream
       │
       │ HTTP GET /detections (every 2s)
       ├────────────────────────────→ Flask Server
       │                              • get_current_detections()
       │ ←──────────────────────────  JSON Array
       │
       │ HTTP GET /alerts (every 2s)
       ├────────────────────────────→ Flask Server
       │                              • get_alerts()
       │ ←──────────────────────────  JSON Array
       │
       ↓
  Update UI
```

## Performance Metrics

### Latency Breakdown (YOLOv8m on RTX 3060)

```
Total Frame Processing Time: ~50ms (20 FPS)

┌────────────────────────────────────────────┐
│ Preprocessing        │ 2ms    │ ████       │
│ YOLOv8 Inference     │ 30ms   │ ████████████████████
│ DeepSORT Tracking    │ 8ms    │ ██████
│ Zone Checking        │ 5ms    │ ████
│ Visualization        │ 5ms    │ ████
└────────────────────────────────────────────┘
```

### Training Progress (100 epochs, YOLOv8m)

```
Epoch:  [██████████████████████████████████████] 100/100

Metrics Evolution:
mAP50     ░░░░░░░░▓▓▓▓▓▓▓███████████  0.52
Precision ░░░░░░░░▓▓▓▓▓▓▓███████████  0.71
Recall    ░░░░░░░░▓▓▓▓▓▓▓███████████  0.68
Loss      ████████▓▓▓▓▓▓▓░░░░░░░░░░  0.8

Training Time: 5h 23m
Final mAP50-95: 0.502
```

---

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Detection Model** | YOLOv8 (Ultralytics) | Object detection |
| **Tracking** | DeepSORT | Multi-object tracking |
| **Deep Learning** | PyTorch | Model training/inference |
| **Computer Vision** | OpenCV | Image processing |
| **Backend API** | Flask | REST API server |
| **Frontend Framework** | React 18 | User interface |
| **Styling** | Tailwind CSS | UI design |
| **Build Tool** | Vite | Fast dev server |
| **HTTP Client** | Axios | API requests |
| **Icons** | Lucide React | UI icons |
| **Data Source** | Kaggle API | Dataset download |

---

## Performance Requirements

### Minimum System
- **Inference**: 5-10 FPS on CPU
- **Training**: Not recommended

### Recommended System
- **Inference**: 30+ FPS on RTX 3060
- **Training**: 5 hours for 100 epochs

### High-End System
- **Inference**: 60+ FPS on RTX 4090
- **Training**: 2-3 hours for 100 epochs

---

© HAL Defense AI Division 2025

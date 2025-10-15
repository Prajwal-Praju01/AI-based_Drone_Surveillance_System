# 🚁 AI-Based Drone Surveillance System - Backend

Complete Python backend with YOLOv8 + DeepSORT for real-time object detection and tracking.

## 🎯 Features

- **YOLOv8 Object Detection**: State-of-the-art real-time detection
- **DeepSORT Tracking**: Multi-object tracking with ID persistence
- **Kaggle Dataset Integration**: Automatic dataset download and preparation
- **Custom Training Pipeline**: Optimized hyperparameters for drone surveillance
- **Restricted Zone Monitoring**: Alert system for zone breaches
- **Flask REST API**: Serves video feed and detection data to frontend
- **Real-time Performance**: Optimized for live video streaming

## 📁 Project Structure

```
backend/
├── config.py              # Configuration (datasets, models, zones)
├── data_preparation.py    # Download & prepare Kaggle datasets
├── train_model.py         # Train YOLOv8 with optimized hyperparameters
├── inference.py           # Real-time detection and tracking
├── app.py                 # Flask server for frontend integration
├── requirements.txt       # Python dependencies
├── data/                  # Dataset storage
├── models/                # Trained model weights
├── checkpoints/           # Training checkpoints
└── logs/                  # Training logs
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Setup Kaggle API (for dataset download)

1. Create Kaggle account at https://www.kaggle.com
2. Go to Account Settings → API → Create New Token
3. Download `kaggle.json`
4. Place it in:
   - **Windows**: `C:\Users\<Username>\.kaggle\kaggle.json`
   - **Linux/Mac**: `~/.kaggle/kaggle.json`

### 3. Download & Prepare Dataset

```bash
python data_preparation.py
```

This will:
- Download drone detection dataset from Kaggle
- Convert to YOLO format
- Create train/val splits
- Generate `data.yaml` for training

### 4. Train the Model

```bash
python train_model.py
```

**Training Options:**

```python
# In train_model.py, choose model variant:
model_name = "yolov8n"  # Fastest, lowest accuracy
model_name = "yolov8s"  # Fast, good accuracy
model_name = "yolov8m"  # ⭐ RECOMMENDED - Best balance
model_name = "yolov8l"  # High accuracy, slower
model_name = "yolov8x"  # Highest accuracy, slowest
```

**Expected Training Time:**
- YOLOv8n: ~2-3 hours (100 epochs, RTX 3060)
- YOLOv8m: ~5-6 hours (100 epochs, RTX 3060)
- CPU only: 10-20x slower

### 5. Run Flask Server

```bash
python app.py
```

Server will start on `http://localhost:5000`

**API Endpoints:**
- `GET /video_feed` - MJPEG video stream
- `GET /detections` - Current detections (JSON)
- `GET /alerts` - Active alerts (JSON)
- `GET /stats` - System statistics (JSON)

### 6. Test Inference Standalone (Optional)

```bash
python inference.py
```

This opens OpenCV window with real-time detection.

## 🎓 Model Comparison

| Model | Params | FLOPs | Speed (ms) | mAP50-95 | Use Case |
|-------|--------|-------|------------|----------|----------|
| YOLOv8n | 3.2M | 8.7B | 1.2 | 37.3 | Edge devices, real-time |
| YOLOv8s | 11.2M | 28.6B | 2.1 | 44.9 | Good balance |
| **YOLOv8m** | **25.9M** | **78.9B** | **4.5** | **50.2** | **⭐ Recommended** |
| YOLOv8l | 43.7M | 165.2B | 7.8 | 52.9 | High accuracy |
| YOLOv8x | 68.2M | 257.8B | 12.1 | 53.9 | Maximum accuracy |

**Recommendation**: Use **YOLOv8m** for best accuracy/speed trade-off in drone surveillance.

## 📊 Training Configuration

### Optimized Hyperparameters

```python
# Optimizer
optimizer: AdamW
lr0: 0.001          # Initial learning rate
lrf: 0.01           # Final learning rate
momentum: 0.937
weight_decay: 0.0005

# Training
epochs: 100
batch_size: 16      # Adjust based on GPU memory
image_size: 640
patience: 50        # Early stopping

# Data Augmentation
mosaic: 1.0
mixup: 0.0
hsv_h: 0.015
hsv_s: 0.7
hsv_v: 0.4
fliplr: 0.5
```

### GPU Requirements

| Model | Min VRAM | Recommended VRAM | Batch Size |
|-------|----------|------------------|------------|
| YOLOv8n | 2GB | 4GB | 32 |
| YOLOv8s | 4GB | 6GB | 16 |
| YOLOv8m | 6GB | 8GB | 16 |
| YOLOv8l | 8GB | 12GB | 8 |
| YOLOv8x | 12GB | 16GB | 4 |

## 🎯 Kaggle Datasets

### Available Datasets

1. **Drone Detection Dataset**
   - Dataset: `dasmehdixtr/drone-dataset-uav`
   - Classes: Drones, people, vehicles
   - Images: 10,000+

2. **Semantic Drone Dataset**
   - Dataset: `bulentsiyah/semantic-drone-dataset`
   - Aerial imagery with annotations
   - Images: 400+ high-res

3. **Human Detection Dataset**
   - Dataset: `constantinwerner/human-detection-dataset`
   - Person detection from various angles
   - Images: 15,000+

### Adding Custom Dataset

Edit `config.py`:

```python
KAGGLE_DATASETS = {
    "my_dataset": "username/dataset-name",
}
```

Then run:

```bash
python data_preparation.py
```

## 🔧 Configuration

### Video Source

Edit `config.py`:

```python
VIDEO_CONFIG = {
    "source": 0,                    # Webcam
    # "source": "video.mp4",        # Video file
    # "source": "rtsp://...",       # RTSP stream
}
```

### Restricted Zones

Define zones in `config.py`:

```python
RESTRICTED_ZONES = [
    {
        "name": "Zone A",
        "polygon": [[100, 100], [500, 100], [500, 400], [100, 400]],
        "alert_classes": ["person", "vehicle"],
    },
]
```

### Detection Thresholds

```python
MODEL_CONFIG = {
    "conf_threshold": 0.25,  # Confidence threshold
    "iou_threshold": 0.45,   # IOU threshold for NMS
}
```

## 📈 Training Results

After training, check:

```
backend/models/drone_surveillance_<timestamp>/
├── weights/
│   ├── best.pt          # Best model checkpoint
│   └── last.pt          # Last epoch checkpoint
├── results.png          # Training curves
├── confusion_matrix.png # Confusion matrix
├── F1_curve.png        # F1 score curve
└── PR_curve.png        # Precision-Recall curve
```

## 🐛 Troubleshooting

### CUDA Out of Memory

```bash
# Reduce batch size in train_model.py
batch_size = 8  # or 4
```

### No Kaggle Datasets Found

```bash
# Manually place dataset in:
backend/data/raw/drone_detection/
```

### Video Feed Not Working

```python
# In config.py, change video source:
VIDEO_CONFIG = {
    "source": 0,  # Try different camera index (0, 1, 2)
}
```

### Slow Training

```bash
# Use smaller model
model_name = "yolov8n"

# Reduce image size
image_size = 416  # instead of 640

# Use fewer epochs
epochs = 50
```

## 📊 Performance Metrics

After training, evaluate:

```python
from train_model import DroneModelTrainer

trainer = DroneModelTrainer()
metrics = trainer.validate(model_path="models/.../best.pt")

print(f"mAP50: {metrics.box.map50:.4f}")
print(f"mAP50-95: {metrics.box.map:.4f}")
print(f"Precision: {metrics.box.mp:.4f}")
print(f"Recall: {metrics.box.mr:.4f}")
```

## 🚀 Production Deployment

### Export to ONNX

```python
from train_model import DroneModelTrainer

trainer = DroneModelTrainer()
trainer.export_model(
    model_path="models/.../best.pt",
    format="onnx"
)
```

### Deploy on Edge Device

```bash
# Use YOLOv8n for edge devices
# Export to TensorRT for NVIDIA Jetson
trainer.export_model(format="engine")  # TensorRT
```

## 📝 API Documentation

### GET /video_feed

Returns MJPEG stream with bounding boxes and tracking IDs.

### GET /detections

Returns JSON:
```json
[
  {
    "object_id": 1,
    "class_name": "person",
    "confidence": 0.95,
    "bbox": [100, 200, 300, 400],
    "zone_status": "SAFE",
    "timestamp": "2025-10-06T10:30:45"
  }
]
```

### GET /alerts

Returns JSON:
```json
[
  {
    "id": 1,
    "title": "Zone A Breach",
    "message": "Person detected in restricted Zone A",
    "severity": "high",
    "zone": "Zone A",
    "object_class": "person",
    "timestamp": "2025-10-06T10:30:45"
  }
]
```

## 🤝 Integration with Frontend

The Flask backend automatically serves data to the React frontend:

1. Start backend: `python app.py`
2. Start frontend: `npm run dev` (in frontend directory)
3. Frontend connects to `http://localhost:5000`

## 📄 License

© HAL Defense AI Division 2025

## 🆘 Support

For issues or questions:
1. Check logs in `backend/logs/`
2. Review training results in `backend/models/`
3. Test inference with `python inference.py`

---

**Built with ❤️ using YOLOv8 + DeepSORT**

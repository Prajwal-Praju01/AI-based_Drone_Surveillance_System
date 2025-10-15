# 🎓 Complete Training Guide
## AI-Based Drone Surveillance System

This guide walks you through training your own YOLOv8 model on real Kaggle datasets for drone surveillance.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Requirements](#system-requirements)
3. [Setup Steps](#setup-steps)
4. [Dataset Preparation](#dataset-preparation)
5. [Model Training](#model-training)
6. [Evaluation & Testing](#evaluation--testing)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- ✅ Python 3.8+ (Download: https://www.python.org/downloads/)
- ✅ Node.js 18+ (Download: https://nodejs.org/)
- ✅ Git (Download: https://git-scm.com/)
- ✅ CUDA Toolkit 11.8+ (For GPU: https://developer.nvidia.com/cuda-downloads)

### Kaggle Account
1. Create account at https://www.kaggle.com
2. Go to Settings → API → Create New Token
3. Download `kaggle.json`
4. Place in:
   - **Windows**: `C:\Users\<YourUsername>\.kaggle\kaggle.json`
   - **Linux/Mac**: `~/.kaggle/kaggle.json`

---

## System Requirements

### Minimum Requirements
- **CPU**: 4+ cores
- **RAM**: 16GB
- **Storage**: 50GB free space
- **GPU**: Optional (NVIDIA with 6GB+ VRAM)

### Recommended Requirements
- **CPU**: 8+ cores (Intel i7/AMD Ryzen 7)
- **RAM**: 32GB
- **Storage**: 100GB SSD
- **GPU**: NVIDIA RTX 3060 (12GB) or better

### Expected Training Times

| Hardware | YOLOv8n | YOLOv8s | YOLOv8m | YOLOv8l | YOLOv8x |
|----------|---------|---------|---------|---------|---------|
| RTX 4090 | 1h | 1.5h | 2.5h | 4h | 6h |
| RTX 3060 | 2h | 3h | 5h | 8h | 12h |
| CPU Only | 20h | 30h | 50h | 80h | 120h |

---

## Setup Steps

### Step 1: Clone/Download Project

```bash
# If using Git
git clone <repository-url>
cd AI-based_Drone_Surveillance_System

# Or download and extract ZIP file
```

### Step 2: Quick Installation

**Option A: Automated (Recommended)**
```bash
# Windows
quick_start.bat

# Linux/Mac
chmod +x quick_start.sh
./quick_start.sh
```

**Option B: Manual Installation**
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../drone-surveillance-frontend
npm install
```

---

## Dataset Preparation

### Option 1: Automated Download (Recommended)

```bash
cd backend
python data_preparation.py
```

This will:
1. ✅ Connect to Kaggle API
2. ✅ Download drone detection dataset (10,000+ images)
3. ✅ Convert to YOLO format
4. ✅ Create train/val splits (80/20)
5. ✅ Generate `data.yaml` configuration

### Option 2: Manual Dataset

If you have your own dataset:

1. **Organize your data:**
```
backend/data/raw/my_dataset/
├── images/
│   ├── img001.jpg
│   ├── img002.jpg
│   └── ...
└── labels/
    ├── img001.txt
    ├── img002.txt
    └── ...
```

2. **Label format (YOLO):**
```
# Each line: class_id center_x center_y width height (normalized 0-1)
0 0.5 0.5 0.3 0.4
1 0.7 0.3 0.2 0.2
```

3. **Run preparation:**
```bash
python data_preparation.py
```

### Kaggle Datasets Available

1. **Drone Detection Dataset** ⭐ Recommended
   - ID: `dasmehdixtr/drone-dataset-uav`
   - Size: ~2GB
   - Images: 10,000+
   - Classes: person, vehicle, bicycle, drone

2. **Semantic Drone Dataset**
   - ID: `bulentsiyah/semantic-drone-dataset`
   - Size: ~400MB
   - Images: 400 (high resolution)
   - Classes: Multiple aerial objects

3. **Human Detection Dataset**
   - ID: `constantinwerner/human-detection-dataset`
   - Size: ~3GB
   - Images: 15,000+
   - Classes: person (various poses/angles)

---

## Model Training

### Method 1: Interactive Training (Recommended)

```bash
cd backend
python setup_and_train.py
```

This interactive script will:
1. ✅ Check GPU availability
2. ✅ Guide you through model selection
3. ✅ Configure training parameters
4. ✅ Train and validate model
5. ✅ Export to ONNX format

### Method 2: Direct Training

```bash
cd backend
python train_model.py
```

**Customize in `train_model.py`:**
```python
# Line 200+
model_name = "yolov8m"  # Choose: yolov8n, yolov8s, yolov8m, yolov8l, yolov8x

trainer = DroneModelTrainer(model_name=model_name)
trainer.train(
    epochs=100,      # More epochs = better accuracy (diminishing returns after 100)
    batch_size=16,   # Reduce if GPU memory error
    img_size=640     # Larger = better accuracy but slower
)
```

### Model Selection Guide

**YOLOv8n** - Nano
- ⚡ Speed: 1.2ms per frame
- 🎯 mAP: 37.3%
- 💾 Size: 6MB
- ✅ Best for: Edge devices, Raspberry Pi, real-time on CPU

**YOLOv8s** - Small
- ⚡ Speed: 2.1ms per frame
- 🎯 mAP: 44.9%
- 💾 Size: 22MB
- ✅ Best for: Balanced performance, general use

**YOLOv8m** - Medium ⭐ **RECOMMENDED**
- ⚡ Speed: 4.5ms per frame
- 🎯 mAP: 50.2%
- 💾 Size: 52MB
- ✅ Best for: Drone surveillance (optimal accuracy/speed)

**YOLOv8l** - Large
- ⚡ Speed: 7.8ms per frame
- 🎯 mAP: 52.9%
- 💾 Size: 87MB
- ✅ Best for: High accuracy requirements

**YOLOv8x** - Extra Large
- ⚡ Speed: 12.1ms per frame
- 🎯 mAP: 53.9%
- 💾 Size: 136MB
- ✅ Best for: Maximum accuracy, offline processing

### Training Configuration

**Optimal Hyperparameters (pre-configured in `config.py`):**

```python
TRAIN_CONFIG = {
    # Optimizer
    "optimizer": "AdamW",        # Best for computer vision
    "lr0": 0.001,                # Initial learning rate
    "lrf": 0.01,                 # Final learning rate
    "momentum": 0.937,           # SGD momentum
    "weight_decay": 0.0005,      # L2 regularization
    
    # Training
    "warmup_epochs": 3,          # Warmup period
    "patience": 50,              # Early stopping patience
    
    # Data Augmentation
    "mosaic": 1.0,               # Mosaic augmentation
    "mixup": 0.0,                # Mixup augmentation
    "hsv_h": 0.015,              # Hue augmentation
    "hsv_s": 0.7,                # Saturation
    "hsv_v": 0.4,                # Value
    "fliplr": 0.5,               # Horizontal flip
    "scale": 0.5,                # Scale augmentation
    "translate": 0.1,            # Translation
}
```

### Monitoring Training

Training progress is saved in `backend/models/drone_surveillance_<timestamp>/`

**Check progress:**
1. **Console output**: Real-time metrics
2. **results.png**: Training curves (loss, mAP, precision, recall)
3. **confusion_matrix.png**: Class prediction accuracy
4. **TensorBoard**: `tensorboard --logdir=backend/models/`

**Key metrics to watch:**
- **mAP50**: Should reach 0.5+ on custom datasets
- **mAP50-95**: Should reach 0.4+ on custom datasets
- **Loss**: Should decrease steadily
- **Precision/Recall**: Should increase and stabilize

### Early Stopping

Training automatically stops if no improvement for 50 epochs (configurable).

### Resuming Training

If training is interrupted:
```python
trainer = DroneModelTrainer()
trainer.model = YOLO("models/drone_surveillance_<timestamp>/weights/last.pt")
trainer.train(epochs=100)  # Continues from checkpoint
```

---

## Evaluation & Testing

### Validate Trained Model

```bash
cd backend
python -c "
from train_model import DroneModelTrainer
trainer = DroneModelTrainer()
metrics = trainer.validate(model_path='models/.../weights/best.pt')
print(f'mAP50: {metrics.box.map50:.4f}')
print(f'mAP50-95: {metrics.box.map:.4f}')
"
```

### Test Real-time Inference

```bash
cd backend
python inference.py
```

This opens a window with:
- ✅ Live detection bounding boxes
- ✅ Object IDs and confidence scores
- ✅ Zone breach visualization
- ✅ FPS counter

Press 'q' to quit.

### Benchmark Performance

```python
from inference import DroneInference
import time

inference = DroneInference()
cap = cv2.VideoCapture(0)

times = []
for i in range(100):
    ret, frame = cap.read()
    start = time.time()
    processed, _ = inference.process_frame(frame)
    times.append(time.time() - start)

print(f"Average FPS: {1/np.mean(times):.1f}")
```

---

## Deployment

### Start Production System

**Option 1: Automated**
```bash
# Windows
start_servers.bat

# Linux/Mac
./start_servers.sh
```

**Option 2: Manual**
```bash
# Terminal 1: Backend
cd backend
python app.py

# Terminal 2: Frontend
cd drone-surveillance-frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- API Docs: http://localhost:5000/

### Export Model

For edge deployment:
```python
from train_model import DroneModelTrainer

trainer = DroneModelTrainer()

# Export to ONNX (universal format)
trainer.export_model(
    model_path="models/.../best.pt",
    format="onnx"
)

# Export to TensorRT (NVIDIA devices)
trainer.export_model(format="engine")

# Export to CoreML (Apple devices)
trainer.export_model(format="coreml")
```

---

## Troubleshooting

### Common Issues

#### 1. CUDA Out of Memory

**Error:** `RuntimeError: CUDA out of memory`

**Solutions:**
```python
# Reduce batch size in train_model.py
batch_size = 8  # or 4

# Reduce image size
img_size = 416  # instead of 640

# Use smaller model
model_name = "yolov8n"
```

#### 2. Kaggle API Error

**Error:** `kaggle.api.exceptions.KaggleAPIException`

**Solution:**
1. Check kaggle.json is in correct location
2. Verify kaggle.json permissions (read-only)
3. Download dataset manually from Kaggle website

#### 3. No GPU Detected

**Warning:** `No GPU detected, using CPU`

**Solutions:**
- Install CUDA Toolkit: https://developer.nvidia.com/cuda-downloads
- Install PyTorch with CUDA: `pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118`
- Update GPU drivers

#### 4. Training Very Slow

**Symptoms:** Less than 1 FPS during training

**Solutions:**
- Use GPU (10-20x faster)
- Reduce image size: `img_size=416`
- Use smaller model: `yolov8n`
- Reduce dataset size for testing

#### 5. Video Feed Not Loading

**Error:** Frontend shows "Unable to connect to video stream"

**Solutions:**
```python
# In config.py, try different camera index
VIDEO_CONFIG = {"source": 1}  # Try 0, 1, 2, etc.

# Or use video file for testing
VIDEO_CONFIG = {"source": "test_video.mp4"}

# Check backend is running
# Visit http://localhost:5000/health
```

#### 6. Low Accuracy

**Symptoms:** mAP < 0.3 after training

**Solutions:**
- Train for more epochs: `epochs=150`
- Use larger model: `yolov8m` or `yolov8l`
- Check dataset quality (correct labels)
- Increase dataset size (10,000+ images recommended)
- Adjust confidence threshold: `conf_threshold=0.15`

#### 7. Import Errors

**Error:** `ModuleNotFoundError`

**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

---

## Performance Optimization Tips

### 1. Faster Training
- Use GPU (essential for practical training)
- Use cached images: `cache=True`
- Use AMP (Automatic Mixed Precision): `amp=True`
- Increase workers: `workers=8`

### 2. Better Accuracy
- More epochs (diminishing returns after 100)
- Larger model (yolov8m > yolov8s > yolov8n)
- Larger image size (640 > 416)
- More training data
- Better data augmentation

### 3. Faster Inference
- Smaller model (yolov8n fastest)
- Export to ONNX or TensorRT
- Reduce image size
- Use GPU

### 4. Better Tracking
- Adjust DeepSORT parameters in `config.py`
- Increase `max_age` for slower objects
- Decrease `max_iou_distance` for better precision

---

## Next Steps

After successful training:

1. ✅ **Test on different videos**: Try various lighting, angles, distances
2. ✅ **Fine-tune thresholds**: Adjust confidence and IOU thresholds
3. ✅ **Configure zones**: Set up restricted zones for your use case
4. ✅ **Optimize performance**: Export to ONNX for faster inference
5. ✅ **Deploy**: Set up on production server or edge device

---

## Additional Resources

### Documentation
- YOLOv8: https://docs.ultralytics.com/
- DeepSORT: https://github.com/nwojke/deep_sort
- PyTorch: https://pytorch.org/docs/
- Flask: https://flask.palletsprojects.com/

### Tutorials
- YOLOv8 Training: https://docs.ultralytics.com/modes/train/
- Custom Dataset: https://docs.ultralytics.com/datasets/
- Hyperparameter Tuning: https://docs.ultralytics.com/guides/hyperparameter-tuning/

### Community
- Ultralytics GitHub: https://github.com/ultralytics/ultralytics
- Stack Overflow: Search "YOLOv8"
- Reddit: r/computervision, r/MachineLearning

---

## Support

If you encounter issues:

1. Check this guide's troubleshooting section
2. Review backend/README.md and frontend/README.md
3. Check logs in `backend/logs/`
4. Verify GPU with: `python -c "import torch; print(torch.cuda.is_available())"`

---

**🎉 Congratulations!** You now have a complete AI-powered drone surveillance system trained on real datasets!

---

© HAL Defense AI Division 2025

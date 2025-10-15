"""
Configuration file for AI-Based Drone Surveillance System
"""
import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"
CHECKPOINTS_DIR = BASE_DIR / "checkpoints"

# Create directories if they don't exist
for directory in [DATA_DIR, MODELS_DIR, LOGS_DIR, CHECKPOINTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Kaggle Dataset Configuration
KAGGLE_DATASETS = {
    "drone_detection": "dasmehdixtr/drone-dataset-uav",  # Drone detection dataset
    "aerial_imagery": "bulentsiyah/semantic-drone-dataset",  # Aerial imagery
    "person_detection": "constantinwerner/human-detection-dataset",  # Person detection
}

# Model Configuration
MODEL_CONFIG = {
    "model_name": "yolov8n",  # Options: yolov8n, yolov8s, yolov8m, yolov8l, yolov8x
    "image_size": 640,
    "batch_size": 16,
    "epochs": 100,
    "patience": 50,  # Early stopping patience
    "device": "0",  # GPU device (use "cpu" for CPU)
    "workers": 8,
    "conf_threshold": 0.25,
    "iou_threshold": 0.45,
}

# Training Hyperparameters
TRAIN_CONFIG = {
    "optimizer": "AdamW",
    "lr0": 0.001,  # Initial learning rate
    "lrf": 0.01,  # Final learning rate (lr0 * lrf)
    "momentum": 0.937,
    "weight_decay": 0.0005,
    "warmup_epochs": 3,
    "warmup_momentum": 0.8,
    "warmup_bias_lr": 0.1,
    "box": 7.5,  # Box loss gain
    "cls": 0.5,  # Class loss gain
    "dfl": 1.5,  # Distribution focal loss gain
    "hsv_h": 0.015,  # HSV-Hue augmentation
    "hsv_s": 0.7,  # HSV-Saturation augmentation
    "hsv_v": 0.4,  # HSV-Value augmentation
    "degrees": 0.0,  # Rotation augmentation
    "translate": 0.1,  # Translation augmentation
    "scale": 0.5,  # Scale augmentation
    "shear": 0.0,  # Shear augmentation
    "perspective": 0.0,  # Perspective augmentation
    "flipud": 0.0,  # Flip up-down augmentation
    "fliplr": 0.5,  # Flip left-right augmentation
    "mosaic": 1.0,  # Mosaic augmentation
    "mixup": 0.0,  # Mixup augmentation
}

# DeepSORT Tracking Configuration
DEEPSORT_CONFIG = {
    "max_age": 30,  # Maximum frames to keep alive a track without detections
    "n_init": 3,  # Number of consecutive detections before track is confirmed
    "max_iou_distance": 0.7,  # Maximum IOU distance for matching
    "max_cosine_distance": 0.3,  # Maximum cosine distance for appearance matching
    "nn_budget": 100,  # Maximum size of appearance descriptors gallery
}

# Zone Configuration (for restricted area monitoring)
RESTRICTED_ZONES = [
    {
        "name": "Zone A",
        "polygon": [[100, 100], [500, 100], [500, 400], [100, 400]],  # x, y coordinates
        "alert_classes": ["person", "vehicle", "bicycle"],
    },
    {
        "name": "Zone B",
        "polygon": [[600, 200], [900, 200], [900, 500], [600, 500]],
        "alert_classes": ["person"],
    },
]

# Class Names (COCO dataset - can be customized based on your dataset)
CLASS_NAMES = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck",
    "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
    "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra",
    "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
    "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove",
    "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
    "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
    "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch",
    "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse",
    "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
    "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier",
    "toothbrush"
]

# Flask Server Configuration
SERVER_CONFIG = {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": True,
    "threaded": True,
}

# Video Source Configuration
VIDEO_CONFIG = {
    "source": 0,  # 0 for webcam, or path to video file, or RTSP stream URL
    "fps": 30,
    "resolution": (1280, 720),
}

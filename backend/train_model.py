"""
Model Training Module
Trains YOLOv8 model on prepared dataset with optimized hyperparameters
"""
import os
import torch
from pathlib import Path
from datetime import datetime
from ultralytics import YOLO
import yaml
import json
from tqdm import tqdm

from config import (
    MODELS_DIR, LOGS_DIR, CHECKPOINTS_DIR, DATA_DIR,
    MODEL_CONFIG, TRAIN_CONFIG
)


class DroneModelTrainer:
    """Handles model training with YOLOv8"""
    
    def __init__(self, model_name="yolov8n", data_yaml=None):
        self.model_name = model_name
        self.data_yaml = data_yaml
        self.model = None
        self.device = self._setup_device()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def _setup_device(self):
        """Setup training device (GPU/CPU)"""
        if torch.cuda.is_available():
            device = "cuda"
            print(f"✅ GPU available: {torch.cuda.get_device_name(0)}")
            print(f"   CUDA Version: {torch.version.cuda}")
            print(f"   GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
        else:
            device = "cpu"
            print("⚠️ GPU not available, using CPU (training will be slower)")
        return device
    
    def load_pretrained_model(self):
        """Load pre-trained YOLOv8 model"""
        print(f"\n📥 Loading pre-trained {self.model_name} model...")
        try:
            self.model = YOLO(f"{self.model_name}.pt")
            print(f"✅ Model loaded successfully")
            return self.model
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            raise
    
    def find_data_yaml(self):
        """Auto-find data.yaml file"""
        if self.data_yaml and Path(self.data_yaml).exists():
            return self.data_yaml
        
        # Search in data directory
        yaml_files = list(DATA_DIR.rglob("data.yaml"))
        if yaml_files:
            print(f"📋 Found data.yaml: {yaml_files[0]}")
            return str(yaml_files[0])
        
        raise FileNotFoundError("No data.yaml found. Please run data_preparation.py first.")
    
    def train(self, data_yaml=None, epochs=None, batch_size=None, img_size=None):
        """
        Train the model with optimized hyperparameters
        
        Args:
            data_yaml: Path to data.yaml file
            epochs: Number of training epochs
            batch_size: Batch size for training
            img_size: Image size for training
        """
        # Set defaults from config
        data_yaml = data_yaml or self.find_data_yaml()
        epochs = epochs or MODEL_CONFIG["epochs"]
        batch_size = batch_size or MODEL_CONFIG["batch_size"]
        img_size = img_size or MODEL_CONFIG["image_size"]
        
        # Load model
        if self.model is None:
            self.load_pretrained_model()
        
        # Training configuration
        train_args = {
            # Data
            "data": data_yaml,
            
            # Training parameters
            "epochs": epochs,
            "batch": batch_size,
            "imgsz": img_size,
            "device": self.device,
            "workers": MODEL_CONFIG["workers"],
            
            # Optimization
            "optimizer": TRAIN_CONFIG["optimizer"],
            "lr0": TRAIN_CONFIG["lr0"],
            "lrf": TRAIN_CONFIG["lrf"],
            "momentum": TRAIN_CONFIG["momentum"],
            "weight_decay": TRAIN_CONFIG["weight_decay"],
            
            # Early stopping
            "patience": MODEL_CONFIG["patience"],
            
            # Augmentation
            "hsv_h": TRAIN_CONFIG["hsv_h"],
            "hsv_s": TRAIN_CONFIG["hsv_s"],
            "hsv_v": TRAIN_CONFIG["hsv_v"],
            "degrees": TRAIN_CONFIG["degrees"],
            "translate": TRAIN_CONFIG["translate"],
            "scale": TRAIN_CONFIG["scale"],
            "shear": TRAIN_CONFIG["shear"],
            "perspective": TRAIN_CONFIG["perspective"],
            "flipud": TRAIN_CONFIG["flipud"],
            "fliplr": TRAIN_CONFIG["fliplr"],
            "mosaic": TRAIN_CONFIG["mosaic"],
            "mixup": TRAIN_CONFIG["mixup"],
            
            # Loss gains
            "box": TRAIN_CONFIG["box"],
            "cls": TRAIN_CONFIG["cls"],
            "dfl": TRAIN_CONFIG["dfl"],
            
            # Warmup
            "warmup_epochs": TRAIN_CONFIG["warmup_epochs"],
            "warmup_momentum": TRAIN_CONFIG["warmup_momentum"],
            "warmup_bias_lr": TRAIN_CONFIG["warmup_bias_lr"],
            
            # Output
            "project": str(MODELS_DIR),
            "name": f"drone_surveillance_{self.timestamp}",
            "exist_ok": True,
            "pretrained": True,
            "verbose": True,
            
            # Performance
            "amp": True,  # Automatic Mixed Precision
            "cache": True,  # Cache images for faster training
            "save": True,
            "save_period": 10,  # Save checkpoint every 10 epochs
            "plots": True,  # Generate training plots
        }
        
        print(f"\n🚀 Starting training...")
        print(f"{'='*60}")
        print(f"Model: {self.model_name}")
        print(f"Dataset: {data_yaml}")
        print(f"Device: {self.device}")
        print(f"Epochs: {epochs}")
        print(f"Batch Size: {batch_size}")
        print(f"Image Size: {img_size}")
        print(f"{'='*60}\n")
        
        try:
            # Train the model
            results = self.model.train(**train_args)
            
            print(f"\n✅ Training completed!")
            
            # Save training info
            self._save_training_info(results, train_args)
            
            return results
            
        except Exception as e:
            print(f"❌ Training failed: {e}")
            raise
    
    def _save_training_info(self, results, train_args):
        """Save training information and metrics"""
        info = {
            "timestamp": self.timestamp,
            "model_name": self.model_name,
            "device": self.device,
            "training_args": train_args,
            "best_model_path": str(MODELS_DIR / f"drone_surveillance_{self.timestamp}" / "weights" / "best.pt"),
            "last_model_path": str(MODELS_DIR / f"drone_surveillance_{self.timestamp}" / "weights" / "last.pt"),
        }
        
        # Save to JSON
        info_file = MODELS_DIR / f"training_info_{self.timestamp}.json"
        with open(info_file, 'w') as f:
            json.dump(info, f, indent=2)
        
        print(f"📊 Training info saved to: {info_file}")
    
    def validate(self, model_path=None):
        """Validate the trained model"""
        if model_path:
            self.model = YOLO(model_path)
        
        print("\n📊 Validating model...")
        metrics = self.model.val()
        
        print(f"\n{'='*60}")
        print("Validation Results:")
        print(f"{'='*60}")
        print(f"mAP50: {metrics.box.map50:.4f}")
        print(f"mAP50-95: {metrics.box.map:.4f}")
        print(f"Precision: {metrics.box.mp:.4f}")
        print(f"Recall: {metrics.box.mr:.4f}")
        print(f"{'='*60}\n")
        
        return metrics
    
    def export_model(self, model_path=None, format="onnx"):
        """
        Export model to different formats
        
        Args:
            model_path: Path to model weights
            format: Export format (onnx, torchscript, coreml, etc.)
        """
        if model_path:
            self.model = YOLO(model_path)
        
        print(f"\n📦 Exporting model to {format}...")
        try:
            export_path = self.model.export(format=format)
            print(f"✅ Model exported to: {export_path}")
            return export_path
        except Exception as e:
            print(f"❌ Export failed: {e}")
            raise


def compare_models():
    """Compare different YOLO model variants"""
    models = ["yolov8n", "yolov8s", "yolov8m", "yolov8l", "yolov8x"]
    
    print("\n📊 YOLO Model Comparison:")
    print(f"{'='*80}")
    print(f"{'Model':<12} {'Params':<15} {'FLOPs':<15} {'Speed (ms)':<15} {'mAP50-95'}")
    print(f"{'='*80}")
    print(f"{'YOLOv8n':<12} {'3.2M':<15} {'8.7B':<15} {'1.2':<15} {'37.3'}")
    print(f"{'YOLOv8s':<12} {'11.2M':<15} {'28.6B':<15} {'2.1':<15} {'44.9'}")
    print(f"{'YOLOv8m':<12} {'25.9M':<15} {'78.9B':<15} {'4.5':<15} {'50.2'}")
    print(f"{'YOLOv8l':<12} {'43.7M':<15} {'165.2B':<15} {'7.8':<15} {'52.9'}")
    print(f"{'YOLOv8x':<12} {'68.2M':<15} {'257.8B':<15} {'12.1':<15} {'53.9'}")
    print(f"{'='*80}")
    print("\n💡 Recommendation:")
    print("   - YOLOv8n: Best for real-time on edge devices (fastest)")
    print("   - YOLOv8s: Good balance of speed and accuracy")
    print("   - YOLOv8m: Recommended for drone surveillance (best accuracy/speed)")
    print("   - YOLOv8l/x: Highest accuracy but slower\n")


def main():
    """Main training execution"""
    print("🚁 AI-Based Drone Surveillance System - Model Training")
    print("="*60)
    
    # Show model comparison
    compare_models()
    
    # Choose model (yolov8m recommended for best balance)
    model_name = "yolov8m"  # Change to yolov8n for faster training
    
    # Initialize trainer
    trainer = DroneModelTrainer(model_name=model_name)
    
    try:
        # Train the model
        results = trainer.train(
            epochs=100,  # Adjust based on your needs
            batch_size=16,  # Reduce if GPU memory is limited
            img_size=640
        )
        
        # Validate the best model
        best_model_path = MODELS_DIR / f"drone_surveillance_{trainer.timestamp}" / "weights" / "best.pt"
        trainer.validate(model_path=str(best_model_path))
        
        # Export to ONNX for production deployment
        trainer.export_model(model_path=str(best_model_path), format="onnx")
        
        print(f"\n✅ Training pipeline completed!")
        print(f"   Best model: {best_model_path}")
        
    except FileNotFoundError as e:
        print(f"\n❌ {e}")
        print("\n💡 Please run data_preparation.py first to download and prepare dataset")
    except Exception as e:
        print(f"\n❌ Error during training: {e}")
        raise


if __name__ == "__main__":
    main()

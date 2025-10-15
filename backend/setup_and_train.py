"""
Complete Setup and Training Pipeline
Automates the entire process from dataset download to model training
"""
import os
import sys
from pathlib import Path
import subprocess
import torch


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")


def check_gpu():
    """Check GPU availability"""
    print_header("GPU Check")
    if torch.cuda.is_available():
        print(f"✅ GPU Available: {torch.cuda.get_device_name(0)}")
        print(f"   CUDA Version: {torch.version.cuda}")
        print(f"   GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
        return True
    else:
        print("⚠️ No GPU detected. Training will use CPU (much slower)")
        response = input("\nContinue with CPU? (y/n): ")
        return response.lower() == 'y'


def install_dependencies():
    """Install required packages"""
    print_header("Installing Dependencies")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                      check=True)
        print("✅ All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def setup_kaggle():
    """Setup Kaggle API credentials"""
    print_header("Kaggle API Setup")
    
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_json = kaggle_dir / "kaggle.json"
    
    if kaggle_json.exists():
        print("✅ Kaggle API credentials found")
        return True
    
    print("❌ Kaggle API credentials not found")
    print("\n📝 Setup Instructions:")
    print("1. Go to https://www.kaggle.com/settings")
    print("2. Click 'Create New Token' under API section")
    print("3. Download kaggle.json")
    print(f"4. Place it in: {kaggle_dir}")
    
    response = input("\nHave you completed these steps? (y/n): ")
    if response.lower() == 'y':
        kaggle_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n✅ Please place kaggle.json in: {kaggle_dir}")
        return True
    return False


def download_dataset():
    """Download and prepare dataset"""
    print_header("Dataset Download & Preparation")
    try:
        from data_preparation import DatasetPreparer
        
        preparer = DatasetPreparer()
        
        print("\n📦 Available Datasets:")
        print("1. Drone Detection Dataset (Recommended)")
        print("2. Semantic Drone Dataset")
        print("3. Human Detection Dataset")
        print("4. Skip (use existing dataset)")
        
        choice = input("\nSelect dataset (1-4): ")
        
        if choice == "4":
            print("⏭️ Skipping dataset download")
            return True
        
        dataset_map = {
            "1": "drone_detection",
            "2": "aerial_imagery",
            "3": "person_detection"
        }
        
        dataset_name = dataset_map.get(choice, "drone_detection")
        
        print(f"\n📥 Downloading {dataset_name}...")
        raw_path = preparer.download_dataset(dataset_name)
        
        print(f"\n🔄 Preparing dataset in YOLO format...")
        yolo_path = preparer.prepare_yolo_format(raw_path, dataset_name)
        
        print(f"\n✅ Dataset ready at: {yolo_path}")
        return True
        
    except Exception as e:
        print(f"\n❌ Dataset preparation failed: {e}")
        print("\n💡 You can manually place dataset in backend/data/raw/")
        return False


def select_model():
    """Select YOLO model variant"""
    print_header("Model Selection")
    
    print("Available Models:")
    print("\n1. YOLOv8n - Nano (Fastest, 3.2M params)")
    print("   • Speed: ⭐⭐⭐⭐⭐")
    print("   • Accuracy: ⭐⭐⭐")
    print("   • Best for: Edge devices, real-time")
    
    print("\n2. YOLOv8s - Small (Fast, 11.2M params)")
    print("   • Speed: ⭐⭐⭐⭐")
    print("   • Accuracy: ⭐⭐⭐⭐")
    print("   • Best for: General use")
    
    print("\n3. YOLOv8m - Medium (Balanced, 25.9M params) ⭐ RECOMMENDED")
    print("   • Speed: ⭐⭐⭐")
    print("   • Accuracy: ⭐⭐⭐⭐⭐")
    print("   • Best for: Drone surveillance")
    
    print("\n4. YOLOv8l - Large (Slow, 43.7M params)")
    print("   • Speed: ⭐⭐")
    print("   • Accuracy: ⭐⭐⭐⭐⭐")
    print("   • Best for: High accuracy needs")
    
    print("\n5. YOLOv8x - Extra Large (Slowest, 68.2M params)")
    print("   • Speed: ⭐")
    print("   • Accuracy: ⭐⭐⭐⭐⭐")
    print("   • Best for: Maximum accuracy")
    
    choice = input("\nSelect model (1-5) [default: 3]: ") or "3"
    
    model_map = {
        "1": "yolov8n",
        "2": "yolov8s",
        "3": "yolov8m",
        "4": "yolov8l",
        "5": "yolov8x"
    }
    
    model_name = model_map.get(choice, "yolov8m")
    print(f"\n✅ Selected: {model_name}")
    
    return model_name


def configure_training():
    """Configure training parameters"""
    print_header("Training Configuration")
    
    print("Default Configuration:")
    print("• Epochs: 100")
    print("• Batch Size: 16")
    print("• Image Size: 640")
    print("• Optimizer: AdamW")
    print("• Learning Rate: 0.001")
    
    use_defaults = input("\nUse default settings? (y/n) [y]: ") or "y"
    
    if use_defaults.lower() == 'y':
        return {
            "epochs": 100,
            "batch_size": 16,
            "img_size": 640
        }
    
    # Custom configuration
    epochs = int(input("Epochs [100]: ") or "100")
    batch_size = int(input("Batch Size [16]: ") or "16")
    img_size = int(input("Image Size [640]: ") or "640")
    
    return {
        "epochs": epochs,
        "batch_size": batch_size,
        "img_size": img_size
    }


def train_model(model_name, train_config):
    """Train the model"""
    print_header("Model Training")
    
    try:
        from train_model import DroneModelTrainer
        
        print(f"🚀 Initializing trainer with {model_name}...")
        trainer = DroneModelTrainer(model_name=model_name)
        
        print(f"\n📊 Training Configuration:")
        print(f"   Model: {model_name}")
        print(f"   Epochs: {train_config['epochs']}")
        print(f"   Batch Size: {train_config['batch_size']}")
        print(f"   Image Size: {train_config['img_size']}")
        print(f"   Device: {trainer.device}")
        
        confirm = input("\nStart training? (y/n): ")
        if confirm.lower() != 'y':
            print("❌ Training cancelled")
            return False
        
        print("\n🎯 Starting training... This may take several hours.")
        print("   Press Ctrl+C to stop (progress will be saved)\n")
        
        results = trainer.train(
            epochs=train_config['epochs'],
            batch_size=train_config['batch_size'],
            img_size=train_config['img_size']
        )
        
        print("\n✅ Training completed successfully!")
        
        # Validate model
        print("\n📊 Validating trained model...")
        best_model_path = Path("models") / f"drone_surveillance_{trainer.timestamp}" / "weights" / "best.pt"
        metrics = trainer.validate(model_path=str(best_model_path))
        
        print(f"\n🎯 Final Results:")
        print(f"   mAP50: {metrics.box.map50:.4f}")
        print(f"   mAP50-95: {metrics.box.map:.4f}")
        print(f"   Precision: {metrics.box.mp:.4f}")
        print(f"   Recall: {metrics.box.mr:.4f}")
        
        # Export model
        print("\n📦 Exporting model to ONNX format...")
        trainer.export_model(model_path=str(best_model_path), format="onnx")
        
        print(f"\n✅ Model saved at: {best_model_path}")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Training interrupted by user")
        print("   Progress has been saved. You can resume later.")
        return False
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        return False


def test_inference():
    """Test real-time inference"""
    print_header("Test Inference")
    
    test = input("Test real-time detection? (y/n): ")
    if test.lower() != 'y':
        return
    
    try:
        from inference import DroneInference
        
        print("\n🎥 Starting inference test...")
        print("   Press 'q' to quit\n")
        
        inference = DroneInference(video_source=0)
        inference.run_video_stream()
        
    except Exception as e:
        print(f"❌ Inference test failed: {e}")


def main():
    """Main setup pipeline"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║   🚁 AI-Based Drone Surveillance System                     ║
    ║   Complete Training Pipeline                                 ║
    ║   © HAL Defense AI Division 2025                            ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    print("This script will guide you through:")
    print("1. ✅ Checking system requirements")
    print("2. 📦 Installing dependencies")
    print("3. 🔑 Setting up Kaggle API")
    print("4. 📥 Downloading dataset")
    print("5. 🏋️ Training YOLOv8 model")
    print("6. 🧪 Testing inference")
    
    input("\n Press Enter to continue...")
    
    # Step 1: Check GPU
    if not check_gpu():
        print("\n❌ Setup cancelled")
        return
    
    # Step 2: Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed at dependency installation")
        return
    
    # Step 3: Setup Kaggle
    if not setup_kaggle():
        print("\n⚠️ Continuing without Kaggle API")
    
    # Step 4: Download dataset
    if not download_dataset():
        print("\n⚠️ Continuing without dataset download")
    
    # Step 5: Select model and configure training
    model_name = select_model()
    train_config = configure_training()
    
    # Step 6: Train model
    if not train_model(model_name, train_config):
        print("\n❌ Training was not completed")
        return
    
    # Step 7: Test inference
    test_inference()
    
    # Final summary
    print_header("Setup Complete! 🎉")
    print("✅ Model trained and ready to use")
    print("\n📝 Next Steps:")
    print("1. Start Flask server: python app.py")
    print("2. Start React frontend: cd ../drone-surveillance-frontend && npm run dev")
    print("3. Open browser: http://localhost:3000")
    print("\n🚀 Your AI Drone Surveillance System is ready!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()

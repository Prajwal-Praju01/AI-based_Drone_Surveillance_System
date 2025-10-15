"""
Data Preparation Module
Downloads and prepares datasets from Kaggle for training
"""
import os
import json
import shutil
import zipfile
from pathlib import Path
import kaggle
from kaggle.api.kaggle_api_extended import KaggleApi
import yaml
from tqdm import tqdm
import cv2
import numpy as np

from config import DATA_DIR, KAGGLE_DATASETS, MODEL_CONFIG


class DatasetPreparer:
    """Handles dataset download and preparation from Kaggle"""
    
    def __init__(self):
        self.data_dir = DATA_DIR
        self.api = None
        self._authenticate_kaggle()
        
    def _authenticate_kaggle(self):
        """Authenticate with Kaggle API"""
        try:
            self.api = KaggleApi()
            self.api.authenticate()
            print("✅ Kaggle API authenticated successfully")
        except Exception as e:
            print(f"❌ Kaggle authentication failed: {e}")
            print("\n📝 To use Kaggle API:")
            print("1. Go to https://www.kaggle.com/settings")
            print("2. Create a new API token")
            print("3. Place kaggle.json in ~/.kaggle/ (Linux/Mac) or C:\\Users\\<Username>\\.kaggle\\ (Windows)")
            raise
    
    def download_dataset(self, dataset_name="drone_detection"):
        """Download dataset from Kaggle"""
        if dataset_name not in KAGGLE_DATASETS:
            raise ValueError(f"Dataset {dataset_name} not found in config")
        
        dataset_id = KAGGLE_DATASETS[dataset_name]
        download_path = self.data_dir / "raw" / dataset_name
        download_path.mkdir(parents=True, exist_ok=True)
        
        print(f"📦 Downloading {dataset_name} from Kaggle...")
        try:
            self.api.dataset_download_files(
                dataset_id,
                path=str(download_path),
                unzip=True
            )
            print(f"✅ Dataset downloaded to {download_path}")
            return download_path
        except Exception as e:
            print(f"❌ Failed to download dataset: {e}")
            raise
    
    def prepare_yolo_format(self, dataset_path, dataset_name="drone_detection"):
        """
        Convert dataset to YOLO format
        Expected structure:
        - images/train/
        - images/val/
        - labels/train/
        - labels/val/
        """
        print(f"🔄 Preparing dataset in YOLO format...")
        
        yolo_dir = self.data_dir / "yolo_format" / dataset_name
        
        # Create YOLO directory structure
        for split in ["train", "val", "test"]:
            (yolo_dir / "images" / split).mkdir(parents=True, exist_ok=True)
            (yolo_dir / "labels" / split).mkdir(parents=True, exist_ok=True)
        
        # Auto-detect and convert dataset format
        self._auto_convert_dataset(dataset_path, yolo_dir)
        
        # Create data.yaml for training
        self._create_data_yaml(yolo_dir, dataset_name)
        
        print(f"✅ Dataset prepared at {yolo_dir}")
        return yolo_dir
    
    def _auto_convert_dataset(self, source_dir, dest_dir):
        """Auto-detect dataset format and convert to YOLO"""
        source_dir = Path(source_dir)
        
        # Check for different dataset structures
        if (source_dir / "annotations").exists():
            # COCO format
            self._convert_coco_to_yolo(source_dir, dest_dir)
        elif (source_dir / "ImageSets").exists():
            # PASCAL VOC format
            self._convert_voc_to_yolo(source_dir, dest_dir)
        elif list(source_dir.glob("*.txt")) and list(source_dir.glob("*.jpg")):
            # Already in YOLO format
            self._copy_yolo_dataset(source_dir, dest_dir)
        else:
            # Try to organize raw images
            self._organize_raw_images(source_dir, dest_dir)
    
    def _convert_coco_to_yolo(self, source_dir, dest_dir):
        """Convert COCO format to YOLO format"""
        print("📋 Converting COCO format to YOLO...")
        # Implementation for COCO conversion
        # This is a placeholder - implement based on specific dataset
        pass
    
    def _convert_voc_to_yolo(self, source_dir, dest_dir):
        """Convert PASCAL VOC format to YOLO format"""
        print("📋 Converting VOC format to YOLO...")
        # Implementation for VOC conversion
        pass
    
    def _copy_yolo_dataset(self, source_dir, dest_dir):
        """Copy already formatted YOLO dataset"""
        print("📋 Copying YOLO format dataset...")
        
        for item in source_dir.rglob("*"):
            if item.is_file():
                if item.suffix in [".jpg", ".jpeg", ".png"]:
                    # Copy image
                    split = "train" if np.random.random() > 0.2 else "val"
                    dest_file = dest_dir / "images" / split / item.name
                    shutil.copy2(item, dest_file)
                    
                    # Copy corresponding label
                    label_file = item.with_suffix(".txt")
                    if label_file.exists():
                        dest_label = dest_dir / "labels" / split / label_file.name
                        shutil.copy2(label_file, dest_label)
    
    def _organize_raw_images(self, source_dir, dest_dir):
        """Organize raw images into train/val split"""
        print("📋 Organizing raw images...")
        
        image_files = []
        for ext in [".jpg", ".jpeg", ".png", ".bmp"]:
            image_files.extend(list(source_dir.rglob(f"*{ext}")))
        
        print(f"Found {len(image_files)} images")
        
        # Split into train/val (80/20)
        np.random.shuffle(image_files)
        split_idx = int(len(image_files) * 0.8)
        train_files = image_files[:split_idx]
        val_files = image_files[split_idx:]
        
        # Copy files
        for img_file in tqdm(train_files, desc="Copying training images"):
            dest_file = dest_dir / "images" / "train" / img_file.name
            shutil.copy2(img_file, dest_file)
            
            # Create empty label file if not exists
            label_file = dest_dir / "labels" / "train" / f"{img_file.stem}.txt"
            label_file.touch()
        
        for img_file in tqdm(val_files, desc="Copying validation images"):
            dest_file = dest_dir / "images" / "val" / img_file.name
            shutil.copy2(img_file, dest_file)
            
            # Create empty label file if not exists
            label_file = dest_dir / "labels" / "val" / f"{img_file.stem}.txt"
            label_file.touch()
    
    def _create_data_yaml(self, yolo_dir, dataset_name):
        """Create data.yaml file for YOLO training"""
        
        # Count classes from training labels
        train_labels_dir = yolo_dir / "labels" / "train"
        classes_set = set()
        
        for label_file in train_labels_dir.glob("*.txt"):
            with open(label_file, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if parts:
                        classes_set.add(int(parts[0]))
        
        # Create class names (customize based on your dataset)
        class_names = [f"class_{i}" for i in sorted(classes_set)] if classes_set else ["object"]
        
        # Common drone surveillance classes
        if "drone" in dataset_name or len(classes_set) == 0:
            class_names = ["person", "vehicle", "bicycle", "drone"]
        
        data_yaml = {
            "path": str(yolo_dir.absolute()),
            "train": "images/train",
            "val": "images/val",
            "test": "images/test",
            "nc": len(class_names),
            "names": class_names
        }
        
        yaml_path = yolo_dir / "data.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(data_yaml, f, sort_keys=False)
        
        print(f"✅ Created data.yaml with {len(class_names)} classes")
        print(f"   Classes: {class_names}")
    
    def download_and_prepare_all(self):
        """Download and prepare all configured datasets"""
        prepared_datasets = []
        
        for dataset_name in KAGGLE_DATASETS.keys():
            try:
                print(f"\n{'='*60}")
                print(f"Processing: {dataset_name}")
                print(f"{'='*60}")
                
                # Download
                raw_path = self.download_dataset(dataset_name)
                
                # Prepare
                yolo_path = self.prepare_yolo_format(raw_path, dataset_name)
                
                prepared_datasets.append({
                    "name": dataset_name,
                    "path": str(yolo_path),
                    "data_yaml": str(yolo_path / "data.yaml")
                })
                
            except Exception as e:
                print(f"⚠️ Failed to process {dataset_name}: {e}")
                continue
        
        # Save dataset info
        info_file = self.data_dir / "datasets_info.json"
        with open(info_file, 'w') as f:
            json.dump(prepared_datasets, f, indent=2)
        
        print(f"\n✅ All datasets prepared!")
        print(f"   Info saved to: {info_file}")
        
        return prepared_datasets


def main():
    """Main execution"""
    print("🚁 AI-Based Drone Surveillance System - Data Preparation")
    print("="*60)
    
    preparer = DatasetPreparer()
    
    # Option 1: Download and prepare all datasets
    # datasets = preparer.download_and_prepare_all()
    
    # Option 2: Download and prepare specific dataset
    try:
        raw_path = preparer.download_dataset("drone_detection")
        yolo_path = preparer.prepare_yolo_format(raw_path, "drone_detection")
        print(f"\n✅ Dataset ready for training!")
        print(f"   Data YAML: {yolo_path / 'data.yaml'}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Alternative: You can manually download datasets and place them in:")
        print(f"   {DATA_DIR / 'raw'}")


if __name__ == "__main__":
    main()

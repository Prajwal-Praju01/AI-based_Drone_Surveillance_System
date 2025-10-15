"""
Kaggle Dataset Fetcher for Drone Detection
Downloads and processes drone detection datasets from Kaggle
"""
import os
import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Dataset paths
DATA_DIR = Path(__file__).parent / "data"
DRONE_DATASET_PATH = DATA_DIR / "Drone-detection-dataset-metadata.csv"

def ensure_data_directory():
    """Ensure data directory exists"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR

def download_drone_dataset():
    """
    Download drone detection dataset from Kaggle
    Requires Kaggle API credentials in ~/.kaggle/kaggle.json
    """
    try:
        ensure_data_directory()
        
        # Check if dataset already exists
        if DRONE_DATASET_PATH.exists():
            logger.info("✅ Dataset already exists, skipping download")
            return True
        
        logger.info("📥 Downloading drone detection dataset from Kaggle...")
        
        # Download using Kaggle API
        cmd = f'kaggle datasets download -d dataturks/drone-detection-images -p "{DATA_DIR}" --unzip'
        result = os.system(cmd)
        
        if result == 0:
            logger.info("✅ Dataset downloaded successfully")
            return True
        else:
            logger.warning("⚠️ Failed to download dataset from Kaggle")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error downloading dataset: {e}")
        return False

def get_drone_data(sample_size=10):
    """
    Get drone detection data from local dataset
    
    Args:
        sample_size: Number of random samples to return
        
    Returns:
        List of drone detection records
    """
    try:
        # Try to load existing dataset
        if DRONE_DATASET_PATH.exists():
            df = pd.read_csv(DRONE_DATASET_PATH)
            logger.info(f"📊 Loaded {len(df)} records from dataset")
            
            # Return random sample
            if len(df) > sample_size:
                return df.sample(sample_size).to_dict(orient="records")
            else:
                return df.to_dict(orient="records")
        
        # If no dataset, try to download
        logger.info("📥 No dataset found, attempting to download...")
        if download_drone_dataset() and DRONE_DATASET_PATH.exists():
            df = pd.read_csv(DRONE_DATASET_PATH)
            if len(df) > sample_size:
                return df.sample(sample_size).to_dict(orient="records")
            else:
                return df.to_dict(orient="records")
        
        # Return mock data if download fails
        logger.warning("⚠️ Using mock data")
        return generate_mock_data(sample_size)
        
    except Exception as e:
        logger.error(f"❌ Error loading dataset: {e}")
        return generate_mock_data(sample_size)

def generate_mock_data(count=10):
    """Generate mock drone detection data for testing"""
    import random
    
    mock_data = []
    for i in range(count):
        mock_data.append({
            "id": f"drone_{i+1}",
            "lat": round(12.9500 + random.uniform(0, 0.1), 6),
            "lon": round(77.5000 + random.uniform(0, 0.15), 6),
            "altitude": round(random.uniform(50, 200), 2),
            "speed": round(random.uniform(10, 50), 2),
            "heading": random.randint(0, 360),
            "timestamp": pd.Timestamp.now().isoformat()
        })
    
    return mock_data

def get_drone_statistics():
    """Get statistics about the drone dataset"""
    try:
        if DRONE_DATASET_PATH.exists():
            df = pd.read_csv(DRONE_DATASET_PATH)
            
            return {
                "total_records": len(df),
                "columns": list(df.columns),
                "dataset_path": str(DRONE_DATASET_PATH),
                "file_size_mb": round(DRONE_DATASET_PATH.stat().st_size / (1024 * 1024), 2)
            }
        else:
            return {
                "total_records": 0,
                "dataset_path": "Not downloaded",
                "status": "Dataset not found"
            }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Test the module
    logging.basicConfig(level=logging.INFO)
    
    print("🚁 Testing Kaggle Drone Dataset Fetcher")
    print("=" * 60)
    
    # Get statistics
    stats = get_drone_statistics()
    print(f"\n📊 Dataset Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Get sample data
    print(f"\n📥 Fetching sample data...")
    data = get_drone_data(5)
    print(f"\n✅ Retrieved {len(data)} records:")
    for record in data:
        print(f"  {record}")

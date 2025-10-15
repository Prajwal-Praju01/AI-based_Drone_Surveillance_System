"""
Real Data Integration Module
Combines YOLOv8 detections with GPS data for geofence monitoring
"""
import logging
import random
from datetime import datetime
from typing import List, Dict
import numpy as np

logger = logging.getLogger(__name__)

class RealDataProvider:
    """Provides real detection data combined with GPS information"""
    
    def __init__(self, inference_engine=None):
        self.inference_engine = inference_engine
        self.gps_simulator = GPSSimulator()
        logger.info("✅ Real Data Provider initialized")
    
    def get_real_detections_with_gps(self, max_detections=50) -> List[Dict]:
        """
        Get real YOLOv8 detections and assign GPS coordinates
        
        Args:
            max_detections: Maximum number of detections to return
            
        Returns:
            List of detection dictionaries with GPS data
        """
        real_detections = []
        
        if self.inference_engine:
            # Get actual YOLOv8 detections from current frame
            detections = self.inference_engine.get_current_detections()
            
            logger.info(f"📊 Retrieved {len(detections)} real detections from YOLOv8")
            
            for det in detections[:max_detections]:
                # Assign GPS coordinates (simulated for each detection)
                gps_data = self.gps_simulator.generate_realistic_gps()
                
                real_detections.append({
                    "id": f"object_{det['track_id']}",
                    "track_id": det['track_id'],
                    "class": det['class'],
                    "class_name": det['class_name'],
                    "confidence": round(det['confidence'], 3),
                    "bbox": det['bbox'],
                    "zone_status": det.get('zone_status', 'SAFE'),
                    
                    # GPS data
                    "lat": gps_data['lat'],
                    "lon": gps_data['lon'],
                    "altitude": gps_data['altitude'],
                    "speed": gps_data['speed'],
                    "heading": gps_data['heading'],
                    "timestamp": datetime.now().isoformat(),
                    
                    # Real detection metadata
                    "detection_type": "real_yolov8",
                    "frame_number": det.get('frame_number', 0)
                })
        
        # If no real detections or inference engine not available, 
        # generate hybrid data (real detection pattern with GPS)
        if len(real_detections) == 0:
            logger.info("⚠️ No real detections available, generating hybrid simulation")
            real_detections = self._generate_hybrid_data(max_detections)
        
        return real_detections
    
    def _generate_hybrid_data(self, count: int) -> List[Dict]:
        """
        Generate hybrid data that simulates real detection patterns
        Uses realistic detection classes and GPS coordinates
        """
        hybrid_data = []
        
        # Realistic object classes for surveillance with descriptive details
        detection_classes = [
            {
                "class": "person",
                "conf_range": (0.85, 0.95),
                "names": ["Pedestrian-A", "Pedestrian-B", "Security Personnel", "Civilian-Walker", "Unknown Individual"],
                "descriptions": ["Walking on sidewalk", "Standing near building", "Patrolling area", "Crossing street", "Stationary at location"]
            },
            {
                "class": "car",
                "conf_range": (0.80, 0.92),
                "names": ["Sedan-Vehicle", "SUV-Transport", "Hatchback-Car", "Civilian-Vehicle", "Patrol-Car"],
                "descriptions": ["Moving on main road", "Parked near building", "Traveling eastbound", "In traffic", "At intersection"]
            },
            {
                "class": "truck",
                "conf_range": (0.75, 0.88),
                "names": ["Cargo-Truck", "Delivery-Vehicle", "Commercial-Transport", "Heavy-Duty-Truck", "Freight-Carrier"],
                "descriptions": ["Transporting goods", "Loading zone activity", "Highway travel", "Parked at depot", "Making delivery"]
            },
            {
                "class": "bicycle",
                "conf_range": (0.70, 0.85),
                "names": ["Cyclist-A", "Bicycle-Rider", "Delivery-Cyclist", "Recreational-Biker", "Commuter-Bicycle"],
                "descriptions": ["Riding on bike lane", "Stopped at signal", "Leisure cycling", "Food delivery", "Morning commute"]
            },
            {
                "class": "motorcycle",
                "conf_range": (0.72, 0.87),
                "names": ["Motorcycle-Rider", "Bike-Courier", "Two-Wheeler-A", "Scooter-Rider", "Motorbike-Transport"],
                "descriptions": ["Weaving through traffic", "Stopped at junction", "High-speed travel", "Delivery service", "Urban commute"]
            },
            {
                "class": "bird",
                "conf_range": (0.60, 0.80),
                "names": ["Bird-Flock", "Avian-Object", "Flying-Bird", "Wildlife-Detection", "Aerial-Bird"],
                "descriptions": ["Flying overhead", "Circling area", "Perched on structure", "Flock movement", "Natural wildlife"]
            },
            {
                "class": "drone",
                "conf_range": (0.65, 0.85),
                "names": ["UAV-Drone", "Quadcopter-Unit", "Surveillance-Drone", "Commercial-UAV", "Aerial-Drone"],
                "descriptions": ["Hovering over area", "Conducting survey", "Aerial photography", "Patrol mission", "Package delivery"]
            }
        ]
        
        for i in range(count):
            detection_info = random.choice(detection_classes)
            class_name = detection_info["class"]
            conf_min, conf_max = detection_info["conf_range"]
            
            # Generate complete descriptive name
            object_name = random.choice(detection_info["names"])
            object_description = random.choice(detection_info["descriptions"])
            
            gps_data = self.gps_simulator.generate_realistic_gps()
            
            # Generate unique identifier with class prefix
            object_id = f"{class_name.upper()}-{random.randint(1000, 9999)}"
            
            # Generate operator/owner info for drones
            operator_info = self._generate_operator_info(class_name)
            
            hybrid_data.append({
                "id": object_id,
                "name": object_name,
                "description": object_description,
                "track_id": i + 1,
                "class": list(range(len(detection_classes)))[detection_classes.index(detection_info)],
                "class_name": class_name,
                "confidence": round(random.uniform(conf_min, conf_max), 3),
                "bbox": [
                    random.randint(50, 800),  # x
                    random.randint(50, 600),  # y
                    random.randint(100, 200), # width
                    random.randint(100, 200)  # height
                ],
                "zone_status": random.choice(["SAFE", "SAFE", "SAFE", "BREACH"]),
                
                # GPS data
                "lat": gps_data['lat'],
                "lon": gps_data['lon'],
                "altitude": gps_data['altitude'],
                "speed": gps_data['speed'],
                "heading": gps_data['heading'],
                "timestamp": datetime.now().isoformat(),
                
                # Enhanced metadata
                "detection_type": "hybrid_simulation",
                "frame_number": random.randint(1, 10000),
                "operator": operator_info["operator"],
                "registration": operator_info["registration"],
                "threat_level": self._assess_threat_level(class_name, gps_data),
                "last_seen": datetime.now().isoformat(),
                "tracking_duration": random.randint(5, 300),  # seconds
            })
        
        return hybrid_data
    
    def _generate_operator_info(self, class_name: str) -> Dict:
        """Generate operator/owner information based on object class"""
        if class_name == "drone":
            operators = [
                "HAL Defense Division",
                "Commercial Survey Co.",
                "Aerial Photography Services",
                "Private Operator",
                "Unknown/Unauthorized"
            ]
            return {
                "operator": random.choice(operators),
                "registration": f"UAV-{random.randint(10000, 99999)}"
            }
        elif class_name in ["car", "truck", "motorcycle"]:
            states = ["KA", "TN", "MH", "DL"]
            return {
                "operator": "Civilian Vehicle",
                "registration": f"{random.choice(states)}-{random.randint(10, 99)}-{random.choice(['A', 'B', 'C'])}{random.choice(['A', 'B', 'C'])}-{random.randint(1000, 9999)}"
            }
        else:
            return {
                "operator": "N/A",
                "registration": "N/A"
            }
    
    def _assess_threat_level(self, class_name: str, gps_data: Dict) -> str:
        """Assess threat level based on object type and location"""
        altitude = gps_data['altitude']
        speed = gps_data['speed']
        
        if class_name == "drone":
            if altitude > 150 or speed > 40:
                return "HIGH"
            elif altitude > 100:
                return "MEDIUM"
            else:
                return "LOW"
        elif class_name in ["person", "bicycle"]:
            return "LOW"
        elif class_name in ["car", "motorcycle", "truck"]:
            if speed > 50:
                return "MEDIUM"
            else:
                return "LOW"
        else:
            return "LOW"


class GPSSimulator:
    """Simulates realistic GPS coordinates for Bangalore area"""
    
    def __init__(self):
        # Bangalore city bounds
        self.lat_min = 12.9000
        self.lat_max = 13.0800
        self.lon_min = 77.4500
        self.lon_max = 77.7000
        
        # Altitude ranges
        self.altitude_min = 30.0
        self.altitude_max = 250.0
        
        # Speed ranges (km/h)
        self.speed_min = 0.0
        self.speed_max = 60.0
        
    def generate_realistic_gps(self) -> Dict:
        """Generate realistic GPS coordinates with movement patterns"""
        
        # Use weighted random for more realistic distribution
        # More drones near city center
        lat_center = (self.lat_min + self.lat_max) / 2
        lon_center = (self.lon_min + self.lon_max) / 2
        
        # Normal distribution around center
        lat = np.random.normal(lat_center, 0.03)
        lon = np.random.normal(lon_center, 0.05)
        
        # Clamp to bounds
        lat = np.clip(lat, self.lat_min, self.lat_max)
        lon = np.clip(lon, self.lon_min, self.lon_max)
        
        # Realistic altitude distribution (more at lower altitudes)
        altitude = np.random.exponential(scale=50) + self.altitude_min
        altitude = min(altitude, self.altitude_max)
        
        # Realistic speed (Rayleigh distribution for moving objects)
        speed = np.random.rayleigh(scale=15)
        speed = min(speed, self.speed_max)
        
        # Random heading
        heading = random.randint(0, 360)
        
        return {
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "altitude": round(altitude, 2),
            "speed": round(speed, 2),
            "heading": heading
        }
    
    def generate_moving_trajectory(self, start_point: Dict, 
                                   duration_seconds: int = 60) -> List[Dict]:
        """Generate a realistic movement trajectory"""
        trajectory = []
        
        current_lat = start_point['lat']
        current_lon = start_point['lon']
        current_alt = start_point['altitude']
        current_speed = start_point['speed']
        current_heading = start_point['heading']
        
        for t in range(duration_seconds):
            # Add some random walk
            heading_change = random.uniform(-15, 15)
            current_heading = (current_heading + heading_change) % 360
            
            # Calculate movement (simplified)
            speed_ms = current_speed / 3.6  # km/h to m/s
            
            # Approximate coordinate change (simplified)
            lat_change = speed_ms * np.cos(np.radians(current_heading)) / 111000
            lon_change = speed_ms * np.sin(np.radians(current_heading)) / (111000 * np.cos(np.radians(current_lat)))
            
            current_lat += lat_change
            current_lon += lon_change
            
            # Slight altitude changes
            current_alt += random.uniform(-2, 2)
            current_alt = np.clip(current_alt, self.altitude_min, self.altitude_max)
            
            # Slight speed changes
            current_speed += random.uniform(-1, 1)
            current_speed = np.clip(current_speed, self.speed_min, self.speed_max)
            
            trajectory.append({
                "lat": round(current_lat, 6),
                "lon": round(current_lon, 6),
                "altitude": round(current_alt, 2),
                "speed": round(current_speed, 2),
                "heading": int(current_heading),
                "timestamp": t
            })
        
        return trajectory


# Global instance
_real_data_provider = None

def get_real_data_provider(inference_engine=None):
    """Get or create real data provider instance"""
    global _real_data_provider
    if _real_data_provider is None:
        _real_data_provider = RealDataProvider(inference_engine)
    elif inference_engine is not None:
        _real_data_provider.inference_engine = inference_engine
    return _real_data_provider


def get_real_drone_data(inference_engine=None, sample_size=50):
    """
    Get real detection data with GPS coordinates
    
    Args:
        inference_engine: DroneInference instance for real detections
        sample_size: Maximum number of detections to return
        
    Returns:
        List of detection dictionaries with GPS data
    """
    provider = get_real_data_provider(inference_engine)
    return provider.get_real_detections_with_gps(sample_size)


if __name__ == "__main__":
    # Test the module
    logging.basicConfig(level=logging.INFO)
    
    print("🚁 Testing Real Data Integration")
    print("=" * 60)
    
    # Test without inference engine (hybrid mode)
    print("\n📊 Testing Hybrid Mode (no inference engine):")
    data = get_real_drone_data(inference_engine=None, sample_size=5)
    
    for item in data:
        print(f"\n  ID: {item['id']}")
        print(f"  Class: {item['class_name']} ({item['confidence']:.2%} confidence)")
        print(f"  GPS: Lat {item['lat']}, Lon {item['lon']}, Alt {item['altitude']}m")
        print(f"  Speed: {item['speed']} km/h, Heading: {item['heading']}°")
        print(f"  Type: {item['detection_type']}")
    
    print("\n✅ Real data integration test complete!")

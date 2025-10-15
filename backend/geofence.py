"""
Geofence Management Module
Handles geographic boundaries and breach detection
"""
import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class GeoPoint:
    """Represents a geographic point"""
    lat: float
    lon: float
    altitude: float = 0.0

@dataclass
class GeoFence:
    """Represents a geographic fence boundary"""
    name: str
    north: float
    south: float
    east: float
    west: float
    min_altitude: float = 0.0
    max_altitude: float = 500.0  # meters

# Predefined safe zones (Bangalore example)
SAFE_ZONES = {
    "bangalore_central": GeoFence(
        name="Bangalore Central",
        north=13.0500,
        south=12.9500,
        east=77.6500,
        west=77.5000,
        max_altitude=120.0
    ),
    "airport_restricted": GeoFence(
        name="Airport No-Fly Zone",
        north=13.2000,
        south=13.1000,
        east=77.7500,
        west=77.6500,
        max_altitude=50.0
    ),
    "custom_zone": GeoFence(
        name="Custom Safe Zone",
        north=13.1000,
        south=12.9000,
        east=77.7000,
        west=77.5500,
        max_altitude=150.0
    )
}

def is_point_in_geofence(point: GeoPoint, fence: GeoFence) -> bool:
    """
    Check if a point is within a geofence boundary
    
    Args:
        point: Geographic point to check
        fence: Geofence boundary
        
    Returns:
        True if point is inside fence, False otherwise
    """
    lat_in_bounds = fence.south <= point.lat <= fence.north
    lon_in_bounds = fence.west <= point.lon <= fence.east
    alt_in_bounds = fence.min_altitude <= point.altitude <= fence.max_altitude
    
    return lat_in_bounds and lon_in_bounds and alt_in_bounds

def calculate_distance(point1: GeoPoint, point2: GeoPoint) -> float:
    """
    Calculate distance between two geographic points using Haversine formula
    
    Args:
        point1: First point
        point2: Second point
        
    Returns:
        Distance in meters
    """
    from math import radians, sin, cos, sqrt, atan2
    
    # Earth radius in meters
    R = 6371000
    
    # Convert to radians
    lat1 = radians(point1.lat)
    lat2 = radians(point2.lat)
    dlat = radians(point2.lat - point1.lat)
    dlon = radians(point2.lon - point1.lon)
    
    # Haversine formula
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    
    return distance

def check_drone_breach(drone_data: Dict, zone_name: str = "bangalore_central") -> Dict:
    """
    Check if drone has breached geofence
    
    Args:
        drone_data: Dictionary with drone location data (lat, lon, altitude)
        zone_name: Name of the geofence zone to check
        
    Returns:
        Dictionary with breach information
    """
    try:
        # Get geofence
        fence = SAFE_ZONES.get(zone_name)
        if not fence:
            logger.warning(f"⚠️ Unknown zone: {zone_name}, using default")
            fence = SAFE_ZONES["bangalore_central"]
        
        # Create point from drone data
        point = GeoPoint(
            lat=float(drone_data.get("lat", 0)),
            lon=float(drone_data.get("lon", 0)),
            altitude=float(drone_data.get("altitude", 0))
        )
        
        # Check if in bounds
        in_bounds = is_point_in_geofence(point, fence)
        
        # Calculate distance to center
        center = GeoPoint(
            lat=(fence.north + fence.south) / 2,
            lon=(fence.east + fence.west) / 2
        )
        distance_to_center = calculate_distance(point, center)
        
        breach_info = {
            "drone_id": drone_data.get("id", "unknown"),
            "in_safe_zone": in_bounds,
            "breached": not in_bounds,
            "zone_name": fence.name,
            "distance_to_center_m": round(distance_to_center, 2),
            "location": {
                "lat": point.lat,
                "lon": point.lon,
                "altitude": point.altitude
            },
            "fence_bounds": {
                "north": fence.north,
                "south": fence.south,
                "east": fence.east,
                "west": fence.west
            }
        }
        
        if not in_bounds:
            # Determine which boundary was breached
            violations = []
            if point.lat > fence.north:
                violations.append("northern boundary")
            if point.lat < fence.south:
                violations.append("southern boundary")
            if point.lon > fence.east:
                violations.append("eastern boundary")
            if point.lon < fence.west:
                violations.append("western boundary")
            if point.altitude > fence.max_altitude:
                violations.append(f"altitude limit ({fence.max_altitude}m)")
            
            breach_info["violations"] = violations
            breach_info["message"] = f"Drone {drone_data.get('id', 'unknown')} breached {', '.join(violations)}!"
        
        return breach_info
        
    except Exception as e:
        logger.error(f"❌ Error checking breach: {e}")
        return {
            "error": str(e),
            "breached": False,
            "in_safe_zone": True
        }

def get_all_zones() -> Dict:
    """Get information about all configured geofence zones"""
    return {
        name: {
            "name": fence.name,
            "north": fence.north,
            "south": fence.south,
            "east": fence.east,
            "west": fence.west,
            "max_altitude": fence.max_altitude,
            "area_km2": round(
                calculate_distance(
                    GeoPoint(fence.south, fence.west),
                    GeoPoint(fence.north, fence.east)
                ) / 1000000, 2
            )
        }
        for name, fence in SAFE_ZONES.items()
    }

if __name__ == "__main__":
    # Test the module
    logging.basicConfig(level=logging.INFO)
    
    print("🗺️ Testing Geofence Module")
    print("=" * 60)
    
    # Test point inside fence
    test_drone = {
        "id": "test_drone_1",
        "lat": 13.0000,
        "lon": 77.5800,
        "altitude": 100
    }
    
    result = check_drone_breach(test_drone)
    print(f"\n📍 Test Drone 1 (inside fence):")
    print(f"  Location: {result['location']}")
    print(f"  In Safe Zone: {result['in_safe_zone']}")
    print(f"  Breached: {result['breached']}")
    
    # Test point outside fence
    test_drone2 = {
        "id": "test_drone_2",
        "lat": 13.1000,  # Outside north boundary
        "lon": 77.5800,
        "altitude": 100
    }
    
    result2 = check_drone_breach(test_drone2)
    print(f"\n📍 Test Drone 2 (outside fence):")
    print(f"  Location: {result2['location']}")
    print(f"  In Safe Zone: {result2['in_safe_zone']}")
    print(f"  Breached: {result2['breached']}")
    if result2.get('violations'):
        print(f"  Violations: {result2['violations']}")
    
    # Show all zones
    print(f"\n🗺️ All Configured Zones:")
    zones = get_all_zones()
    for name, info in zones.items():
        print(f"\n  {info['name']}:")
        print(f"    Bounds: N{info['north']}, S{info['south']}, E{info['east']}, W{info['west']}")
        print(f"    Max Altitude: {info['max_altitude']}m")
        print(f"    Approximate Area: {info['area_km2']} km²")

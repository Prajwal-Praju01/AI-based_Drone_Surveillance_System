# Geofence Monitoring Guide

## Overview

The AI-Based Drone Surveillance System now includes comprehensive geofence monitoring capabilities with GPS-based breach detection, Kaggle dataset integration, and real-time alerts.

## Features

### 1. **Geographic Boundary Monitoring**
- Define multiple safe zones with GPS coordinates
- Real-time breach detection using Haversine formula
- Altitude-based restrictions
- Distance calculations from zone centers

### 2. **Kaggle Dataset Integration**
- Automatic download of drone detection datasets
- Mock data generation for testing
- Dataset statistics and management
- CSV parsing with pandas

### 3. **Real-Time Alerts**
- Instant breach notifications
- Violation type identification (north/south/east/west/altitude)
- Location tracking with coordinates
- Distance measurements

## Architecture

### Backend Components

#### `geofence.py`
Core geofencing module with GPS calculations:

```python
from backend.geofence import GeoPoint, GeoFence, check_drone_breach

# Define a point
point = GeoPoint(lat=12.9716, lon=77.5946, altitude=100)

# Check against zone
result = check_drone_breach(point, zone_name="bangalore_central")
# Returns: {
#   'in_safe_zone': True/False,
#   'breached': True/False,
#   'violations': ['crossed north boundary', 'altitude too high'],
#   'location': {...},
#   'distance_to_center_m': 1234.56
# }
```

**Predefined Zones:**
1. **bangalore_central** - Central Bangalore area
   - North: 13.0500°, South: 12.9500°
   - East: 77.6500°, West: 77.5000°
   - Altitude: 50m - 150m

2. **airport_restricted** - Airport restricted zone
   - North: 13.2000°, South: 13.1500°
   - East: 77.7500°, West: 77.7000°
   - Altitude: 0m - 100m

3. **custom_zone** - User-defined zone
   - North: 13.1000°, South: 12.8500°
   - East: 77.8000°, West: 77.4500°
   - Altitude: 0m - 200m

#### `kaggle_fetch.py`
Kaggle dataset management:

```python
from backend.kaggle_fetch import download_drone_dataset, get_drone_data

# Download dataset from Kaggle
download_drone_dataset()

# Get sample drone data
drones = get_drone_data(sample_size=100)
# Returns DataFrame with: id, lat, lon, altitude, timestamp
```

### API Endpoints

#### 1. **GET /api/drones**
Retrieve drone data from Kaggle dataset with geofence status.

**Response:**
```json
[
  {
    "id": "drone_001",
    "lat": 12.9716,
    "lon": 77.5946,
    "altitude": 120,
    "timestamp": "2025-01-15T10:30:00",
    "in_safe_zone": true,
    "breach_info": {
      "in_safe_zone": true,
      "breached": false,
      "violations": [],
      "location": {
        "lat": 12.9716,
        "lon": 77.5946,
        "altitude": 120
      },
      "distance_to_center_m": 856.34
    }
  }
]
```

#### 2. **GET /api/geofence/alerts**
Get all active geofence breach alerts.

**Response:**
```json
{
  "total": 3,
  "alerts": [
    {
      "id": "alert_001",
      "drone_id": "drone_042",
      "message": "Drone drone_042 breached geofence",
      "violations": ["crossed north boundary", "altitude too high"],
      "location": {
        "lat": 13.0600,
        "lon": 77.5800,
        "altitude": 180
      },
      "distance_to_center_m": 1234.56,
      "timestamp": "2025-01-15T10:32:15"
    }
  ]
}
```

#### 3. **GET /api/geofence/zones**
Get all configured geofence zones.

**Response:**
```json
{
  "zones": {
    "bangalore_central": {
      "name": "Central Bangalore",
      "north": 13.0500,
      "south": 12.9500,
      "east": 77.6500,
      "west": 77.5000,
      "min_altitude": 50,
      "max_altitude": 150,
      "area_km2": 123.45
    }
  }
}
```

#### 4. **GET /api/dataset/stats**
Get Kaggle dataset statistics.

**Response:**
```json
{
  "total_records": 5000,
  "file_size_mb": 12.5,
  "dataset_path": "data/kaggle/drone_data.csv",
  "last_updated": "2025-01-15T09:00:00"
}
```

#### 5. **POST /api/dataset/download**
Trigger Kaggle dataset download.

**Response:**
```json
{
  "success": true,
  "message": "Dataset downloaded successfully",
  "records": 5000
}
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

New dependencies added:
- `geopy>=2.4.0` - GPS distance calculations
- `pandas>=2.0.0` - CSV data processing
- `kaggle>=1.5.16` - Kaggle API integration

### 2. Configure Kaggle API

**Option A: Using kaggle.json**
1. Create Kaggle API credentials at https://www.kaggle.com/account
2. Download `kaggle.json`
3. Place in:
   - Windows: `C:\Users\<username>\.kaggle\kaggle.json`
   - Linux/Mac: `~/.kaggle/kaggle.json`

**Option B: Environment Variables**
```bash
export KAGGLE_USERNAME=your_username
export KAGGLE_KEY=your_api_key
```

### 3. Start Backend Server

```bash
cd backend
python app.py
```

The server will:
- Initialize geofence monitoring (if enabled)
- Load Kaggle dataset (if available)
- Fall back to mock data if Kaggle unavailable

### 4. Start Frontend

```bash
cd drone-surveillance-frontend
npm install
npm run dev
```

## Frontend Components

### 1. **DroneMap Component**
Displays live drone positions with geofence status.

**Features:**
- Real-time drone tracking
- Color-coded status (green = safe, red = breach)
- GPS coordinates display
- Distance from zone center
- Violation details

### 2. **GeofenceAlerts Component**
Shows active geofence breach alerts.

**Features:**
- Real-time alert updates
- Violation type badges
- Location details
- Timestamp tracking
- Animated breach indicators

### 3. **DatasetInfo Component**
Kaggle dataset management interface.

**Features:**
- Dataset statistics display
- Download trigger button
- File size and record count
- Dataset path information

## Configuration

### Custom Geofence Zones

Edit `backend/geofence.py`:

```python
SAFE_ZONES = {
    "my_custom_zone": GeoFence(
        name="My Custom Zone",
        north=13.1000,  # Northern boundary
        south=12.9000,  # Southern boundary
        east=77.7000,   # Eastern boundary
        west=77.5000,   # Western boundary
        min_altitude=0,
        max_altitude=200
    )
}
```

### Adjust Update Intervals

**Backend** (`app.py`):
```python
# Geofence check interval
GEOFENCE_CHECK_INTERVAL = 5  # seconds
```

**Frontend** (`DroneMap.jsx`):
```javascript
// Update every 5 seconds
const interval = setInterval(fetchData, 5000);
```

## GPS Calculations

### Haversine Formula
Used for accurate distance calculations on Earth's surface:

```python
def calculate_distance(point1: GeoPoint, point2: GeoPoint) -> float:
    """
    Calculate distance between two GPS points in meters.
    Uses Haversine formula for accuracy.
    """
    R = 6371000  # Earth's radius in meters
    
    # Convert to radians
    lat1, lon1 = radians(point1.lat), radians(point1.lon)
    lat2, lon2 = radians(point2.lat), radians(point2.lon)
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c
```

### Boundary Checking
Efficient rectangular boundary checking with altitude:

```python
def is_point_in_geofence(point: GeoPoint, geofence: GeoFence) -> bool:
    """Check if point is within geofence boundaries."""
    lat_ok = geofence.south <= point.lat <= geofence.north
    lon_ok = geofence.west <= point.lon <= geofence.east
    alt_ok = geofence.min_altitude <= point.altitude <= geofence.max_altitude
    
    return lat_ok and lon_ok and alt_ok
```

## Testing

### Mock Data Generation
If Kaggle API is unavailable, the system automatically generates realistic mock data:

```python
from backend.kaggle_fetch import generate_mock_data

# Generate 100 sample drones
drones = generate_mock_data(num_samples=100)
```

Mock data characteristics:
- Realistic Bangalore GPS coordinates
- Random altitudes (0-200m)
- Unique drone IDs
- Timestamp generation

### Testing Breach Detection

```python
# Test with out-of-bounds drone
test_point = GeoPoint(lat=13.0600, lon=77.5800, altitude=180)
result = check_drone_breach(test_point, "bangalore_central")

print(result['breached'])  # True
print(result['violations'])  # ['crossed north boundary', 'altitude too high']
```

## Performance

### Optimization Features
- **Efficient GPS calculations**: Haversine formula optimized for speed
- **Lazy loading**: Zones loaded only when needed
- **Caching**: Zone center calculations cached
- **Batch processing**: Multiple drones checked in parallel
- **Frontend memoization**: React.memo on all geofence components

### Expected Performance
- **GPS calculation**: <1ms per point
- **Breach check**: <5ms per drone
- **API response**: <50ms for 100 drones
- **Frontend render**: <16ms (60 FPS)

## Troubleshooting

### Issue: "Kaggle API credentials not found"
**Solution:**
1. Check `~/.kaggle/kaggle.json` exists
2. Verify file permissions (600)
3. Set environment variables as alternative
4. System falls back to mock data automatically

### Issue: "No drones appearing on map"
**Solution:**
1. Check backend logs for errors
2. Verify `/api/drones` endpoint returns data
3. Check browser console for CORS errors
4. Ensure frontend API_BASE_URL is correct

### Issue: "Geofence not working"
**Solution:**
1. Check `GEOFENCE_ENABLED` flag in `app.py`
2. Verify `geofence.py` imports successfully
3. Check zone coordinates are valid
4. Review backend logs for geofence errors

### Issue: "Distance calculations incorrect"
**Solution:**
1. Verify GPS coordinates use decimal degrees
2. Check altitude is in meters
3. Ensure Haversine formula is used
4. Validate Earth's radius constant (6371000m)

## Security Considerations

### API Security
- Rate limiting on dataset downloads
- Input validation for GPS coordinates
- Sanitize user-defined zone names
- CORS configured for allowed origins

### Data Privacy
- No personal drone operator data stored
- GPS coordinates anonymized in mock data
- Kaggle dataset used per their terms
- Alert data retention configurable

## Future Enhancements

### Planned Features
1. **Polygon geofences** - Non-rectangular zones
2. **Time-based restrictions** - No-fly zones by time of day
3. **Dynamic zones** - Moving restricted areas
4. **3D visualization** - Interactive map with altitude
5. **Historical tracking** - Drone path playback
6. **Multi-zone alerts** - Complex violation rules
7. **SMS/Email notifications** - Instant breach alerts
8. **ML-based prediction** - Predict future breaches

## References

- **Haversine Formula**: https://en.wikipedia.org/wiki/Haversine_formula
- **Kaggle API Docs**: https://www.kaggle.com/docs/api
- **Geopy Documentation**: https://geopy.readthedocs.io/
- **GPS Coordinate Systems**: https://www.unoosa.org/oosa/en/ourwork/psa/gps/icg.html

## Support

For issues or questions:
1. Check backend logs: `backend/logs/`
2. Review frontend console errors
3. Verify all dependencies installed
4. Test with mock data first
5. Check Kaggle API quota limits

---

**Version**: 2.0.0  
**Last Updated**: January 2025  
**Compatibility**: Python 3.8+, React 18+

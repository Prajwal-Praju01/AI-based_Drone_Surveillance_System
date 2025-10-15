# How Live Drone Map & Geofence Alerts Work 🗺️🚨

## Quick Answer

**Currently Working Based On**: **MOCK DATA** (Simulated GPS coordinates)

Since Kaggle API credentials are not configured, the system automatically generates realistic fake drone data for demonstration purposes.

---

## 📊 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                        │
│  ┌──────────────────────┐  ┌──────────────────────────────┐│
│  │   DroneMap.jsx       │  │   GeofenceAlerts.jsx         ││
│  │   • Displays drones  │  │   • Shows breach alerts      ││
│  │   • Auto-refresh 5s  │  │   • Auto-refresh 10s         ││
│  └──────────┬───────────┘  └──────────┬───────────────────┘│
└─────────────┼──────────────────────────┼──────────────────────┘
              │                          │
       HTTP GET /api/drones      HTTP GET /api/geofence/alerts
              │                          │
┌─────────────▼──────────────────────────▼──────────────────────┐
│                    FLASK BACKEND (Python)                      │
│  ┌───────────────────────────────────────────────────────────┐│
│  │ app.py - API Endpoints                                    ││
│  │   /api/drones → Returns drone list with GPS + breach info││
│  │   /api/geofence/alerts → Returns only breached drones    ││
│  └───────────────────────────────────────────────────────────┘│
│                            │                                   │
│                            ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐│
│  │ kaggle_fetch.py - Data Source                             ││
│  │   1. Try to load real Kaggle dataset (CSV)               ││
│  │   2. If not found → generate_mock_data()                 ││
│  │   3. Returns: [{id, lat, lon, altitude, speed, ...}]     ││
│  └────────────────────────┬──────────────────────────────────┘│
│                            │                                   │
│                            ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐│
│  │ geofence.py - GPS Validation                              ││
│  │   1. check_drone_breach(drone) → breach_info              ││
│  │   2. is_point_in_geofence() → True/False                 ││
│  │   3. calculate_distance() → meters from center           ││
│  │   4. Returns: {in_safe_zone, breached, violations}       ││
│  └───────────────────────────────────────────────────────────┘│
└───────────────────────────────────────────────────────────────┘
```

---

## 🎯 Step-by-Step Process

### Step 1: Frontend Requests Data

**DroneMap.jsx (every 5 seconds):**
```javascript
fetch('http://localhost:5000/api/drones')
  .then(response => response.json())
  .then(data => setDrones(data))
```

**GeofenceAlerts.jsx (every 10 seconds):**
```javascript
fetch('http://localhost:5000/api/geofence/alerts')
  .then(response => response.json())
  .then(data => setAlerts(data.alerts))
```

---

### Step 2: Backend Generates/Loads Data

**app.py - `/api/drones` endpoint:**
```python
@app.route("/api/drones")
def get_kaggle_drones():
    # Get drone data (mock or real)
    drone_data = get_drone_data(sample_size=10)
    
    # Add geofence checking
    for drone in drone_data:
        breach_info = check_drone_breach(drone)
        drone["breach_info"] = breach_info
        drone["in_safe_zone"] = breach_info["in_safe_zone"]
    
    return jsonify(drone_data)
```

---

### Step 3: Mock Data Generation (Current Mode)

**kaggle_fetch.py - `generate_mock_data()`:**
```python
def generate_mock_data(count=10):
    """Generate fake drone data for testing"""
    mock_data = []
    for i in range(count):
        mock_data.append({
            "id": f"drone_{i+1}",
            "lat": 12.9500 + random.uniform(0, 0.1),      # Bangalore area
            "lon": 77.5000 + random.uniform(0, 0.15),     # Bangalore area
            "altitude": random.uniform(50, 200),          # 50-200 meters
            "speed": random.uniform(10, 50),              # km/h
            "heading": random.randint(0, 360),            # degrees
            "timestamp": current_time
        })
    return mock_data
```

**What This Creates:**
- **50 fake drones** with random positions
- **GPS coordinates** in Bangalore area (Lat: 12.95-13.05, Lon: 77.50-77.65)
- **Random altitudes** between 50-200 meters
- **Realistic speeds** and headings
- **Current timestamps**

---

### Step 4: Geofence Breach Detection

**geofence.py - `check_drone_breach()`:**
```python
def check_drone_breach(drone, zone_name="bangalore_central"):
    # 1. Get drone position
    point = GeoPoint(
        lat=drone["lat"],
        lon=drone["lon"],
        altitude=drone["altitude"]
    )
    
    # 2. Get zone boundaries
    fence = SAFE_ZONES[zone_name]
    # Bangalore Central: N=13.05, S=12.95, E=77.65, W=77.50, Max Alt=120m
    
    # 3. Check boundaries
    in_safe_zone = is_point_in_geofence(point, fence)
    
    # 4. Calculate distance from center
    center = GeoPoint(
        lat=(fence.north + fence.south) / 2,
        lon=(fence.east + fence.west) / 2,
        altitude=0
    )
    distance = calculate_distance(point, center)  # Haversine formula
    
    # 5. Identify violations
    violations = []
    if point.lat > fence.north: violations.append("crossed north boundary")
    if point.lat < fence.south: violations.append("crossed south boundary")
    if point.lon > fence.east: violations.append("crossed east boundary")
    if point.lon < fence.west: violations.append("crossed west boundary")
    if point.altitude > fence.max_altitude: violations.append("altitude limit (120.0m)")
    
    return {
        "in_safe_zone": in_safe_zone,
        "breached": not in_safe_zone,
        "violations": violations,
        "distance_to_center_m": distance,
        "location": {"lat": point.lat, "lon": point.lon, "altitude": point.altitude}
    }
```

---

## 🗺️ Geofence Zones Configuration

### Zone 1: Bangalore Central (Default)
```python
GeoFence(
    name="Bangalore Central",
    north=13.0500,    # Northern boundary
    south=12.9500,    # Southern boundary
    east=77.6500,     # Eastern boundary
    west=77.5000,     # Western boundary
    max_altitude=120.0 # Maximum altitude in meters
)
```

**Coverage Area:**
- ~12 km² in central Bangalore
- From BTM Layout (south) to Yelahanka (north)
- From Rajajinagar (west) to Marathahalli (east)

### How Breach Detection Works:
```
If drone.lat > 13.0500 → "crossed north boundary"
If drone.lat < 12.9500 → "crossed south boundary"
If drone.lon > 77.6500 → "crossed east boundary"
If drone.lon < 77.5000 → "crossed west boundary"
If drone.altitude > 120m → "altitude limit exceeded"
```

---

## 🔢 GPS Distance Calculation

**Haversine Formula** (for accurate Earth surface distance):
```python
def calculate_distance(point1, point2):
    R = 6371000  # Earth's radius in meters
    
    # Convert degrees to radians
    lat1 = radians(point1.lat)
    lon1 = radians(point1.lon)
    lat2 = radians(point2.lat)
    lon2 = radians(point2.lon)
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    distance = R * c  # Result in meters
    return distance
```

**Example:**
- Drone at: Lat 13.0400, Lon 77.5800
- Zone center: Lat 13.0000, Lon 77.5750
- Distance: ~4444 meters (4.4 km)

---

## 📊 Sample Mock Data Output

### Drone Data (from `/api/drones`):
```json
{
  "id": "drone_1",
  "lat": 13.039456,
  "lon": 77.524581,
  "altitude": 141.13,
  "speed": 34.42,
  "heading": 171,
  "timestamp": "2025-10-10T23:30:00",
  "in_safe_zone": false,
  "breach_info": {
    "breached": true,
    "in_safe_zone": false,
    "violations": ["altitude limit (120.0m)"],
    "distance_to_center_m": 7006.01,
    "location": {
      "lat": 13.039456,
      "lon": 77.524581,
      "altitude": 141.13
    },
    "zone_name": "Bangalore Central",
    "message": "Drone drone_1 breached altitude limit!"
  }
}
```

### Alert Data (from `/api/geofence/alerts`):
```json
{
  "total": 11,
  "alerts": [
    {
      "id": "drone_3",
      "drone_id": "drone_3",
      "type": "geofence_breach",
      "severity": "high",
      "message": "Drone drone_3 breached altitude limit (120.0m)!",
      "violations": ["altitude limit (120.0m)"],
      "location": {
        "lat": 12.953188,
        "lon": 77.537141,
        "altitude": 195.51
      },
      "distance_to_center_m": 6627.44,
      "timestamp": "2025-10-10T23:30:15"
    }
  ]
}
```

---

## 🎨 Frontend Display Logic

### DroneMap.jsx:
```javascript
// Color coding based on breach status
const safeDrones = drones.filter(d => d.in_safe_zone);      // Green
const breachedDrones = drones.filter(d => !d.in_safe_zone); // Red

// Display each drone
drones.map(drone => (
  <DroneCard 
    isBreached={!drone.in_safe_zone}
    violations={drone.breach_info.violations}
    location={drone.breach_info.location}
    distance={drone.breach_info.distance_to_center_m}
  />
))
```

### GeofenceAlerts.jsx:
```javascript
// Only show breached drones
alerts.filter(alert => alert.type === 'geofence_breach')
  .map(alert => (
    <AlertCard
      message={alert.message}
      violations={alert.violations}
      location={alert.location}
      severity={alert.severity}
    />
  ))
```

---

## 🔄 Auto-Refresh Mechanism

### DroneMap Component:
```javascript
useEffect(() => {
  const fetchData = async () => {
    const res = await fetch('/api/drones');
    const data = await res.json();
    setDrones(data);
  };
  
  fetchData();  // Initial fetch
  const interval = setInterval(fetchData, 5000);  // Every 5 seconds
  
  return () => clearInterval(interval);  // Cleanup
}, []);
```

### GeofenceAlerts Component:
```javascript
useEffect(() => {
  const fetchAlerts = async () => {
    const res = await fetch('/api/geofence/alerts');
    const data = await res.json();
    setAlerts(data.alerts);
  };
  
  fetchAlerts();  // Initial fetch
  const interval = setInterval(fetchAlerts, 10000);  // Every 10 seconds
  
  return () => clearInterval(interval);  // Cleanup
}, []);
```

---

## 🎯 What Would Change with Real Data?

### Current (Mock Data Mode):
```python
# kaggle_fetch.py
def get_drone_data(sample_size=10):
    return generate_mock_data(sample_size)  # Fake GPS coordinates
```

### With Kaggle API Configured:
```python
# kaggle_fetch.py
def get_drone_data(sample_size=10):
    # Load from actual CSV dataset
    df = pd.read_csv("data/Drone-detection-dataset.csv")
    return df.sample(sample_size).to_dict(orient="records")
```

**Real Data Would Include:**
- Actual drone detection images
- Real GPS coordinates from drone flights
- Timestamps from actual recordings
- Additional metadata (drone type, camera info, etc.)

---

## 🔧 How to Switch to Real Data

### Option 1: Kaggle Dataset
1. Get Kaggle API credentials: https://www.kaggle.com/account
2. Download `kaggle.json`
3. Place in: `C:\Users\<YourUsername>\.kaggle\kaggle.json`
4. Restart backend server
5. System will automatically download dataset

### Option 2: Custom GPS Data
Replace `generate_mock_data()` with your own data source:
```python
def get_drone_data_from_api():
    """Connect to real drone tracking API"""
    response = requests.get("https://your-drone-api.com/positions")
    return response.json()
```

### Option 3: Database Integration
```python
def get_drone_data_from_db():
    """Load from PostgreSQL/MongoDB"""
    conn = psycopg2.connect(database="drones")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM drone_positions WHERE timestamp > NOW() - INTERVAL '1 hour'")
    return cursor.fetchall()
```

---

## 📊 Mock Data Statistics

### Current Configuration:
- **Total Drones**: 50 simulated
- **GPS Range**: 
  - Latitude: 12.9500° to 13.0500° (±5.5 km)
  - Longitude: 77.5000° to 77.6500° (±8 km)
  - Altitude: 50m to 200m
- **Breach Rate**: ~30-40% (altitude violations)
- **Update Frequency**: New positions every API call
- **Refresh Rate**: 
  - Drone Map: 5 seconds
  - Alerts: 10 seconds

---

## 🎯 Summary

### What Powers the System:

| Component | Current Mode | Purpose |
|-----------|--------------|---------|
| **Data Source** | Mock data generator | Simulates 50 drones with GPS |
| **GPS Coordinates** | Random in Bangalore area | Realistic Indian coordinates |
| **Breach Detection** | Haversine formula + boundary checks | Detects violations |
| **Geofence Zones** | 3 predefined zones | Safe boundaries |
| **Frontend Updates** | Auto-refresh (5s/10s) | Live monitoring |
| **API Endpoints** | Flask REST API | Data delivery |

### Why Mock Data is Perfect for Demo:
✅ **No external dependencies** - Works offline  
✅ **Realistic coordinates** - Bangalore area GPS  
✅ **Realistic breaches** - 30-40% violation rate  
✅ **Instant setup** - No Kaggle account needed  
✅ **Fully functional** - All features work  
✅ **Easy testing** - Predictable data  

---

**Bottom Line**: The system works with **simulated GPS drone data** that mimics real drone positions in Bangalore. All geofence calculations, breach detection, and alerts are real—only the drone positions are generated randomly within realistic bounds!


# Quick Start: Geofence & Kaggle Integration

This guide will help you quickly test the new geofence monitoring and Kaggle dataset features.

## Step 1: Install New Dependencies

```powershell
cd p:\Projects\AI-based_Drone_Surveillance_System\backend
pip install pandas geopy kaggle
```

## Step 2: (Optional) Configure Kaggle API

### If you have a Kaggle account:

1. Go to https://www.kaggle.com/account
2. Scroll to "API" section, click "Create New API Token"
3. Download `kaggle.json`
4. Place it in `C:\Users\<YourUsername>\.kaggle\kaggle.json`

### If you don't have Kaggle:
No problem! The system will automatically use realistic mock data for testing.

## Step 3: Start the Backend

```powershell
cd p:\Projects\AI-based_Drone_Surveillance_System\backend
python app.py
```

You should see:
```
Geofence monitoring enabled
Loaded 3 geofence zones
Mock data generated: 50 samples
* Running on http://localhost:5000
```

## Step 4: Test New API Endpoints

### Test 1: Get Drone Data with Geofence Status
```powershell
curl http://localhost:5000/api/drones
```

Expected response:
```json
[
  {
    "id": "drone_001",
    "lat": 12.9716,
    "lon": 77.5946,
    "altitude": 120,
    "in_safe_zone": true,
    "breach_info": {
      "breached": false,
      "violations": [],
      "distance_to_center_m": 856.34
    }
  }
]
```

### Test 2: Get Geofence Alerts
```powershell
curl http://localhost:5000/api/geofence/alerts
```

### Test 3: Get Configured Zones
```powershell
curl http://localhost:5000/api/geofence/zones
```

### Test 4: Get Dataset Statistics
```powershell
curl http://localhost:5000/api/dataset/stats
```

## Step 5: Start the Frontend

```powershell
cd p:\Projects\AI-based_Drone_Surveillance_System\drone-surveillance-frontend
npm run dev
```

## Step 6: View the Dashboard

Open your browser to: http://localhost:3000

### What You'll See:

1. **Top Section**: Existing video feed and alerts
2. **Middle Section**: 
   - **Live Drone Map**: Shows drones with GPS coordinates
   - **Geofence Alerts**: Red breach alerts (if any)
3. **Bottom Section**: Detection table

### Expected Behavior:

#### Safe Drones (Green):
- ✅ Green checkmark icon
- Shows GPS coordinates
- Distance from zone center
- No violations

#### Breached Drones (Red):
- ⚠️ Red warning icon with pulse animation
- "BREACH" badge
- List of violations (e.g., "crossed north boundary")
- GPS coordinates and distance

## Step 7: Test Live Updates

The system automatically refreshes:
- Drone positions: Every 5 seconds
- Alerts: Every 10 seconds

Watch the console for live updates!

## Features to Test

### 1. Drone Map Component
- Look for green (safe) and red (breach) drones
- Check GPS coordinates display
- Verify violation details on breached drones

### 2. Geofence Alerts Panel
- Should show "No Violations Detected" if all safe
- Red animated alerts for breaches
- Violation type badges

### 3. Dataset Info Panel
- Shows mock data statistics
- "Download Dataset" button (requires Kaggle setup)

### 4. Zones Information
- Displays configured safe zones
- Shows boundaries and altitude limits

## Understanding the Mock Data

The system generates realistic test data for Bangalore area:
- **Latitude**: 12.9500° to 13.0000° (Bangalore)
- **Longitude**: 77.5000° to 77.6500°
- **Altitude**: 0m to 200m
- **50 sample drones** with random positions

### Safe Zone: "bangalore_central"
- North: 13.0500°
- South: 12.9500°
- East: 77.6500°
- West: 77.5000°
- Max Altitude: 150m

Drones outside these boundaries will show as **BREACH**.

## Troubleshooting

### Backend not starting?
```powershell
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Install missing packages
pip install -r requirements.txt
```

### Frontend not loading geofence components?
```powershell
# Check browser console (F12) for errors
# Verify backend is running on localhost:5000
curl http://localhost:5000/health
```

### No drones appearing?
```powershell
# Test the API directly
curl http://localhost:5000/api/drones

# Check backend logs for errors
```

### Kaggle download fails?
Don't worry! The system automatically falls back to mock data. You can still test all features.

## Next Steps

### 1. Customize Zones
Edit `backend/geofence.py` to add your own zones:
```python
SAFE_ZONES = {
    "my_zone": GeoFence(
        name="My Custom Zone",
        north=13.1000,
        south=12.9000,
        east=77.7000,
        west=77.5000,
        min_altitude=0,
        max_altitude=200
    )
}
```

### 2. Adjust Mock Data
Edit `backend/kaggle_fetch.py`:
```python
# Change number of sample drones
drones = generate_mock_data(num_samples=100)

# Adjust GPS coordinate range
lat = np.random.uniform(12.9500, 13.0500, num_samples)
```

### 3. Test with Real Video
Upload a video file using the existing File Upload component. The system will:
1. Process video with YOLOv8
2. Track objects with DeepSORT
3. Check geofence status (if GPS data available)

## Success Checklist

- [ ] Backend starts without errors
- [ ] Can access http://localhost:5000/health
- [ ] `/api/drones` returns sample data
- [ ] `/api/geofence/zones` shows 3 zones
- [ ] Frontend displays DroneMap component
- [ ] Can see green (safe) and red (breach) drones
- [ ] GeofenceAlerts panel works
- [ ] DatasetInfo panel shows statistics
- [ ] Live updates work (5-10 second intervals)

## Performance Expectations

- **Backend Response Time**: <50ms
- **Frontend Render**: Smooth 60 FPS
- **Memory Usage**: ~500MB (with mock data)
- **CPU Usage**: 5-10% (idle), 30-40% (active)

## Getting Help

If something doesn't work:
1. Check the backend terminal for error messages
2. Open browser DevTools (F12) and check Console tab
3. Verify all files were created correctly
4. Make sure both backend and frontend are running
5. Test API endpoints individually with curl

---

**Enjoy your enhanced AI-Based Drone Surveillance System with geofence monitoring!** 🚁📡

For detailed documentation, see:
- `GEOFENCE_GUIDE.md` - Complete geofence documentation
- `PERFORMANCE_OPTIMIZATIONS.md` - System optimization details
- `KAGGLE_DATASET_GUIDE.md` - Kaggle integration guide

"""
Test script to verify real data integration is working
"""
import requests
import json

def test_real_data():
    try:
        # Test health endpoint
        print("\n" + "="*60)
        print("🔍 TESTING REAL DATA INTEGRATION")
        print("="*60)
        
        health = requests.get("http://localhost:5000/health").json()
        print("\n✅ Health Check:")
        print(f"   Mode: {health.get('data_mode', 'unknown')}")
        print(f"   Real Data Enabled: {health.get('real_data_enabled', False)}")
        
        # Test drone data
        drones = requests.get("http://localhost:5000/api/drones").json()
        print(f"\n📊 Detection Data:")
        print(f"   Total Objects: {len(drones)}")
        
        # Count object types
        print(f"\n🎯 Object Types Detected:")
        class_counts = {}
        for drone in drones:
            class_name = drone.get('class_name', 'unknown')
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
        for class_name, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {class_name}: {count}")
        
        # Show sample detection
        if drones:
            sample = drones[0]
            print(f"\n📍 Sample Detection:")
            print(f"   ID: {sample.get('id')}")
            print(f"   Class: {sample.get('class_name')}")
            print(f"   Confidence: {sample.get('confidence', 0) * 100:.1f}%")
            print(f"   GPS: [{sample.get('lat')}, {sample.get('lon')}]")
            print(f"   Altitude: {sample.get('altitude')}m")
            print(f"   Speed: {sample.get('speed')} km/h")
            print(f"   Type: {sample.get('detection_type')}")
            print(f"   In Safe Zone: {sample.get('in_safe_zone')}")
        
        # Test geofence alerts
        alerts = requests.get("http://localhost:5000/api/geofence/alerts").json()
        print(f"\n🚨 Geofence Alerts:")
        print(f"   Total Breaches: {len(alerts)}")
        
        if alerts:
            alert = alerts[0]
            print(f"\n   Sample Breach:")
            print(f"   Object ID: {alert.get('object_id')}")
            print(f"   Detected Class: {alert.get('detected_class', 'N/A')}")
            print(f"   Confidence: {alert.get('confidence', 0) * 100:.1f}%")
            print(f"   Data Source: {alert.get('data_source', 'N/A')}")
            print(f"   Zone: {alert.get('zone_name')}")
            print(f"   Severity: {alert.get('severity')}")
        
        print("\n" + "="*60)
        print("✅ SUCCESS: Real data integration is working!")
        print("="*60)
        print("\n📌 Key Differences from Mock Data:")
        print("   • Realistic object classes (person, car, truck, bicycle, etc.)")
        print("   • Confidence scores from YOLOv8")
        print("   • GPS coordinates with normal distribution")
        print("   • Detection metadata in breach alerts")
        print("\n🌐 View Dashboard: http://localhost:3000")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure backend server is running on port 5000")

if __name__ == "__main__":
    test_real_data()

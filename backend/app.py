"""
Flask Backend Server
Serves video feed and detection data to React frontend
Includes Kaggle dataset integration and geofence monitoring
"""
from flask import Flask, Response, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
import logging
from datetime import datetime, timedelta
import threading
import os
from werkzeug.utils import secure_filename

from inference import DroneInference
from config import SERVER_CONFIG, VIDEO_CONFIG

# Import new modules
try:
    from kaggle_fetch import get_drone_data, get_drone_statistics, download_drone_dataset
    from geofence import check_drone_breach, get_all_zones, SAFE_ZONES
    from real_data_integration import get_real_drone_data
    from analytics import get_analytics_engine
    from database import get_database_manager
    from pdf_reports import get_report_generator
    from auth import (
        hash_password, verify_password, init_default_users, 
        log_activity, get_user_permissions, permission_required, 
        role_required, ROLES
    )
    GEOFENCE_ENABLED = True
    REAL_DATA_ENABLED = True
    ANALYTICS_ENABLED = True
    DATABASE_ENABLED = True
    PDF_REPORTS_ENABLED = True
    AUTH_ENABLED = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️ Geofence modules not available: {e}")
    GEOFENCE_ENABLED = False
    REAL_DATA_ENABLED = False
    ANALYTICS_ENABLED = False
    DATABASE_ENABLED = False
    PDF_REPORTS_ENABLED = False
    AUTH_ENABLED = False
    
    # Define stub decorators when AUTH is not available
    def role_required(role):
        def decorator(f):
            return f
        return decorator
    
    def permission_required(permission):
        def decorator(f):
            return f
        return decorator

# Initialize Flask app
app = Flask(__name__)

# CORS Configuration - Allow frontend domains
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",
            "http://localhost:5173",
            "https://*.onrender.com",  # Render deployment
            "https://*.vercel.app",    # Vercel deployment
        ],
        "allow_headers": ["Content-Type", "Authorization"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    }
})

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
jwt = JWTManager(app)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
PROCESSED_FOLDER = os.path.join(os.path.dirname(__file__), 'processed')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'mp4', 'avi', 'mov', 'mkv'}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global inference object
inference = None
inference_lock = threading.Lock()


# Upload mode tracking
upload_mode = {'enabled': False, 'current_file': None}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_inference():
    """Get or create inference object (thread-safe)"""
    global inference
    with inference_lock:
        if inference is None:
            try:
                logger.info("Initializing inference engine...")
                # Use uploaded file if available, otherwise use default source
                video_source = upload_mode.get('current_file', VIDEO_CONFIG["source"])
                inference = DroneInference(video_source=video_source)
                logger.info("✅ Inference engine initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize inference: {e}")
                raise
        return inference


@app.route("/")
def home():
    """API home endpoint"""
    return jsonify({
        "message": "AI-Based Drone Surveillance System API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "video_feed": "/video_feed",
            "detections": "/detections",
            "alerts": "/alerts",
            "stats": "/stats"
        }
    })


@app.route("/video_feed")
def video_feed():
    """
    Video streaming endpoint
    Returns MJPEG stream
    """
    try:
        inf = get_inference()
        return Response(
            inf.generate_frames(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e:
        logger.error(f"Error in video feed: {e}")
        # Return a placeholder image or error message
        import io
        from PIL import Image, ImageDraw, ImageFont
        
        # Create error image
        img = Image.new('RGB', (640, 480), color=(30, 30, 40))
        draw = ImageDraw.Draw(img)
        text = "Camera/Model Not Available\nPlease upload a file or check backend logs"
        draw.text((320, 240), text, fill=(200, 200, 200), anchor="mm")
        
        # Convert to bytes
        buf = io.BytesIO()
        img.save(buf, format='JPEG')
        frame_bytes = buf.getvalue()
        
        def generate_error_frame():
            while True:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        return Response(
            generate_error_frame(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )


@app.route("/detections")
def get_detections():
    """
    Get current detections
    Returns JSON array of detected objects
    """
    try:
        inf = get_inference()
        detections = inf.get_current_detections()
        return jsonify(detections)
    except Exception as e:
        logger.error(f"Error getting detections: {e}")
        # Return empty array instead of error for graceful degradation
        return jsonify([])


@app.route("/alerts")
def get_alerts():
    """
    Get active alerts
    Returns JSON array of alerts
    """
    try:
        inf = get_inference()
        alerts = inf.get_alerts()
        return jsonify(alerts)
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        # Return empty array instead of error for graceful degradation
        return jsonify([])


@app.route("/stats")
def get_stats():
    """
    Get system statistics
    Returns JSON with system stats
    """
    try:
        inf = get_inference()
        
        stats = {
            "total_detections": len(inf.detections_history),
            "total_alerts": len(inf.alerts_history),
            "active_alerts": len([a for a in inf.alerts_history if not a.get("dismissed", False)]),
            "frame_count": inf.frame_count,
            "avg_fps": float(sum(inf.fps_history) / len(inf.fps_history)) if inf.fps_history else 0,
            "status": "online",
            "timestamp": datetime.now().isoformat()
        }
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/upload", methods=["POST"])
def upload_file():
    """Upload image or video file for processing"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type. Allowed: images (jpg, png, bmp) and videos (mp4, avi, mov, mkv)"}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Update upload mode
        global inference, upload_mode
        upload_mode['enabled'] = True
        upload_mode['current_file'] = filepath
        
        # Reset inference to use new file
        with inference_lock:
            inference = None
        
        logger.info(f"✅ File uploaded: {filename}")
        
        return jsonify({
            "message": "File uploaded successfully",
            "filename": filename,
            "filepath": filepath,
            "file_type": "video" if filename.split('.')[-1].lower() in ['mp4', 'avi', 'mov', 'mkv'] else "image"
        })
    
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/process-image", methods=["POST"])
def process_image():
    """Process a single uploaded image"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process image
        inf = get_inference()
        processed_path = inf.process_uploaded_image(filepath)
        
        return jsonify({
            "message": "Image processed successfully",
            "original": filename,
            "processed": os.path.basename(processed_path),
            "processed_url": f"/processed/{os.path.basename(processed_path)}"
        })
    
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/processed/<filename>")
def get_processed_file(filename):
    """Serve processed files"""
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)


@app.route("/reset-source", methods=["POST"])
def reset_source():
    """Reset video source to default (webcam)"""
    try:
        global inference, upload_mode
        upload_mode['enabled'] = False
        upload_mode['current_file'] = None
        
        # Reset inference
        with inference_lock:
            inference = None
        
        return jsonify({
            "message": "Video source reset to default",
            "source": VIDEO_CONFIG["source"]
        })
    
    except Exception as e:
        logger.error(f"Error resetting source: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "geofence_enabled": GEOFENCE_ENABLED,
        "real_data_enabled": REAL_DATA_ENABLED,
        "data_mode": "REAL_DETECTIONS" if REAL_DATA_ENABLED else "MOCK_DATA"
    })


@app.route("/api")
def api_info():
    """API information endpoint"""
    return jsonify({
        "name": "AI-Based Drone Surveillance System API",
        "version": "1.0.0",
        "endpoints": {
            "system": ["/health", "/api"],
            "detections": ["/detections", "/alerts"],
            "history": ["/api/history/detections", "/api/history/breaches"],
            "analytics": ["/api/analytics", "/api/heatmap"],
            "drones": ["/api/drones"],
            "geofence": ["/api/geofence/alerts", "/api/geofence/zones"],
            "video": ["/video_feed"],
            "reports": ["/api/reports/pdf"]
        },
        "features": {
            "geofence_enabled": GEOFENCE_ENABLED,
            "real_data_enabled": REAL_DATA_ENABLED,
            "analytics_enabled": ANALYTICS_ENABLED,
            "database_enabled": DATABASE_ENABLED,
            "pdf_reports_enabled": PDF_REPORTS_ENABLED,
            "auth_enabled": AUTH_ENABLED
        }
    })


# ==================== NEW ENDPOINTS FOR GEOFENCE & KAGGLE ====================

@app.route("/api/drones")
def get_kaggle_drones():
    """Get real detection data with GPS and geofence checking"""
    try:
        if not GEOFENCE_ENABLED:
            return jsonify({"error": "Geofence module not available"}), 503
        
        # Get real detection data from YOLOv8 + GPS
        if REAL_DATA_ENABLED:
            inf = get_inference()
            drone_data = get_real_drone_data(inference_engine=inf, sample_size=50)
            logger.info(f"📊 Using REAL detection data: {len(drone_data)} objects")
        else:
            # Fallback to mock data
            drone_data = get_drone_data(sample_size=10)
            logger.info(f"📊 Using MOCK data: {len(drone_data)} objects")
        
        # Add geofence breach information
        for drone in drone_data:
            # Ensure lat/lon exist
            if "lat" not in drone or "lon" not in drone:
                import random
                drone["lat"] = round(12.9500 + random.uniform(0, 0.1), 6)
                drone["lon"] = round(77.5000 + random.uniform(0, 0.15), 6)
                drone["altitude"] = round(random.uniform(50, 200), 2)
            
            # Check breach
            breach_info = check_drone_breach(drone)
            drone["breach_info"] = breach_info
            drone["in_safe_zone"] = breach_info.get("in_safe_zone", True)
        
        return jsonify(drone_data)
        
    except Exception as e:
        logger.error(f"Error fetching drone data: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/geofence/alerts")
def get_geofence_alerts():
    """Get alerts for drones breaching geofence"""
    try:
        if not GEOFENCE_ENABLED:
            return jsonify({"alerts": []})
        
        # Get real detection data
        if REAL_DATA_ENABLED:
            inf = get_inference()
            drone_data = get_real_drone_data(inference_engine=inf, sample_size=50)
            logger.info(f"🚨 Checking REAL detections for breaches: {len(drone_data)} objects")
        else:
            drone_data = get_drone_data(sample_size=20)
            logger.info(f"🚨 Checking MOCK data for breaches: {len(drone_data)} objects")
        
        alerts = []
        
        for drone in drone_data:
            # Ensure location data
            if "lat" not in drone or "lon" not in drone:
                import random
                drone["lat"] = round(12.9500 + random.uniform(-0.05, 0.15), 6)
                drone["lon"] = round(77.5000 + random.uniform(-0.05, 0.2), 6)
                drone["altitude"] = round(random.uniform(50, 250), 2)
            
            # Check for breach
            breach_info = check_drone_breach(drone)
            
            if breach_info.get("breached", False):
                alert_data = {
                    "id": drone.get("id", "unknown"),
                    "drone_id": drone.get("id", "unknown"),
                    "message": breach_info.get("message", "Geofence breach detected"),
                    "violations": breach_info.get("violations", []),
                    "location": breach_info.get("location", {}),
                    "distance_to_center_m": breach_info.get("distance_to_center_m", 0),
                    "timestamp": datetime.now().isoformat(),
                    "severity": "high",
                    "type": "geofence_breach"
                }
                
                # Add detection metadata if available
                if "class_name" in drone:
                    alert_data["detected_class"] = drone["class_name"]
                if "confidence" in drone:
                    alert_data["confidence"] = drone["confidence"]
                if "detection_type" in drone:
                    alert_data["data_source"] = drone["detection_type"]
                
                alerts.append(alert_data)
        
        return jsonify({"alerts": alerts, "total": len(alerts)})
        
    except Exception as e:
        logger.error(f"Error getting geofence alerts: {e}")
        return jsonify({"alerts": [], "error": str(e)})


@app.route("/api/geofence/zones")
def get_zones():
    """Get all configured geofence zones"""
    try:
        if not GEOFENCE_ENABLED:
            return jsonify({"zones": {}})
        
        zones = get_all_zones()
        return jsonify({
            "zones": zones,
            "default_zone": "bangalore_central",
            "total_zones": len(zones)
        })
        
    except Exception as e:
        logger.error(f"Error getting zones: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/dataset/stats")
def get_dataset_stats():
    """Get statistics about the Kaggle dataset"""
    try:
        if not GEOFENCE_ENABLED:
            return jsonify({"error": "Kaggle module not available"}), 503
        
        stats = get_drone_statistics()
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting dataset stats: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/dataset/download", methods=["POST"])
def trigger_dataset_download():
    """Trigger Kaggle dataset download"""
    try:
        if not GEOFENCE_ENABLED:
            return jsonify({"error": "Kaggle module not available"}), 503
        
        logger.info("📥 Starting Kaggle dataset download...")
        success = download_drone_dataset()
        
        if success:
            stats = get_drone_statistics()
            return jsonify({
                "success": True,
                "message": "Dataset downloaded successfully",
                "stats": stats
            })
        else:
            return jsonify({
                "success": False,
                "message": "Failed to download dataset. Check Kaggle API credentials."
            }), 500
            
    except Exception as e:
        logger.error(f"Error downloading dataset: {e}")
        return jsonify({"error": str(e)}), 500


# ==================== ANALYTICS ENDPOINT ====================

@app.route("/api/analytics")
def get_analytics():
    """Get system analytics and metrics"""
    try:
        if not ANALYTICS_ENABLED:
            # Return mock analytics if module not available
            return jsonify({
                "total_detections": 0,
                "total_breaches": 0,
                "active_objects": 0,
                "avg_response_time": 0,
                "detection_by_class": {},
                "threat_distribution": {"LOW": 0, "MEDIUM": 0, "HIGH": 0},
                "hourly_activity": [0] * 24,
                "zone_status": {},
                "recent_events": []
            })
        
        time_range = request.args.get('range', '24h')
        analytics_engine = get_analytics_engine()
        
        # Record current detections
        if REAL_DATA_ENABLED:
            inf = get_inference()
            drone_data = get_real_drone_data(inference_engine=inf, sample_size=50)
            
            for detection in drone_data:
                analytics_engine.record_detection(detection)
                
                # Record breaches
                if not detection.get('in_safe_zone', True):
                    analytics_engine.record_breach(detection)
        
        analytics = analytics_engine.get_analytics(time_range)
        return jsonify(analytics)
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        return jsonify({"error": str(e)}), 500


# ==================== HISTORY & DATABASE ENDPOINTS ====================

@app.route("/api/history/detections")
def get_detection_history():
    """Get historical detection data with filters"""
    if not DATABASE_ENABLED:
        return jsonify({"error": "Database not available"}), 503
    
    try:
        db = get_database_manager()
        
        # Parse query parameters
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        class_name = request.args.get('class_name')
        object_id = request.args.get('object_id')
        search = request.args.get('search')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Convert datetime strings
        from datetime import datetime as dt
        start_dt = dt.fromisoformat(start_time) if start_time else None
        end_dt = dt.fromisoformat(end_time) if end_time else None
        
        # Get detections
        detections = db.get_detections(
            start_time=start_dt,
            end_time=end_dt,
            class_name=class_name,
            object_id=object_id,
            limit=limit,
            offset=offset
        )
        
        # Get total count
        total = db.get_detection_count(
            start_time=start_dt,
            end_time=end_dt,
            class_name=class_name
        )
        
        # Get statistics
        statistics = db.get_detection_statistics(hours=24)
        
        return jsonify({
            "detections": detections,
            "total": total,
            "statistics": statistics,
            "page": {
                "limit": limit,
                "offset": offset
            }
        })
    except Exception as e:
        logger.error(f"Detection history error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/history/breaches")
def get_breach_history():
    """Get historical breach data with filters"""
    if not DATABASE_ENABLED:
        return jsonify({"error": "Database not available"}), 503
    
    try:
        db = get_database_manager()
        
        # Parse query parameters
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        zone_name = request.args.get('zone_name')
        threat_level = request.args.get('threat_level')
        resolved = request.args.get('resolved')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Convert parameters
        from datetime import datetime as dt
        start_dt = dt.fromisoformat(start_time) if start_time else None
        end_dt = dt.fromisoformat(end_time) if end_time else None
        resolved_bool = None if resolved is None else (resolved.lower() == 'true')
        
        # Get breaches
        breaches = db.get_breaches(
            start_time=start_dt,
            end_time=end_dt,
            zone_name=zone_name,
            threat_level=threat_level,
            resolved=resolved_bool,
            limit=limit,
            offset=offset
        )
        
        # Get total count
        total = db.get_breach_count(
            start_time=start_dt,
            end_time=end_dt,
            zone_name=zone_name,
            threat_level=threat_level,
            resolved=resolved_bool
        )
        
        # Get statistics
        statistics = db.get_breach_statistics(hours=24)
        
        return jsonify({
            "breaches": breaches,
            "total": total,
            "statistics": statistics,
            "page": {
                "limit": limit,
                "offset": offset
            }
        })
    except Exception as e:
        logger.error(f"Breach history error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/history/breaches/<int:breach_id>/resolve", methods=["POST"])
def resolve_breach(breach_id):
    """Mark a breach as resolved"""
    if not DATABASE_ENABLED:
        return jsonify({"error": "Database not available"}), 503
    
    try:
        db = get_database_manager()
        data = request.get_json()
        
        resolved_by = data.get('resolved_by', 'unknown')
        notes = data.get('notes', '')
        
        success = db.resolve_breach(breach_id, resolved_by, notes)
        
        if success:
            return jsonify({"success": True, "message": "Breach resolved"})
        else:
            return jsonify({"error": "Breach not found"}), 404
    except Exception as e:
        logger.error(f"Resolve breach error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/history/detections/export")
def export_detections():
    """Export detection data as CSV or JSON"""
    if not DATABASE_ENABLED:
        return jsonify({"error": "Database not available"}), 503
    
    try:
        db = get_database_manager()
        format_type = request.args.get('format', 'csv')
        
        # Get filters
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        class_name = request.args.get('class_name')
        
        from datetime import datetime as dt
        start_dt = dt.fromisoformat(start_time) if start_time else None
        end_dt = dt.fromisoformat(end_time) if end_time else None
        
        # Get all detections (no pagination for export)
        detections = db.get_detections(
            start_time=start_dt,
            end_time=end_dt,
            class_name=class_name,
            limit=10000
        )
        
        if format_type == 'csv':
            import csv
            from io import StringIO
            
            output = StringIO()
            if detections:
                writer = csv.DictWriter(output, fieldnames=detections[0].keys())
                writer.writeheader()
                writer.writerows(detections)
            
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={"Content-Disposition": "attachment;filename=detections.csv"}
            )
        else:
            return jsonify(detections)
    except Exception as e:
        logger.error(f"Export error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/history/breaches/export")
def export_breaches():
    """Export breach data as CSV or JSON"""
    if not DATABASE_ENABLED:
        return jsonify({"error": "Database not available"}), 503
    
    try:
        db = get_database_manager()
        format_type = request.args.get('format', 'csv')
        
        # Get filters
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        zone_name = request.args.get('zone_name')
        threat_level = request.args.get('threat_level')
        
        from datetime import datetime as dt
        start_dt = dt.fromisoformat(start_time) if start_time else None
        end_dt = dt.fromisoformat(end_time) if end_time else None
        
        # Get all breaches (no pagination for export)
        breaches = db.get_breaches(
            start_time=start_dt,
            end_time=end_dt,
            zone_name=zone_name,
            threat_level=threat_level,
            limit=10000
        )
        
        if format_type == 'csv':
            import csv
            from io import StringIO
            
            output = StringIO()
            if breaches:
                # Flatten violations for CSV
                for breach in breaches:
                    if isinstance(breach.get('violations'), list):
                        breach['violations'] = ', '.join(breach['violations'])
                
                writer = csv.DictWriter(output, fieldnames=breaches[0].keys())
                writer.writeheader()
                writer.writerows(breaches)
            
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={"Content-Disposition": "attachment;filename=breaches.csv"}
            )
        else:
            return jsonify(breaches)
    except Exception as e:
        logger.error(f"Export error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/database/stats")
def get_database_stats():
    """Get database statistics"""
    if not DATABASE_ENABLED:
        return jsonify({"error": "Database not available"}), 503
    
    try:
        db = get_database_manager()
        stats = db.get_database_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Database stats error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/heatmap")
def get_heatmap_data():
    """Aggregate detection or breach coordinates for heatmap visualization"""
    if not DATABASE_ENABLED:
        return jsonify({"error": "Database not available"}), 503
    try:
        db = get_database_manager()
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        class_name = request.args.get('class_name')
        zone_name = request.args.get('zone_name')
        threat_level = request.args.get('threat_level')
        type_ = request.args.get('type', 'detections')  # 'detections' or 'breaches'
        
        from datetime import datetime as dt
        start_dt = dt.fromisoformat(start_time) if start_time else None
        end_dt = dt.fromisoformat(end_time) if end_time else None
        points = []
        if type_ == 'detections':
            detections = db.get_detections(
                start_time=start_dt,
                end_time=end_dt,
                class_name=class_name,
                limit=10000
            )
            for d in detections:
                # [lat, lon, intensity]
                points.append([
                    float(d['latitude']),
                    float(d['longitude']),
                    float(d.get('confidence', 1.0))
                ])
        else:
            breaches = db.get_breaches(
                start_time=start_dt,
                end_time=end_dt,
                zone_name=zone_name,
                threat_level=threat_level,
                limit=10000
            )
            for b in breaches:
                intensity = 1.0
                if b['threat_level'] == 'HIGH':
                    intensity = 1.0
                elif b['threat_level'] == 'MEDIUM':
                    intensity = 0.7
                else:
                    intensity = 0.4
                points.append([
                    float(b['latitude']),
                    float(b['longitude']),
                    intensity
                ])
        return jsonify({"points": points})
    except Exception as e:
        logger.error(f"Heatmap error: {e}")
        return jsonify({"error": str(e)}), 500


# ==================== PDF REPORT ENDPOINTS ====================

@app.route("/api/reports/detections/pdf")
def generate_detection_pdf():
    """Generate PDF report for detections"""
    if not DATABASE_ENABLED or not PDF_REPORTS_ENABLED:
        return jsonify({"error": "PDF reports not available"}), 503
    
    try:
        db = get_database_manager()
        report_gen = get_report_generator()
        
        # Parse filters
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        class_name = request.args.get('class_name')
        
        from datetime import datetime as dt
        start_dt = dt.fromisoformat(start_time) if start_time else None
        end_dt = dt.fromisoformat(end_time) if end_time else None
        
        # Get data
        detections = db.get_detections(
            start_time=start_dt,
            end_time=end_dt,
            class_name=class_name,
            limit=1000
        )
        
        statistics = db.get_detection_statistics(hours=24)
        
        filters = {
            'start_date': start_time.split('T')[0] if start_time else 'N/A',
            'end_date': end_time.split('T')[0] if end_time else 'N/A',
            'class_name': class_name or 'All'
        }
        
        # Generate PDF
        pdf_buffer = report_gen.generate_detection_report(detections, statistics, filters)
        
        return Response(
            pdf_buffer.getvalue(),
            mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment;filename=detection_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'}
        )
    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/reports/breaches/pdf")
def generate_breach_pdf():
    """Generate PDF report for breaches"""
    if not DATABASE_ENABLED or not PDF_REPORTS_ENABLED:
        return jsonify({"error": "PDF reports not available"}), 503
    
    try:
        db = get_database_manager()
        report_gen = get_report_generator()
        
        # Parse filters
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        zone_name = request.args.get('zone_name')
        threat_level = request.args.get('threat_level')
        
        from datetime import datetime as dt
        start_dt = dt.fromisoformat(start_time) if start_time else None
        end_dt = dt.fromisoformat(end_time) if end_time else None
        
        # Get data
        breaches = db.get_breaches(
            start_time=start_dt,
            end_time=end_dt,
            zone_name=zone_name,
            threat_level=threat_level,
            limit=1000
        )
        
        statistics = db.get_breach_statistics(hours=24)
        
        filters = {
            'start_date': start_time.split('T')[0] if start_time else 'N/A',
            'end_date': end_time.split('T')[0] if end_time else 'N/A',
            'zone_name': zone_name or 'All',
            'threat_level': threat_level or 'All'
        }
        
        # Generate PDF
        pdf_buffer = report_gen.generate_breach_report(breaches, statistics, filters)
        
        return Response(
            pdf_buffer.getvalue(),
            mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment;filename=breach_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'}
        )
    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/reports/analytics/pdf")
def generate_analytics_pdf():
    """Generate PDF report for analytics"""
    if not ANALYTICS_ENABLED or not PDF_REPORTS_ENABLED:
        return jsonify({"error": "PDF reports not available"}), 503
    
    try:
        analytics_engine = get_analytics_engine()
        report_gen = get_report_generator()
        
        time_range = request.args.get('range', '24h')
        
        # Get analytics data
        analytics = analytics_engine.get_analytics(time_range)
        
        # Generate PDF
        pdf_buffer = report_gen.generate_analytics_report(analytics, time_range)
        
        return Response(
            pdf_buffer.getvalue(),
            mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment;filename=analytics_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'}
        )
    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        return jsonify({"error": str(e)}), 500


# ==============================================================================


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route("/api/auth/login", methods=["POST"])
def login():
    """Login endpoint - returns JWT tokens"""
    if not AUTH_ENABLED:
        return jsonify({"error": "Authentication not available"}), 503
    
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400
        
        # Get database
        db_manager = get_database_manager()
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Find user
            cursor.execute('SELECT * FROM users WHERE username = ? AND is_active = 1', (username,))
            user = cursor.fetchone()
            
            if not user:
                log_activity(db_manager, username, 'login_failed', 'User not found or inactive')
                return jsonify({"error": "Invalid credentials"}), 401
            
            # Verify password
            user_dict = {
                'id': user[0],
                'username': user[1],
                'password_hash': user[2],
                'email': user[3],
                'role': user[4],
                'created_at': user[5],
                'last_login': user[6],
                'is_active': user[7]
            }
            
            if not verify_password(password, user_dict['password_hash']):
                log_activity(db_manager, username, 'login_failed', 'Invalid password')
                return jsonify({"error": "Invalid credentials"}), 401
            
            # Update last login
            cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', 
                          (datetime.now().isoformat(), user_dict['id']))
            conn.commit()
            
            # Create tokens
            access_token = create_access_token(
                identity=username,
                additional_claims={'role': user_dict['role']}
            )
            refresh_token = create_refresh_token(identity=username)
            
            # Log successful login
            log_activity(db_manager, username, 'login_success', f"Role: {user_dict['role']}")
            
            return jsonify({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'username': user_dict['username'],
                    'email': user_dict['email'],
                    'role': user_dict['role'],
                    'permissions': get_user_permissions(user_dict['role'])
                }
            }), 200
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/auth/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    if not AUTH_ENABLED:
        return jsonify({"error": "Authentication not available"}), 503
    
    try:
        identity = get_jwt_identity()
        
        # Get user role
        db_manager = get_database_manager()
        cursor = db_manager.conn.cursor()
        cursor.execute('SELECT role FROM users WHERE username = ?', (identity,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({"error": "User not found"}), 404
        
        role = result[0]
        
        # Create new access token
        access_token = create_access_token(
            identity=identity,
            additional_claims={'role': role}
        )
        
        return jsonify({'access_token': access_token}), 200
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/auth/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Get current user info"""
    if not AUTH_ENABLED:
        return jsonify({"error": "Authentication not available"}), 503
    
    try:
        identity = get_jwt_identity()
        claims = get_jwt()
        role = claims.get('role', 'viewer')
        
        # Get user details
        db_manager = get_database_manager()
        cursor = db_manager.conn.cursor()
        cursor.execute('SELECT username, email, role, created_at, last_login FROM users WHERE username = ?', 
                      (identity,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            'username': user[0],
            'email': user[1],
            'role': user[2],
            'permissions': get_user_permissions(user[2]),
            'created_at': user[3],
            'last_login': user[4]
        }), 200
        
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/auth/logout", methods=["POST"])
@jwt_required()
def logout():
    """Logout endpoint - log the activity"""
    if not AUTH_ENABLED:
        return jsonify({"error": "Authentication not available"}), 503
    
    try:
        identity = get_jwt_identity()
        
        # Log logout
        db_manager = get_database_manager()
        log_activity(db_manager.conn, identity, 'logout', 'User logged out')
        
        return jsonify({"message": "Logged out successfully"}), 200
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/users", methods=["GET"])
@role_required('admin')
def get_users():
    """Get all users (admin only)"""
    if not AUTH_ENABLED:
        return jsonify({"error": "Authentication not available"}), 503
    
    try:
        db_manager = get_database_manager()
        cursor = db_manager.conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, role, created_at, last_login, is_active
            FROM users
            ORDER BY created_at DESC
        ''')
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'role': row[3],
                'created_at': row[4],
                'last_login': row[5],
                'is_active': row[6]
            })
        
        return jsonify(users), 200
        
    except Exception as e:
        logger.error(f"Get users error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/users", methods=["POST"])
@role_required('admin')
def create_user():
    """Create a new user (admin only)"""
    if not AUTH_ENABLED:
        return jsonify({"error": "Authentication not available"}), 503
    
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        role = data.get('role', 'viewer')
        
        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400
        
        if role not in ROLES:
            return jsonify({"error": f"Invalid role. Must be one of: {', '.join(ROLES.keys())}"}), 400
        
        # Hash password
        password_hash = hash_password(password)
        
        # Create user
        db_manager = get_database_manager()
        cursor = db_manager.conn.cursor()
        
        cursor.execute('''
            INSERT INTO users (username, password_hash, email, role, created_at, is_active)
            VALUES (?, ?, ?, ?, ?, 1)
        ''', (username, password_hash, email, role, datetime.now().isoformat()))
        
        db_manager.conn.commit()
        
        # Log activity
        identity = get_jwt_identity()
        log_activity(db_manager.conn, identity, 'user_created', f"Created user: {username} (role: {role})")
        
        return jsonify({
            "message": "User created successfully",
            "username": username,
            "role": role
        }), 201
        
    except Exception as e:
        logger.error(f"Create user error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/users/<int:user_id>", methods=["PUT"])
@role_required('admin')
def update_user(user_id):
    """Update a user (admin only)"""
    if not AUTH_ENABLED:
        return jsonify({"error": "Authentication not available"}), 503
    
    try:
        data = request.get_json()
        
        db_manager = get_database_manager()
        cursor = db_manager.conn.cursor()
        
        # Build update query
        updates = []
        params = []
        
        if 'email' in data:
            updates.append('email = ?')
            params.append(data['email'])
        
        if 'role' in data:
            if data['role'] not in ROLES:
                return jsonify({"error": f"Invalid role. Must be one of: {', '.join(ROLES.keys())}"}), 400
            updates.append('role = ?')
            params.append(data['role'])
        
        if 'is_active' in data:
            updates.append('is_active = ?')
            params.append(1 if data['is_active'] else 0)
        
        if 'password' in data:
            password_hash = hash_password(data['password'])
            updates.append('password_hash = ?')
            params.append(password_hash)
        
        if not updates:
            return jsonify({"error": "No fields to update"}), 400
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        
        cursor.execute(query, params)
        db_manager.conn.commit()
        
        # Log activity
        identity = get_jwt_identity()
        log_activity(db_manager.conn, identity, 'user_updated', f"Updated user ID: {user_id}")
        
        return jsonify({"message": "User updated successfully"}), 200
        
    except Exception as e:
        logger.error(f"Update user error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/activity-logs", methods=["GET"])
@role_required('admin')
def get_activity_logs():
    """Get activity logs (admin only)"""
    if not AUTH_ENABLED:
        return jsonify({"error": "Authentication not available"}), 503
    
    try:
        limit = request.args.get('limit', 100, type=int)
        username = request.args.get('username', None)
        
        db_manager = get_database_manager()
        cursor = db_manager.conn.cursor()
        
        if username:
            cursor.execute('''
                SELECT id, username, action, details, timestamp
                FROM activity_logs
                WHERE username = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (username, limit))
        else:
            cursor.execute('''
                SELECT id, username, action, details, timestamp
                FROM activity_logs
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
        
        logs = []
        for row in cursor.fetchall():
            logs.append({
                'id': row[0],
                'username': row[1],
                'action': row[2],
                'details': row[3],
                'timestamp': row[4]
            })
        
        return jsonify(logs), 200
        
    except Exception as e:
        logger.error(f"Get activity logs error: {e}")
        return jsonify({"error": str(e)}), 500


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500


def main():
    """Run Flask server"""
    # Use PORT from environment (for Render/Heroku) or default
    port = int(os.environ.get("PORT", SERVER_CONFIG["port"]))
    host = os.environ.get("HOST", SERVER_CONFIG["host"])
    
    print("🚁 AI-Based Drone Surveillance System - Backend Server")
    print("="*60)
    print(f"🌐 Starting server on {host}:{port}")
    print(f"📡 Video source: {VIDEO_CONFIG['source']}")
    print("="*60)
    
    # Initialize database and default users
    if DATABASE_ENABLED and AUTH_ENABLED:
        try:
            db_manager = get_database_manager()
            init_default_users(db_manager)
            print("✅ Authentication system initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize authentication: {e}")
    
    # Initialize inference on startup
    try:
        get_inference()
    except Exception as e:
        logger.warning(f"⚠️ Could not initialize inference on startup: {e}")
        logger.info("   Inference will be initialized on first request")
    
    # Run Flask server
    app.run(
        host=host,
        port=port,
        debug=SERVER_CONFIG["debug"],
        threaded=SERVER_CONFIG["threaded"]
    )


if __name__ == "__main__":
    main()

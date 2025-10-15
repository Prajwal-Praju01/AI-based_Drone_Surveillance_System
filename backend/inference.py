"""
Real-time Inference Module
Performs object detection and tracking on video stream
"""
import cv2
import numpy as np
from pathlib import Path
import time
from datetime import datetime
from collections import deque
import torch
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort

from config import (
    MODELS_DIR, MODEL_CONFIG, DEEPSORT_CONFIG,
    RESTRICTED_ZONES, CLASS_NAMES, VIDEO_CONFIG
)


class DroneInference:
    """Real-time object detection and tracking for drone surveillance"""
    
    def __init__(self, model_path=None, video_source=0):
        self.model_path = model_path or self._find_best_model()
        self.video_source = video_source
        self.model = None
        self.tracker = None
        self.detections_history = deque(maxlen=200)  # Increased for better history
        self.alerts_history = deque(maxlen=100)  # Increased for better alert tracking
        self.fps_history = deque(maxlen=30)
        self.frame_count = 0
        self.skip_frames = 1  # Process every frame (set to 2 to skip every other frame)
        self.last_detections = []  # Cache last frame's detections
        
        self._initialize_model()
        self._initialize_tracker()
    
    def _find_best_model(self):
        """Find the best trained model"""
        # Look for custom trained model
        best_models = list(MODELS_DIR.rglob("best.pt"))
        if best_models:
            print(f"✅ Found trained model: {best_models[0]}")
            return str(best_models[0])
        
        # Fall back to pre-trained model
        print("⚠️ No custom model found, using pre-trained YOLOv8")
        return f"{MODEL_CONFIG['model_name']}.pt"
    
    def _initialize_model(self):
        """Initialize YOLO model"""
        print(f"📥 Loading model: {self.model_path}")
        
        # Fix for PyTorch 2.6+ weights_only issue
        # Temporarily disable weights_only for trusted YOLO models
        import torch
        original_load = torch.load
        torch.load = lambda *args, **kwargs: original_load(*args, **{**kwargs, 'weights_only': False})
        
        try:
            self.model = YOLO(self.model_path)
            
            # Set model parameters
            self.model.conf = MODEL_CONFIG["conf_threshold"]
            self.model.iou = MODEL_CONFIG["iou_threshold"]
            
            print(f"✅ Model loaded successfully")
        finally:
            # Restore original torch.load
            torch.load = original_load
    
    def _initialize_tracker(self):
        """Initialize DeepSORT tracker"""
        print("📥 Initializing DeepSORT tracker...")
        self.tracker = DeepSort(
            max_age=DEEPSORT_CONFIG["max_age"],
            n_init=DEEPSORT_CONFIG["n_init"],
            max_iou_distance=DEEPSORT_CONFIG["max_iou_distance"],
            max_cosine_distance=DEEPSORT_CONFIG["max_cosine_distance"],
            nn_budget=DEEPSORT_CONFIG["nn_budget"],
        )
        print("✅ Tracker initialized")
    
    def is_point_in_zone(self, point, zone_polygon):
        """Check if a point is inside a polygon zone"""
        x, y = point
        polygon = np.array(zone_polygon)
        return cv2.pointPolygonTest(polygon, (float(x), float(y)), False) >= 0
    
    def check_zone_breach(self, bbox, class_name):
        """Check if detection breaches any restricted zone"""
        center_x = (bbox[0] + bbox[2]) / 2
        center_y = (bbox[1] + bbox[3]) / 2
        
        for zone in RESTRICTED_ZONES:
            if class_name in zone["alert_classes"]:
                if self.is_point_in_zone((center_x, center_y), zone["polygon"]):
                    return True, zone["name"]
        
        return False, None
    
    def process_frame(self, frame):
        """Process a single frame with detection and tracking - optimized"""
        start_time = time.time()
        self.frame_count += 1
        
        # Frame skipping for performance (optional)
        if self.skip_frames > 1 and self.frame_count % self.skip_frames != 0:
            # Return previous frame's detections without reprocessing
            if hasattr(self, 'last_processed_frame'):
                return self.last_processed_frame, self.last_detections
        
        # Run YOLO detection
        results = self.model(frame, verbose=False)[0]
        
        # Prepare detections for tracker
        detections = []
        current_frame_detections = []
        
        for box in results.boxes:
            # Extract detection info
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            class_name = results.names[cls]
            
            # Prepare for DeepSORT ([x1, y1, width, height], confidence, class_name)
            width = x2 - x1
            height = y2 - y1
            detections.append(([x1, y1, width, height], conf, class_name))
        
        # Update tracker
        tracks = self.tracker.update_tracks(detections, frame=frame)
        
        # Process tracked objects
        for track in tracks:
            if not track.is_confirmed():
                continue
            
            track_id = track.track_id
            bbox = track.to_ltrb()  # [left, top, right, bottom]
            class_name = track.get_det_class()
            confidence = track.get_det_conf()
            
            # Check zone breach
            is_breach, zone_name = self.check_zone_breach(bbox, class_name)
            zone_status = "BREACH" if is_breach else "SAFE"
            
            # Store detection data
            detection_data = {
                "object_id": track_id,
                "class_name": class_name,
                "confidence": confidence,
                "bbox": bbox.tolist(),
                "zone_status": zone_status,
                "zone_name": zone_name,
                "timestamp": datetime.now().isoformat()
            }
            current_frame_detections.append(detection_data)
            
            # Generate alert if breach detected
            if is_breach:
                alert = {
                    "id": len(self.alerts_history) + 1,
                    "title": f"Zone {zone_name} Breach",
                    "message": f"{class_name.capitalize()} detected in restricted {zone_name}",
                    "severity": "high",
                    "zone": zone_name,
                    "object_class": class_name,
                    "object_id": track_id,
                    "timestamp": datetime.now().isoformat(),
                    "read": False,
                    "dismissed": False
                }
                self.alerts_history.append(alert)
            
            # Draw on frame
            self._draw_detection(frame, bbox, track_id, class_name, confidence, zone_status)
        
        # Draw zones
        self._draw_zones(frame)
        
        # Calculate FPS
        fps = 1 / (time.time() - start_time)
        self.fps_history.append(fps)
        avg_fps = np.mean(self.fps_history)
        
        # Draw FPS and frame counter
        cv2.putText(frame, f"FPS: {avg_fps:.1f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Frames: {self.frame_count}", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Update detections history
        self.detections_history.extend(current_frame_detections)
        
        # Cache for frame skipping
        self.last_processed_frame = frame.copy()
        self.last_detections = current_frame_detections
        
        return frame, current_frame_detections
    
    def _draw_detection(self, frame, bbox, track_id, class_name, confidence, zone_status):
        """Draw detection box and label on frame"""
        x1, y1, x2, y2 = map(int, bbox)
        
        # Choose color based on zone status
        if zone_status == "BREACH":
            color = (0, 0, 255)  # Red
        else:
            color = (0, 255, 0)  # Green
        
        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Draw label
        label = f"ID:{track_id} {class_name} {confidence:.2f}"
        label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
        
        # Label background
        cv2.rectangle(frame, (x1, y1 - label_size[1] - 10),
                     (x1 + label_size[0], y1), color, -1)
        
        # Label text
        cv2.putText(frame, label, (x1, y1 - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # Draw zone status
        if zone_status == "BREACH":
            cv2.putText(frame, "BREACH!", (x1, y2 + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
    def _draw_zones(self, frame):
        """Draw restricted zones on frame"""
        overlay = frame.copy()
        
        for zone in RESTRICTED_ZONES:
            polygon = np.array(zone["polygon"], dtype=np.int32)
            
            # Draw semi-transparent zone
            cv2.fillPoly(overlay, [polygon], (0, 0, 255))
            cv2.polylines(frame, [polygon], True, (0, 0, 255), 2)
            
            # Draw zone name
            x, y = polygon[0]
            cv2.putText(frame, zone["name"], (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Blend overlay with original frame
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
    
    def get_current_detections(self):
        """Get current detections (last 2 seconds) - optimized"""
        if not self.detections_history:
            return []
        
        current_time = datetime.now()
        time_threshold = 2.0  # seconds
        recent_detections = []
        
        # Iterate in reverse (newest first) and stop early
        for detection in reversed(self.detections_history):
            try:
                det_time = datetime.fromisoformat(detection["timestamp"])
                time_diff = (current_time - det_time).total_seconds()
                
                if time_diff <= time_threshold:
                    recent_detections.append(detection)
                else:
                    # Stop early since detections are ordered
                    break
            except (KeyError, ValueError):
                continue
        
        # Limit to 50 most recent to avoid frontend overload
        return recent_detections[:50]
    
    def get_alerts(self):
        """Get all alerts"""
        return list(self.alerts_history)
    
    def run_video_stream(self):
        """Run inference on video stream"""
        print(f"🎥 Starting video stream from: {self.video_source}")
        
        cap = cv2.VideoCapture(self.video_source)
        
        if not cap.isOpened():
            raise Exception(f"Failed to open video source: {self.video_source}")
        
        print("✅ Video stream started. Press 'q' to quit.")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process frame
                processed_frame, detections = self.process_frame(frame)
                
                # Display
                cv2.imshow("Drone Surveillance", processed_frame)
                
                # Quit on 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("\n✅ Video stream stopped")
    
    def process_uploaded_image(self, image_path):
        """Process a single uploaded image and save result"""
        from config import MODELS_DIR
        
        # Read image
        frame = cv2.imread(image_path)
        if frame is None:
            raise Exception(f"Failed to read image: {image_path}")
        
        # Process frame
        processed_frame, detections = self.process_frame(frame)
        
        # Save processed image
        output_dir = Path(__file__).parent / "processed"
        output_dir.mkdir(exist_ok=True)
        
        output_filename = f"processed_{Path(image_path).name}"
        output_path = output_dir / output_filename
        
        cv2.imwrite(str(output_path), processed_frame)
        
        return str(output_path)
    
    def generate_frames(self):
        """Generator for video frames (for Flask streaming) - optimized with FPS limiting"""
        # Check if video source is a file or camera
        is_file = isinstance(self.video_source, str) and Path(self.video_source).exists()
        
        cap = cv2.VideoCapture(self.video_source)
        
        if not cap.isOpened():
            # If file doesn't exist or can't be opened, try default camera
            print(f"⚠️ Could not open {self.video_source}, trying default camera...")
            cap = cv2.VideoCapture(0)
        
        # FPS limiting to reduce CPU usage
        target_fps = 15  # Process at 15 FPS instead of max speed
        frame_time = 1.0 / target_fps
        last_frame_time = time.time()
        
        # JPEG encoding quality (lower = faster, smaller)
        jpeg_quality = 85
        
        try:
            while True:
                # FPS limiting
                current_time = time.time()
                elapsed = current_time - last_frame_time
                if elapsed < frame_time:
                    time.sleep(frame_time - elapsed)
                last_frame_time = time.time()
                
                ret, frame = cap.read()
                
                # If video file ended, loop it
                if not ret and is_file:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                elif not ret:
                    break
                
                # Process frame
                processed_frame, _ = self.process_frame(frame)
                
                # Encode frame to JPEG with quality setting
                ret, buffer = cv2.imencode('.jpg', processed_frame, 
                                          [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality])
                frame_bytes = buffer.tobytes()
                
                # Yield frame in MJPEG format
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        finally:
            cap.release()


def main():
    """Test inference standalone"""
    print("🚁 AI-Based Drone Surveillance System - Real-time Inference")
    print("="*60)
    
    # Initialize inference
    inference = DroneInference(video_source=0)  # Use 0 for webcam
    
    # Run video stream
    inference.run_video_stream()


if __name__ == "__main__":
    main()

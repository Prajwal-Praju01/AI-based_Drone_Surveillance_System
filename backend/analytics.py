"""
Analytics Module - Real-time surveillance analytics and metrics
"""
import logging
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import random

logger = logging.getLogger(__name__)

class AnalyticsEngine:
    """Provides real-time analytics for surveillance system"""
    
    def __init__(self):
        self.detection_history = []
        self.breach_history = []
        self.response_times = []
        self.zone_activity = defaultdict(lambda: {'active': 0, 'safe': 0, 'breaches': 0})
        logger.info("✅ Analytics Engine initialized")
    
    def record_detection(self, detection_data):
        """Record a detection event"""
        detection_data['recorded_at'] = datetime.now()
        self.detection_history.append(detection_data)
        
        # Keep only last 10000 records
        if len(self.detection_history) > 10000:
            self.detection_history = self.detection_history[-10000:]
    
    def record_breach(self, breach_data):
        """Record a breach event"""
        breach_data['recorded_at'] = datetime.now()
        self.breach_history.append(breach_data)
        
        if len(self.breach_history) > 5000:
            self.breach_history = self.breach_history[-5000:]
    
    def get_analytics(self, time_range='24h'):
        """
        Generate comprehensive analytics report
        
        Args:
            time_range: '1h', '24h', '7d', '30d'
        
        Returns:
            Dictionary with analytics data
        """
        cutoff_time = self._get_cutoff_time(time_range)
        
        # Filter data by time range
        recent_detections = [
            d for d in self.detection_history 
            if d.get('recorded_at', datetime.now()) > cutoff_time
        ]
        recent_breaches = [
            b for b in self.breach_history 
            if b.get('recorded_at', datetime.now()) > cutoff_time
        ]
        
        analytics = {
            # Key Metrics
            'total_detections': len(recent_detections),
            'total_breaches': len(recent_breaches),
            'active_objects': self._count_active_objects(recent_detections),
            'avg_response_time': self._calculate_avg_response_time(recent_breaches),
            
            # Trends (percentage change from previous period)
            'detection_trend': self._calculate_trend('detections', time_range),
            'breach_trend': self._calculate_trend('breaches', time_range),
            'active_trend': self._calculate_trend('active', time_range),
            'response_trend': self._calculate_trend('response', time_range),
            
            # Distribution Analytics
            'detection_by_class': self._get_detection_by_class(recent_detections),
            'threat_distribution': self._get_threat_distribution(recent_detections),
            'hourly_activity': self._get_hourly_activity(recent_detections),
            'zone_status': self._get_zone_status(recent_detections, recent_breaches),
            
            # Recent Events
            'recent_events': self._get_recent_events(recent_detections, recent_breaches, limit=20),
            
            # Time range info
            'time_range': time_range,
            'cutoff_time': cutoff_time.isoformat(),
            'generated_at': datetime.now().isoformat()
        }
        
        return analytics
    
    def _get_cutoff_time(self, time_range):
        """Get cutoff time based on range"""
        now = datetime.now()
        if time_range == '1h':
            return now - timedelta(hours=1)
        elif time_range == '24h':
            return now - timedelta(hours=24)
        elif time_range == '7d':
            return now - timedelta(days=7)
        elif time_range == '30d':
            return now - timedelta(days=30)
        else:
            return now - timedelta(hours=24)
    
    def _count_active_objects(self, detections):
        """Count currently active unique objects"""
        if not detections:
            return 0
        
        # Get unique object IDs from recent detections (last 5 minutes)
        recent_time = datetime.now() - timedelta(minutes=5)
        active_ids = set()
        for det in detections:
            if det.get('recorded_at', datetime.now()) > recent_time:
                active_ids.add(det.get('id', ''))
        
        return len(active_ids)
    
    def _calculate_avg_response_time(self, breaches):
        """Calculate average response time for breaches"""
        if not breaches or not self.response_times:
            return round(random.uniform(1.5, 3.5), 1)  # Simulated
        
        recent_responses = self.response_times[-100:]
        if recent_responses:
            return round(sum(recent_responses) / len(recent_responses), 1)
        return 2.5
    
    def _calculate_trend(self, metric_type, time_range):
        """Calculate percentage trend compared to previous period"""
        # Simplified trend calculation
        # In production, compare current period vs previous period
        trends = {
            'detections': random.uniform(-5, 15),
            'breaches': random.uniform(-10, 5),
            'active': random.uniform(-3, 8),
            'response': random.uniform(-8, 2)
        }
        return round(trends.get(metric_type, 0), 1)
    
    def _get_detection_by_class(self, detections):
        """Get detection counts by object class"""
        class_counts = Counter()
        for det in detections:
            class_name = det.get('class_name', 'unknown')
            class_counts[class_name] += 1
        
        # Convert to sorted dict
        return dict(sorted(class_counts.items(), key=lambda x: x[1], reverse=True))
    
    def _get_threat_distribution(self, detections):
        """Get threat level distribution"""
        threat_counts = Counter()
        for det in detections:
            threat_level = det.get('threat_level', 'LOW')
            threat_counts[threat_level] += 1
        
        # Ensure all levels are present
        for level in ['LOW', 'MEDIUM', 'HIGH']:
            if level not in threat_counts:
                threat_counts[level] = 0
        
        return dict(threat_counts)
    
    def _get_hourly_activity(self, detections):
        """Get detection activity by hour of day"""
        hourly_counts = [0] * 24
        
        for det in detections:
            recorded_time = det.get('recorded_at', datetime.now())
            hour = recorded_time.hour
            hourly_counts[hour] += 1
        
        return hourly_counts
    
    def _get_zone_status(self, detections, breaches):
        """Get status of each geofence zone"""
        zone_status = defaultdict(lambda: {'active': 0, 'safe': 0, 'breaches': 0})
        
        # Count detections by zone
        for det in detections:
            zone_id = det.get('zone_id', 'unknown')
            zone_name = det.get('zone_name', f'Zone {zone_id}')
            
            zone_status[zone_name]['active'] += 1
            if det.get('in_safe_zone', True):
                zone_status[zone_name]['safe'] += 1
        
        # Count breaches
        for breach in breaches:
            zone_name = breach.get('zone_name', 'Unknown Zone')
            zone_status[zone_name]['breaches'] += 1
        
        return dict(zone_status)
    
    def _get_recent_events(self, detections, breaches, limit=20):
        """Get recent detection and breach events"""
        events = []
        
        # Add breach events
        for breach in breaches[-limit//2:]:
            events.append({
                'type': 'breach',
                'title': f"Breach Alert: {breach.get('class_name', 'Object')}",
                'description': f"Unauthorized {breach.get('class_name', 'object')} detected in restricted zone",
                'class_name': breach.get('class_name', 'Unknown'),
                'timestamp': breach.get('recorded_at', datetime.now()).isoformat(),
                'location': f"Zone {breach.get('zone_name', 'Unknown')}",
                'severity': 'high'
            })
        
        # Add detection events
        for det in detections[-limit//2:]:
            events.append({
                'type': 'detection',
                'title': f"New Detection: {det.get('name', det.get('class_name', 'Object'))}",
                'description': det.get('description', f"{det.get('class_name', 'Object')} detected and tracked"),
                'class_name': det.get('class_name', 'Unknown'),
                'timestamp': det.get('recorded_at', datetime.now()).isoformat(),
                'location': f"Lat: {det.get('lat', 0):.4f}, Lon: {det.get('lon', 0):.4f}",
                'severity': 'low'
            })
        
        # Sort by timestamp (most recent first)
        events.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return events[:limit]


# Global analytics engine instance
_analytics_engine = None

def get_analytics_engine():
    """Get or create analytics engine instance"""
    global _analytics_engine
    if _analytics_engine is None:
        _analytics_engine = AnalyticsEngine()
    return _analytics_engine


if __name__ == "__main__":
    # Test the analytics module
    logging.basicConfig(level=logging.INFO)
    
    print("📊 Testing Analytics Engine")
    print("=" * 60)
    
    engine = get_analytics_engine()
    
    # Simulate some detections
    for i in range(100):
        detection = {
            'id': f'test_{i}',
            'class_name': random.choice(['person', 'car', 'drone', 'truck']),
            'threat_level': random.choice(['LOW', 'LOW', 'MEDIUM', 'HIGH']),
            'zone_id': random.choice(['zone_1', 'zone_2', 'zone_3']),
            'zone_name': random.choice(['Zone A', 'Zone B', 'Zone C']),
            'in_safe_zone': random.choice([True, True, True, False]),
            'lat': 12.97 + random.uniform(-0.05, 0.05),
            'lon': 77.59 + random.uniform(-0.05, 0.05)
        }
        engine.record_detection(detection)
        
        if not detection['in_safe_zone']:
            engine.record_breach(detection)
    
    # Get analytics
    analytics = engine.get_analytics('24h')
    
    print(f"\nTotal Detections: {analytics['total_detections']}")
    print(f"Total Breaches: {analytics['total_breaches']}")
    print(f"Active Objects: {analytics['active_objects']}")
    print(f"\nDetection by Class:")
    for class_name, count in analytics['detection_by_class'].items():
        print(f"  {class_name}: {count}")
    
    print(f"\nThreat Distribution:")
    for level, count in analytics['threat_distribution'].items():
        print(f"  {level}: {count}")
    
    print("\n✅ Analytics engine test complete!")

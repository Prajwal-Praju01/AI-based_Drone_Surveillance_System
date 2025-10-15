"""
Populate database with sample historical data for testing.
Run this script once to create sample detection and breach records.
"""

import sys
import os
from datetime import datetime, timedelta
import random
import logging

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from database import get_database_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample data configurations
OBJECT_CLASSES = ['person', 'car', 'truck', 'bicycle', 'motorcycle', 'bird', 'drone']
OPERATORS = [
    'Phoenix Aerial Services',
    'Skyward Technologies',
    'Aerial Solutions Inc',
    'DroneWorks Ltd',
    'Unknown Operator',
    'Private Individual',
    'Government Agency'
]
ZONES = ['Restricted Area Alpha', 'Perimeter Zone Beta', 'No-Fly Zone Gamma']
THREAT_LEVELS = ['LOW', 'MEDIUM', 'HIGH']

# Base coordinates (adjust for your location)
BASE_LAT = 37.7749
BASE_LON = -122.4194


def generate_random_detection(timestamp):
    """Generate a random detection record"""
    class_name = random.choice(OBJECT_CLASSES)
    
    return {
        'object_id': f"{class_name}_{random.randint(1000, 9999)}",
        'class_name': class_name,
        'confidence': round(random.uniform(0.75, 0.99), 3),
        'latitude': BASE_LAT + random.uniform(-0.01, 0.01),
        'longitude': BASE_LON + random.uniform(-0.01, 0.01),
        'altitude': round(random.uniform(10, 500), 2),
        'speed': round(random.uniform(0, 80), 2),
        'heading': random.randint(0, 360),
        'operator_name': random.choice(OPERATORS),
        'registration': f"N{random.randint(10000, 99999)}",
        'description': f"{class_name.title()} detected in monitoring area",
        'timestamp': timestamp.isoformat()
    }


def generate_random_breach(detection_id, detection_data, timestamp):
    """Generate a random breach record based on detection"""
    zone = random.choice(ZONES)
    
    # Threat level based on object class
    if detection_data['class_name'] in ['drone', 'person']:
        threat_level = random.choice(['MEDIUM', 'HIGH'])
    elif detection_data['class_name'] in ['truck', 'car']:
        threat_level = random.choice(['LOW', 'MEDIUM'])
    else:
        threat_level = 'LOW'
    
    violations = []
    if detection_data['altitude'] > 400:
        violations.append('altitude_violation')
    if random.random() < 0.3:
        violations.append('unauthorized_entry')
    if random.random() < 0.2:
        violations.append('speed_violation')
    
    if not violations:
        violations = ['perimeter_breach']
    
    return {
        'detection_id': detection_id,
        'object_id': detection_data['object_id'],
        'class_name': detection_data['class_name'],
        'zone_name': zone,
        'threat_level': threat_level,
        'latitude': detection_data['latitude'],
        'longitude': detection_data['longitude'],
        'violations': violations,
        'distance_to_center': round(random.uniform(0, 1000), 2),
        'timestamp': timestamp.isoformat()
    }


def populate_database(days=7, detections_per_day=100, breach_rate=0.15):
    """
    Populate database with sample data.
    
    Args:
        days: Number of days of historical data to generate
        detections_per_day: Number of detections per day
        breach_rate: Percentage of detections that result in breaches
    """
    logger.info("Starting database population...")
    logger.info(f"Generating {days} days of data with {detections_per_day} detections/day")
    
    db = get_database_manager()
    
    # Log system event
    db.log_system_event(
        event_type='data_population',
        severity='info',
        message='Starting sample data population',
        details={'days': days, 'detections_per_day': detections_per_day}
    )
    
    detection_count = 0
    breach_count = 0
    
    # Generate data for each day
    for day in range(days):
        day_start = datetime.now() - timedelta(days=days-day)
        
        # Generate detections throughout the day
        for i in range(detections_per_day):
            # Random time during the day
            hours = random.randint(0, 23)
            minutes = random.randint(0, 59)
            seconds = random.randint(0, 59)
            
            timestamp = day_start.replace(
                hour=hours,
                minute=minutes,
                second=seconds,
                microsecond=0
            )
            
            # Generate detection
            detection_data = generate_random_detection(timestamp)
            detection_id = db.log_detection(detection_data)
            detection_count += 1
            
            # Randomly generate breaches
            if random.random() < breach_rate:
                breach_data = generate_random_breach(detection_id, detection_data, timestamp)
                breach_id = db.log_breach(breach_data)
                breach_count += 1
                
                # Randomly resolve some older breaches
                if day < days - 1 and random.random() < 0.7:
                    db.resolve_breach(
                        breach_id,
                        resolved_by='system_operator',
                        notes='Resolved during routine patrol'
                    )
            
            # Progress indicator
            if (detection_count % 100) == 0:
                logger.info(f"Generated {detection_count} detections, {breach_count} breaches...")
    
    # Log completion
    db.log_system_event(
        event_type='data_population',
        severity='info',
        message='Sample data population completed',
        details={
            'total_detections': detection_count,
            'total_breaches': breach_count
        }
    )
    
    logger.info("=" * 60)
    logger.info("Database population completed!")
    logger.info(f"✅ Total detections created: {detection_count}")
    logger.info(f"✅ Total breaches created: {breach_count}")
    logger.info("=" * 60)
    
    # Show statistics
    stats = db.get_database_stats()
    logger.info("\n📊 Database Statistics:")
    logger.info(f"  - Total records: {stats['total_detections']} detections, {stats['total_breaches']} breaches")
    logger.info(f"  - Database size: {stats['database_size_mb']} MB")
    logger.info(f"  - Database path: {stats['database_path']}")


if __name__ == '__main__':
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description='Populate database with sample surveillance data')
    parser.add_argument('--days', type=int, default=7, help='Number of days of historical data (default: 7)')
    parser.add_argument('--per-day', type=int, default=100, help='Detections per day (default: 100)')
    parser.add_argument('--breach-rate', type=float, default=0.15, help='Breach rate 0-1 (default: 0.15)')
    
    args = parser.parse_args()
    
    try:
        populate_database(
            days=args.days,
            detections_per_day=args.per_day,
            breach_rate=args.breach_rate
        )
    except Exception as e:
        logger.error(f"❌ Error populating database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

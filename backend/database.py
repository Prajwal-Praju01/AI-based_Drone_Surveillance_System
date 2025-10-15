"""
Database module for persistent storage of detection and breach events.
Provides SQLite-based logging with search, filter, and replay capabilities.
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager
import os

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database operations for surveillance system."""
    
    def __init__(self, db_path: str = "surveillance_data.db"):
        """Initialize database manager with specified database path."""
        self.db_path = db_path
        self._initialize_database()
        logger.info(f"Database initialized at: {self.db_path}")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def _initialize_database(self):
        """Create database tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Detections table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS detections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    object_id TEXT NOT NULL,
                    class_name TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    altitude REAL,
                    speed REAL,
                    heading REAL,
                    operator_name TEXT,
                    registration TEXT,
                    description TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON detections(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_class ON detections(class_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_object_id ON detections(object_id)")
            
            # Breaches table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS breaches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    detection_id INTEGER,
                    object_id TEXT NOT NULL,
                    class_name TEXT NOT NULL,
                    zone_name TEXT NOT NULL,
                    threat_level TEXT NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    violations TEXT,
                    distance_to_center REAL,
                    resolved BOOLEAN DEFAULT 0,
                    resolved_at DATETIME,
                    resolved_by TEXT,
                    notes TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (detection_id) REFERENCES detections(id)
                )
            """)
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_breach_timestamp ON breaches(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_breach_zone ON breaches(zone_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_breach_resolved ON breaches(resolved)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_breach_threat ON breaches(threat_level)")
            
            # System events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    details TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_event_type ON system_events(event_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_event_timestamp ON system_events(timestamp)")
            
            logger.info("Database tables initialized successfully")
    
    # ===================== DETECTION OPERATIONS =====================
    
    def log_detection(self, detection_data: Dict) -> int:
        """
        Log a detection event to the database.
        
        Args:
            detection_data: Dictionary containing detection information
            
        Returns:
            ID of the inserted detection record
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO detections (
                    object_id, class_name, confidence, latitude, longitude,
                    altitude, speed, heading, operator_name, registration, description, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                detection_data.get('object_id'),
                detection_data.get('class_name'),
                detection_data.get('confidence'),
                detection_data.get('latitude'),
                detection_data.get('longitude'),
                detection_data.get('altitude'),
                detection_data.get('speed'),
                detection_data.get('heading'),
                detection_data.get('operator_name'),
                detection_data.get('registration'),
                detection_data.get('description'),
                detection_data.get('timestamp', datetime.now().isoformat())
            ))
            
            detection_id = cursor.lastrowid
            logger.debug(f"Logged detection {detection_id}: {detection_data.get('class_name')}")
            return detection_id
    
    def get_detections(self, 
                       start_time: Optional[datetime] = None,
                       end_time: Optional[datetime] = None,
                       class_name: Optional[str] = None,
                       object_id: Optional[str] = None,
                       limit: int = 1000,
                       offset: int = 0) -> List[Dict]:
        """
        Retrieve detections with optional filters.
        
        Args:
            start_time: Filter detections after this time
            end_time: Filter detections before this time
            class_name: Filter by object class
            object_id: Filter by specific object ID
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of detection dictionaries
        """
        query = "SELECT * FROM detections WHERE 1=1"
        params = []
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())
        
        if class_name:
            query += " AND class_name = ?"
            params.append(class_name)
        
        if object_id:
            query += " AND object_id = ?"
            params.append(object_id)
        
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            detections = []
            for row in cursor.fetchall():
                detections.append(dict(row))
            
            logger.info(f"Retrieved {len(detections)} detections")
            return detections
    
    def get_detection_by_id(self, detection_id: int) -> Optional[Dict]:
        """Retrieve a specific detection by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM detections WHERE id = ?", (detection_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_detection_count(self, 
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None,
                           class_name: Optional[str] = None) -> int:
        """Get total count of detections matching filters."""
        query = "SELECT COUNT(*) as count FROM detections WHERE 1=1"
        params = []
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())
        
        if class_name:
            query += " AND class_name = ?"
            params.append(class_name)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()['count']
    
    # ===================== BREACH OPERATIONS =====================
    
    def log_breach(self, breach_data: Dict) -> int:
        """
        Log a breach event to the database.
        
        Args:
            breach_data: Dictionary containing breach information
            
        Returns:
            ID of the inserted breach record
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Convert violations list to JSON string
            violations_json = json.dumps(breach_data.get('violations', []))
            
            cursor.execute("""
                INSERT INTO breaches (
                    detection_id, object_id, class_name, zone_name, threat_level,
                    latitude, longitude, violations, distance_to_center, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                breach_data.get('detection_id'),
                breach_data.get('object_id'),
                breach_data.get('class_name'),
                breach_data.get('zone_name'),
                breach_data.get('threat_level'),
                breach_data.get('latitude'),
                breach_data.get('longitude'),
                violations_json,
                breach_data.get('distance_to_center'),
                breach_data.get('timestamp', datetime.now().isoformat())
            ))
            
            breach_id = cursor.lastrowid
            logger.warning(f"Logged breach {breach_id}: {breach_data.get('zone_name')} - {breach_data.get('threat_level')}")
            return breach_id
    
    def get_breaches(self,
                     start_time: Optional[datetime] = None,
                     end_time: Optional[datetime] = None,
                     zone_name: Optional[str] = None,
                     threat_level: Optional[str] = None,
                     resolved: Optional[bool] = None,
                     limit: int = 1000,
                     offset: int = 0) -> List[Dict]:
        """
        Retrieve breaches with optional filters.
        
        Args:
            start_time: Filter breaches after this time
            end_time: Filter breaches before this time
            zone_name: Filter by zone name
            threat_level: Filter by threat level (LOW, MEDIUM, HIGH)
            resolved: Filter by resolution status
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of breach dictionaries
        """
        query = "SELECT * FROM breaches WHERE 1=1"
        params = []
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())
        
        if zone_name:
            query += " AND zone_name = ?"
            params.append(zone_name)
        
        if threat_level:
            query += " AND threat_level = ?"
            params.append(threat_level)
        
        if resolved is not None:
            query += " AND resolved = ?"
            params.append(1 if resolved else 0)
        
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            breaches = []
            for row in cursor.fetchall():
                breach = dict(row)
                # Parse violations JSON
                if breach.get('violations'):
                    breach['violations'] = json.loads(breach['violations'])
                breaches.append(breach)
            
            logger.info(f"Retrieved {len(breaches)} breaches")
            return breaches
    
    def resolve_breach(self, breach_id: int, resolved_by: str, notes: str = "") -> bool:
        """
        Mark a breach as resolved.
        
        Args:
            breach_id: ID of the breach to resolve
            resolved_by: Username/identifier of resolver
            notes: Optional resolution notes
            
        Returns:
            True if successful, False otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE breaches 
                SET resolved = 1, 
                    resolved_at = ?,
                    resolved_by = ?,
                    notes = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), resolved_by, notes, breach_id))
            
            success = cursor.rowcount > 0
            if success:
                logger.info(f"Breach {breach_id} resolved by {resolved_by}")
            return success
    
    def get_breach_count(self,
                        start_time: Optional[datetime] = None,
                        end_time: Optional[datetime] = None,
                        resolved: Optional[bool] = None) -> int:
        """Get total count of breaches matching filters."""
        query = "SELECT COUNT(*) as count FROM breaches WHERE 1=1"
        params = []
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())
        
        if resolved is not None:
            query += " AND resolved = ?"
            params.append(1 if resolved else 0)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()['count']
    
    # ===================== SYSTEM EVENTS =====================
    
    def log_system_event(self, event_type: str, severity: str, message: str, details: Dict = None):
        """
        Log a system event (startup, shutdown, errors, etc.).
        
        Args:
            event_type: Type of event (startup, shutdown, error, warning, info)
            severity: Severity level (critical, error, warning, info, debug)
            message: Event message
            details: Optional additional details as dictionary
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            details_json = json.dumps(details) if details else None
            
            cursor.execute("""
                INSERT INTO system_events (event_type, severity, message, details)
                VALUES (?, ?, ?, ?)
            """, (event_type, severity, message, details_json))
            
            logger.debug(f"System event logged: {event_type} - {message}")
    
    def get_system_events(self,
                         start_time: Optional[datetime] = None,
                         event_type: Optional[str] = None,
                         severity: Optional[str] = None,
                         limit: int = 100) -> List[Dict]:
        """Retrieve system events with filters."""
        query = "SELECT * FROM system_events WHERE 1=1"
        params = []
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        
        if severity:
            query += " AND severity = ?"
            params.append(severity)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            events = []
            for row in cursor.fetchall():
                event = dict(row)
                if event.get('details'):
                    event['details'] = json.loads(event['details'])
                events.append(event)
            
            return events
    
    # ===================== ANALYTICS & STATISTICS =====================
    
    def get_detection_statistics(self, hours: int = 24) -> Dict:
        """
        Get aggregated detection statistics for the specified time period.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Dictionary containing various statistics
        """
        start_time = datetime.now() - timedelta(hours=hours)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total detections
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM detections
                WHERE timestamp >= ?
            """, (start_time.isoformat(),))
            total = cursor.fetchone()['total']
            
            # Detections by class
            cursor.execute("""
                SELECT class_name, COUNT(*) as count
                FROM detections
                WHERE timestamp >= ?
                GROUP BY class_name
                ORDER BY count DESC
            """, (start_time.isoformat(),))
            by_class = {row['class_name']: row['count'] for row in cursor.fetchall()}
            
            # Detections by hour
            cursor.execute("""
                SELECT 
                    strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                    COUNT(*) as count
                FROM detections
                WHERE timestamp >= ?
                GROUP BY hour
                ORDER BY hour
            """, (start_time.isoformat(),))
            by_hour = {row['hour']: row['count'] for row in cursor.fetchall()}
            
            # Unique objects
            cursor.execute("""
                SELECT COUNT(DISTINCT object_id) as unique_objects
                FROM detections
                WHERE timestamp >= ?
            """, (start_time.isoformat(),))
            unique_objects = cursor.fetchone()['unique_objects']
            
            return {
                'total_detections': total,
                'unique_objects': unique_objects,
                'by_class': by_class,
                'by_hour': by_hour,
                'time_period_hours': hours
            }
    
    def get_breach_statistics(self, hours: int = 24) -> Dict:
        """Get aggregated breach statistics."""
        start_time = datetime.now() - timedelta(hours=hours)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total breaches
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM breaches
                WHERE timestamp >= ?
            """, (start_time.isoformat(),))
            total = cursor.fetchone()['total']
            
            # Breaches by zone
            cursor.execute("""
                SELECT zone_name, COUNT(*) as count
                FROM breaches
                WHERE timestamp >= ?
                GROUP BY zone_name
                ORDER BY count DESC
            """, (start_time.isoformat(),))
            by_zone = {row['zone_name']: row['count'] for row in cursor.fetchall()}
            
            # Breaches by threat level
            cursor.execute("""
                SELECT threat_level, COUNT(*) as count
                FROM breaches
                WHERE timestamp >= ?
                GROUP BY threat_level
            """, (start_time.isoformat(),))
            by_threat = {row['threat_level']: row['count'] for row in cursor.fetchall()}
            
            # Resolution rate
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN resolved = 1 THEN 1 ELSE 0 END) as resolved
                FROM breaches
                WHERE timestamp >= ?
            """, (start_time.isoformat(),))
            row = cursor.fetchone()
            resolution_rate = (row['resolved'] / row['total'] * 100) if row['total'] > 0 else 0
            
            return {
                'total_breaches': total,
                'by_zone': by_zone,
                'by_threat_level': by_threat,
                'resolution_rate': round(resolution_rate, 2),
                'time_period_hours': hours
            }
    
    # ===================== MAINTENANCE =====================
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """
        Remove old records to maintain database size.
        
        Args:
            days_to_keep: Number of days of data to retain
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Delete old detections
            cursor.execute("DELETE FROM detections WHERE timestamp < ?", (cutoff_date.isoformat(),))
            detections_deleted = cursor.rowcount
            
            # Delete old breaches
            cursor.execute("DELETE FROM breaches WHERE timestamp < ?", (cutoff_date.isoformat(),))
            breaches_deleted = cursor.rowcount
            
            # Delete old system events
            cursor.execute("DELETE FROM system_events WHERE timestamp < ?", (cutoff_date.isoformat(),))
            events_deleted = cursor.rowcount
            
            # Vacuum database to reclaim space
            cursor.execute("VACUUM")
            
            logger.info(f"Cleanup completed: {detections_deleted} detections, {breaches_deleted} breaches, {events_deleted} events deleted")
            
            return {
                'detections_deleted': detections_deleted,
                'breaches_deleted': breaches_deleted,
                'events_deleted': events_deleted
            }
    
    def get_database_stats(self) -> Dict:
        """Get database size and record counts."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) as count FROM detections")
            detection_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM breaches")
            breach_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM system_events")
            event_count = cursor.fetchone()['count']
            
            # Database file size
            db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            db_size_mb = round(db_size / (1024 * 1024), 2)
            
            return {
                'total_detections': detection_count,
                'total_breaches': breach_count,
                'total_events': event_count,
                'database_size_mb': db_size_mb,
                'database_path': self.db_path
            }


# Singleton instance
_db_manager = None

def get_database_manager(db_path: str = "surveillance_data.db") -> DatabaseManager:
    """Get or create the singleton database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(db_path)
    return _db_manager

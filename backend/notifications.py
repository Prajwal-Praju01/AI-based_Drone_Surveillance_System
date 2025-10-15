"""
Notification System - Email and SMS alerts for critical breaches
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class NotificationManager:
    """Manages email and SMS notifications for security alerts"""
    
    def __init__(self):
        # Email configuration (uses environment variables)
        self.email_enabled = os.getenv('EMAIL_NOTIFICATIONS', 'false').lower() == 'true'
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_username)
        self.to_emails = os.getenv('ALERT_EMAILS', '').split(',')
        
        # SMS configuration (Twilio or similar)
        self.sms_enabled = os.getenv('SMS_NOTIFICATIONS', 'false').lower() == 'true'
        self.sms_provider = os.getenv('SMS_PROVIDER', 'twilio')
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID', '')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN', '')
        self.twilio_from_number = os.getenv('TWILIO_FROM_NUMBER', '')
        self.alert_phone_numbers = os.getenv('ALERT_PHONES', '').split(',')
        
        # Notification throttling
        self.last_notification_time = {}
        self.min_notification_interval = 60  # seconds
        
        if self.email_enabled:
            logger.info("✅ Email notifications enabled")
        if self.sms_enabled:
            logger.info("✅ SMS notifications enabled")
    
    def send_breach_alert(self, breach_data):
        """
        Send notification for breach event
        
        Args:
            breach_data: Dictionary with breach information
        """
        # Check if we should send notification (throttling)
        breach_key = f"{breach_data.get('zone_name', 'unknown')}_{breach_data.get('class_name', 'unknown')}"
        if not self._should_notify(breach_key):
            logger.debug(f"Skipping notification for {breach_key} (throttled)")
            return
        
        # Prepare notification content
        subject = f"🚨 BREACH ALERT: {breach_data.get('class_name', 'Object')} in {breach_data.get('zone_name', 'Restricted Zone')}"
        
        message = self._format_breach_message(breach_data)
        
        # Send email
        if self.email_enabled and self.to_emails:
            try:
                self._send_email(subject, message)
                logger.info(f"📧 Email alert sent for breach: {breach_key}")
            except Exception as e:
                logger.error(f"Failed to send email alert: {e}")
        
        # Send SMS
        if self.sms_enabled and self.alert_phone_numbers:
            try:
                sms_message = self._format_sms_message(breach_data)
                self._send_sms(sms_message)
                logger.info(f"📱 SMS alert sent for breach: {breach_key}")
            except Exception as e:
                logger.error(f"Failed to send SMS alert: {e}")
        
        # Update last notification time
        self.last_notification_time[breach_key] = datetime.now()
    
    def _should_notify(self, breach_key):
        """Check if enough time has passed since last notification"""
        last_time = self.last_notification_time.get(breach_key)
        if last_time is None:
            return True
        
        time_since_last = (datetime.now() - last_time).total_seconds()
        return time_since_last >= self.min_notification_interval
    
    def _format_breach_message(self, breach_data):
        """Format detailed breach message for email"""
        message = f"""
SECURITY BREACH DETECTED
========================

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

BREACH DETAILS:
--------------
Object Type: {breach_data.get('class_name', 'Unknown').upper()}
Object Name: {breach_data.get('name', 'N/A')}
Confidence: {breach_data.get('confidence', 0) * 100:.1f}%
Threat Level: {breach_data.get('threat_level', 'MEDIUM')}

LOCATION:
---------
Zone: {breach_data.get('zone_name', 'Unknown Zone')}
Latitude: {breach_data.get('lat', 0):.6f}
Longitude: {breach_data.get('lon', 0):.6f}
Altitude: {breach_data.get('altitude', 0):.1f}m
Speed: {breach_data.get('speed', 0):.1f} km/h
Heading: {breach_data.get('heading', 0)}°

OPERATOR INFORMATION:
--------------------
Operator: {breach_data.get('operator', 'Unknown')}
Registration: {breach_data.get('registration', 'N/A')}

VIOLATIONS:
-----------
"""
        
        violations = breach_data.get('breach_info', {}).get('violations', [])
        if violations:
            for violation in violations:
                message += f"• {violation}\n"
        else:
            message += "• Unauthorized presence in restricted zone\n"
        
        message += """
ACTION REQUIRED:
----------------
1. Verify the breach on the live dashboard
2. Contact security personnel if threat level is HIGH
3. Log incident in security report

Dashboard: http://localhost:3000
API Status: http://localhost:5000/health

---
AI-Based Drone Surveillance System
Automated Security Alert
"""
        return message
    
    def _format_sms_message(self, breach_data):
        """Format concise breach message for SMS"""
        message = f"""🚨 BREACH ALERT
{breach_data.get('class_name', 'Object').upper()} in {breach_data.get('zone_name', 'Zone')}
Threat: {breach_data.get('threat_level', 'MEDIUM')}
Lat: {breach_data.get('lat', 0):.4f}
Lon: {breach_data.get('lon', 0):.4f}
Time: {datetime.now().strftime('%H:%M:%S')}
Check dashboard immediately."""
        return message
    
    def _send_email(self, subject, message):
        """Send email notification"""
        if not self.smtp_username or not self.smtp_password:
            logger.warning("Email credentials not configured")
            return
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = ', '.join([email.strip() for email in self.to_emails if email.strip()])
        msg['Subject'] = subject
        
        # Add body
        msg.attach(MIMEText(message, 'plain'))
        
        # Send email
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            
            text = msg.as_string()
            server.sendmail(self.from_email, [email.strip() for email in self.to_emails if email.strip()], text)
            server.quit()
            
            logger.info("✅ Email sent successfully")
        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            raise
    
    def _send_sms(self, message):
        """Send SMS notification via Twilio"""
        if not self.sms_enabled or not self.twilio_account_sid:
            logger.warning("SMS credentials not configured")
            return
        
        try:
            # Import Twilio client (only if enabled)
            from twilio.rest import Client
            
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            
            # Send to all configured phone numbers
            for phone_number in self.alert_phone_numbers:
                if not phone_number.strip():
                    continue
                
                message_obj = client.messages.create(
                    body=message,
                    from_=self.twilio_from_number,
                    to=phone_number.strip()
                )
                
                logger.info(f"✅ SMS sent to {phone_number}: {message_obj.sid}")
                
        except ImportError:
            logger.error("❌ Twilio library not installed. Run: pip install twilio")
        except Exception as e:
            logger.error(f"❌ Failed to send SMS: {e}")
            raise
    
    def send_system_alert(self, alert_type, message):
        """Send general system alert"""
        subject = f"🔔 System Alert: {alert_type}"
        
        full_message = f"""
SYSTEM NOTIFICATION
===================

Alert Type: {alert_type}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

MESSAGE:
--------
{message}

---
AI-Based Drone Surveillance System
"""
        
        if self.email_enabled:
            try:
                self._send_email(subject, full_message)
            except Exception as e:
                logger.error(f"Failed to send system alert email: {e}")


# Global notification manager instance
_notification_manager = None

def get_notification_manager():
    """Get or create notification manager instance"""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager


if __name__ == "__main__":
    # Test notification system
    logging.basicConfig(level=logging.INFO)
    
    print("📧 Testing Notification System")
    print("=" * 60)
    
    manager = get_notification_manager()
    
    # Test breach alert
    test_breach = {
        'class_name': 'drone',
        'name': 'UAV-Drone',
        'confidence': 0.87,
        'threat_level': 'HIGH',
        'zone_name': 'Restricted Zone A',
        'lat': 12.9716,
        'lon': 77.5946,
        'altitude': 150.0,
        'speed': 45.0,
        'heading': 180,
        'operator': 'Unknown',
        'registration': 'N/A',
        'breach_info': {
            'violations': ['Altitude exceeds maximum', 'Unauthorized operator']
        }
    }
    
    print("\nTest breach data:")
    print(manager._format_breach_message(test_breach))
    
    print("\nTest SMS message:")
    print(manager._format_sms_message(test_breach))
    
    print("\n✅ Notification system test complete!")
    print("\nTo enable notifications, set environment variables:")
    print("  EMAIL_NOTIFICATIONS=true")
    print("  SMTP_USERNAME=your-email@gmail.com")
    print("  SMTP_PASSWORD=your-app-password")
    print("  ALERT_EMAILS=alert1@example.com,alert2@example.com")
    print("\nFor SMS (optional):")
    print("  SMS_NOTIFICATIONS=true")
    print("  TWILIO_ACCOUNT_SID=your-account-sid")
    print("  TWILIO_AUTH_TOKEN=your-auth-token")
    print("  TWILIO_FROM_NUMBER=+1234567890")
    print("  ALERT_PHONES=+1234567890,+0987654321")

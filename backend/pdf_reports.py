"""
PDF Report Generator for Surveillance System
Generates professional PDF reports for detections, breaches, and analytics.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from io import BytesIO
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate PDF reports for surveillance data."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            spaceBefore=12,
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#374151'),
            spaceAfter=6,
        ))
        
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        ))
    
    def generate_detection_report(self, detections, statistics, filters):
        """
        Generate PDF report for detections.
        
        Args:
            detections: List of detection dictionaries
            statistics: Statistics dictionary
            filters: Applied filters dictionary
            
        Returns:
            BytesIO buffer containing PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        story = []
        
        # Title
        title = Paragraph("Detection Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Report metadata
        metadata = [
            ['Report Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Report Type:', 'Detection Log'],
            ['Date Range:', f"{filters.get('start_date', 'N/A')} to {filters.get('end_date', 'N/A')}"],
            ['Total Records:', str(len(detections))],
        ]
        
        if filters.get('class_name'):
            metadata.append(['Filtered by Class:', filters['class_name']])
        
        metadata_table = Table(metadata, colWidths=[2*inch, 4*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e5e7eb')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(metadata_table)
        story.append(Spacer(1, 20))
        
        # Statistics Summary
        if statistics:
            story.append(Paragraph("Statistics Summary", self.styles['SectionHeader']))
            story.append(Spacer(1, 12))
            
            stats_data = [
                ['Metric', 'Value'],
                ['Total Detections', str(statistics.get('total_detections', 0))],
                ['Unique Objects', str(statistics.get('unique_objects', 0))],
                ['Time Period', f"{statistics.get('time_period_hours', 24)} hours"],
            ]
            
            # Add class distribution
            by_class = statistics.get('by_class', {})
            if by_class:
                story.append(Spacer(1, 8))
                story.append(Paragraph("Detection by Class:", self.styles['SubHeader']))
                for class_name, count in sorted(by_class.items(), key=lambda x: x[1], reverse=True):
                    stats_data.append([f"  {class_name.title()}", str(count)])
            
            stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(stats_table)
            story.append(Spacer(1, 20))
        
        # Detection Details
        story.append(Paragraph("Detection Details", self.styles['SectionHeader']))
        story.append(Spacer(1, 12))
        
        if detections:
            # Table headers
            detection_data = [['Time', 'Object ID', 'Class', 'Confidence', 'Location', 'Operator']]
            
            # Add detection rows (limit to first 100 for PDF size)
            for detection in detections[:100]:
                detection_data.append([
                    datetime.fromisoformat(detection['timestamp']).strftime('%Y-%m-%d %H:%M'),
                    detection['object_id'][:15],
                    detection['class_name'].title(),
                    f"{detection['confidence']*100:.1f}%",
                    f"{detection['latitude']:.4f}, {detection['longitude']:.4f}",
                    detection.get('operator_name', 'Unknown')[:20],
                ])
            
            if len(detections) > 100:
                detection_data.append(['...', '...', '...', '...', '...', '...'])
                detection_data.append([f"Showing first 100 of {len(detections)} records", '', '', '', '', ''])
            
            detection_table = Table(detection_data, colWidths=[1.2*inch, 1*inch, 0.8*inch, 0.8*inch, 1.5*inch, 1.2*inch])
            detection_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')]),
            ]))
            story.append(detection_table)
        else:
            story.append(Paragraph("No detections found for the selected criteria.", self.styles['Normal']))
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
        story.append(Spacer(1, 6))
        footer = Paragraph("AI-Based Drone Surveillance System | Report Generated Automatically", self.styles['Footer'])
        story.append(footer)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_breach_report(self, breaches, statistics, filters):
        """Generate PDF report for breaches."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        story = []
        
        # Title
        title = Paragraph("🚨 Breach Incident Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Report metadata
        metadata = [
            ['Report Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Report Type:', 'Breach Incident Log'],
            ['Date Range:', f"{filters.get('start_date', 'N/A')} to {filters.get('end_date', 'N/A')}"],
            ['Total Incidents:', str(len(breaches))],
        ]
        
        if filters.get('zone_name'):
            metadata.append(['Filtered by Zone:', filters['zone_name']])
        if filters.get('threat_level'):
            metadata.append(['Filtered by Threat:', filters['threat_level']])
        
        metadata_table = Table(metadata, colWidths=[2*inch, 4*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fee2e2')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(metadata_table)
        story.append(Spacer(1, 20))
        
        # Statistics Summary
        if statistics:
            story.append(Paragraph("Incident Statistics", self.styles['SectionHeader']))
            story.append(Spacer(1, 12))
            
            stats_data = [
                ['Metric', 'Value'],
                ['Total Breaches', str(statistics.get('total_breaches', 0))],
                ['Resolution Rate', f"{statistics.get('resolution_rate', 0):.1f}%"],
            ]
            
            # Threat distribution
            by_threat = statistics.get('by_threat_level', {})
            if by_threat:
                stats_data.append(['', ''])
                stats_data.append(['Threat Distribution:', ''])
                for level, count in sorted(by_threat.items()):
                    stats_data.append([f"  {level}", str(count)])
            
            # Zone distribution
            by_zone = statistics.get('by_zone', {})
            if by_zone:
                stats_data.append(['', ''])
                stats_data.append(['Zone Distribution:', ''])
                for zone, count in sorted(by_zone.items(), key=lambda x: x[1], reverse=True):
                    stats_data.append([f"  {zone}", str(count)])
            
            stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fef2f2')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(stats_table)
            story.append(Spacer(1, 20))
        
        # Breach Details
        story.append(Paragraph("Breach Incident Details", self.styles['SectionHeader']))
        story.append(Spacer(1, 12))
        
        if breaches:
            breach_data = [['Time', 'Object', 'Zone', 'Threat', 'Location', 'Status']]
            
            for breach in breaches[:100]:
                # Determine status
                status = '✓ Resolved' if breach.get('resolved') else '⚠ Active'
                
                # Format threat level with color indicator
                threat = breach['threat_level']
                threat_indicator = '🔴' if threat == 'HIGH' else '🟡' if threat == 'MEDIUM' else '🟢'
                
                breach_data.append([
                    datetime.fromisoformat(breach['timestamp']).strftime('%Y-%m-%d %H:%M'),
                    f"{breach['class_name'].title()} ({breach['object_id'][:10]})",
                    breach['zone_name'][:20],
                    f"{threat_indicator} {threat}",
                    f"{breach['latitude']:.4f}, {breach['longitude']:.4f}",
                    status,
                ])
            
            if len(breaches) > 100:
                breach_data.append(['...', '...', '...', '...', '...', '...'])
                breach_data.append([f"Showing first 100 of {len(breaches)} incidents", '', '', '', '', ''])
            
            breach_table = Table(breach_data, colWidths=[1.2*inch, 1.2*inch, 1.3*inch, 0.9*inch, 1.3*inch, 0.9*inch])
            breach_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fef2f2')]),
            ]))
            story.append(breach_table)
        else:
            story.append(Paragraph("No breach incidents found for the selected criteria.", self.styles['Normal']))
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
        story.append(Spacer(1, 6))
        footer = Paragraph("AI-Based Drone Surveillance System | Confidential Report", self.styles['Footer'])
        story.append(footer)
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_analytics_report(self, analytics, time_range):
        """Generate comprehensive analytics report."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        story = []
        
        # Title
        title = Paragraph("Analytics Dashboard Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Report metadata
        metadata = [
            ['Report Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Report Type:', 'System Analytics'],
            ['Time Range:', time_range],
        ]
        
        metadata_table = Table(metadata, colWidths=[2*inch, 4*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#dbeafe')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(metadata_table)
        story.append(Spacer(1, 20))
        
        # Key Metrics
        story.append(Paragraph("Key Performance Indicators", self.styles['SectionHeader']))
        story.append(Spacer(1, 12))
        
        metrics_data = [
            ['Metric', 'Current', 'Trend'],
            ['Total Detections', str(analytics.get('total_detections', 0)), analytics.get('detection_trend', '+0%')],
            ['Total Breaches', str(analytics.get('total_breaches', 0)), analytics.get('breach_trend', '+0%')],
            ['Active Objects', str(analytics.get('active_objects', 0)), analytics.get('active_trend', '+0%')],
            ['Avg Response Time', f"{analytics.get('avg_response_time', 0):.2f}s", analytics.get('response_trend', '+0%')],
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f9ff')]),
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 20))
        
        # Detection by Class
        detection_by_class = analytics.get('detection_by_class', {})
        if detection_by_class:
            story.append(Paragraph("Detection Distribution by Object Class", self.styles['SectionHeader']))
            story.append(Spacer(1, 12))
            
            class_data = [['Object Class', 'Count', 'Percentage']]
            total = sum(detection_by_class.values())
            
            for class_name, count in sorted(detection_by_class.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total * 100) if total > 0 else 0
                class_data.append([
                    class_name.title(),
                    str(count),
                    f"{percentage:.1f}%"
                ])
            
            class_table = Table(class_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
            class_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecfdf5')]),
            ]))
            story.append(class_table)
            story.append(Spacer(1, 20))
        
        # Threat Distribution
        threat_dist = analytics.get('threat_distribution', {})
        if threat_dist:
            story.append(Paragraph("Threat Level Distribution", self.styles['SectionHeader']))
            story.append(Spacer(1, 12))
            
            threat_data = [['Threat Level', 'Count', 'Percentage']]
            total = sum(threat_dist.values())
            
            for level in ['HIGH', 'MEDIUM', 'LOW']:
                count = threat_dist.get(level, 0)
                percentage = (count / total * 100) if total > 0 else 0
                indicator = '🔴' if level == 'HIGH' else '🟡' if level == 'MEDIUM' else '🟢'
                threat_data.append([
                    f"{indicator} {level}",
                    str(count),
                    f"{percentage:.1f}%"
                ])
            
            threat_table = Table(threat_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
            threat_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fef2f2')]),
            ]))
            story.append(threat_table)
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
        story.append(Spacer(1, 6))
        footer = Paragraph("AI-Based Drone Surveillance System | Analytics Report", self.styles['Footer'])
        story.append(footer)
        
        doc.build(story)
        buffer.seek(0)
        return buffer


# Singleton instance
_report_generator = None

def get_report_generator():
    """Get or create the singleton report generator instance."""
    global _report_generator
    if _report_generator is None:
        _report_generator = ReportGenerator()
    return _report_generator

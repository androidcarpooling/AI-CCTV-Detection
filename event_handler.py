"""Event handling system for face recognition events."""
import json
import logging
import requests
from datetime import datetime
from typing import Dict, Optional, List
from config import Config

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EventHandler:
    """Handle face recognition events (alerts, logs, webhooks)."""
    
    def __init__(self, webhook_url: str = None):
        """
        Initialize event handler.
        
        Args:
            webhook_url: Optional webhook URL for sending events
        """
        self.webhook_url = webhook_url or Config.WEBHOOK_URL
        self.events = []  # In-memory event log
    
    def log_event(self, event_type: str, data: Dict):
        """
        Log an event.
        
        Args:
            event_type: Type of event ('match', 'detection', 'alert', etc.)
            data: Event data dictionary
        """
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': event_type,
            'data': data
        }
        
        self.events.append(event)
        logger.info(f"Event: {event_type} - {json.dumps(data)}")
        
        # Send to webhook if configured
        if self.webhook_url:
            self._send_webhook(event)
    
    def alert(self, person_id: str, person_name: str, similarity: float, image_path: str = None, metadata: Dict = None):
        """
        Trigger an alert for a matched face.
        
        Args:
            person_id: Matched person ID
            person_name: Matched person name
            similarity: Similarity score
            image_path: Path to detected face image
            metadata: Additional metadata
        """
        alert_data = {
            'person_id': person_id,
            'person_name': person_name,
            'similarity': similarity,
            'image_path': image_path,
            'metadata': metadata or {}
        }
        self.log_event('alert', alert_data)
    
    def track(self, person_id: str, person_name: str, location: str = None, frame_number: int = None, timestamp: float = None):
        """
        Track a person detection.
        
        Args:
            person_id: Person ID
            person_name: Person name
            location: Detection location/context
            frame_number: Video frame number
            timestamp: Detection timestamp
        """
        track_data = {
            'person_id': person_id,
            'person_name': person_name,
            'location': location,
            'frame_number': frame_number,
            'timestamp': timestamp or datetime.utcnow().timestamp()
        }
        self.log_event('track', track_data)
    
    def detection(self, num_faces: int, bboxes: List = None, source: str = None):
        """
        Log face detection event.
        
        Args:
            num_faces: Number of faces detected
            bboxes: List of bounding boxes
            source: Source identifier (video path, RTSP URL, etc.)
        """
        detection_data = {
            'num_faces': num_faces,
            'bboxes': bboxes,
            'source': source
        }
        self.log_event('detection', detection_data)
    
    def _send_webhook(self, event: Dict):
        """
        Send event to webhook URL.
        
        Args:
            event: Event dictionary
        """
        try:
            response = requests.post(
                self.webhook_url,
                json=event,
                timeout=5
            )
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to send webhook: {e}")
    
    def get_events(self, event_type: str = None, limit: int = 100) -> List[Dict]:
        """
        Get recent events.
        
        Args:
            event_type: Filter by event type (optional)
            limit: Maximum number of events to return
            
        Returns:
            List of event dictionaries
        """
        events = self.events
        if event_type:
            events = [e for e in events if e['type'] == event_type]
        return events[-limit:]
    
    def clear_events(self):
        """Clear all events."""
        self.events = []


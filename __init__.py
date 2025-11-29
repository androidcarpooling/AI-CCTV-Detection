"""Face Recognition System using InsightFace."""

__version__ = '1.0.0'

from .face_detector import FaceDetector
from .face_recognizer import FaceRecognizer
from .database import Database
from .matcher import FaceMatcher
from .processor import FaceRecognitionProcessor
from .event_handler import EventHandler

__all__ = [
    'FaceDetector',
    'FaceRecognizer',
    'Database',
    'FaceMatcher',
    'FaceRecognitionProcessor',
    'EventHandler'
]


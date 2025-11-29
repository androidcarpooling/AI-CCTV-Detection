"""Face detection using SCRFD (InsightFace)."""
import ssl
import urllib.request
ssl._create_default_https_context = ssl._create_unverified_context

# Patch urllib for InsightFace downloads
_original_urlopen = urllib.request.urlopen
def _patched_urlopen(*args, **kwargs):
    ctx = ssl._create_unverified_context()
    if 'context' not in kwargs:
        kwargs['context'] = ctx
    return _original_urlopen(*args, **kwargs)
urllib.request.urlopen = _patched_urlopen

import cv2
import numpy as np
import insightface
from config import Config

class FaceDetector:
    """SCRFD-based face detector."""
    
    def __init__(self):
        """Initialize SCRFD face detector."""
        self.detector = insightface.app.FaceAnalysis(
            name=Config.DETECTOR_MODEL,
            providers=['CPUExecutionProvider']  # Use CUDAExecutionProvider for GPU
        )
        self.detector.prepare(ctx_id=-1, det_size=(640, 640))  # -1 for CPU
    
    def detect(self, image):
        """
        Detect faces in an image.
        
        Args:
            image: numpy array (BGR format) or path to image file
            
        Returns:
            List of detected faces with bounding boxes and landmarks
        """
        if isinstance(image, str):
            image = cv2.imread(image)
        
        if image is None:
            return []
        
        # Convert to RGB if needed
        if len(image.shape) == 3 and image.shape[2] == 3:
            # InsightFace expects RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = image
        
        # Detect faces
        faces = self.detector.get(image_rgb)
        
        results = []
        for face in faces:
            results.append({
                'bbox': face.bbox.astype(int).tolist(),  # [x1, y1, x2, y2]
                'landmarks': face.landmark_2d_106.astype(int).tolist() if hasattr(face, 'landmark_2d_106') else None,
                'kps': face.kps.astype(int).tolist() if hasattr(face, 'kps') else None,  # 5 keypoints
                'det_score': float(face.det_score),
                'face': face  # Keep original face object for alignment
            })
        
        return results
    
    def detect_batch(self, images):
        """
        Detect faces in multiple images.
        
        Args:
            images: List of images (numpy arrays or file paths)
            
        Returns:
            List of detection results for each image
        """
        return [self.detect(img) for img in images]


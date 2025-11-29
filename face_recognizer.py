"""Face recognition using ArcFace (InsightFace)."""
import ssl
import urllib.request
ssl._create_default_https_context = ssl._create_unverified_context

# Patch urllib for InsightFace downloads
_original_urlopen = urllib.request.urlopen
def _patched_urlopen(*args, **kwargs):
    if 'context' not in kwargs:
        kwargs['context'] = ssl._create_unverified_context()
    return _original_urlopen(*args, **kwargs)
urllib.request.urlopen = _patched_urlopen

import cv2
import numpy as np
import insightface
from config import Config

class FaceRecognizer:
    """ArcFace-based face recognizer."""
    
    def __init__(self, model_name=None):
        """
        Initialize ArcFace face recognizer.
        
        Args:
            model_name: Model name ('buffalo_l' or 'glint360k_r100_fp16')
        """
        self.model_name = model_name or Config.RECOGNIZER_MODEL
        self.recognizer = insightface.app.FaceAnalysis(
            name=self.model_name,
            providers=['CPUExecutionProvider']  # Use CUDAExecutionProvider for GPU
        )
        self.recognizer.prepare(ctx_id=0, det_size=(640, 640))
    
    def get_embedding(self, image, face=None):
        """
        Generate face embedding from image.
        
        Args:
            image: numpy array (BGR format) or path to image file
            face: Optional face object from detector (for pre-detected faces)
            
        Returns:
            512-dimensional embedding vector (numpy array)
        """
        if isinstance(image, str):
            image = cv2.imread(image)
        
        if image is None:
            return None
        
        # Convert to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        if face is not None:
            # Use pre-detected face
            embedding = face.normed_embedding
        else:
            # Detect and extract embedding
            faces = self.recognizer.get(image_rgb)
            if len(faces) == 0:
                return None
            # Use the first (largest) face
            embedding = faces[0].normed_embedding
        
        return embedding.astype(np.float32)
    
    def get_embeddings(self, image, faces):
        """
        Generate embeddings for multiple detected faces.
        
        Args:
            image: numpy array (BGR format)
            faces: List of detected face objects from detector
            
        Returns:
            List of 512-dimensional embedding vectors
        """
        if isinstance(image, str):
            image = cv2.imread(image)
        
        if image is None:
            return []
        
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        detected_faces = self.recognizer.get(image_rgb)
        
        embeddings = []
        for face_obj in detected_faces:
            embeddings.append(face_obj.normed_embedding.astype(np.float32))
        
        return embeddings
    
    def align_face(self, image, face):
        """
        Align and crop face to 112x112 using InsightFace utilities.
        
        Args:
            image: numpy array (BGR format)
            face: Face object from detector
            
        Returns:
            Aligned face image (112x112)
        """
        if isinstance(image, str):
            image = cv2.imread(image)
        
        # InsightFace already provides aligned faces
        # But we can also manually align using landmarks
        if hasattr(face, 'norm_crop'):
            # Use pre-aligned face if available
            aligned = face.norm_crop
        else:
            # Manual alignment using 5 keypoints
            if hasattr(face, 'kps') and face.kps is not None:
                # InsightFace FaceAnalysis already provides norm_crop
                # If not available, fall back to bbox crop
                bbox = face.bbox.astype(int)
                x1, y1, x2, y2 = bbox[0], bbox[1], bbox[2], bbox[3]
                cropped = image[y1:y2, x1:x2]
                aligned = cv2.resize(cropped, Config.FACE_SIZE)
            else:
                # Fallback: crop using bounding box
                bbox = face.bbox.astype(int)
                x1, y1, x2, y2 = bbox[0], bbox[1], bbox[2], bbox[3]
                cropped = image[y1:y2, x1:x2]
                aligned = cv2.resize(cropped, Config.FACE_SIZE)
        
        return aligned


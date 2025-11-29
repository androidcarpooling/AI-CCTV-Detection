"""Main processing pipeline for face recognition."""
import os
import cv2
import numpy as np
from typing import List, Dict, Optional
from face_detector import FaceDetector
from face_recognizer import FaceRecognizer
from matcher import FaceMatcher
from event_handler import EventHandler
from input_handlers import ImageHandler, VideoHandler, RTSPHandler

class FaceRecognitionProcessor:
    """Main face recognition processing pipeline."""
    
    def __init__(self, database, similarity_threshold: float = None):
        """
        Initialize processor.
        
        Args:
            database: Database instance
            similarity_threshold: Similarity threshold for matching
        """
        self.detector = FaceDetector()
        self.recognizer = FaceRecognizer()
        self.matcher = FaceMatcher(database, threshold=similarity_threshold)
        self.event_handler = EventHandler()
    
    def process_image(self, image_path: str, source: str = None) -> List[Dict]:
        """
        Process a single image.
        
        Args:
            image_path: Path to image file
            source: Source identifier
            
        Returns:
            List of detection results
        """
        image = cv2.imread(image_path)
        if image is None:
            return []
        
        # Detect faces
        faces = self.detector.detect(image)
        self.event_handler.detection(len(faces), source=source or image_path)
        
        results = []
        for face_info in faces:
            # Get embedding
            embedding = self.recognizer.get_embedding(image, face_info['face'])
            if embedding is None:
                continue
            
            # Match against database
            is_match, person_id, person_name, similarity = self.matcher.is_match(embedding)
            
            result = {
                'bbox': face_info['bbox'],
                'det_score': face_info['det_score'],
                'matched': is_match,
                'person_id': person_id,
                'person_name': person_name,
                'similarity': similarity
            }
            
            if is_match:
                self.event_handler.alert(person_id, person_name, similarity, image_path)
                self.event_handler.track(person_id, person_name, location=source or image_path)
            
            results.append(result)
        
        return results
    
    def process_video(self, video_path: str, output_file: str = None, fps: int = 1) -> List[Dict]:
        """
        Process a video file.
        
        Args:
            video_path: Path to video file
            output_file: Optional output file path for results
            fps: Process every Nth frame
            
        Returns:
            List of detection results
        """
        results = []
        
        with VideoHandler(video_path, fps=fps) as video:
            for frame_num, frame, timestamp in video.frames():
                # Detect faces
                faces = self.detector.detect(frame)
                self.event_handler.detection(len(faces), source=video_path)
                
                for face_info in faces:
                    # Get embedding
                    embedding = self.recognizer.get_embedding(frame, face_info['face'])
                    if embedding is None:
                        continue
                    
                    # Match against database
                    is_match, person_id, person_name, similarity = self.matcher.is_match(embedding)
                    
                    result = {
                        'frame': frame_num,
                        'timestamp': timestamp,
                        'bbox': face_info['bbox'],
                        'det_score': face_info['det_score'],
                        'matched': is_match,
                        'person_id': person_id,
                        'person_name': person_name,
                        'similarity': similarity
                    }
                    
                    if is_match:
                        self.event_handler.alert(person_id, person_name, similarity, metadata={'frame': frame_num})
                        self.event_handler.track(person_id, person_name, location=video_path, frame_number=frame_num, timestamp=timestamp)
                    
                    results.append(result)
        
        if output_file:
            import json
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
        
        return results
    
    def process_rtsp(self, rtsp_url: str, max_frames: int = None):
        """
        Process RTSP stream (runs indefinitely until interrupted).
        
        Args:
            rtsp_url: RTSP stream URL
            max_frames: Maximum number of frames to process (None = infinite)
        """
        frame_count = 0
        
        with RTSPHandler(rtsp_url) as stream:
            for frame_num, frame, timestamp in stream.frames():
                if max_frames and frame_count >= max_frames:
                    break
                
                # Detect faces
                faces = self.detector.detect(frame)
                self.event_handler.detection(len(faces), source=rtsp_url)
                
                for face_info in faces:
                    # Get embedding
                    embedding = self.recognizer.get_embedding(frame, face_info['face'])
                    if embedding is None:
                        continue
                    
                    # Match against database
                    is_match, person_id, person_name, similarity = self.matcher.is_match(embedding)
                    
                    if is_match:
                        self.event_handler.alert(person_id, person_name, similarity, metadata={'frame': frame_num})
                        self.event_handler.track(person_id, person_name, location=rtsp_url, frame_number=frame_num, timestamp=timestamp)
                
                frame_count += 1
    
    def build_watchlist(self, photos_dir: str, person_id_prefix: str = "person") -> int:
        """
        Build watchlist from directory of photos.
        
        Args:
            photos_dir: Directory containing photos
            person_id_prefix: Prefix for person IDs
            
        Returns:
            Number of faces added
        """
        count = 0
        
        for image_path, image in ImageHandler.load_images(photos_dir):
            # Extract person name from filename or directory
            filename = os.path.basename(image_path)
            person_name = os.path.splitext(filename)[0]
            person_id = f"{person_id_prefix}_{count}"
            
            # Detect and get embedding
            faces = self.detector.detect(image)
            if len(faces) == 0:
                print(f"No faces detected in {image_path}")
                continue
            
            # Use the first (largest) face
            face_info = faces[0]
            embedding = self.recognizer.get_embedding(image, face_info['face'])
            
            if embedding is not None:
                # Add to database
                self.matcher.database.add_face(person_id, person_name, embedding, image_path)
                self.matcher.invalidate_cache()  # Refresh cache
                count += 1
                print(f"Added {person_name} ({person_id}) from {image_path}")
        
        return count


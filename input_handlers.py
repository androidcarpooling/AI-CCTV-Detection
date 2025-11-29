"""Input handlers for images, video files, and RTSP streams."""
import cv2
import os
import glob
import numpy as np
from typing import Iterator, Tuple, Optional
from pathlib import Path

class ImageHandler:
    """Handle image file inputs."""
    
    @staticmethod
    def load_images(directory: str, extensions: Tuple[str] = ('.jpg', '.jpeg', '.png', '.bmp')) -> Iterator[Tuple[str, np.ndarray]]:
        """
        Load images from directory.
        
        Args:
            directory: Directory path
            extensions: Image file extensions
            
        Yields:
            (image_path, image_array) tuples
        """
        directory = Path(directory)
        for ext in extensions:
            pattern = str(directory / f'**/*{ext}')
            for img_path in glob.glob(pattern, recursive=True):
                image = cv2.imread(img_path)
                if image is not None:
                    yield img_path, image
    
    @staticmethod
    def load_image(image_path: str) -> Optional[np.ndarray]:
        """
        Load a single image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Image array or None if failed
        """
        return cv2.imread(image_path)

class VideoHandler:
    """Handle video file inputs."""
    
    def __init__(self, video_path: str, fps: int = 1):
        """
        Initialize video handler.
        
        Args:
            video_path: Path to video file
            fps: Process every Nth frame (1 = all frames)
        """
        self.video_path = video_path
        self.fps = fps
        self.cap = None
    
    def __enter__(self):
        """Open video file."""
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Failed to open video: {self.video_path}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close video file."""
        if self.cap:
            self.cap.release()
    
    def frames(self) -> Iterator[Tuple[int, np.ndarray, float]]:
        """
        Iterate through video frames.
        
        Yields:
            (frame_number, frame_array, timestamp) tuples
        """
        frame_count = 0
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            if frame_count % self.fps == 0:
                timestamp = self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                yield frame_count, frame, timestamp
            
            frame_count += 1
    
    def get_total_frames(self) -> int:
        """Get total number of frames in video."""
        return int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    def get_fps(self) -> float:
        """Get video FPS."""
        return self.cap.get(cv2.CAP_PROP_FPS)

class RTSPHandler:
    """Handle RTSP stream inputs."""
    
    def __init__(self, rtsp_url: str, reconnect_delay: int = 5):
        """
        Initialize RTSP handler.
        
        Args:
            rtsp_url: RTSP stream URL
            reconnect_delay: Delay in seconds before reconnecting on failure
        """
        self.rtsp_url = rtsp_url
        self.reconnect_delay = reconnect_delay
        self.cap = None
    
    def __enter__(self):
        """Open RTSP stream."""
        self.cap = cv2.VideoCapture(self.rtsp_url)
        if not self.cap.isOpened():
            raise ValueError(f"Failed to open RTSP stream: {self.rtsp_url}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close RTSP stream."""
        if self.cap:
            self.cap.release()
    
    def frames(self) -> Iterator[Tuple[int, np.ndarray, float]]:
        """
        Iterate through RTSP frames.
        
        Yields:
            (frame_number, frame_array, timestamp) tuples
        """
        import time
        frame_count = 0
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                # Try to reconnect
                time.sleep(self.reconnect_delay)
                self.cap.release()
                self.cap = cv2.VideoCapture(self.rtsp_url)
                if not self.cap.isOpened():
                    break
                continue
            
            timestamp = time.time()
            yield frame_count, frame, timestamp
            frame_count += 1


"""Configuration management for the face recognition system."""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""
    
    # Face recognition settings
    SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', '0.35'))
    FACE_SIZE = (112, 112)
    EMBEDDING_SIZE = 512
    
    # Model settings
    DETECTOR_MODEL = 'buffalo_l'  # Use buffalo_l which includes detection + recognition
    RECOGNIZER_MODEL = 'buffalo_l'  # ArcFace model (or 'glint360k_r100_fp16')
    
    # Database settings
    DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'sqlite')
    DATABASE_URL = os.getenv('DATABASE_URL', 'watchlist.db')
    
    # Redis settings
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
    
    # PostgreSQL settings
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', '5432'))
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'face_recognition')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')
    
    # Event settings
    WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Processing settings
    VIDEO_FPS = 1  # Process every Nth frame
    RTSP_RECONNECT_DELAY = 5  # seconds


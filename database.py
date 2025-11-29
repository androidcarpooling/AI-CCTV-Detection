"""Database abstraction layer for face embeddings."""
import sqlite3
import json
import numpy as np
from typing import List, Dict, Optional, Tuple
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis
import pickle
from datetime import datetime
from config import Config

Base = declarative_base()

class FaceRecord(Base):
    """SQLAlchemy model for face records."""
    __tablename__ = 'faces'
    
    id = Column(Integer, primary_key=True)
    person_id = Column(String, index=True)
    person_name = Column(String)
    embedding = Column(Text)  # JSON serialized embedding
    image_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Database:
    """Database abstraction for face embeddings."""
    
    def __init__(self, db_type=None, connection_string=None):
        """
        Initialize database connection.
        
        Args:
            db_type: 'sqlite', 'postgresql', 'redis', or None (auto-detect from config)
            connection_string: Database connection string
        """
        self.db_type = db_type or Config.DATABASE_TYPE
        
        if self.db_type == 'sqlite':
            self._init_sqlite(connection_string or Config.DATABASE_URL)
        elif self.db_type == 'postgresql':
            self._init_postgresql(connection_string)
        elif self.db_type == 'redis':
            self._init_redis()
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
    
    def _init_sqlite(self, db_path):
        """Initialize SQLite database."""
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.redis_client = None
    
    def _init_postgresql(self, connection_string):
        """Initialize PostgreSQL database."""
        if connection_string:
            db_url = connection_string
        else:
            db_url = f"postgresql://{Config.POSTGRES_USER}:{Config.POSTGRES_PASSWORD}@{Config.POSTGRES_HOST}:{Config.POSTGRES_PORT}/{Config.POSTGRES_DB}"
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.redis_client = None
    
    def _init_redis(self):
        """Initialize Redis database."""
        self.redis_client = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            decode_responses=False
        )
        self.engine = None
        self.Session = None
    
    def add_face(self, person_id: str, person_name: str, embedding: np.ndarray, image_path: str = None) -> int:
        """
        Add a face embedding to the database.
        
        Args:
            person_id: Unique identifier for the person
            person_name: Name of the person
            embedding: 512-dimensional embedding vector
            image_path: Optional path to source image
            
        Returns:
            Record ID
        """
        if self.db_type == 'redis':
            return self._add_face_redis(person_id, person_name, embedding, image_path)
        else:
            return self._add_face_sql(person_id, person_name, embedding, image_path)
    
    def _add_face_sql(self, person_id: str, person_name: str, embedding: np.ndarray, image_path: str = None) -> int:
        """Add face to SQL database."""
        session = self.Session()
        try:
            embedding_json = json.dumps(embedding.tolist())
            record = FaceRecord(
                person_id=person_id,
                person_name=person_name,
                embedding=embedding_json,
                image_path=image_path
            )
            session.add(record)
            session.commit()
            return record.id
        finally:
            session.close()
    
    def _add_face_redis(self, person_id: str, person_name: str, embedding: np.ndarray, image_path: str = None) -> str:
        """Add face to Redis database."""
        key = f"face:{person_id}:{datetime.utcnow().timestamp()}"
        data = {
            'person_id': person_id,
            'person_name': person_name,
            'embedding': pickle.dumps(embedding),
            'image_path': image_path,
            'created_at': datetime.utcnow().isoformat()
        }
        self.redis_client.set(key, pickle.dumps(data))
        # Also maintain an index
        self.redis_client.sadd(f"person:{person_id}", key)
        return key
    
    def get_all_embeddings(self) -> List[Tuple[str, str, np.ndarray]]:
        """
        Get all face embeddings from database.
        
        Returns:
            List of (person_id, person_name, embedding) tuples
        """
        if self.db_type == 'redis':
            return self._get_all_embeddings_redis()
        else:
            return self._get_all_embeddings_sql()
    
    def _get_all_embeddings_sql(self) -> List[Tuple[str, str, np.ndarray]]:
        """Get all embeddings from SQL database."""
        session = self.Session()
        try:
            records = session.query(FaceRecord).all()
            results = []
            for record in records:
                embedding = np.array(json.loads(record.embedding))
                results.append((record.person_id, record.person_name, embedding))
            return results
        finally:
            session.close()
    
    def _get_all_embeddings_redis(self) -> List[Tuple[str, str, np.ndarray]]:
        """Get all embeddings from Redis database."""
        results = []
        for key in self.redis_client.scan_iter(match="face:*"):
            key_bytes = key if isinstance(key, bytes) else key.encode()
            data_bytes = self.redis_client.get(key_bytes)
            if data_bytes:
                data = pickle.loads(data_bytes)
                embedding = pickle.loads(data['embedding'])
                results.append((data['person_id'], data['person_name'], embedding))
        return results
    
    def get_person_embeddings(self, person_id: str) -> List[np.ndarray]:
        """
        Get all embeddings for a specific person.
        
        Args:
            person_id: Person identifier
            
        Returns:
            List of embedding vectors
        """
        if self.db_type == 'redis':
            return self._get_person_embeddings_redis(person_id)
        else:
            return self._get_person_embeddings_sql(person_id)
    
    def _get_person_embeddings_sql(self, person_id: str) -> List[np.ndarray]:
        """Get person embeddings from SQL database."""
        session = self.Session()
        try:
            records = session.query(FaceRecord).filter_by(person_id=person_id).all()
            return [np.array(json.loads(r.embedding)) for r in records]
        finally:
            session.close()
    
    def _get_person_embeddings_redis(self, person_id: str) -> List[np.ndarray]:
        """Get person embeddings from Redis database."""
        keys = self.redis_client.smembers(f"person:{person_id}")
        embeddings = []
        for key in keys:
            key_bytes = key if isinstance(key, bytes) else key.encode()
            data_bytes = self.redis_client.get(key_bytes)
            if data_bytes:
                data = pickle.loads(data_bytes)
                embeddings.append(pickle.loads(data['embedding']))
        return embeddings
    
    def count_faces(self) -> int:
        """Get total number of face records."""
        if self.db_type == 'redis':
            return sum(1 for _ in self.redis_client.scan_iter(match="face:*"))
        else:
            session = self.Session()
            try:
                return session.query(FaceRecord).count()
            finally:
                session.close()


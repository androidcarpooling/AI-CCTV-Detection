"""Real-time face matching using cosine similarity."""
import numpy as np
from typing import List, Tuple, Optional
from database import Database
from config import Config

class FaceMatcher:
    """Real-time face matcher using cosine similarity."""
    
    def __init__(self, database: Database, threshold: float = None):
        """
        Initialize face matcher.
        
        Args:
            database: Database instance
            threshold: Cosine similarity threshold (default: 0.35)
        """
        self.database = database
        self.threshold = threshold or Config.SIMILARITY_THRESHOLD
        self._embeddings_cache = None
        self._cache_valid = False
    
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First embedding vector
            vec2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        # Normalize vectors
        vec1_norm = vec1 / (np.linalg.norm(vec1) + 1e-8)
        vec2_norm = vec2 / (np.linalg.norm(vec2) + 1e-8)
        # Cosine similarity
        similarity = np.dot(vec1_norm, vec2_norm)
        return float(similarity)
    
    def match(self, query_embedding: np.ndarray, top_k: int = 1) -> List[Tuple[str, str, float]]:
        """
        Match a query embedding against the database.
        
        Args:
            query_embedding: Query face embedding (512-dim)
            top_k: Number of top matches to return
            
        Returns:
            List of (person_id, person_name, similarity_score) tuples
        """
        # Get all embeddings from database
        if not self._cache_valid or self._embeddings_cache is None:
            self._embeddings_cache = self.database.get_all_embeddings()
            self._cache_valid = True
        
        matches = []
        for person_id, person_name, db_embedding in self._embeddings_cache:
            similarity = self.cosine_similarity(query_embedding, db_embedding)
            if similarity >= self.threshold:
                matches.append((person_id, person_name, similarity))
        
        # Sort by similarity (descending)
        matches.sort(key=lambda x: x[2], reverse=True)
        
        return matches[:top_k]
    
    def match_batch(self, query_embeddings: List[np.ndarray], top_k: int = 1) -> List[List[Tuple[str, str, float]]]:
        """
        Match multiple query embeddings.
        
        Args:
            query_embeddings: List of query embeddings
            top_k: Number of top matches per query
            
        Returns:
            List of match results for each query
        """
        return [self.match(emb, top_k) for emb in query_embeddings]
    
    def is_match(self, query_embedding: np.ndarray) -> Tuple[bool, Optional[str], Optional[str], float]:
        """
        Check if query embedding matches anyone in database.
        
        Args:
            query_embedding: Query face embedding
            
        Returns:
            (is_match, person_id, person_name, best_similarity)
        """
        matches = self.match(query_embedding, top_k=1)
        if matches:
            person_id, person_name, similarity = matches[0]
            return True, person_id, person_name, similarity
        return False, None, None, 0.0
    
    def invalidate_cache(self):
        """Invalidate the embeddings cache."""
        self._cache_valid = False
        self._embeddings_cache = None


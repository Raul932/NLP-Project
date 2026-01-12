"""
HSO (Hirst-St-Onge) Similarity Algorithm

Based on path length and number of direction changes.
HSO(s1, s2) = C - path_length - k * direction_changes
"""

from collections import deque
from typing import Optional, Tuple
from .base import BaseSimilarity


class HsoSimilarity(BaseSimilarity):
    """
    Hirst-St-Onge similarity measure.
    
    Two concepts are related if they are connected by a path
    that is not too long and does not change direction too often.
    """
    
    # Constants for the formula
    CONST_C = 16  # Base constant
    CONST_K = 1   # Penalty for direction changes
    MAX_PATH_LENGTH = 8  # Maximum allowed path length
    MAX_DIRECTION_CHANGES = 5  # Maximum allowed direction changes
    
    def _find_path_with_directions(
        self, 
        synset1_id: str, 
        synset2_id: str
    ) -> Optional[Tuple[int, int]]:
        """
        Find path between synsets and count direction changes.
        
        Direction changes occur when transitioning from going UP (to hypernyms)
        to going DOWN (to hyponyms) or vice versa.
        
        Returns:
            Tuple of (path_length, direction_changes) or None if no path found
        """
        if synset1_id == synset2_id:
            return (0, 0)
            
        # BFS with direction tracking
        # State: (synset_id, path_length, direction_changes, last_direction)
        # Direction: 'up' for hypernym, 'down' for hyponym, None for start
        
        queue = deque([(synset1_id, 0, 0, None, {synset1_id})])
        best_result = None
        
        while queue:
            current_id, path_len, dir_changes, last_dir, visited = queue.popleft()
            
            # Skip if path is too long
            if path_len > self.MAX_PATH_LENGTH:
                continue
                
            # Skip if too many direction changes
            if dir_changes > self.MAX_DIRECTION_CHANGES:
                continue
            
            # Get hypernyms and hyponyms using loader methods
            hypernyms = self.loader.get_hypernyms(current_id)
            hyponyms = self.loader.get_hyponyms(current_id)
                
            # Try going UP (hypernyms)
            for hypernym_id in hypernyms:
                if hypernym_id == synset2_id:
                    new_changes = dir_changes + (1 if last_dir == 'down' else 0)
                    result = (path_len + 1, new_changes)
                    if best_result is None or self._score(result) > self._score(best_result):
                        best_result = result
                    continue
                    
                if hypernym_id not in visited:
                    new_changes = dir_changes + (1 if last_dir == 'down' else 0)
                    new_visited = visited | {hypernym_id}
                    queue.append((hypernym_id, path_len + 1, new_changes, 'up', new_visited))
                    
            # Try going DOWN (hyponyms)
            for hyponym_id in hyponyms:
                if hyponym_id == synset2_id:
                    new_changes = dir_changes + (1 if last_dir == 'up' else 0)
                    result = (path_len + 1, new_changes)
                    if best_result is None or self._score(result) > self._score(best_result):
                        best_result = result
                    continue
                    
                if hyponym_id not in visited:
                    new_changes = dir_changes + (1 if last_dir == 'up' else 0)
                    new_visited = visited | {hyponym_id}
                    queue.append((hyponym_id, path_len + 1, new_changes, 'down', new_visited))
                    
        return best_result
        
    def _score(self, result: Tuple[int, int]) -> float:
        """Calculate HSO score from path length and direction changes."""
        path_len, dir_changes = result
        return self.CONST_C - path_len - (self.CONST_K * dir_changes)
        
    def calculate_synset_similarity(self, synset1_id: str, synset2_id: str) -> float:
        """
        Calculate HSO similarity between two synsets.
        
        Formula: HSO = C - path_length - k * direction_changes
        
        Returns:
            float: Similarity score (higher is more similar)
        """
        if synset1_id == synset2_id:
            return float(self.CONST_C)
            
        result = self._find_path_with_directions(synset1_id, synset2_id)
        
        if result is None:
            return 0.0
            
        score = self._score(result)
        
        # Return 0 for negative scores
        return max(0.0, score)

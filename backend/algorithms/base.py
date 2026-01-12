"""
Base Similarity Module

Provides the base class for all similarity algorithms.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rowordnet_loader import RoWordNetLoader


class BaseSimilarity(ABC):
    """Base class for all similarity algorithms."""
    
    def __init__(self, loader: RoWordNetLoader):
        self.loader = loader
        
    @abstractmethod
    def calculate_synset_similarity(self, synset1_id: str, synset2_id: str) -> float:
        """Calculate similarity between two synsets."""
        pass
        
    def calculate_word_similarity(self, word1: str, word2: str) -> List[Tuple[str, str, float]]:
        """
        Calculate similarity between two words.
        Returns list of (synset1_id, synset2_id, similarity) tuples for all synset pairs.
        """
        synsets1 = self.loader.get_synsets_for_word(word1)
        synsets2 = self.loader.get_synsets_for_word(word2)
        
        if not synsets1 or not synsets2:
            return []
            
        results = []
        for s1 in synsets1:
            for s2 in synsets2:
                # Get synset IDs and POS
                s1_id = self.loader.get_synset_id(s1)
                s2_id = self.loader.get_synset_id(s2)
                s1_pos = self.loader.get_synset_pos(s1)
                s2_pos = self.loader.get_synset_pos(s2)
                
                # Only compare synsets with the same POS
                if s1_pos == s2_pos:
                    sim = self.calculate_synset_similarity(s1_id, s2_id)
                    results.append((s1_id, s2_id, sim))
                    
        return results
        
    def get_max_similarity(self, word1: str, word2: str) -> float:
        """Get the maximum similarity score between two words."""
        results = self.calculate_word_similarity(word1, word2)
        if not results:
            return 0.0
        return max(r[2] for r in results)
        
    def get_best_pair(self, word1: str, word2: str) -> Optional[Tuple[str, str, float]]:
        """Get the synset pair with highest similarity."""
        results = self.calculate_word_similarity(word1, word2)
        if not results:
            return None
        return max(results, key=lambda x: x[2])


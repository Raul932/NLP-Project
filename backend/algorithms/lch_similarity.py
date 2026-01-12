"""
LCH (Leacock-Chodorow) Similarity Algorithm

Uses path length and maximum taxonomy depth.
LCH(s1, s2) = -log(path_length / (2 * max_depth))
"""

import math
from .base import BaseSimilarity


class LchSimilarity(BaseSimilarity):
    """
    Leacock-Chodorow similarity measure.
    
    Uses the shortest path and the maximum depth of the taxonomy
    to calculate a scaled similarity score.
    """
    
    def calculate_synset_similarity(self, synset1_id: str, synset2_id: str) -> float:
        """
        Calculate LCH similarity between two synsets.
        
        Formula: LCH = -log(path_length / (2 * max_depth))
        
        Returns:
            float: Similarity score (higher is more similar)
        """
        if synset1_id == synset2_id:
            # Return maximum possible similarity
            synset = self.loader.get_synset(synset1_id)
            pos = synset.pos if synset else 'n'
            max_depth = self.loader.get_max_depth(pos)
            return -math.log(1 / (2 * max_depth + 1))
            
        path_length = self.loader.find_shortest_path_length(synset1_id, synset2_id)
        
        if path_length < 0:
            return 0.0
            
        # Get POS from first synset to determine max_depth
        synset = self.loader.get_synset(synset1_id)
        pos = synset.pos if synset else 'n'
        max_depth = self.loader.get_max_depth(pos)
        
        # path_length + 1 because we count edges, and identical synsets have path 0
        numerator = path_length + 1
        denominator = 2 * max_depth + 1
        
        if numerator >= denominator:
            return 0.0
            
        return -math.log(numerator / denominator)

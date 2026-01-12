"""
PATH Similarity Algorithm

Computes similarity as the inverse of the shortest path length.
PATH(s1, s2) = 1 / path_length(s1, s2)
"""

from .base import BaseSimilarity


class PathSimilarity(BaseSimilarity):
    """
    Path-based similarity measure.
    
    The similarity is calculated as the inverse of the shortest path
    length between two synsets in the taxonomy.
    """
    
    def calculate_synset_similarity(self, synset1_id: str, synset2_id: str) -> float:
        """
        Calculate PATH similarity between two synsets.
        
        Returns:
            float: Similarity score (0 to 1, higher is more similar)
        """
        if synset1_id == synset2_id:
            return 1.0
            
        path_length = self.loader.find_shortest_path_length(synset1_id, synset2_id)
        
        if path_length <= 0:
            return 0.0
            
        # Add 1 to path_length because similarity should be 1 for identical synsets
        # and decrease for longer paths
        return 1.0 / (path_length + 1)

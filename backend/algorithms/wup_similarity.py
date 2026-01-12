"""
WUP (Wu-Palmer) Similarity Algorithm

Calculates similarity based on depth of LCS and depths of synsets.
WUP(s1, s2) = (2 * depth(LCS)) / (depth(s1) + depth(s2))
"""

from .base import BaseSimilarity


class WupSimilarity(BaseSimilarity):
    """
    Wu-Palmer similarity measure.
    
    Uses the depths of the synsets and their Least Common Subsumer (LCS)
    to calculate similarity. Values range from 0 to 1.
    """
    
    def calculate_synset_similarity(self, synset1_id: str, synset2_id: str) -> float:
        """
        Calculate WUP similarity between two synsets.
        
        Formula: WUP = (2 * depth(LCS)) / (depth(s1) + depth(s2))
        
        Returns:
            float: Similarity score (0 to 1, higher is more similar)
        """
        if synset1_id == synset2_id:
            return 1.0
            
        # Find Least Common Subsumer
        lcs_id = self.loader.find_lcs(synset1_id, synset2_id)
        
        if lcs_id is None:
            return 0.0
            
        # Get depths
        depth_lcs = self.loader.get_depth(lcs_id)
        depth_s1 = self.loader.get_depth(synset1_id)
        depth_s2 = self.loader.get_depth(synset2_id)
        
        # Calculate WUP similarity
        denominator = depth_s1 + depth_s2
        if denominator == 0:
            return 0.0
            
        return (2.0 * depth_lcs) / denominator

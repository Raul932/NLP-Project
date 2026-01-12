"""
LIN Similarity Algorithm

Normalized Information Content similarity.
LIN(s1, s2) = (2 * IC(LCS)) / (IC(s1) + IC(s2))
"""

from .base import BaseSimilarity


class LinSimilarity(BaseSimilarity):
    """
    Lin similarity measure.
    
    Normalized version of IC-based similarity using LCS.
    Values range from 0 to 1.
    """
    
    def calculate_synset_similarity(self, synset1_id: str, synset2_id: str) -> float:
        """
        Calculate LIN similarity between two synsets.
        
        Formula: LIN = (2 * IC(LCS)) / (IC(s1) + IC(s2))
        
        Returns:
            float: Similarity score (0 to 1, higher is more similar)
        """
        if synset1_id == synset2_id:
            return 1.0
            
        # Find Least Common Subsumer
        lcs_id = self.loader.find_lcs(synset1_id, synset2_id)
        
        if lcs_id is None:
            return 0.0
            
        # Get Information Content values
        ic_s1 = self.loader.get_information_content(synset1_id)
        ic_s2 = self.loader.get_information_content(synset2_id)
        ic_lcs = self.loader.get_information_content(lcs_id)
        
        # Calculate similarity
        denominator = ic_s1 + ic_s2
        
        if denominator == 0:
            return 0.0
            
        return (2.0 * ic_lcs) / denominator

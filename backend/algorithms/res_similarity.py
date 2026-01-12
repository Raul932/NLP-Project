"""
RES (Resnik) Similarity Algorithm

Uses Information Content of the Least Common Subsumer.
RES(s1, s2) = IC(LCS(s1, s2))
"""

from .base import BaseSimilarity


class ResSimilarity(BaseSimilarity):
    """
    Resnik similarity measure.
    
    Similarity is defined as the Information Content (IC) of the
    Least Common Subsumer (LCS) of the two synsets.
    """
    
    def calculate_synset_similarity(self, synset1_id: str, synset2_id: str) -> float:
        """
        Calculate RES similarity between two synsets.
        
        Formula: RES = IC(LCS(s1, s2))
        
        Returns:
            float: Information content of LCS (higher is more similar)
        """
        if synset1_id == synset2_id:
            return self.loader.get_information_content(synset1_id)
            
        # Find Least Common Subsumer
        lcs_id = self.loader.find_lcs(synset1_id, synset2_id)
        
        if lcs_id is None:
            return 0.0
            
        # Return IC of LCS
        return self.loader.get_information_content(lcs_id)

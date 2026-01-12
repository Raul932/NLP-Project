"""
JCN (Jiang-Conrath) Similarity Algorithm

Uses Information Content distance.
distance = IC(s1) + IC(s2) - 2*IC(LCS)
JCN(s1, s2) = 1 / distance
"""

from .base import BaseSimilarity


class JcnSimilarity(BaseSimilarity):
    """
    Jiang-Conrath similarity measure.
    
    Based on Information Content, calculates a semantic distance
    and converts it to similarity.
    """
    
    # Maximum similarity value to avoid infinity
    MAX_SIMILARITY = 1e10
    
    def calculate_synset_similarity(self, synset1_id: str, synset2_id: str) -> float:
        """
        Calculate JCN similarity between two synsets.
        
        Formula: 
        distance = IC(s1) + IC(s2) - 2*IC(LCS)
        JCN = 1 / distance
        
        Returns:
            float: Similarity score (higher is more similar)
        """
        if synset1_id == synset2_id:
            return self.MAX_SIMILARITY
            
        # Find Least Common Subsumer
        lcs_id = self.loader.find_lcs(synset1_id, synset2_id)
        
        if lcs_id is None:
            return 0.0
            
        # Get Information Content values
        ic_s1 = self.loader.get_information_content(synset1_id)
        ic_s2 = self.loader.get_information_content(synset2_id)
        ic_lcs = self.loader.get_information_content(lcs_id)
        
        # Calculate distance
        distance = ic_s1 + ic_s2 - (2 * ic_lcs)
        
        # Avoid division by zero
        if distance <= 0:
            return self.MAX_SIMILARITY
            
        return 1.0 / distance

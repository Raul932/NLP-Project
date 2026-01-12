"""
LESK Similarity Algorithm

Based on gloss/definition overlap between synsets.
Uses adapted Lesk that considers related synsets' glosses.
"""

import re
from typing import Set
from .base import BaseSimilarity


class LeskSimilarity(BaseSimilarity):
    """
    Lesk (gloss overlap) similarity measure.
    
    Calculates similarity based on the overlap of words in the
    definitions (glosses) of the synsets and their related synsets.
    """
    
    # Common stop words to ignore
    STOP_WORDS = {
        'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been',
        'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'could', 'should', 'may', 'might', 'must', 'shall',
        'can', 'of', 'in', 'to', 'for', 'with', 'on', 'at', 'by',
        'from', 'as', 'into', 'through', 'during', 'before', 'after',
        'above', 'below', 'between', 'under', 'again', 'further',
        'then', 'once', 'here', 'there', 'when', 'where', 'why',
        'how', 'all', 'each', 'few', 'more', 'most', 'other', 'some',
        'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
        'than', 'too', 'very', 'just', 'and', 'but', 'if', 'or',
        'because', 'while', 'although', 'this', 'that', 'these',
        'those', 'it', 'its', 'i', 'you', 'he', 'she', 'we', 'they',
        'what', 'which', 'who', 'whom', 'whose',
        # Romanian stop words
        'un', 'o', 'una', 'este', 'sunt', 'era', 'fost', 'fi', 'fiind',
        'avea', 'are', 'au', 'de', 'la', 'cu', 'pe', 'in', 'pentru',
        'din', 'ca', 'prin', 'despre', 'spre', 'intre', 'sub', 'peste',
        'dupa', 'inainte', 'aici', 'acolo', 'cand', 'unde', 'cum',
        'toti', 'toate', 'fiecare', 'mai', 'cel', 'cea', 'cei', 'cele',
        'alt', 'alta', 'alti', 'alte', 'nici', 'numai', 'doar', 'si',
        'dar', 'daca', 'sau', 'pentru', 'ca', 'aceasta', 'acest',
        'aceste', 'acestea', 'el', 'ea', 'ei', 'ele', 'noi', 'voi',
        'ce', 'care', 'cine', 'cui'
    }
    
    def _tokenize(self, text: str) -> Set[str]:
        """Tokenize text into set of meaningful words."""
        if not text:
            return set()
            
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation and split
        words = re.findall(r'\b[a-zA-Z\u0100-\u017F]+\b', text)
        
        # Filter stop words and short words
        return {w for w in words if w not in self.STOP_WORDS and len(w) > 2}
        
    def _get_extended_gloss(self, synset_id: str) -> Set[str]:
        """Get tokens from synset definition and related synsets' definitions."""
        tokens = set()
        
        # Get own definition
        definition = self.loader.get_definition(synset_id)
        tokens.update(self._tokenize(definition))
        
        # Get synset literals as additional context using loader method
        synset = self.loader.get_synset(synset_id)
        if synset:
            literals = self.loader.get_synset_literals(synset)
            for literal in literals:
                tokens.update(self._tokenize(literal))
                
        # Get related synsets' definitions
        related = self.loader.get_related_synsets(synset_id)
        for rel_id in related[:5]:  # Limit to avoid too much noise
            rel_def = self.loader.get_definition(rel_id)
            tokens.update(self._tokenize(rel_def))
            
        return tokens
        
    def calculate_synset_similarity(self, synset1_id: str, synset2_id: str) -> float:
        """
        Calculate LESK similarity between two synsets.
        
        Based on word overlap in glosses.
        
        Returns:
            float: Number of overlapping words (higher is more similar)
        """
        if synset1_id == synset2_id:
            gloss_tokens = self._get_extended_gloss(synset1_id)
            return float(len(gloss_tokens))
            
        # Get extended glosses
        tokens1 = self._get_extended_gloss(synset1_id)
        tokens2 = self._get_extended_gloss(synset2_id)
        
        if not tokens1 or not tokens2:
            return 0.0
            
        # Calculate overlap
        overlap = tokens1.intersection(tokens2)
        
        return float(len(overlap))

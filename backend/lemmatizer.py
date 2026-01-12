"""
Romanian Lemmatizer Module

Simple rule-based lemmatizer for Romanian words.
Strips common suffixes to find base forms that exist in RoWordNet.
"""

from typing import Optional, List
import re


class RomanianLemmatizer:
    """
    Simple rule-based Romanian lemmatizer.
    Tries to find base forms by removing common inflectional suffixes.
    """
    
    # Common noun suffixes (definite articles and plurals)
    NOUN_SUFFIXES = [
        # Definite articles
        'ul', 'le', 'a', 'ua', 'ului', 'ilor', 'elor',
        # Plurals  
        'i', 'e', 'uri', 'ele', 'ii', 'iile',
        # Combinations
        'urile', 'ilor', 'elor',
    ]
    
    # Common verb suffixes (conjugations)
    VERB_SUFFIXES = [
        # Present tense
        'ez', 'ezi', 'ează', 'ăm', 'ați', 'esc', 'ești', 'ește', 'im', 'iți',
        # Past tense
        'am', 'ai', 'a', 'ară', 'ați', 'au',
        'eam', 'eai', 'ea', 'eau',
        'iam', 'iai', 'ia', 'iau',
        # Participle
        'at', 'it', 'ut', 'ât',
        # Infinitive
        'a', 'ea', 'e', 'i', 'î',
    ]
    
    # Common adjective suffixes
    ADJ_SUFFIXES = [
        'ă', 'e', 'i', 'ul', 'a', 'ei', 'ului', 'ilor',
    ]
    
    # Irregular forms mapping
    IRREGULARS = {
        'câinele': 'câine',
        'câinelui': 'câine',
        'câini': 'câine',
        'câinii': 'câine',
        'pisica': 'pisică',
        'pisicii': 'pisică',
        'pisici': 'pisică',
        'oameni': 'om',
        'oamenii': 'om',
        'omul': 'om',
        'copii': 'copil',
        'copiii': 'copil',
        'copilul': 'copil',
        'femei': 'femeie',
        'femeile': 'femeie',
        'bărbați': 'bărbat',
        'bărbații': 'bărbat',
        'case': 'casă',
        'casele': 'casă',
        'casei': 'casă',
        'mașini': 'mașină',
        'mașinile': 'mașină',
        'copaci': 'copac',
        'copacii': 'copac',
        'flori': 'floare',
        'florile': 'floare',
        'cărți': 'carte',
        'cărțile': 'carte',
    }
    
    def __init__(self, wordnet_lookup=None):
        """
        Initialize lemmatizer.
        
        Args:
            wordnet_lookup: Optional function to check if word exists in wordnet
        """
        self.wordnet_lookup = wordnet_lookup
        
    def lemmatize(self, word: str) -> str:
        """
        Find the base form (lemma) of a Romanian word.
        
        Args:
            word: The inflected word
            
        Returns:
            The base form if found, otherwise the original word
        """
        word_lower = word.lower().strip()
        
        # Check irregular forms first
        if word_lower in self.IRREGULARS:
            return self.IRREGULARS[word_lower]
        
        # If we have a wordnet lookup function, try to find valid forms
        if self.wordnet_lookup:
            # Try original word first
            if self.wordnet_lookup(word_lower):
                return word_lower
            
            # Try stripping common suffixes
            candidates = self._generate_candidates(word_lower)
            for candidate in candidates:
                if self.wordnet_lookup(candidate):
                    return candidate
        
        # Without wordnet lookup, just try stripping suffixes
        return self._strip_suffix(word_lower)
    
    def _generate_candidates(self, word: str) -> List[str]:
        """Generate possible base forms by stripping suffixes."""
        candidates = []
        
        # Try all suffixes
        all_suffixes = self.NOUN_SUFFIXES + self.VERB_SUFFIXES + self.ADJ_SUFFIXES
        # Sort by length (longest first)
        all_suffixes = sorted(set(all_suffixes), key=len, reverse=True)
        
        for suffix in all_suffixes:
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                base = word[:-len(suffix)]
                candidates.append(base)
                # Also try adding back common endings
                for ending in ['ă', 'e', 'a']:
                    candidates.append(base + ending)
        
        return candidates
    
    def _strip_suffix(self, word: str) -> str:
        """Strip the most likely suffix without wordnet validation."""
        all_suffixes = sorted(
            set(self.NOUN_SUFFIXES + self.VERB_SUFFIXES + self.ADJ_SUFFIXES),
            key=len, 
            reverse=True
        )
        
        for suffix in all_suffixes:
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                return word[:-len(suffix)]
        
        return word
    
    def lemmatize_sentence(self, sentence: str) -> List[str]:
        """
        Lemmatize all words in a sentence.
        
        Args:
            sentence: Input sentence
            
        Returns:
            List of lemmatized words
        """
        words = re.findall(r'\b[a-zA-Z\u0100-\u017Făâîșț]+\b', sentence.lower())
        return [self.lemmatize(word) for word in words]


# Global instance
_lemmatizer = None


def get_lemmatizer(wordnet_lookup=None) -> RomanianLemmatizer:
    """Get or create the Romanian lemmatizer."""
    global _lemmatizer
    if _lemmatizer is None:
        _lemmatizer = RomanianLemmatizer(wordnet_lookup)
    return _lemmatizer

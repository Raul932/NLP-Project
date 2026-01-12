"""
RoWordNet Loader Module

Uses the rowordnet library directly for faster and more reliable loading.
Implements caching for computed values like IC and depths.
"""

import os
import pickle
import math
from typing import List, Dict, Set, Optional, Tuple
from collections import deque

# Import rowordnet library
import rowordnet


class RoWordNetLoader:
    """
    Wrapper around rowordnet library with caching for computed values.
    """
    
    def __init__(self, pickle_path: str = None):
        print("Loading RoWordNet...")
        
        # Load rowordnet - use the library's built-in loading
        if pickle_path and os.path.exists(pickle_path):
            print(f"Loading from pickle: {pickle_path}")
            self.rwn = rowordnet.RoWordNet(pickle_path)
        else:
            print("Loading default RoWordNet...")
            self.rwn = rowordnet.RoWordNet()
        
        print("Building word index...")
        self._build_word_index()
        
        # Cache for computed values (lazy loading)
        self._depth_cache: Dict[str, int] = {}
        self._ic_cache: Dict[str, float] = {}
        self._max_depth: Dict[str, int] = {'n': 20, 'v': 15, 'a': 10, 'r': 10}
        self._descendant_counts: Dict[str, int] = {}
        
        print(f"Loaded {len(self.word_to_synsets)} unique words")
        print("RoWordNet ready!")
        
    def _build_word_index(self):
        """Build index from words to synset IDs."""
        self.word_to_synsets: Dict[str, List[str]] = {}
        self.synset_cache: Dict[str, object] = {}
        
        for synset_id in self.rwn.synsets():
            synset = self.rwn.synset(synset_id)
            self.synset_cache[synset_id] = synset
            
            # Get literals (words) from synset
            try:
                literals = synset.literals
                for literal in literals:
                    word_lower = literal.lower()
                    if word_lower not in self.word_to_synsets:
                        self.word_to_synsets[word_lower] = []
                    self.word_to_synsets[word_lower].append(synset_id)
            except:
                pass
                
    def get_synsets_for_word(self, word: str) -> List[object]:
        """Get all synsets containing the given word."""
        word_lower = word.lower()
        synset_ids = self.word_to_synsets.get(word_lower, [])
        return [self.synset_cache[sid] for sid in synset_ids if sid in self.synset_cache]
        
    def get_synset(self, synset_id: str):
        """Get synset by ID."""
        if synset_id in self.synset_cache:
            return self.synset_cache[synset_id]
        try:
            synset = self.rwn.synset(synset_id)
            self.synset_cache[synset_id] = synset
            return synset
        except:
            return None
            
    def get_synset_id(self, synset) -> str:
        """Get synset ID from synset object."""
        return synset.id if hasattr(synset, 'id') else str(synset)
        
    def get_synset_pos(self, synset) -> str:
        """Get POS of synset as letter (n, v, a, r)."""
        # POS mapping: RoWordNet uses different codes
        pos_map = {
            'n': 'n', 'v': 'v', 'a': 'a', 'r': 'r',  # already letters
            '0': 'n', '1': 'v', '2': 'a', '3': 'r',  # numeric strings
            0: 'n', 1: 'v', 2: 'a', 3: 'r',          # numeric values
            'NOUN': 'n', 'VERB': 'v', 'ADJ': 'a', 'ADV': 'r',  # full names
        }
        try:
            pos = synset.pos
            return pos_map.get(pos, pos_map.get(str(pos), 'n'))
        except:
            return 'n'
            
    def get_synset_literals(self, synset) -> List[str]:
        """Get literals from synset."""
        try:
            return list(synset.literals)
        except:
            return []
            
    def get_synset_definition(self, synset) -> str:
        """Get definition from synset."""
        try:
            return synset.definition or ""
        except:
            return ""
            
    def get_hypernyms(self, synset_id: str) -> List[str]:
        """Get hypernym synset IDs (parent concepts)."""
        try:
            relations = self.rwn.outbound_relations(synset_id)
            # outbound_relations returns (target_synset_id, relation_type)
            return [target_id for target_id, rel_type in relations if 'hypernym' in rel_type.lower()]
        except Exception as e:
            return []
            
    def get_hyponyms(self, synset_id: str) -> List[str]:
        """Get hyponym synset IDs (child concepts)."""
        try:
            relations = self.rwn.outbound_relations(synset_id)
            # hyponyms are outbound relations of type 'hyponym'
            return [target_id for target_id, rel_type in relations if 'hyponym' in rel_type.lower()]
        except Exception as e:
            return []
            
    def get_depth(self, synset_id: str) -> int:
        """Get depth of synset from root. Root has depth 1. Uses caching."""
        if synset_id in self._depth_cache:
            return self._depth_cache[synset_id]
            
        # BFS to find shortest path to root
        visited = set()
        queue = deque([(synset_id, 1)])
        
        while queue:
            current_id, depth = queue.popleft()
            if current_id in visited:
                continue
            visited.add(current_id)
            
            hypernyms = self.get_hypernyms(current_id)
            
            if not hypernyms:
                # Found root
                self._depth_cache[synset_id] = depth
                return depth
                
            for hypernym_id in hypernyms:
                if hypernym_id not in visited:
                    queue.append((hypernym_id, depth + 1))
                    
        # Default depth
        self._depth_cache[synset_id] = 1
        return 1
        
    def get_max_depth(self, pos: str = 'n') -> int:
        """Get maximum depth of taxonomy for given POS."""
        return self._max_depth.get(pos, 20)
        
    def get_information_content(self, synset_id: str) -> float:
        """Get Information Content of a synset. Uses lazy computation and caching."""
        if synset_id in self._ic_cache:
            return self._ic_cache[synset_id]
            
        # Count descendants
        count = self._count_descendants(synset_id)
        
        # Total synsets (approximate)
        total = len(self.synset_cache) + 1
        
        # Compute IC
        prob = count / total
        ic = -math.log(prob) if prob > 0 else 0
        
        self._ic_cache[synset_id] = ic
        return ic
        
    def _count_descendants(self, synset_id: str) -> int:
        """Count all descendants of a synset."""
        if synset_id in self._descendant_counts:
            return self._descendant_counts[synset_id]
            
        visited = set()
        queue = deque([synset_id])
        count = 0
        
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            count += 1
            
            for hyponym in self.get_hyponyms(current):
                if hyponym not in visited:
                    queue.append(hyponym)
                    
        self._descendant_counts[synset_id] = count
        return count
        
    def find_shortest_path_length(self, synset1_id: str, synset2_id: str) -> int:
        """Find shortest path length between two synsets."""
        if synset1_id == synset2_id:
            return 0
            
        # Bidirectional BFS
        visited1 = {synset1_id: 0}
        visited2 = {synset2_id: 0}
        queue1 = deque([(synset1_id, 0)])
        queue2 = deque([(synset2_id, 0)])
        
        while queue1 or queue2:
            # Expand from synset1
            if queue1:
                current, dist = queue1.popleft()
                if current in visited2:
                    return dist + visited2[current]
                    
                neighbors = self.get_hypernyms(current) + self.get_hyponyms(current)
                for neighbor in neighbors:
                    if neighbor not in visited1:
                        visited1[neighbor] = dist + 1
                        queue1.append((neighbor, dist + 1))
                        if neighbor in visited2:
                            return dist + 1 + visited2[neighbor]
                            
            # Expand from synset2
            if queue2:
                current, dist = queue2.popleft()
                if current in visited1:
                    return dist + visited1[current]
                    
                neighbors = self.get_hypernyms(current) + self.get_hyponyms(current)
                for neighbor in neighbors:
                    if neighbor not in visited2:
                        visited2[neighbor] = dist + 1
                        queue2.append((neighbor, dist + 1))
                        if neighbor in visited1:
                            return dist + 1 + visited1[neighbor]
                            
        return -1
        
    def find_lcs(self, synset1_id: str, synset2_id: str) -> Optional[str]:
        """Find Least Common Subsumer (deepest common ancestor)."""
        if synset1_id == synset2_id:
            return synset1_id
            
        # Get all ancestors of both synsets
        ancestors1 = self._get_all_ancestors(synset1_id)
        ancestors1.add(synset1_id)
        
        ancestors2 = self._get_all_ancestors(synset2_id)
        ancestors2.add(synset2_id)
        
        # Find common ancestors
        common = ancestors1.intersection(ancestors2)
        
        if not common:
            return None
            
        # Find deepest common ancestor
        deepest = None
        max_depth = -1
        
        for ancestor_id in common:
            depth = self.get_depth(ancestor_id)
            if depth > max_depth:
                max_depth = depth
                deepest = ancestor_id
                
        return deepest
        
    def _get_all_ancestors(self, synset_id: str) -> Set[str]:
        """Get all ancestors (hypernyms) of a synset."""
        ancestors = set()
        queue = deque([synset_id])
        
        while queue:
            current = queue.popleft()
            for hypernym in self.get_hypernyms(current):
                if hypernym not in ancestors:
                    ancestors.add(hypernym)
                    queue.append(hypernym)
                    
        return ancestors
        
    def get_definition(self, synset_id: str) -> str:
        """Get definition/gloss of a synset."""
        synset = self.get_synset(synset_id)
        if synset:
            return self.get_synset_definition(synset)
        return ""
        
    def get_related_synsets(self, synset_id: str) -> List[str]:
        """Get directly related synsets."""
        return self.get_hypernyms(synset_id) + self.get_hyponyms(synset_id)


# Synset wrapper class for API compatibility
class SynsetWrapper:
    """Wrapper to provide consistent interface for synsets."""
    
    def __init__(self, synset, loader: RoWordNetLoader):
        self._synset = synset
        self._loader = loader
        
    @property
    def id(self) -> str:
        return self._loader.get_synset_id(self._synset)
        
    @property
    def pos(self) -> str:
        return self._loader.get_synset_pos(self._synset)
        
    @property
    def literals(self) -> List[str]:
        return self._loader.get_synset_literals(self._synset)
        
    @property
    def definition(self) -> str:
        return self._loader.get_synset_definition(self._synset)


# Global instance
_loader_instance: Optional[RoWordNetLoader] = None


def get_rowordnet_loader(pickle_path: str = None) -> RoWordNetLoader:
    """Get or create the RoWordNet loader singleton."""
    global _loader_instance
    
    if _loader_instance is None:
        _loader_instance = RoWordNetLoader(pickle_path)
        
    return _loader_instance

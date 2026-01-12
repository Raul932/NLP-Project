"""
RoWordNet Similarity API

FastAPI backend for computing semantic similarity between Romanian words.
"""

import os
import sys
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rowordnet_loader import get_rowordnet_loader
from algorithms import (
    PathSimilarity,
    WupSimilarity,
    LchSimilarity,
    ResSimilarity,
    JcnSimilarity,
    LinSimilarity,
    LeskSimilarity,
    HsoSimilarity
)
from lemmatizer import get_lemmatizer, RomanianLemmatizer

# Create FastAPI app
app = FastAPI(
    title="RoWordNet Similarity API",
    description="Compute semantic similarity between Romanian words using RoWordNet",
    version="1.0.0"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable for loader and algorithms
_loader = None
_algorithms = {}


def get_loader():
    """Get or initialize the RoWordNet loader."""
    global _loader
    if _loader is None:
        # Path to rowordnet.pickle (one level up from backend folder)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pickle_path = os.path.join(base_dir, 'rowordnet.pickle')
        _loader = get_rowordnet_loader(pickle_path)
    return _loader


def get_algorithms():
    """Get or initialize all similarity algorithms."""
    global _algorithms
    if not _algorithms:
        loader = get_loader()
        _algorithms = {
            'path': PathSimilarity(loader),
            'wup': WupSimilarity(loader),
            'lch': LchSimilarity(loader),
            'res': ResSimilarity(loader),
            'jcn': JcnSimilarity(loader),
            'lin': LinSimilarity(loader),
            'lesk': LeskSimilarity(loader),
            'hso': HsoSimilarity(loader)
        }
    return _algorithms


def parse_word_input(word_input: str) -> tuple:
    """
    Parse word input in format: word#pos#sense or just word.
    Returns (word, pos, sense_index) tuple.
    pos can be: n (noun), v (verb), a (adjective), r (adverb)
    sense_index is 1-based (1 means first sense)
    """
    parts = word_input.strip().split('#')
    word = parts[0].lower()
    pos = parts[1].lower() if len(parts) > 1 else None
    sense = int(parts[2]) if len(parts) > 2 else None
    return (word, pos, sense)


def get_synset_by_spec(word: str, pos: str = None, sense: int = None):
    """
    Get synset by word, optionally filtered by POS and sense index.
    Returns (synset, synset_id) or (None, None) if not found.
    """
    loader = get_loader()
    synsets = loader.get_synsets_for_word(word)
    
    if not synsets:
        return None, None
    
    # Filter by POS if specified
    if pos:
        synsets = [s for s in synsets if loader.get_synset_pos(s) == pos]
    
    if not synsets:
        return None, None
    
    # Select by sense index if specified (1-based)
    if sense and sense >= 1 and sense <= len(synsets):
        synset = synsets[sense - 1]
    else:
        synset = synsets[0]  # Default to first sense
    
    return synset, loader.get_synset_id(synset)


def calculate_sentence_similarity(sentence1: str, sentence2: str, algorithm_name: str = 'wup') -> float:
    """
    Calculate semantic similarity between two sentences.
    Uses a matrix-based approach comparing all word pairs.
    
    Method:
    1. Build similarity matrix between all word pairs
    2. For each word in s1, find max similarity to any word in s2
    3. For each word in s2, find max similarity to any word in s1
    4. Average both directions, weighted by sentence lengths
    """
    import re
    
    # Simple tokenization
    words1 = re.findall(r'\b[a-zA-Z\u0100-\u017F]+\b', sentence1.lower())
    words2 = re.findall(r'\b[a-zA-Z\u0100-\u017F]+\b', sentence2.lower())
    
    if not words1 or not words2:
        return 0.0
    
    loader = get_loader()
    algorithms = get_algorithms()
    algorithm = algorithms.get(algorithm_name.lower())
    
    if not algorithm:
        return 0.0
    
    # Filter to words that exist in RoWordNet
    valid_words1 = [w for w in words1 if loader.get_synsets_for_word(w)]
    valid_words2 = [w for w in words2 if loader.get_synsets_for_word(w)]
    
    if not valid_words1 or not valid_words2:
        return 0.0
    
    # Build similarity matrix
    sim_matrix = []
    for w1 in valid_words1:
        row = []
        for w2 in valid_words2:
            if w1 == w2:
                # Same word gets 1.0, but we'll weight this later
                row.append(1.0)
            else:
                sim = algorithm.get_max_similarity(w1, w2)
                row.append(sim)
        sim_matrix.append(row)
    
    # Calculate sentence similarity as average of best matches
    # Direction 1: for each word in s1, find best match in s2
    sum1 = 0.0
    for row in sim_matrix:
        sum1 += max(row) if row else 0.0
    avg1 = sum1 / len(valid_words1) if valid_words1 else 0.0
    
    # Direction 2: for each word in s2, find best match in s1
    sum2 = 0.0
    for j in range(len(valid_words2)):
        col_max = 0.0
        for i in range(len(valid_words1)):
            if sim_matrix[i][j] > col_max:
                col_max = sim_matrix[i][j]
        sum2 += col_max
    avg2 = sum2 / len(valid_words2) if valid_words2 else 0.0
    
    # Final similarity: harmonic mean of both directions
    if avg1 + avg2 == 0:
        return 0.0
    
    return (2 * avg1 * avg2) / (avg1 + avg2)


# Request/Response models
class SimilarityRequest(BaseModel):
    word1: str
    word2: str


class SynsetInfo(BaseModel):
    id: str
    literals: List[str]
    pos: str
    definition: str


class AlgorithmResult(BaseModel):
    algorithm: str
    similarity: float
    synset1: Optional[str] = None
    synset2: Optional[str] = None


class SimilarityResponse(BaseModel):
    word1: str
    word2: str
    results: List[AlgorithmResult]
    synsets1: List[SynsetInfo]
    synsets2: List[SynsetInfo]


class WordSynsetsResponse(BaseModel):
    word: str
    synsets: List[SynsetInfo]


class SentenceSimilarityRequest(BaseModel):
    sentence1: str
    sentence2: str
    algorithm: str = "wup"  # Default algorithm


class SentenceSimilarityResponse(BaseModel):
    sentence1: str
    sentence2: str
    algorithm: str
    similarity: float
    words1: List[str]
    words2: List[str]
    matrix: List[List[float]]  # Similarity matrix [words1 x words2]


# API Endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize loader and algorithms on startup."""
    print("Initializing RoWordNet loader...")
    get_loader()
    get_algorithms()
    print("Initialization complete!")


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "RoWordNet Similarity API",
        "version": "1.0.0",
        "algorithms": ["PATH", "WUP", "LCH", "RES", "JCN", "LIN", "LESK", "HSO"]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    loader = get_loader()
    return {
        "status": "healthy",
        "synsets_loaded": len(loader.synset_cache),
        "words_indexed": len(loader.word_to_synsets)
    }


@app.post("/similarity", response_model=SimilarityResponse)
async def calculate_similarity(request: SimilarityRequest):
    """
    Calculate similarity between two words using all algorithms.
    
    Supports format: word or word#pos#sense (e.g., caine#n#1)
    Returns similarity scores for all 8 algorithms along with synset info.
    """
    # Parse word inputs for potential pos#sense specification
    word1_input = request.word1.strip()
    word2_input = request.word2.strip()
    
    if not word1_input or not word2_input:
        raise HTTPException(status_code=400, detail="Both words must be provided")
    
    word1, pos1, sense1 = parse_word_input(word1_input)
    word2, pos2, sense2 = parse_word_input(word2_input)
    
    loader = get_loader()
    algorithms = get_algorithms()
    
    # Get synsets for both words
    synsets1 = loader.get_synsets_for_word(word1)
    synsets2 = loader.get_synsets_for_word(word2)
    
    if not synsets1:
        raise HTTPException(status_code=404, detail=f"Word '{word1}' not found in RoWordNet")
    if not synsets2:
        raise HTTPException(status_code=404, detail=f"Word '{word2}' not found in RoWordNet")
    
    # Filter synsets by POS if specified
    if pos1:
        synsets1 = [s for s in synsets1 if loader.get_synset_pos(s) == pos1]
        if not synsets1:
            raise HTTPException(status_code=404, detail=f"No synsets with POS '{pos1}' for '{word1}'")
    if pos2:
        synsets2 = [s for s in synsets2 if loader.get_synset_pos(s) == pos2]
        if not synsets2:
            raise HTTPException(status_code=404, detail=f"No synsets with POS '{pos2}' for '{word2}'")
    
    # Select specific sense if specified
    if sense1 and sense1 >= 1 and sense1 <= len(synsets1):
        synsets1 = [synsets1[sense1 - 1]]
    if sense2 and sense2 >= 1 and sense2 <= len(synsets2):
        synsets2 = [synsets2[sense2 - 1]]
    
    # Calculate similarity for each algorithm
    results = []
    for name, algorithm in algorithms.items():
        # If specific synsets selected, use those
        if (sense1 or sense2) and len(synsets1) == 1 and len(synsets2) == 1:
            s1_id = loader.get_synset_id(synsets1[0])
            s2_id = loader.get_synset_id(synsets2[0])
            # Check POS match for most algorithms
            s1_pos = loader.get_synset_pos(synsets1[0])
            s2_pos = loader.get_synset_pos(synsets2[0])
            if s1_pos == s2_pos or name in ['lesk', 'hso']:
                similarity = algorithm.calculate_synset_similarity(s1_id, s2_id)
                results.append(AlgorithmResult(
                    algorithm=name.upper(),
                    similarity=round(similarity, 6),
                    synset1=s1_id,
                    synset2=s2_id
                ))
            else:
                results.append(AlgorithmResult(
                    algorithm=name.upper(),
                    similarity=0.0
                ))
        else:
            # Find best pair across all synsets
            best_pair = algorithm.get_best_pair(word1, word2)
            if best_pair:
                synset1_id, synset2_id, similarity = best_pair
                results.append(AlgorithmResult(
                    algorithm=name.upper(),
                    similarity=round(similarity, 6),
                    synset1=synset1_id,
                    synset2=synset2_id
                ))
            else:
                results.append(AlgorithmResult(
                    algorithm=name.upper(),
                    similarity=0.0
                ))
    
    # Format synset info
    synsets1_info = []
    for s in synsets1:
        definition = loader.get_synset_definition(s)
        synsets1_info.append(SynsetInfo(
            id=loader.get_synset_id(s),
            literals=loader.get_synset_literals(s),
            pos=loader.get_synset_pos(s),
            definition=definition[:200] if definition else ""
        ))
    
    synsets2_info = []
    for s in synsets2:
        definition = loader.get_synset_definition(s)
        synsets2_info.append(SynsetInfo(
            id=loader.get_synset_id(s),
            literals=loader.get_synset_literals(s),
            pos=loader.get_synset_pos(s),
            definition=definition[:200] if definition else ""
        ))
    
    return SimilarityResponse(
        word1=word1,
        word2=word2,
        results=results,
        synsets1=synsets1_info,
        synsets2=synsets2_info
    )


@app.get("/synsets/{word}", response_model=WordSynsetsResponse)
async def get_word_synsets(word: str):
    """Get all synsets for a word."""
    word = word.strip().lower()
    
    if not word:
        raise HTTPException(status_code=400, detail="Word must be provided")
    
    loader = get_loader()
    synsets = loader.get_synsets_for_word(word)
    
    if not synsets:
        raise HTTPException(status_code=404, detail=f"Word '{word}' not found in RoWordNet")
    
    synsets_info = []
    for s in synsets:
        definition = loader.get_synset_definition(s)
        synsets_info.append(SynsetInfo(
            id=loader.get_synset_id(s),
            literals=loader.get_synset_literals(s),
            pos=loader.get_synset_pos(s),
            definition=definition[:200] if definition else ""
        ))
    
    return WordSynsetsResponse(word=word, synsets=synsets_info)


@app.post("/sentence-similarity", response_model=SentenceSimilarityResponse)
async def calculate_sentence_sim(request: SentenceSimilarityRequest):
    """
    Calculate similarity between two sentences.
    Uses word-by-word comparison with the specified algorithm.
    """
    import re
    
    sentence1 = request.sentence1.strip()
    sentence2 = request.sentence2.strip()
    algorithm = request.algorithm.lower()
    
    if not sentence1 or not sentence2:
        raise HTTPException(status_code=400, detail="Both sentences must be provided")
    
    algorithms = get_algorithms()
    if algorithm not in algorithms:
        raise HTTPException(
            status_code=400, 
            detail=f"Unknown algorithm '{algorithm}'. Valid: {list(algorithms.keys())}"
        )
    
    loader = get_loader()
    
    # Create lemmatizer with wordnet lookup
    def wordnet_exists(word):
        return bool(loader.get_synsets_for_word(word))
    
    lemmatizer = RomanianLemmatizer(wordnet_lookup=wordnet_exists)
    
    # Tokenize sentences (including Romanian diacritics)
    words1 = re.findall(r'\b[a-zA-ZăâîșțĂÂÎȘȚ]+\b', sentence1.lower())
    words2 = re.findall(r'\b[a-zA-ZăâîșțĂÂÎȘȚ]+\b', sentence2.lower())
    
    # Lemmatize and filter to words in RoWordNet
    words1_lemmas = []
    for w in words1:
        lemma = lemmatizer.lemmatize(w)
        if loader.get_synsets_for_word(lemma):
            words1_lemmas.append(lemma)
        elif loader.get_synsets_for_word(w):
            words1_lemmas.append(w)
    
    words2_lemmas = []
    for w in words2:
        lemma = lemmatizer.lemmatize(w)
        if loader.get_synsets_for_word(lemma):
            words2_lemmas.append(lemma)
        elif loader.get_synsets_for_word(w):
            words2_lemmas.append(w)
    
    # Use lemmatized words
    words1_filtered = list(dict.fromkeys(words1_lemmas))  # Remove duplicates, preserve order
    words2_filtered = list(dict.fromkeys(words2_lemmas))
    
    if not words1_filtered or not words2_filtered:
        return SentenceSimilarityResponse(
            sentence1=sentence1,
            sentence2=sentence2,
            algorithm=algorithm.upper(),
            similarity=0.0,
            words1=words1_filtered,
            words2=words2_filtered,
            matrix=[]
        )
    
    # Build similarity matrix
    alg = algorithms[algorithm]
    sim_matrix = []
    for w1 in words1_filtered:
        row = []
        for w2 in words2_filtered:
            if w1 == w2:
                row.append(1.0)
            else:
                sim = alg.get_max_similarity(w1, w2)
                row.append(round(sim, 4))
        sim_matrix.append(row)
    
    # Calculate overall similarity using harmonic mean of bidirectional averages
    # Direction 1: for each word in s1, find best match in s2
    sum1 = sum(max(row) if row else 0.0 for row in sim_matrix)
    avg1 = sum1 / len(words1_filtered) if words1_filtered else 0.0
    
    # Direction 2: for each word in s2, find best match in s1
    sum2 = 0.0
    for j in range(len(words2_filtered)):
        col_max = max(sim_matrix[i][j] for i in range(len(words1_filtered)))
        sum2 += col_max
    avg2 = sum2 / len(words2_filtered) if words2_filtered else 0.0
    
    # Harmonic mean
    if avg1 + avg2 == 0:
        similarity = 0.0
    else:
        similarity = (2 * avg1 * avg2) / (avg1 + avg2)
    
    return SentenceSimilarityResponse(
        sentence1=sentence1,
        sentence2=sentence2,
        algorithm=algorithm.upper(),
        similarity=round(similarity, 4),
        words1=words1_filtered,
        words2=words2_filtered,
        matrix=sim_matrix
    )


@app.get("/algorithms")
async def list_algorithms():
    """List available similarity algorithms with descriptions."""
    return {
        "algorithms": [
            {
                "name": "PATH",
                "description": "Path-based similarity: 1 / path_length",
                "range": "0 to 1"
            },
            {
                "name": "WUP",
                "description": "Wu-Palmer: (2 * depth(LCS)) / (depth(s1) + depth(s2))",
                "range": "0 to 1"
            },
            {
                "name": "LCH",
                "description": "Leacock-Chodorow: -log(path / (2 * max_depth))",
                "range": "0 to ~3.7"
            },
            {
                "name": "RES",
                "description": "Resnik: IC(LCS)",
                "range": "0 to max_IC"
            },
            {
                "name": "JCN",
                "description": "Jiang-Conrath: 1 / (IC(s1) + IC(s2) - 2*IC(LCS))",
                "range": "0 to infinity"
            },
            {
                "name": "LIN",
                "description": "Lin: (2 * IC(LCS)) / (IC(s1) + IC(s2))",
                "range": "0 to 1"
            },
            {
                "name": "LESK",
                "description": "Lesk: Gloss overlap count",
                "range": "0 to gloss_length"
            },
            {
                "name": "HSO",
                "description": "Hirst-St-Onge: C - path - k*direction_changes",
                "range": "0 to 16"
            }
        ]
    }


# Run with: uvicorn main:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

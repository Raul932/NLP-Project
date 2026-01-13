'use client';

import { useState } from 'react';
import SimilarityForm from '@/components/SimilarityForm';
import ResultsTable from '@/components/ResultsTable';

// API response types
interface SynsetInfo {
    id: string;
    literals: string[];
    pos: string;
    definition: string;
}

interface AlgorithmResult {
    algorithm: string;
    similarity: number;
    synset1?: string;
    synset2?: string;
}

interface SimilarityResponse {
    word1: string;
    word2: string;
    results: AlgorithmResult[];
    synsets1: SynsetInfo[];
    synsets2: SynsetInfo[];
}

interface SentenceSimilarityResponse {
    sentence1: string;
    sentence2: string;
    algorithm: string;
    similarity: number;
    words1: string[];
    words2: string[];
    words1_found: boolean[];
    words2_found: boolean[];
    matrix: (number | null)[][];
}

// Algorithm descriptions for info section
const algorithmInfo = [
    { name: 'PATH', formula: '1 / path_length', description: 'Inverse of shortest path between synsets' },
    { name: 'WUP', formula: '2*depth(LCS) / (depth(s1)+depth(s2))', description: 'Wu-Palmer depth-based similarity' },
    { name: 'LCH', formula: '-log(path / 2*max_depth)', description: 'Leacock-Chodorow log-scaled path' },
    { name: 'RES', formula: 'IC(LCS)', description: 'Resnik Information Content of LCS' },
    { name: 'JCN', formula: '1 / (IC(s1)+IC(s2)-2*IC(LCS))', description: 'Jiang-Conrath IC distance' },
    { name: 'LIN', formula: '2*IC(LCS) / (IC(s1)+IC(s2))', description: 'Lin normalized IC similarity' },
    { name: 'LESK', formula: 'gloss_overlap', description: 'Gloss/definition word overlap' },
    { name: 'HSO', formula: 'C - path - k*dir_changes', description: 'Hirst-St-Onge path with direction penalty' },
];

const algorithms = ['wup', 'path', 'lch', 'res', 'jcn', 'lin', 'lesk', 'hso'];

export default function Home() {
    const [mode, setMode] = useState<'word' | 'sentence'>('word');
    const [results, setResults] = useState<SimilarityResponse | null>(null);
    const [sentenceResults, setSentenceResults] = useState<SentenceSimilarityResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Sentence mode state
    const [sentence1, setSentence1] = useState('');
    const [sentence2, setSentence2] = useState('');
    const [selectedAlgorithm, setSelectedAlgorithm] = useState('wup');

    const handleWordSubmit = async (word1: string, word2: string) => {
        setLoading(true);
        setError(null);
        setResults(null);

        try {
            const response = await fetch('http://localhost:8000/similarity', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ word1, word2 }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to calculate similarity');
            }

            const data: SimilarityResponse = await response.json();
            setResults(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    const handleSentenceSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!sentence1.trim() || !sentence2.trim()) return;

        setLoading(true);
        setError(null);
        setSentenceResults(null);

        try {
            const response = await fetch('http://localhost:8000/sentence-similarity', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    sentence1: sentence1.trim(),
                    sentence2: sentence2.trim(),
                    algorithm: selectedAlgorithm
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to calculate similarity');
            }

            const data: SentenceSimilarityResponse = await response.json();
            setSentenceResults(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="container">
            {/* Header */}
            <header className="header">
                <h1>RoWordNet Similarity</h1>
                <p>
                    Compute semantic similarity between Romanian words or sentences using 8 different algorithms.
                    Based on the Romanian WordNet lexical database.
                </p>
            </header>

            {/* Mode Tabs */}
            <div className="card" style={{ padding: '0.5rem' }}>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button
                        onClick={() => setMode('word')}
                        style={{
                            flex: 1,
                            padding: '1rem',
                            background: mode === 'word' ? 'var(--primary-gradient)' : 'transparent',
                            border: mode === 'word' ? 'none' : '1px solid var(--border-glow)',
                            borderRadius: '8px',
                            color: 'white',
                            cursor: 'pointer',
                            fontWeight: 600,
                            fontSize: '1rem'
                        }}
                    >
                        Word Similarity
                    </button>
                    <button
                        onClick={() => setMode('sentence')}
                        style={{
                            flex: 1,
                            padding: '1rem',
                            background: mode === 'sentence' ? 'var(--primary-gradient)' : 'transparent',
                            border: mode === 'sentence' ? 'none' : '1px solid var(--border-glow)',
                            borderRadius: '8px',
                            color: 'white',
                            cursor: 'pointer',
                            fontWeight: 600,
                            fontSize: '1rem'
                        }}
                    >
                        Sentence Similarity
                    </button>
                </div>
            </div>

            {/* Word Mode */}
            {mode === 'word' && (
                <>
                    <div className="card">
                        <h2>Enter Words</h2>
                        <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem', fontSize: '0.875rem' }}>
                            Format: word or word#pos#sense (e.g., caine#n#1)
                        </p>
                        <SimilarityForm onSubmit={handleWordSubmit} loading={loading} />

                        {error && (
                            <div className="error-message">
                                {error}
                            </div>
                        )}
                    </div>

                    {results && (
                        <div className="card fade-in">
                            <h2>Similarity Results</h2>
                            <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
                                Comparing <strong style={{ color: 'var(--accent-blue)' }}>{results.word1}</strong> and{' '}
                                <strong style={{ color: 'var(--accent-purple)' }}>{results.word2}</strong>
                            </p>
                            <ResultsTable results={results.results} />

                            {/* Synset details */}
                            <div className="form-row" style={{ marginTop: '2rem' }}>
                                <div>
                                    <h3 style={{ marginBottom: '1rem', color: 'var(--accent-blue)' }}>
                                        Synsets for &quot;{results.word1}&quot;
                                    </h3>
                                    <div className="synset-list">
                                        {results.synsets1.slice(0, 5).map((synset, index) => (
                                            <div key={synset.id} className="synset-item">
                                                <div className="synset-id">
                                                    #{index + 1} - {synset.id}
                                                </div>
                                                <div className="synset-literals">
                                                    {synset.literals.join(', ')}
                                                    <span className="synset-pos">{synset.pos}</span>
                                                </div>
                                                {synset.definition && (
                                                    <div className="synset-definition">{synset.definition}</div>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                                <div>
                                    <h3 style={{ marginBottom: '1rem', color: 'var(--accent-purple)' }}>
                                        Synsets for &quot;{results.word2}&quot;
                                    </h3>
                                    <div className="synset-list">
                                        {results.synsets2.slice(0, 5).map((synset, index) => (
                                            <div key={synset.id} className="synset-item">
                                                <div className="synset-id">
                                                    #{index + 1} - {synset.id}
                                                </div>
                                                <div className="synset-literals">
                                                    {synset.literals.join(', ')}
                                                    <span className="synset-pos">{synset.pos}</span>
                                                </div>
                                                {synset.definition && (
                                                    <div className="synset-definition">{synset.definition}</div>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </>
            )}

            {/* Sentence Mode */}
            {mode === 'sentence' && (
                <>
                    <div className="card">
                        <h2>Enter Sentences</h2>

                        {/* Example sentences */}
                        <div style={{ marginBottom: '1.5rem' }}>
                            <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', display: 'block', marginBottom: '0.5rem' }}>
                                Try examples:
                            </span>
                            {[
                                ['câine pisică animal mamifer', 'lup vulpe urs fiară'],
                                ['copac frunză floare plantă', 'arbore pământ natură iarbă'],
                                ['doctor medic spital boală', 'profesor elev școală carte'],
                                ['mașină automobil drum transport', 'avion zbor cer aeroport'],
                            ].map((pair, index) => (
                                <button
                                    key={index}
                                    type="button"
                                    onClick={() => {
                                        setSentence1(pair[0]);
                                        setSentence2(pair[1]);
                                    }}
                                    disabled={loading}
                                    style={{
                                        background: 'rgba(102, 126, 234, 0.1)',
                                        border: '1px solid var(--border-glow)',
                                        color: 'var(--text-secondary)',
                                        padding: '0.5rem 0.75rem',
                                        borderRadius: '6px',
                                        cursor: 'pointer',
                                        fontSize: '0.75rem',
                                        marginRight: '0.5rem',
                                        marginBottom: '0.5rem',
                                        transition: 'all 0.2s ease',
                                    }}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.background = 'rgba(102, 126, 234, 0.2)';
                                        e.currentTarget.style.color = 'var(--text-primary)';
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.background = 'rgba(102, 126, 234, 0.1)';
                                        e.currentTarget.style.color = 'var(--text-secondary)';
                                    }}
                                >
                                    &quot;{pair[0]}&quot; / &quot;{pair[1]}&quot;
                                </button>
                            ))}
                        </div>

                        <form onSubmit={handleSentenceSubmit}>
                            <div className="form-group">
                                <label className="form-label" htmlFor="sentence1">
                                    First Sentence
                                </label>
                                <textarea
                                    id="sentence1"
                                    className="form-input"
                                    value={sentence1}
                                    onChange={(e) => setSentence1(e.target.value)}
                                    placeholder="Enter first Romanian sentence..."
                                    disabled={loading}
                                    style={{ minHeight: '80px', resize: 'vertical' }}
                                />
                            </div>
                            <div className="form-group">
                                <label className="form-label" htmlFor="sentence2">
                                    Second Sentence
                                </label>
                                <textarea
                                    id="sentence2"
                                    className="form-input"
                                    value={sentence2}
                                    onChange={(e) => setSentence2(e.target.value)}
                                    placeholder="Enter second Romanian sentence..."
                                    disabled={loading}
                                    style={{ minHeight: '80px', resize: 'vertical' }}
                                />
                            </div>
                            <div className="form-group">
                                <label className="form-label" htmlFor="algorithm">
                                    Algorithm
                                </label>
                                <select
                                    id="algorithm"
                                    className="form-input"
                                    value={selectedAlgorithm}
                                    onChange={(e) => setSelectedAlgorithm(e.target.value)}
                                    disabled={loading}
                                >
                                    {algorithms.map((alg) => (
                                        <option key={alg} value={alg}>{alg.toUpperCase()}</option>
                                    ))}
                                </select>
                            </div>
                            <button
                                type="submit"
                                className="btn btn-primary btn-full"
                                disabled={loading || !sentence1.trim() || !sentence2.trim()}
                            >
                                {loading ? (
                                    <>
                                        <span className="spinner"></span>
                                        Calculating...
                                    </>
                                ) : (
                                    'Calculate Sentence Similarity'
                                )}
                            </button>
                        </form>

                        {error && (
                            <div className="error-message">
                                {error}
                            </div>
                        )}
                    </div>

                    {sentenceResults && (
                        <div className="card fade-in">
                            <h2>Sentence Similarity Results</h2>
                            <div style={{
                                textAlign: 'center',
                                padding: '2rem',
                                background: 'rgba(102, 126, 234, 0.1)',
                                borderRadius: '12px',
                                marginBottom: '1.5rem'
                            }}>
                                <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                                    {sentenceResults.algorithm} Similarity Score
                                </div>
                                <div style={{
                                    fontSize: '3rem',
                                    fontWeight: 800,
                                    background: 'var(--primary-gradient)',
                                    WebkitBackgroundClip: 'text',
                                    WebkitTextFillColor: 'transparent'
                                }}>
                                    {sentenceResults.similarity.toFixed(4)}
                                </div>
                            </div>

                            <div className="form-row">
                                <div>
                                    <h4 style={{ marginBottom: '0.5rem', color: 'var(--accent-blue)' }}>
                                        Words found in Sentence 1
                                    </h4>
                                    <p style={{ color: 'var(--text-secondary)' }}>
                                        {sentenceResults.words1.length > 0
                                            ? sentenceResults.words1.join(', ')
                                            : 'No words found in RoWordNet'}
                                    </p>
                                </div>
                                <div>
                                    <h4 style={{ marginBottom: '0.5rem', color: 'var(--accent-purple)' }}>
                                        Words found in Sentence 2
                                    </h4>
                                    <p style={{ color: 'var(--text-secondary)' }}>
                                        {sentenceResults.words2.length > 0
                                            ? sentenceResults.words2.join(', ')
                                            : 'No words found in RoWordNet'}
                                    </p>
                                </div>
                            </div>

                            {/* Similarity Matrix */}
                            {sentenceResults.matrix && sentenceResults.matrix.length > 0 && (
                                <div style={{ marginTop: '2rem' }}>
                                    <h4 style={{ marginBottom: '1rem' }}>Similarity Matrix</h4>
                                    <div style={{ overflowX: 'auto' }}>
                                        <table style={{
                                            width: '100%',
                                            borderCollapse: 'collapse',
                                            fontSize: '0.875rem'
                                        }}>
                                            <thead>
                                                <tr>
                                                    <th style={{
                                                        padding: '0.75rem',
                                                        background: 'rgba(102, 126, 234, 0.2)',
                                                        border: '1px solid var(--border-glow)',
                                                        textAlign: 'left'
                                                    }}>
                                                        S1 ↓ / S2 →
                                                    </th>
                                                    {sentenceResults.words2.map((w2, j) => (
                                                        <th key={j} style={{
                                                            padding: '0.75rem',
                                                            background: 'rgba(118, 75, 162, 0.2)',
                                                            border: '1px solid var(--border-glow)',
                                                            textAlign: 'center',
                                                            color: sentenceResults.words2_found?.[j] ? 'var(--accent-purple)' : 'var(--text-secondary)',
                                                            textDecoration: sentenceResults.words2_found?.[j] ? 'none' : 'line-through'
                                                        }}>
                                                            {w2}
                                                            {!sentenceResults.words2_found?.[j] && <span style={{ fontSize: '0.7rem', marginLeft: '0.25rem' }}>✗</span>}
                                                        </th>
                                                    ))}
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {sentenceResults.matrix.map((row, i) => (
                                                    <tr key={i}>
                                                        <td style={{
                                                            padding: '0.75rem',
                                                            background: 'rgba(102, 126, 234, 0.1)',
                                                            border: '1px solid var(--border-glow)',
                                                            fontWeight: 600,
                                                            color: sentenceResults.words1_found?.[i] ? 'var(--accent-blue)' : 'var(--text-secondary)',
                                                            textDecoration: sentenceResults.words1_found?.[i] ? 'none' : 'line-through'
                                                        }}>
                                                            {sentenceResults.words1[i]}
                                                            {!sentenceResults.words1_found?.[i] && <span style={{ fontSize: '0.7rem', marginLeft: '0.25rem' }}>✗</span>}
                                                        </td>
                                                        {row.map((val, j) => (
                                                            <td key={j} style={{
                                                                padding: '0.75rem',
                                                                border: '1px solid var(--border-glow)',
                                                                textAlign: 'center',
                                                                background: val === null
                                                                    ? 'rgba(100, 100, 100, 0.1)'
                                                                    : val >= 0.8
                                                                        ? 'rgba(46, 213, 115, 0.3)'
                                                                        : val >= 0.5
                                                                            ? 'rgba(255, 200, 0, 0.2)'
                                                                            : 'transparent',
                                                                color: val === null
                                                                    ? 'var(--text-secondary)'
                                                                    : val >= 0.8 ? 'var(--accent-green)' : 'var(--text-primary)'
                                                            }}>
                                                                {val === null ? '—' : val.toFixed(4)}
                                                            </td>
                                                        ))}
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </>
            )}

            {/* Algorithm Info */}
            <div className="card info-section">
                <h2>Similarity Algorithms</h2>
                <div className="info-grid">
                    {algorithmInfo.map((alg) => (
                        <div key={alg.name} className="info-item">
                            <h4>{alg.name}</h4>
                            <p><code style={{ color: 'var(--accent-pink)' }}>{alg.formula}</code></p>
                            <p>{alg.description}</p>
                        </div>
                    ))}
                </div>
            </div>

            {/* Footer */}
            <footer className="footer">
                <p>RoWordNet Similarity Demo - NLP Project</p>
                <p style={{ marginTop: '0.5rem' }}>
                    Algorithms implemented from scratch: PATH, WUP, LCH, RES, JCN, LIN, LESK, HSO
                </p>
            </footer>
        </main>
    );
}

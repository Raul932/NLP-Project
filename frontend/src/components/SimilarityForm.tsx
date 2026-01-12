'use client';

import { useState, FormEvent } from 'react';

interface SimilarityFormProps {
    onSubmit: (word1: string, word2: string) => void;
    loading: boolean;
}

export default function SimilarityForm({ onSubmit, loading }: SimilarityFormProps) {
    const [word1, setWord1] = useState('');
    const [word2, setWord2] = useState('');

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault();
        if (word1.trim() && word2.trim()) {
            onSubmit(word1.trim(), word2.trim());
        }
    };

    // Example word pairs for quick testing
    const examplePairs = [
        ['câine', 'pisică'],
        ['floare', 'copac'],
        ['mașină', 'avion'],
        ['carte', 'jurnal'],
    ];

    // Examples with POS and sense
    const posExamples = [
        ['câine#n#1', 'pisică#n#1'],
        ['floare#n#1', 'copac#n#1'],
        ['merge#v#1', 'aleargă#v#1'],
    ];

    const handleExampleClick = (pair: string[]) => {
        setWord1(pair[0]);
        setWord2(pair[1]);
    };

    return (
        <form onSubmit={handleSubmit}>
            <div className="form-row">
                <div className="form-group">
                    <label className="form-label" htmlFor="word1">
                        First Word
                    </label>
                    <input
                        id="word1"
                        type="text"
                        className="form-input"
                        value={word1}
                        onChange={(e) => setWord1(e.target.value)}
                        placeholder="Enter first Romanian word..."
                        disabled={loading}
                        autoComplete="off"
                    />
                </div>
                <div className="form-group">
                    <label className="form-label" htmlFor="word2">
                        Second Word
                    </label>
                    <input
                        id="word2"
                        type="text"
                        className="form-input"
                        value={word2}
                        onChange={(e) => setWord2(e.target.value)}
                        placeholder="Enter second Romanian word..."
                        disabled={loading}
                        autoComplete="off"
                    />
                </div>
            </div>

            {/* Example word pairs */}
            <div style={{ marginBottom: '1.5rem' }}>
                <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginRight: '0.75rem' }}>
                    Try examples:
                </span>
                {examplePairs.map((pair, index) => (
                    <button
                        key={index}
                        type="button"
                        onClick={() => handleExampleClick(pair)}
                        disabled={loading}
                        style={{
                            background: 'rgba(102, 126, 234, 0.1)',
                            border: '1px solid var(--border-glow)',
                            color: 'var(--text-secondary)',
                            padding: '0.25rem 0.75rem',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontSize: '0.875rem',
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
                        {pair[0]} / {pair[1]}
                    </button>
                ))}
            </div>

            {/* POS/Sense examples */}
            <div style={{ marginBottom: '1.5rem' }}>
                <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginRight: '0.75rem' }}>
                    With POS#sense:
                </span>
                {posExamples.map((pair, index) => (
                    <button
                        key={`pos-${index}`}
                        type="button"
                        onClick={() => handleExampleClick(pair)}
                        disabled={loading}
                        style={{
                            background: 'rgba(118, 75, 162, 0.1)',
                            border: '1px solid rgba(118, 75, 162, 0.3)',
                            color: 'var(--text-secondary)',
                            padding: '0.25rem 0.75rem',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontSize: '0.75rem',
                            marginRight: '0.5rem',
                            marginBottom: '0.5rem',
                            transition: 'all 0.2s ease',
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.background = 'rgba(118, 75, 162, 0.2)';
                            e.currentTarget.style.color = 'var(--text-primary)';
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.background = 'rgba(118, 75, 162, 0.1)';
                            e.currentTarget.style.color = 'var(--text-secondary)';
                        }}
                    >
                        {pair[0]} / {pair[1]}
                    </button>
                ))}
            </div>

            <button
                type="submit"
                className="btn btn-primary btn-full"
                disabled={loading || !word1.trim() || !word2.trim()}
            >
                {loading ? (
                    <>
                        <span className="spinner"></span>
                        Calculating...
                    </>
                ) : (
                    'Calculate Similarity'
                )}
            </button>
        </form>
    );
}

'use client';

interface AlgorithmResult {
    algorithm: string;
    similarity: number;
    synset1?: string;
    synset2?: string;
}

interface ResultsTableProps {
    results: AlgorithmResult[];
}

// Normalize similarity scores for visual bar display
function normalizeScore(algorithm: string, score: number): number {
    // Different algorithms have different ranges
    switch (algorithm) {
        case 'PATH':
        case 'WUP':
        case 'LIN':
            // Already 0-1 range
            return Math.min(score, 1);
        case 'LCH':
            // Range is roughly 0-3.7
            return Math.min(score / 3.7, 1);
        case 'RES':
            // Range depends on corpus, typically 0-10
            return Math.min(score / 10, 1);
        case 'JCN':
            // Can be very large, cap at reasonable value
            return Math.min(score / 10, 1);
        case 'LESK':
            // Overlap count, typically 0-20
            return Math.min(score / 20, 1);
        case 'HSO':
            // Range is 0-16
            return Math.min(score / 16, 1);
        default:
            return Math.min(score, 1);
    }
}

// Format score for display
function formatScore(score: number): string {
    if (score >= 1000000) {
        return 'MAX';
    }
    if (score >= 100) {
        return score.toFixed(2);
    }
    return score.toFixed(4);
}

export default function ResultsTable({ results }: ResultsTableProps) {
    // Sort by similarity (descending)
    const sortedResults = [...results].sort((a, b) => b.similarity - a.similarity);

    return (
        <table className="results-table">
            <thead>
                <tr>
                    <th>Algorithm</th>
                    <th>Score</th>
                    <th style={{ width: '30%' }}>Visual</th>
                    <th>Best Synset Pair</th>
                </tr>
            </thead>
            <tbody>
                {sortedResults.map((result) => {
                    const normalizedScore = normalizeScore(result.algorithm, result.similarity);

                    return (
                        <tr key={result.algorithm}>
                            <td>
                                <span className="algorithm-name">{result.algorithm}</span>
                            </td>
                            <td>
                                <span className="similarity-value">{formatScore(result.similarity)}</span>
                            </td>
                            <td>
                                <div className="similarity-bar">
                                    <div
                                        className="similarity-bar-fill"
                                        style={{ width: `${normalizedScore * 100}%` }}
                                    />
                                </div>
                            </td>
                            <td style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontFamily: 'JetBrains Mono, monospace' }}>
                                {result.synset1 && result.synset2 ? (
                                    <span title={`${result.synset1} - ${result.synset2}`}>
                                        {result.synset1.slice(-15)} / {result.synset2.slice(-15)}
                                    </span>
                                ) : (
                                    <span>-</span>
                                )}
                            </td>
                        </tr>
                    );
                })}
            </tbody>
        </table>
    );
}

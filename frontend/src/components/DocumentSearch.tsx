'use client';

import { useState } from 'react';

interface SearchResult {
  content: string;
  metadata: {
    filename: string;
    content_category: string;
  };
}

export default function DocumentSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `http://localhost:8000/search?query=${encodeURIComponent(query)}&max_results=5`
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const searchResults = await response.json();
      setResults(searchResults);
    } catch (err) {
      setError('Failed to search documents. Please check the API connection.');
      console.error('Search failed:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-card p-6 rounded-lg shadow-lg">
      <h3 className="text-xl font-bold mb-4 text-contrast">Regulatory Document Search</h3>
      
      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex space-x-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search regulations, guidelines, or compliance requirements..."
            className="flex-1"
          />
          <button
            type="submit"
            disabled={isLoading || !query.trim()}
            className="btn-primary px-4 py-2 rounded-lg"
          >
            {isLoading ? (
              <div className="animate-spin w-5 h-5 border-2 border-primary-foreground border-t-transparent rounded-full"></div>
            ) : (
              'Search'
            )}
          </button>
        </div>
      </form>

      {error && (
        <div className="bg-destructive/10 border border-destructive/20 p-3 rounded-lg mb-4">
          <span className="text-destructive text-sm">{error}</span>
        </div>
      )}

      {results.length > 0 && (
        <div className="space-y-4">
          <h4 className="font-semibold text-contrast">Search Results ({results.length})</h4>
          {results.map((result, index) => (
            <div key={index} className="border border-border p-4 rounded-lg">
              <div className="flex items-start justify-between mb-2">
                <h5 className="font-medium text-contrast">{result.metadata.filename}</h5>
                <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded">
                  {result.metadata.content_category}
                </span>
              </div>
              <p className="text-sm text-muted-foreground">
                {result.content.substring(0, 300)}
                {result.content.length > 300 && '...'}
              </p>
            </div>
          ))}
        </div>
      )}

      {results.length === 0 && !isLoading && !error && query && (
        <div className="text-center text-muted-foreground py-8">
          No results found for &quot;{query}&quot;
        </div>
      )}
    </div>
  );
}
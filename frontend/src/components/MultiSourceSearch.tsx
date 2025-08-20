'use client';

import { useState } from 'react';

interface SearchResult {
  title: string;
  url: string;
  content: string;
  score: number;
  source: string;
  query: string;
}

interface SearchResponse {
  results: SearchResult[];
  total_results: number;
  search_time: number;
  sources_used: string[];
}

export default function MultiSourceSearch() {
  const [queries, setQueries] = useState<string[]>(['']);
  const [selectedAPIs, setSelectedAPIs] = useState<string[]>(['tavily']);
  const [maxResults, setMaxResults] = useState(5);
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string>('');

  const availableAPIs = [
    { id: 'tavily', name: 'Tavily (Web Search)', description: 'Real-time web search and news' },
    { id: 'perplexity', name: 'Perplexity', description: 'AI-powered research assistant' },
    { id: 'exa', name: 'Exa', description: 'Neural web search' },
    { id: 'arxiv', name: 'ArXiv', description: 'Academic papers and preprints' },
    { id: 'pubmed', name: 'PubMed', description: 'Medical and life science literature' }
  ];

  const addQuery = () => {
    setQueries([...queries, '']);
  };

  const updateQuery = (index: number, value: string) => {
    const newQueries = [...queries];
    newQueries[index] = value;
    setQueries(newQueries);
  };

  const removeQuery = (index: number) => {
    if (queries.length > 1) {
      setQueries(queries.filter((_, i) => i !== index));
    }
  };

  const toggleAPI = (apiId: string) => {
    if (selectedAPIs.includes(apiId)) {
      setSelectedAPIs(selectedAPIs.filter(id => id !== apiId));
    } else {
      setSelectedAPIs([...selectedAPIs, apiId]);
    }
  };

  const handleSearch = async () => {
    if (queries.filter(q => q.trim()).length === 0) {
      setError('Please enter at least one search query');
      return;
    }

    if (selectedAPIs.length === 0) {
      setError('Please select at least one search API');
      return;
    }

    setIsSearching(true);
    setError('');
    
    try {
      const response = await fetch('http://localhost:8000/research/multi-source-search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          queries: queries.filter(q => q.trim()),
          search_apis: selectedAPIs,
          max_results: maxResults
        }),
      });

      if (!response.ok) {
        throw new Error(`Search failed: ${response.statusText}`);
      }

      const data = await response.json();
      setSearchResults(data[0]); // API returns array, take first result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Search Configuration */}
      <div className="bg-card p-6 rounded-lg shadow-lg">
        <h2 className="text-2xl font-bold mb-4 text-contrast">Multi-Source Intelligence Search</h2>
        <p className="text-muted-foreground mb-6">
          Search across multiple APIs simultaneously for comprehensive intelligence gathering
        </p>

        {/* Search Queries */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-contrast mb-3">
            Search Queries ({queries.filter(q => q.trim()).length}/5)
          </label>
          {queries.map((query, index) => (
            <div key={index} className="flex space-x-2 mb-2">
              <input
                type="text"
                value={query}
                onChange={(e) => updateQuery(index, e.target.value)}
                placeholder="Enter search query..."
                className="flex-1 px-3 py-2 border border-input bg-background rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              />
              {queries.length > 1 && (
                <button
                  onClick={() => removeQuery(index)}
                  className="px-3 py-2 bg-destructive text-destructive-foreground rounded-md hover:bg-destructive/90"
                >
                  Remove
                </button>
              )}
            </div>
          ))}
          {queries.length < 5 && (
            <button
              onClick={addQuery}
              className="mt-2 px-4 py-2 bg-secondary text-secondary-foreground rounded-md hover:bg-accent"
            >
              Add Query
            </button>
          )}
        </div>

        {/* API Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-contrast mb-3">
            Search APIs ({selectedAPIs.length} selected)
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {availableAPIs.map((api) => (
              <div
                key={api.id}
                className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                  selectedAPIs.includes(api.id)
                    ? 'border-primary bg-primary/10'
                    : 'border-input hover:bg-accent'
                }`}
                onClick={() => toggleAPI(api.id)}
              >
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={selectedAPIs.includes(api.id)}
                    onChange={() => toggleAPI(api.id)}
                    className="w-4 h-4"
                  />
                  <div>
                    <div className="font-medium text-contrast">{api.name}</div>
                    <div className="text-sm text-muted-foreground">{api.description}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Search Settings */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-contrast mb-2">
            Max Results per API
          </label>
          <input
            type="number"
            value={maxResults}
            onChange={(e) => setMaxResults(parseInt(e.target.value) || 5)}
            min="1"
            max="20"
            className="w-24 px-3 py-2 border border-input bg-background rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        {/* Search Button */}
        <button
          onClick={handleSearch}
          disabled={isSearching}
          className="w-full bg-primary text-primary-foreground py-3 px-6 rounded-lg font-medium hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSearching ? 'Searching...' : 'Start Multi-Source Search'}
        </button>

        {error && (
          <div className="mt-4 p-3 bg-destructive/10 border border-destructive text-destructive rounded-md">
            {error}
          </div>
        )}
      </div>

      {/* Search Results */}
      {searchResults && (
        <div className="bg-card p-6 rounded-lg shadow-lg">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-bold text-contrast">Search Results</h3>
            <div className="text-sm text-muted-foreground">
              {searchResults.total_results} results in {searchResults.search_time.toFixed(2)}s
            </div>
          </div>

          {/* Sources Used */}
          <div className="mb-4">
            <div className="flex flex-wrap gap-2">
              {searchResults.sources_used.map((source) => (
                <span
                  key={source}
                  className="px-2 py-1 bg-primary/10 text-primary text-xs rounded-full"
                >
                  {source}
                </span>
              ))}
            </div>
          </div>

          {/* Results */}
          <div className="space-y-4">
            {searchResults.results.map((result, index) => (
              <div key={index} className="border border-input rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <a
                    href={result.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-lg font-semibold text-primary hover:underline"
                  >
                    {result.title}
                  </a>
                  <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                    <span className="bg-secondary px-2 py-1 rounded text-xs">{result.source}</span>
                    <span>Score: {result.score.toFixed(2)}</span>
                  </div>
                </div>
                <p className="text-muted-foreground text-sm mb-2">
                  Query: "{result.query}"
                </p>
                <p className="text-contrast">
                  {result.content.length > 300 
                    ? `${result.content.substring(0, 300)}...` 
                    : result.content
                  }
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

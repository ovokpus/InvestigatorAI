'use client';

import { useState } from 'react';

interface ExchangeRateResult {
  result: string;
  source: string;
  timestamp: string;
}

export default function ExchangeRate() {
  const [fromCurrency, setFromCurrency] = useState('EUR');
  const [toCurrency, setToCurrency] = useState('USD');
  const [result, setResult] = useState<ExchangeRateResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const currencies = [
    { code: 'USD', name: 'US Dollar' },
    { code: 'EUR', name: 'Euro' },
    { code: 'GBP', name: 'British Pound' },
    { code: 'JPY', name: 'Japanese Yen' },
    { code: 'CAD', name: 'Canadian Dollar' },
    { code: 'AUD', name: 'Australian Dollar' },
    { code: 'CHF', name: 'Swiss Franc' },
    { code: 'CNY', name: 'Chinese Yuan' },
    { code: 'AED', name: 'UAE Dirham' },
    { code: 'SAR', name: 'Saudi Riyal' }
  ];

  const handleLookup = async (e: React.FormEvent) => {
    e.preventDefault();
    
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `http://localhost:8000/exchange-rate?from_currency=${fromCurrency}&to_currency=${toCurrency}`
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const exchangeResult = await response.json();
      setResult(exchangeResult);
    } catch (err) {
      setError('Failed to fetch exchange rate. Please check the API connection.');
      console.error('Exchange rate lookup failed:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-card p-6 rounded-lg shadow-lg">
      <h3 className="text-xl font-bold mb-4 text-contrast">Currency Exchange Rate</h3>
      
      <form onSubmit={handleLookup} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
          <div>
            <label className="block text-sm font-medium text-contrast mb-2">
              From Currency
            </label>
            <select
              value={fromCurrency}
              onChange={(e) => setFromCurrency(e.target.value)}
              className="w-full"
            >
              {currencies.map((currency) => (
                <option key={currency.code} value={currency.code}>
                  {currency.code} - {currency.name}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-contrast mb-2">
              To Currency
            </label>
            <select
              value={toCurrency}
              onChange={(e) => setToCurrency(e.target.value)}
              className="w-full"
            >
              {currencies.map((currency) => (
                <option key={currency.code} value={currency.code}>
                  {currency.code} - {currency.name}
                </option>
              ))}
            </select>
          </div>
          
          <button
            type="submit"
            disabled={isLoading}
            className="btn-primary px-4 py-2 rounded-lg h-fit"
          >
            {isLoading ? (
              <div className="flex items-center space-x-2">
                <div className="animate-spin w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full"></div>
                <span>Loading...</span>
              </div>
            ) : (
              'Get Rate'
            )}
          </button>
        </div>
      </form>

      {error && (
        <div className="bg-destructive/10 border border-destructive/20 p-3 rounded-lg mt-4">
          <span className="text-destructive text-sm">{error}</span>
        </div>
      )}

      {result && (
        <div className="mt-6 p-4 bg-primary/5 border border-primary/20 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-lg font-semibold text-contrast">
                {fromCurrency} → {toCurrency}
              </div>
              <div className="text-2xl font-bold text-primary mt-1">
                {result.result}
              </div>
            </div>
            <div className="text-right text-sm text-muted-foreground">
              <div>Source: {result.source}</div>
              <div>{new Date(result.timestamp).toLocaleString()}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
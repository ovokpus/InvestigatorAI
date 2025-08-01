'use client';

import { useState, useEffect } from 'react';

interface HealthData {
  status: string;
  api_keys_available: boolean;
  vector_store_initialized: boolean;
  timestamp: string;
  version: string;
}

export default function HealthStatus() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('http://localhost:8000/health');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setHealth(data);
        setError(null);
      } catch (err) {
        setError('Failed to connect to API');
        console.error('Health check failed:', err);
      } finally {
        setIsLoading(false);
      }
    };

    checkHealth();
    // Check health every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <div className="bg-card p-4 rounded-lg shadow">
        <div className="flex items-center space-x-2">
          <div className="animate-spin w-4 h-4 border-2 border-primary border-t-transparent rounded-full"></div>
          <span className="text-muted-foreground">Checking API status...</span>
        </div>
      </div>
    );
  }

  if (error || !health) {
    return (
      <div className="bg-destructive/10 border border-destructive/20 p-4 rounded-lg">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-destructive rounded-full"></div>
          <span className="text-destructive font-medium">API Offline</span>
          <span className="text-sm text-muted-foreground">- {error}</span>
        </div>
      </div>
    );
  }

  const isHealthy = health.status === 'healthy' && health.api_keys_available && health.vector_store_initialized;

  return (
    <div className="bg-card p-4 rounded-lg shadow">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className={`w-3 h-3 rounded-full ${isHealthy ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
          <span className="font-medium text-contrast">
            API Status: {health.status}
          </span>
          <span className="text-sm text-muted-foreground">v{health.version}</span>
        </div>
        
        <div className="flex items-center space-x-6 text-sm">
          <div className="flex items-center space-x-2">
            <span className="text-muted-foreground">AI Models:</span>
            <span className={`${health.api_keys_available ? 'text-green-600' : 'text-red-600'}`}>
              {health.api_keys_available ? '✓ Ready' : '✗ Unavailable'}
            </span>
          </div>
          
          <div className="flex items-center space-x-2">
            <span className="text-muted-foreground">Vector DB:</span>
            <span className={`${health.vector_store_initialized ? 'text-green-600' : 'text-red-600'}`}>
              {health.vector_store_initialized ? '✓ Ready' : '✗ Unavailable'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
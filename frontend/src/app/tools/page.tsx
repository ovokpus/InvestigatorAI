'use client';

import Header from '@/components/Header';
import HealthStatus from '@/components/HealthStatus';
import DocumentSearch from '@/components/DocumentSearch';
import ExchangeRate from '@/components/ExchangeRate';

export default function ToolsPage() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="mb-8">
          <HealthStatus />
        </div>

        {/* Navigation Bar */}
        <div className="mb-8">
          <nav className="flex space-x-4">
            <a 
              href="/" 
              className="px-4 py-2 bg-secondary text-secondary-foreground hover:bg-accent rounded-lg font-medium transition-colors"
            >
              Investigation
            </a>
            <span className="px-4 py-2 bg-primary text-primary-foreground rounded-lg font-medium">
              Tools & Search
            </span>
            <a 
              href="/help" 
              className="px-4 py-2 bg-secondary text-secondary-foreground hover:bg-accent rounded-lg font-medium transition-colors"
            >
              Help & Docs
            </a>
            <a 
              href="/help#quick-start" 
              className="px-4 py-2 bg-green-600 text-white hover:bg-green-700 rounded-lg font-medium transition-colors"
            >
              🚀 Quick Start
            </a>
          </nav>
        </div>

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-contrast mb-2">Investigation Tools</h1>
          <p className="text-muted-foreground">
            Additional tools to support your fraud investigation workflow
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          <DocumentSearch />
          <ExchangeRate />
        </div>

        <div className="mt-8 bg-card p-6 rounded-lg shadow-lg">
          <h2 className="text-2xl font-bold mb-4 text-contrast">Available APIs</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold text-contrast mb-2">Search & Analysis</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• Document search in regulatory databases</li>
                <li>• Web search for current information</li>
                <li>• ArXiv research paper search</li>
                <li>• Vector similarity search</li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold text-contrast mb-2">Financial Data</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• Real-time exchange rates</li>
                <li>• Currency conversion</li>
                <li>• Financial market data integration</li>
                <li>• Economic indicators</li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
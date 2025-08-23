'use client';

import Link from 'next/link';
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
            <Link 
              href="/" 
              className="px-4 py-2 bg-secondary text-secondary-foreground hover:bg-accent rounded-lg font-medium transition-colors"
            >
              Investigation
            </Link>
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

        {/* Enhanced Research Capabilities - Coming Soon */}
        <div className="mt-8 bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-950/20 dark:to-indigo-950/20 rounded-lg p-6 border border-purple-200 dark:border-purple-800">
          <div className="mb-4">
            <h2 className="text-2xl font-bold text-purple-800 dark:text-purple-200 mb-2 flex items-center space-x-2">
              <span>🚧</span>
              <span>Coming Soon: Enhanced Research Capabilities</span>
            </h2>
            <p className="text-purple-700 dark:text-purple-300">
              Sophisticated research workflows with multi-source intelligence and quality assessment are in development
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-4">
            <div className="bg-white/50 dark:bg-gray-900/20 p-4 rounded-lg">
              <h3 className="font-semibold text-purple-800 dark:text-purple-200 mb-2">Multi-Source Search</h3>
                                <ul className="space-y-1 text-sm text-purple-700 dark:text-purple-300">
                    <li>• Tavily (Real-time Web & News)</li>
                    <li>• ArXiv (Regulatory Research)</li>
                  </ul>
              <p className="text-xs text-purple-600 dark:text-purple-400 mt-2 italic">
                Focused on fraud investigation & compliance research
              </p>
            </div>
            
            <div className="bg-white/50 dark:bg-gray-900/20 p-4 rounded-lg">
              <h3 className="font-semibold text-purple-800 dark:text-purple-200 mb-2">Research Planning</h3>
              <ul className="space-y-1 text-sm text-purple-700 dark:text-purple-300">
                <li>• Dynamic section generation</li>
                <li>• Quality assessment criteria</li>
                <li>• Iterative refinement</li>
                <li>• Progress tracking</li>
                <li>• Resumable sessions</li>
              </ul>
            </div>
            
            <div className="bg-white/50 dark:bg-gray-900/20 p-4 rounded-lg">
              <h3 className="font-semibold text-purple-800 dark:text-purple-200 mb-2">Specialized Agents</h3>
              <ul className="space-y-1 text-sm text-purple-700 dark:text-purple-300">
                <li>• Financial compliance research</li>
                <li>• Academic investigation</li>
                <li>• AML/sanctions analysis</li>
                <li>• Domain-specific expertise</li>
                <li>• Regulatory intelligence</li>
              </ul>
            </div>
          </div>
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
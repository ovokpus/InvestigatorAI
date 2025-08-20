'use client';

import { useState } from 'react';
import Link from 'next/link';
import Header from '@/components/Header';
import HealthStatus from '@/components/HealthStatus';
import MultiSourceSearch from '@/components/MultiSourceSearch';
import ResearchPlanner from '@/components/ResearchPlanner';
import ResearchSessions from '@/components/ResearchSessions';

export default function EnhancedResearchPage() {
  const [activeTab, setActiveTab] = useState<'search' | 'plan' | 'sessions'>('search');

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
            <Link 
              href="/tools" 
              className="px-4 py-2 bg-secondary text-secondary-foreground hover:bg-accent rounded-lg font-medium transition-colors"
            >
              Tools & Search
            </Link>
            <span className="px-4 py-2 bg-primary text-primary-foreground rounded-lg font-medium">
              🔬 Enhanced Research
            </span>
            <Link 
              href="/help" 
              className="px-4 py-2 bg-secondary text-secondary-foreground hover:bg-accent rounded-lg font-medium transition-colors"
            >
              Help & Docs
            </Link>
          </nav>
        </div>

        {/* Enhanced Research Header */}
        <div className="mb-8 bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-950/20 dark:to-indigo-950/20 rounded-lg p-6 border border-purple-200 dark:border-purple-800">
          <h1 className="text-3xl font-bold text-purple-800 dark:text-purple-200 mb-3">
            🔬 Enhanced Deep Research
          </h1>
          <p className="text-purple-700 dark:text-purple-300 leading-relaxed">
            Advanced research capabilities powered by multi-source intelligence, iterative refinement, and quality assessment. 
            Conduct comprehensive investigations across financial compliance, academic research, and specialized domains with 
            real-time progress tracking and resumable sessions.
          </p>
          
          <div className="mt-4 flex space-x-6 text-sm">
            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              <span className="text-purple-600 dark:text-purple-400">Multi-Source Search (5 APIs)</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
              <span className="text-purple-600 dark:text-purple-400">Iterative Quality Assessment</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 bg-orange-500 rounded-full"></span>
              <span className="text-purple-600 dark:text-purple-400">Resumable Sessions</span>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="mb-6">
          <div className="flex space-x-1 bg-secondary/20 p-1 rounded-lg">
            <button
              onClick={() => setActiveTab('search')}
              className={`flex-1 px-4 py-2 rounded-md font-medium transition-colors ${
                activeTab === 'search'
                  ? 'bg-primary text-primary-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-contrast'
              }`}
            >
              🔍 Multi-Source Search
            </button>
            <button
              onClick={() => setActiveTab('plan')}
              className={`flex-1 px-4 py-2 rounded-md font-medium transition-colors ${
                activeTab === 'plan'
                  ? 'bg-primary text-primary-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-contrast'
              }`}
            >
              📋 Research Planning
            </button>
            <button
              onClick={() => setActiveTab('sessions')}
              className={`flex-1 px-4 py-2 rounded-md font-medium transition-colors ${
                activeTab === 'sessions'
                  ? 'bg-primary text-primary-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-contrast'
              }`}
            >
              📊 Research Sessions
            </button>
          </div>
        </div>

        {/* Tab Content */}
        <div>
          {activeTab === 'search' && <MultiSourceSearch />}
          {activeTab === 'plan' && <ResearchPlanner />}
          {activeTab === 'sessions' && <ResearchSessions />}
        </div>
      </main>
    </div>
  );
}

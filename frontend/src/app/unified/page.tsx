'use client';

import { useState } from 'react';
import Link from 'next/link';
import UnifiedInvestigationForm from '@/components/UnifiedInvestigationForm';
import UnifiedInvestigationResults from '@/components/UnifiedInvestigationResults';
import Header from '@/components/Header';
import HealthStatus from '@/components/HealthStatus';

// Unified form data interface
interface UnifiedFormData {
  investigation_type: 'fraud_transaction' | 'entity_research' | 'academic_research' | 'general_research';
  amount?: number;
  currency?: string;
  description?: string;
  customer_name?: string;
  account_type?: string;
  risk_rating?: string;
  country_to?: string;
  topic?: string;
  entity_name?: string;
  entity_type?: string;
  field?: string;
  context?: string;
  include_market_analysis?: boolean;
  priority?: string;
}

// Import the interface from the results component to avoid conflicts
interface UnifiedInvestigationResponse {
  investigation_id: string;
  investigation_type: string;
  status: string;
  duration_seconds: number;
  
  // Results (one will be populated based on type)
  fraud_result?: {
    investigation_id: string;
    status: string;
    final_decision: string;
    agents_completed: number;
    total_messages: number;
    transaction_details: Record<string, unknown>;
    all_agents_finished: boolean;
    error?: string;
    full_results?: Record<string, unknown>;
    performance?: Record<string, unknown>;
  };
  research_result?: {
    type: string;
    result: Record<string, unknown>;
    status?: string;
    findings?: string[];
    summary?: string;
  };
  
  // Common metadata
  agents_used: string[];
  error_message?: string;
  performance_metrics?: {
    duration_seconds: number;
    start_time: string;
    end_time: string;
    parallel_execution_time?: number;
  };
}

export default function UnifiedInvestigationPage() {
  const [investigation, setInvestigation] = useState<UnifiedInvestigationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');

  const handleInvestigationSubmit = async (formData: UnifiedFormData) => {
    setIsLoading(true);
    setProgress(0);
    setProgressMessage('Initializing investigation...');
    setInvestigation(null);
    
    try {
      console.log('🚀 Starting unified investigation:', formData);
      
      // Call the new unified endpoint
      const response = await fetch('http://localhost:8000/investigate/unified', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      console.log('📡 Response status:', response.status);

      if (!response.ok) {
        // Handle HTTP error responses
        let errorMessage = 'Investigation failed. Please try again.';
        
        if (response.status === 413) {
          errorMessage = '⚠️ Investigation Too Complex\n\nThe AI analysis exceeded the maximum token limit. Please try:\n• Shorter descriptions\n• Simpler details\n• Break complex cases into smaller investigations';
        } else if (response.status === 429) {
          errorMessage = '⏳ Rate Limit Exceeded\n\nToo many requests at once. You are limited to 5 requests per minute. Please wait and try again.';
        } else if (response.status === 401) {
          errorMessage = '🔐 Authentication Error\n\nAPI key configuration issue. Please contact support.';
        } else if (response.status === 503) {
          errorMessage = '🔧 Service Temporarily Unavailable\n\nUnified investigation service is temporarily down. Please try again in a few moments.';
        } else {
          // Try to get detailed error from response
          try {
            const errorData = await response.json();
            if (errorData?.detail) {
              errorMessage = `❌ ${errorData.detail}`;
            }
          } catch {
            errorMessage = `❌ HTTP ${response.status}: ${response.statusText}`;
          }
        }
        
        alert(errorMessage);
        return;
      }

      // Simulate progress for non-streaming response
      const progressSteps = [
        { progress: 20, message: 'Routing to appropriate investigation service...' },
        { progress: 40, message: 'Analyzing request parameters...' },
        { progress: 60, message: 'Executing investigation logic...' },
        { progress: 80, message: 'Processing results...' },
        { progress: 95, message: 'Finalizing investigation...' }
      ];

      // Update progress incrementally
      for (let i = 0; i < progressSteps.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 500));
        setProgress(progressSteps[i].progress);
        setProgressMessage(progressSteps[i].message);
      }

      // Parse the response
      const result: UnifiedInvestigationResponse = await response.json();
      console.log('✅ Investigation completed:', result);

      setProgress(100);
      setProgressMessage('Investigation completed successfully!');
      setInvestigation(result);
      
    } catch (error: unknown) {
      console.error('❌ Investigation failed:', error);
      
      let errorMessage = '🌐 Connection Error\n\nCannot connect to the API server. Please ensure the backend is running on localhost:8000.';
      
      if (error instanceof Error && error.message && !error.message.includes('fetch')) {
        errorMessage = `❌ ${error.message}`;
      }
      
      alert(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewInvestigation = () => {
    setInvestigation(null);
    setProgress(0);
    setProgressMessage('');
  };



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
              Legacy Investigation
            </Link>
            <span className="px-4 py-2 bg-primary text-primary-foreground rounded-lg font-medium">
              🎯 Unified Investigation
            </span>
            <Link 
              href="/tools" 
              className="px-4 py-2 bg-secondary text-secondary-foreground hover:bg-accent rounded-lg font-medium transition-colors"
            >
              Tools & Search
            </Link>
            <Link 
              href="/research" 
              className="px-4 py-2 bg-purple-600 text-white hover:bg-purple-700 rounded-lg font-medium transition-colors"
            >
              🔬 Enhanced Research
            </Link>
            <Link 
              href="/help" 
              className="px-4 py-2 bg-secondary text-secondary-foreground hover:bg-accent rounded-lg font-medium transition-colors"
            >
              Help & Docs
            </Link>
          </nav>
        </div>

        {/* App Description */}
        <div className="mb-8 bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-950/20 dark:to-blue-950/20 rounded-lg p-6 border border-green-200 dark:border-green-800">
          <h2 className="text-2xl font-bold text-green-800 dark:text-green-200 mb-3">
            🎯 Unified Investigation Platform
          </h2>
          <p className="text-green-700 dark:text-green-300 leading-relaxed">
            <strong>NEW:</strong> InvestigatorAI 2.0 introduces a unified investigation platform supporting 4 investigation types: 
            fraud transactions, entity research, academic research, and general research. Enhanced with parallel processing, 
            memory optimization, circuit breakers, and rate limiting for production-ready reliability.
          </p>
          <div className="mt-4 flex flex-wrap gap-4 text-sm">
            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              <span className="text-green-600 dark:text-green-400">30% Faster with Parallel Processing</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
              <span className="text-green-600 dark:text-green-400">Memory Optimized (60% Smaller Responses)</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
              <span className="text-green-600 dark:text-green-400">Circuit Breaker Protection</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 bg-orange-500 rounded-full"></span>
              <span className="text-green-600 dark:text-green-400">Rate Limited (5 req/min)</span>
            </div>
          </div>
        </div>

        {!investigation ? (
          <div className="grid lg:grid-cols-2 gap-8">
            <div>
              <div className="bg-card p-6 rounded-lg shadow-lg">
                <h2 className="text-2xl font-bold mb-4 text-contrast">
                  Unified Investigation System
                </h2>
                <p className="text-muted-foreground mb-6">
                  Select an investigation type and provide details to start a comprehensive 
                  AI-powered investigation using our unified multi-agent platform.
                </p>
                <UnifiedInvestigationForm 
                  onSubmit={handleInvestigationSubmit} 
                  isLoading={isLoading} 
                />
              </div>
            </div>
            
            <div>
              <div className="bg-card p-6 rounded-lg shadow-lg">
                <h2 className="text-2xl font-bold mb-4 text-contrast">
                  {isLoading ? 'Investigation Progress' : 'Investigation Types'}
                </h2>
                
                {/* Progress Bar */}
                {isLoading && (
                  <div className="mb-6">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium text-contrast">Overall Progress</span>
                      <span className="text-sm font-medium text-contrast">{progress}%</span>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                      <div 
                        className="bg-primary h-2 rounded-full transition-all duration-500 ease-out"
                        style={{ width: `${progress}%` }}
                      ></div>
                    </div>
                    {progressMessage && (
                      <div className="mt-3 p-3 bg-primary/10 rounded-lg border border-primary/20">
                        <div className="flex items-center space-x-2">
                          <div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
                          <span className="text-sm font-medium text-primary">Current Activity:</span>
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">
                          {progressMessage}
                        </p>
                      </div>
                    )}
                  </div>
                )}
                
                {/* Investigation Types Overview */}
                {!isLoading && (
                  <div className="space-y-4">
                    <div className="border border-red-200 dark:border-red-800 rounded-lg p-4 bg-red-50 dark:bg-red-950/20">
                      <h3 className="font-semibold text-red-800 dark:text-red-200 flex items-center space-x-2">
                        <span>🚨</span>
                        <span>Fraud Transaction</span>
                      </h3>
                      <p className="text-sm text-red-700 dark:text-red-300 mt-1">
                        Multi-agent fraud analysis with regulatory compliance
                      </p>
                    </div>
                    
                    <div className="border border-blue-200 dark:border-blue-800 rounded-lg p-4 bg-blue-50 dark:bg-blue-950/20">
                      <h3 className="font-semibold text-blue-800 dark:text-blue-200 flex items-center space-x-2">
                        <span>🏢</span>
                        <span>Entity Research</span>
                      </h3>
                      <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                        Financial entity investigation with AML/sanctions screening
                      </p>
                    </div>
                    
                    <div className="border border-purple-200 dark:border-purple-800 rounded-lg p-4 bg-purple-50 dark:bg-purple-950/20">
                      <h3 className="font-semibold text-purple-800 dark:text-purple-200 flex items-center space-x-2">
                        <span>🎓</span>
                        <span>Academic Research</span>
                      </h3>
                      <p className="text-sm text-purple-700 dark:text-purple-300 mt-1">
                        Scientific literature analysis and methodology extraction
                      </p>
                    </div>
                    
                    <div className="border border-green-200 dark:border-green-800 rounded-lg p-4 bg-green-50 dark:bg-green-950/20">
                      <h3 className="font-semibold text-green-800 dark:text-green-200 flex items-center space-x-2">
                        <span>🔍</span>
                        <span>General Research</span>
                      </h3>
                      <p className="text-sm text-green-700 dark:text-green-300 mt-1">
                        Iterative quality-driven research with multiple sources
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          <UnifiedInvestigationResults 
            investigation={investigation} 
            onNewInvestigation={handleNewInvestigation}
          />
        )}
      </main>
    </div>
  );
}

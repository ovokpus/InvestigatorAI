'use client';

import { useState } from 'react';
import InvestigationForm from '../components/InvestigationForm';
import InvestigationResults from '../components/InvestigationResults';
import Header from '../components/Header';
import HealthStatus from '../components/HealthStatus';

interface FormData {
  amount: number;
  currency: string;
  description: string;
  customer_name: string;
  account_type: string;
  risk_rating: string;
  country_to: string;
}

interface Investigation {
  investigation_id: string;
  status: string;
  final_decision: string;
  agents_completed: number;
  total_messages: number;
  transaction_details: Record<string, unknown>;
  all_agents_finished: boolean;
  error?: string;
  full_results?: Record<string, unknown>;
}

interface ProgressUpdate {
  type: string;
  step: string;
  agent: string;
  agent_title?: string;
  message: string;
  progress: number;
  completed_agents?: number;
  error?: boolean;
  result?: Investigation;
}

export default function Home() {
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [progressUpdates, setProgressUpdates] = useState<ProgressUpdate[]>([]);
  const [currentProgress, setCurrentProgress] = useState(0);

  const handleInvestigationSubmit = async (formData: FormData) => {
    setIsLoading(true);
    setProgressUpdates([]);
    setCurrentProgress(0);
    setInvestigation(null);
    
    try {
      // Use streaming endpoint for real-time progress
      const response = await fetch('http://localhost:8000/investigate/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        // Handle HTTP error responses
        let errorMessage = 'Investigation failed. Please try again.';
        
        if (response.status === 413) {
          errorMessage = '⚠️ Investigation Too Complex\n\nThe AI analysis exceeded the maximum token limit. Please try:\n• Shorter transaction description\n• Simpler customer details\n• Break complex cases into smaller investigations';
        } else if (response.status === 429) {
          errorMessage = '⏳ Rate Limit Exceeded\n\nToo many requests at once. Please wait a moment and try again.';
        } else if (response.status === 401) {
          errorMessage = '🔐 Authentication Error\n\nAPI key configuration issue. Please contact support.';
        } else if (response.status === 503) {
          errorMessage = '🔧 Service Temporarily Unavailable\n\nAI service is temporarily down. Please try again in a few moments.';
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

      // Read the streaming response
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      
      if (!reader) {
        throw new Error('Unable to read streaming response');
      }

      let buffer = '';
      
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        
        // Keep the last potentially incomplete line in buffer
        buffer = lines.pop() || '';
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6)) as ProgressUpdate;
              
              // Update progress state
              setProgressUpdates(prev => [...prev, data]);
              setCurrentProgress(data.progress);
              
              // Handle completion
              if (data.type === 'complete' && data.result) {
                console.log('✅ Completion event received:', data);
                setInvestigation(data.result);
                setIsLoading(false);
                console.log('✅ Investigation completed, loading set to false');
                return; // Exit successfully
              }
              
              // Handle errors
              if (data.type === 'error') {
                throw new Error(data.message);
              }
              
            } catch (parseError) {
              console.error('Error parsing SSE data:', parseError);
            }
          }
        }
      }
      
    } catch (error: unknown) {
      console.error('Investigation failed:', error);
      
      let errorMessage = '🌐 Connection Error\n\nCannot connect to the API server. Please ensure the backend is running on localhost:8000.';
      
      if (error instanceof Error && error.message && !error.message.includes('fetch')) {
        errorMessage = `❌ ${error.message}`;
      }
      
      alert(errorMessage);
      setIsLoading(false);
      setProgressUpdates([]);
      setCurrentProgress(0);
    }
  };

  const handleNewInvestigation = () => {
    setInvestigation(null);
    setProgressUpdates([]);
    setCurrentProgress(0);
  };

  // Helper functions for progress tracking
  const getStepStatus = (agentName: string): 'completed' | 'active' | 'pending' => {
    const latestUpdate = progressUpdates
      .filter(update => update.agent === agentName)
      .slice(-1)[0];
    
    if (!latestUpdate) return 'pending';
    
    if (latestUpdate.step === 'agent_complete') return 'completed';
    if (latestUpdate.step === 'agent_start' || latestUpdate.step === 'agent_working') return 'active';
    
    return 'pending';
  };

  const getStepMessage = (agentName: string): string => {
    const latestUpdate = progressUpdates
      .filter(update => update.agent === agentName)
      .slice(-1)[0];
    
    return latestUpdate?.message || '';
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
            <span className="px-4 py-2 bg-primary text-primary-foreground rounded-lg font-medium">
              Investigation
            </span>
            <a 
              href="/tools" 
              className="px-4 py-2 bg-secondary text-secondary-foreground hover:bg-accent rounded-lg font-medium transition-colors"
            >
              Tools & Search
            </a>
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

        {/* App Description */}
        <div className="mb-8 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20 rounded-lg p-6 border border-blue-200 dark:border-blue-800">
          <h2 className="text-2xl font-bold text-blue-800 dark:text-blue-200 mb-3">🔍 What InvestigatorAI Does</h2>
          <p className="text-blue-700 dark:text-blue-300 leading-relaxed">
            InvestigatorAI is a multi-agent fraud investigation system that transforms suspicious transaction analysis from a 6-hour manual process into a 90-minute AI-assisted workflow. 
            Our platform combines 4 specialized AI agents with real regulatory data from INTERPOL, FinCEN, and FFIEC to provide comprehensive fraud investigation, 
            compliance checking, and audit-ready documentation—reducing investigation time by 75% while ensuring regulatory compliance and improving fraud detection quality.
          </p>
        </div>

        {!investigation ? (
          <div className="grid lg:grid-cols-2 gap-8">
            <div>
              <div className="bg-card p-6 rounded-lg shadow-lg">
                <h2 className="text-2xl font-bold mb-4 text-contrast">
                  Start New Investigation
                </h2>
                <p className="text-muted-foreground mb-6">
                  Enter transaction details below to begin a comprehensive fraud investigation 
                  using our multi-agent AI system.
                </p>
                <InvestigationForm 
                  onSubmit={handleInvestigationSubmit} 
                  isLoading={isLoading} 
                />
              </div>
            </div>
            
            <div>
              <div className="bg-card p-6 rounded-lg shadow-lg">
                <h2 className="text-2xl font-bold mb-4 text-contrast">
                  {isLoading ? 'Investigation Progress' : 'How It Works'}
                </h2>
                
                {/* Progress Bar */}
                {isLoading && (
                  <div className="mb-6">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium text-contrast">Overall Progress</span>
                      <span className="text-sm font-medium text-contrast">{currentProgress}%</span>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                      <div 
                        className="bg-primary h-2 rounded-full transition-all duration-500 ease-out"
                        style={{ width: `${currentProgress}%` }}
                      ></div>
                    </div>
                  </div>
                )}
                
                <div className="space-y-4">
                  {/* Step 1: Regulatory Research */}
                  <div className="flex items-start space-x-3">
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all duration-300 ${
                      getStepStatus('regulatory_research') === 'completed' 
                        ? 'bg-green-500 text-white' 
                        : getStepStatus('regulatory_research') === 'active'
                        ? 'bg-primary text-primary-foreground animate-pulse'
                        : 'bg-primary text-primary-foreground'
                    }`}>
                      {getStepStatus('regulatory_research') === 'completed' ? '✓' : '1'}
                    </div>
                    <div className="flex-1">
                      <h3 className={`font-semibold ${getStepStatus('regulatory_research') === 'active' ? 'text-primary' : 'text-contrast'}`}>
                        Regulatory Research
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        Analyzing regulatory compliance and sanctions
                      </p>
                      {getStepMessage('regulatory_research') && (
                        <p className="text-xs text-blue-600 dark:text-blue-400 mt-1 font-medium">
                          {getStepMessage('regulatory_research')}
                        </p>
                      )}
                    </div>
                  </div>
                  
                  {/* Step 2: Evidence Collection */}
                  <div className="flex items-start space-x-3">
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all duration-300 ${
                      getStepStatus('evidence_collection') === 'completed' 
                        ? 'bg-green-500 text-white' 
                        : getStepStatus('evidence_collection') === 'active'
                        ? 'bg-primary text-primary-foreground animate-pulse'
                        : 'bg-primary text-primary-foreground'
                    }`}>
                      {getStepStatus('evidence_collection') === 'completed' ? '✓' : '2'}
                    </div>
                    <div className="flex-1">
                      <h3 className={`font-semibold ${getStepStatus('evidence_collection') === 'active' ? 'text-primary' : 'text-contrast'}`}>
                        Evidence Collection
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        Gathering transaction evidence and patterns
                      </p>
                      {getStepMessage('evidence_collection') && (
                        <p className="text-xs text-blue-600 dark:text-blue-400 mt-1 font-medium">
                          {getStepMessage('evidence_collection')}
                        </p>
                      )}
                    </div>
                  </div>
                  
                  {/* Step 3: Compliance Check */}
                  <div className="flex items-start space-x-3">
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all duration-300 ${
                      getStepStatus('compliance_check') === 'completed' 
                        ? 'bg-green-500 text-white' 
                        : getStepStatus('compliance_check') === 'active'
                        ? 'bg-primary text-primary-foreground animate-pulse'
                        : 'bg-primary text-primary-foreground'
                    }`}>
                      {getStepStatus('compliance_check') === 'completed' ? '✓' : '3'}
                    </div>
                    <div className="flex-1">
                      <h3 className={`font-semibold ${getStepStatus('compliance_check') === 'active' ? 'text-primary' : 'text-contrast'}`}>
                        Compliance Check
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        Verifying regulatory requirements
                      </p>
                      {getStepMessage('compliance_check') && (
                        <p className="text-xs text-blue-600 dark:text-blue-400 mt-1 font-medium">
                          {getStepMessage('compliance_check')}
                        </p>
                      )}
                    </div>
                  </div>
                  
                  {/* Step 4: Report Generation */}
                  <div className="flex items-start space-x-3">
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all duration-300 ${
                      getStepStatus('report_generation') === 'completed' 
                        ? 'bg-green-500 text-white' 
                        : getStepStatus('report_generation') === 'active'
                        ? 'bg-primary text-primary-foreground animate-pulse'
                        : 'bg-primary text-primary-foreground'
                    }`}>
                      {getStepStatus('report_generation') === 'completed' ? '✓' : '4'}
                    </div>
                    <div className="flex-1">
                      <h3 className={`font-semibold ${getStepStatus('report_generation') === 'active' ? 'text-primary' : 'text-contrast'}`}>
                        Final Report
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        Generating detailed investigation report
                      </p>
                      {getStepMessage('report_generation') && (
                        <p className="text-xs text-blue-600 dark:text-blue-400 mt-1 font-medium">
                          {getStepMessage('report_generation')}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
                
                {/* Current Activity Display */}
                {isLoading && progressUpdates.length > 0 && (
                  <div className="mt-6 p-4 bg-secondary/20 rounded-lg border border-primary/20">
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
                      <span className="text-sm font-medium text-primary">Current Activity:</span>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">
                      {progressUpdates[progressUpdates.length - 1]?.message || 'Processing...'}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          <InvestigationResults 
            investigation={investigation} 
            onNewInvestigation={handleNewInvestigation}
          />
        )}
      </main>
    </div>
  );
}

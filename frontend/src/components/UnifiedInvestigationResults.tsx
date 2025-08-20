'use client';

import { useState } from 'react';

// Unified investigation response interface
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

interface UnifiedInvestigationResultsProps {
  investigation: UnifiedInvestigationResponse;
  onNewInvestigation: () => void;
}

export default function UnifiedInvestigationResults({ 
  investigation, 
  onNewInvestigation 
}: UnifiedInvestigationResultsProps) {
  const [activeTab, setActiveTab] = useState<'summary' | 'details' | 'performance'>('summary');
  
  // Download investigation report
  const handleDownloadReport = () => {
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const downloadUrl = `${baseUrl}/investigate/download/${investigation.investigation_id}`;
      
      // Create a temporary link and trigger download
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `investigation_report_${investigation.investigation_id}.txt`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Failed to download report:', error);
      alert('Failed to download report. Please try again.');
    }
  };

  const getInvestigationTypeDisplay = (type: string) => {
    switch (type) {
      case 'fraud_transaction': return '🚨 Fraud Transaction Investigation';
      case 'entity_research': return '🏢 Entity Research Investigation';
      case 'academic_research': return '🎓 Academic Research Investigation';
      case 'general_research': return '🔍 General Research Investigation';
      default: return `${type} Investigation`;
    }
  };

  const getStatusDisplay = () => {
    if (investigation.status === 'completed') {
      if (investigation.investigation_type === 'fraud_transaction' && investigation.fraud_result) {
        return {
          color: investigation.fraud_result.final_decision?.includes('HIGH RISK') ? 'red' : 
                 investigation.fraud_result.final_decision?.includes('LOW RISK') ? 'green' : 'yellow',
          text: investigation.fraud_result.final_decision || 'Completed'
        };
      }
      return { color: 'green', text: 'Completed Successfully' };
    } else if (investigation.status === 'failed') {
      return { color: 'red', text: 'Investigation Failed' };
    }
    return { color: 'yellow', text: investigation.status };
  };

  const statusDisplay = getStatusDisplay();

  const renderFraudResults = () => {
    if (!investigation.fraud_result) return null;

    const fraud = investigation.fraud_result;
    
    return (
      <div className="space-y-6">
        {/* Decision Banner */}
        <div className={`p-4 rounded-lg border-l-4 ${
          fraud.final_decision?.includes('HIGH RISK') 
            ? 'bg-red-50 border-red-500 dark:bg-red-950/20' 
            : fraud.final_decision?.includes('LOW RISK')
            ? 'bg-green-50 border-green-500 dark:bg-green-950/20'
            : 'bg-yellow-50 border-yellow-500 dark:bg-yellow-950/20'
        }`}>
          <h3 className={`font-bold text-lg ${
            fraud.final_decision?.includes('HIGH RISK') ? 'text-red-800 dark:text-red-200' :
            fraud.final_decision?.includes('LOW RISK') ? 'text-green-800 dark:text-green-200' :
            'text-yellow-800 dark:text-yellow-200'
          }`}>
            Final Decision
          </h3>
          <p className={`mt-2 ${
            fraud.final_decision?.includes('HIGH RISK') ? 'text-red-700 dark:text-red-300' :
            fraud.final_decision?.includes('LOW RISK') ? 'text-green-700 dark:text-green-300' :
            'text-yellow-700 dark:text-yellow-300'
          }`}>
            {fraud.final_decision}
          </p>
        </div>

        {/* Investigation Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-secondary/20 p-4 rounded-lg">
            <h4 className="font-semibold text-contrast">Agents Completed</h4>
            <p className="text-2xl font-bold text-primary mt-1">
              {fraud.agents_completed}/4
            </p>
          </div>
          <div className="bg-secondary/20 p-4 rounded-lg">
            <h4 className="font-semibold text-contrast">Total Messages</h4>
            <p className="text-2xl font-bold text-primary mt-1">
              {fraud.total_messages}
            </p>
          </div>
          <div className="bg-secondary/20 p-4 rounded-lg">
            <h4 className="font-semibold text-contrast">Duration</h4>
            <p className="text-2xl font-bold text-primary mt-1">
              {investigation.duration_seconds?.toFixed(1)}s
            </p>
          </div>
        </div>

        {/* Transaction Details */}
        {fraud.transaction_details && (
          <div className="bg-card p-4 rounded-lg">
            <h4 className="font-semibold text-contrast mb-3">Transaction Details</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
              {Object.entries(fraud.transaction_details).map(([key, value]) => (
                <div key={key} className="flex justify-between">
                  <span className="text-muted-foreground capitalize">
                    {key.replace(/_/g, ' ')}:
                  </span>
                  <span className="text-contrast font-medium">
                    {String(value)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderResearchResults = () => {
    if (!investigation.research_result) return null;

    const research = investigation.research_result;
    
    return (
      <div className="space-y-6">
        {/* Research Summary */}
        <div className="bg-purple-50 dark:bg-purple-950/20 p-4 rounded-lg border border-purple-200 dark:border-purple-800">
          <h3 className="font-bold text-lg text-purple-800 dark:text-purple-200">
            Research Summary
          </h3>
          <p className="mt-2 text-purple-700 dark:text-purple-300">
            {research.summary || 'Research completed successfully'}
          </p>
        </div>

        {/* Research Type */}
        <div className="bg-card p-4 rounded-lg">
          <h4 className="font-semibold text-contrast mb-3">Research Type</h4>
          <p className="text-contrast">
            {research.type || 'General Research'}
          </p>
        </div>

        {/* Findings */}
        {research.findings && research.findings.length > 0 && (
          <div className="bg-card p-4 rounded-lg">
            <h4 className="font-semibold text-contrast mb-3">Key Findings</h4>
            <ul className="space-y-2">
              {research.findings.map((finding, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <span className="text-primary">•</span>
                  <span className="text-contrast">{finding}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Research Result Details */}
        {research.result && (
          <div className="bg-card p-4 rounded-lg">
            <h4 className="font-semibold text-contrast mb-3">Research Details</h4>
            <div className="space-y-2 text-sm">
              {Object.entries(research.result).map(([key, value]) => (
                <div key={key} className="flex justify-between">
                  <span className="text-muted-foreground capitalize">
                    {key.replace(/_/g, ' ')}:
                  </span>
                  <span className="text-contrast font-medium">
                    {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderPerformanceMetrics = () => {
    if (!investigation.performance_metrics) return null;

    const metrics = investigation.performance_metrics;
    
    return (
      <div className="space-y-6">
        {/* Performance Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="bg-secondary/20 p-4 rounded-lg">
            <h4 className="font-semibold text-contrast">Total Duration</h4>
            <p className="text-2xl font-bold text-primary mt-1">
              {metrics.duration_seconds?.toFixed(1)}s
            </p>
          </div>
          
          {metrics.parallel_execution_time && (
            <div className="bg-secondary/20 p-4 rounded-lg">
              <h4 className="font-semibold text-contrast">Parallel Execution</h4>
              <p className="text-2xl font-bold text-green-600 mt-1">
                {metrics.parallel_execution_time.toFixed(1)}s
              </p>
            </div>
          )}
          
          <div className="bg-secondary/20 p-4 rounded-lg">
            <h4 className="font-semibold text-contrast">Agents Used</h4>
            <p className="text-2xl font-bold text-primary mt-1">
              {investigation.agents_used?.length || 0}
            </p>
          </div>
        </div>

        {/* Agent Performance */}
        {investigation.agents_used && investigation.agents_used.length > 0 && (
          <div className="bg-card p-4 rounded-lg">
            <h4 className="font-semibold text-contrast mb-3">Agents Utilized</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {investigation.agents_used.map((agent, index) => (
                <div key={index} className="flex items-center space-x-3 p-3 bg-secondary/10 rounded-lg">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-contrast capitalize">
                    {agent.replace(/_/g, ' ')}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Timing Details */}
        <div className="bg-card p-4 rounded-lg">
          <h4 className="font-semibold text-contrast mb-3">Timing Details</h4>
          <div className="space-y-2 text-sm">
            {metrics.start_time && (
              <div className="flex justify-between">
                <span className="text-muted-foreground">Start Time:</span>
                <span className="text-contrast font-medium">
                  {new Date(metrics.start_time).toLocaleString()}
                </span>
              </div>
            )}
            {metrics.end_time && (
              <div className="flex justify-between">
                <span className="text-muted-foreground">End Time:</span>
                <span className="text-contrast font-medium">
                  {new Date(metrics.end_time).toLocaleString()}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-card p-6 rounded-lg shadow-lg">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h2 className="text-2xl font-bold text-contrast">
              Investigation Results
            </h2>
            <p className="text-muted-foreground mt-1">
              {getInvestigationTypeDisplay(investigation.investigation_type)}
            </p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={handleDownloadReport}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2"
              title="Download Investigation Report"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span>Download Report</span>
            </button>
            <button
              onClick={onNewInvestigation}
              className="btn-primary px-4 py-2 rounded-lg font-medium"
            >
              New Investigation
            </button>
          </div>
        </div>
        
        {/* Status and ID */}
        <div className="flex flex-wrap gap-4 text-sm">
          <div className="flex items-center space-x-2">
            <span className="text-muted-foreground">Status:</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              statusDisplay.color === 'green' ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-200' :
              statusDisplay.color === 'red' ? 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-200' :
              'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-200'
            }`}>
              {statusDisplay.text}
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-muted-foreground">Investigation ID:</span>
            <span className="text-contrast font-mono text-xs">
              {investigation.investigation_id}
            </span>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {investigation.error_message && (
        <div className="bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-800 p-4 rounded-lg">
          <h3 className="font-bold text-red-800 dark:text-red-200">Investigation Error</h3>
          <p className="mt-2 text-red-700 dark:text-red-300">
            {investigation.error_message}
          </p>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="bg-card rounded-lg shadow-lg overflow-hidden">
        <div className="flex border-b border-secondary/20">
          <button
            onClick={() => setActiveTab('summary')}
            className={`flex-1 px-6 py-3 font-medium transition-colors ${
              activeTab === 'summary'
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:text-contrast hover:bg-secondary/10'
            }`}
          >
            Summary
          </button>
          <button
            onClick={() => setActiveTab('details')}
            className={`flex-1 px-6 py-3 font-medium transition-colors ${
              activeTab === 'details'
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:text-contrast hover:bg-secondary/10'
            }`}
          >
            Details
          </button>
          <button
            onClick={() => setActiveTab('performance')}
            className={`flex-1 px-6 py-3 font-medium transition-colors ${
              activeTab === 'performance'
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:text-contrast hover:bg-secondary/10'
            }`}
          >
            Performance
          </button>
        </div>
        
        <div className="p-6">
          {activeTab === 'summary' && (
            <div>
              {investigation.investigation_type === 'fraud_transaction' && renderFraudResults()}
              {investigation.investigation_type !== 'fraud_transaction' && renderResearchResults()}
            </div>
          )}
          
          {activeTab === 'details' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-contrast">Investigation Details</h3>
              <pre className="bg-secondary/10 p-4 rounded-lg text-xs overflow-auto">
                {JSON.stringify(investigation, null, 2)}
              </pre>
            </div>
          )}
          
          {activeTab === 'performance' && renderPerformanceMetrics()}
        </div>
      </div>
    </div>
  );
}

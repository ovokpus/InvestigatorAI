'use client';
import React, { useState } from 'react';
import { ReportGenerationViewer as EnhancedReportGenerationViewer, OtherAgentsViewer as EnhancedOtherAgentsViewer } from './EnhancedInvestigationResults';
import { 
  cleanInvestigationContent, 
  splitContentIntoSegments, 
  stripMarkdownFormatting,
  parseMarkdownBoldSections
} from '@/utils/markdownUtils';

interface MarkdownRendererProps {
  content: string;
}

function MarkdownRenderer({ content }: MarkdownRendererProps) {
  // Parse the content into structured sections
  const parseContent = (text: string) => {
    const lines = text.split('\n');
    
    const sections = {
      header: '',
      keyFindings: '',
      status: ''
    };
    
    let currentSection = 'header';
    let keyFindingsStarted = false;
    
    for (const line of lines) {
      if (line.includes('FRAUD INVESTIGATION COMPLETE')) {
        sections.header = line;
      } else if (line.includes('KEY FINDINGS')) {
        currentSection = 'keyFindings';
        keyFindingsStarted = true;
        continue;
      } else if (line.includes('INVESTIGATION STATUS')) {
        currentSection = 'status';
        sections.status = line;
        continue;
      }
      
      if (currentSection === 'keyFindings' && keyFindingsStarted) {
        sections.keyFindings += line + '\n';
      }
    }
    
    return sections;
  };

  const renderAgentSection = (title: string, content: string) => {
    // Use the extracted utility functions for better maintainability
    const processedContent = cleanInvestigationContent(content);
    const segments = splitContentIntoSegments(processedContent);
    
    return (
      <div className="mb-4 bg-white border border-gray-200 rounded-lg shadow-sm overflow-visible">
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-4 py-2 border-b border-gray-200">
          <h3 className="text-base font-semibold text-gray-900 flex items-center">
            <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
            {title}
          </h3>
        </div>
        <div className="px-4 py-3 space-y-2">
          {segments.map((segment, index) => {
            const trimmed = segment.trim();
            
            // Handle bold headers (our marked sections)
            if (trimmed.startsWith('**') && trimmed.includes(':**')) {
              return (
                <div key={index} className="font-bold text-blue-800 mt-3 mb-1 text-sm border-b border-blue-200 pb-1">
                  {stripMarkdownFormatting(trimmed)}
                </div>
              );
            }
            
            // Handle bullet points
            if (trimmed.startsWith('•')) {
              return (
                <div key={index} className="flex items-start space-x-2 ml-3 my-1 p-1 bg-gray-50 rounded">
                  <span className="text-blue-500 mt-0.5 font-bold text-sm">•</span>
                  <span className="text-gray-700 leading-tight flex-1 text-sm">{trimmed.substring(1).trim()}</span>
                </div>
              );
            }
            
            // Handle numbered lists
            if (/^\d+\.\s/.test(trimmed)) {
              const match = trimmed.match(/^(\d+)\.\s(.+)$/);
              if (match) {
                return (
                  <div key={index} className="flex items-start space-x-2 ml-3 my-1 p-2 bg-blue-50 rounded border-l-2 border-blue-300">
                    <span className="font-bold text-blue-700 min-w-[1.5rem] bg-white px-1 py-0.5 rounded text-xs text-center">{match[1]}</span>
                    <span className="text-gray-700 leading-tight flex-1 text-sm">{match[2]}</span>
                  </div>
                );
              }
            }
            
            // Handle CFR regulations
            if (/^\d+\s+CFR/i.test(trimmed)) {
              return (
                <div key={index} className="bg-yellow-50 border-l-2 border-yellow-400 pl-3 py-1 my-1 rounded-r">
                  <span className="text-gray-800 font-medium text-sm">{trimmed}</span>
                </div>
              );
            }
            
            // Handle dates
            if (/^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d+\s+days?\s+ago)/i.test(trimmed)) {
              return (
                <div key={index} className="text-gray-600 italic bg-gray-100 px-2 py-1 rounded inline-block my-1 text-xs">
                  📅 {trimmed}
                </div>
              );
            }
            
            // Regular content - but break up if still too long
            const content = trimmed;
            if (content.length > 250) {
              // Try to break at periods or semicolons
              const sentences = content.split(/[.;]\s+/).filter(s => s.trim());
              if (sentences.length > 1) {
                return (
                  <div key={index} className="space-y-1 p-2 bg-gray-50 rounded border-l border-gray-300">
                    {sentences.map((sentence, sentIndex) => (
                      <div key={sentIndex} className="text-gray-700 leading-tight text-sm">
                        {sentence.trim()}{sentIndex < sentences.length - 1 && !sentence.match(/[.;]$/) ? '.' : ''}
                      </div>
                    ))}
                  </div>
                );
              }
            }
            
            return (
              <div key={index} className="text-gray-700 leading-tight text-sm p-1 rounded">
                {content}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  // Simplified - no complex formatting functions needed

  const sections = parseContent(content);
  
  return (
    <div className="max-w-5xl mx-auto space-y-3 font-mono text-sm leading-tight">
      {/* Header */}
      {sections.header && (
        <div className="text-center py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg shadow-lg">
          <div className="flex items-center justify-center space-x-3">
            <span className="text-xl">🔍</span>
            <h1 className="text-lg font-bold">FRAUD INVESTIGATION COMPLETE</h1>
          </div>
        </div>
      )}
      
      {/* Key Findings Header */}
      <div className="bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 rounded-lg p-3">
        <div className="flex items-center space-x-3">
          <span className="text-lg">📊</span>
          <h2 className="text-base font-semibold text-gray-900">KEY FINDINGS</h2>
        </div>
      </div>
      
      {/* Key Findings Content */}
      {sections.keyFindings && (
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-4">
          <div className="prose max-w-none">
            {renderKeyFindingsAsDocument(sections.keyFindings)}
          </div>
        </div>
      )}
      
      {/* Status */}
      {sections.status && (
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg p-3">
          <div className="flex items-center space-x-3">
            <span className="text-lg">✅</span>
            <p className="text-base font-bold text-gray-900">
                                {stripMarkdownFormatting(sections.status)}
            </p>
          </div>
        </div>
      )}
    </div>
  );

  function renderKeyFindingsAsDocument(content: string): React.ReactNode {
    const agents = ['Regulatory Research', 'Evidence Collection', 'Compliance Check', 'Report Generation'];
    const agentSections: { [key: string]: string } = {};
    
    let currentAgent = '';
    const lines = content.split('\n');
    
    for (const line of lines) {
      const agentMatch = agents.find(agent => line.includes(agent + ':') || line.includes(agent));
      if (agentMatch) {
        currentAgent = agentMatch;
        agentSections[currentAgent] = line.replace(agentMatch + ':', '').replace(agentMatch, '').trim();
      } else if (currentAgent && line.trim()) {
        agentSections[currentAgent] += '\n' + line;
      }
    }
    
    // If no agent sections found, show raw content as fallback
    if (Object.keys(agentSections).length === 0) {
      return (
        <div className="whitespace-pre-wrap font-mono text-sm">
          {content}
        </div>
      );
    }
    
    return (
      <div className="space-y-1">
        {Object.entries(agentSections).map(([agent, content]) => 
          <div key={agent}>{renderAgentSection(agent, content)}</div>
        )}
      </div>
    );
  }
}

interface TransactionDetails {
  amount?: number;
  currency?: string;
  customer_name?: string;
  country_to?: string;
  account_type?: string;
  description?: string;
  risk_rating?: string;
}

interface InvestigationMessage {
  content: string;
  additional_kwargs?: Record<string, unknown>;
  response_metadata?: Record<string, unknown>;
  type: string;
  name?: string;
  id?: string | null;
  example?: boolean;
}

interface FullResults {
  messages?: InvestigationMessage[];
  [key: string]: unknown;
}

interface Investigation {
  investigation_id: string;
  status: string;
  final_decision: string;
  agents_completed: number;
  total_messages: number;
  transaction_details: TransactionDetails;
  all_agents_finished: boolean;
  error?: string;
  full_results?: FullResults;
  final_report?: string;
  final_report_available?: boolean;
  ragas_validated_messages?: InvestigationMessage[];
}

interface InvestigationResultsProps {
  investigation: Investigation;
  onNewInvestigation: () => void;
}





export default function InvestigationResults({ investigation, onNewInvestigation }: InvestigationResultsProps) {
  const [copySuccess, setCopySuccess] = useState(false);
  const [downloadSuccess, setDownloadSuccess] = useState(false);

  const copyToClipboard = async (text: string) => {
    try {
      // Clean up the text for clipboard (remove markdown formatting)
      const cleanText = text
        .replace(/\*\*(.*?)\*\*/g, '$1') // Remove ** markdown
        .replace(/🔍/g, '') // Remove emojis if desired
        .trim();
      
      await navigator.clipboard.writeText(cleanText);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = text.replace(/\*\*(.*?)\*\*/g, '$1');
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      try {
        document.execCommand('copy');
        setCopySuccess(true);
        setTimeout(() => setCopySuccess(false), 2000);
      } catch (fallbackErr) {
        console.error('Fallback copy failed: ', fallbackErr);
      }
      document.body.removeChild(textArea);
    }
  };

  const generateReportContent = (investigation: Investigation): string => {
    const timestamp = new Date().toISOString();
    let content = `FRAUD INVESTIGATION REPORT\n`;
    content += `Generated: ${timestamp}\n`;
    content += `Investigation ID: ${investigation.investigation_id}\n`;
    content += `Status: ${investigation.status}\n`;
    content += `Final Decision: ${investigation.final_decision}\n\n`;
    
    // Transaction Details
    if (investigation.transaction_details) {
      content += `TRANSACTION DETAILS:\n`;
      content += `Customer: ${investigation.transaction_details.customer_name || 'N/A'}\n`;
      content += `Amount: ${investigation.transaction_details.currency || '$'}${investigation.transaction_details.amount || 'N/A'}\n`;
      content += `Account Type: ${investigation.transaction_details.account_type || 'N/A'}\n`;
      content += `Country To: ${investigation.transaction_details.country_to || 'N/A'}\n`;
      content += `Description: ${investigation.transaction_details.description || 'N/A'}\n`;
      content += `Risk Rating: ${investigation.transaction_details.risk_rating || 'N/A'}\n\n`;
    }
    
    // Final Report
    if (investigation.final_report) {
      content += `INVESTIGATION FINDINGS:\n`;
      content += `${investigation.final_report}\n\n`;
    }
    
    // Full Results if available
    if (investigation.full_results) {
      content += `DETAILED ANALYSIS:\n`;
      content += `Agents Completed: ${investigation.agents_completed}/${investigation.full_results.total_agents || 'N/A'}\n`;
      content += `Total Messages: ${investigation.total_messages}\n\n`;
      
      if (investigation.full_results.agent_results) {
        Object.entries(investigation.full_results.agent_results).forEach(([agentName, result]) => {
          content += `${agentName.toUpperCase()} AGENT:\n`;
          if (typeof result === 'string') {
            content += `${result}\n\n`;
          } else if (result && typeof result === 'object') {
            content += `${JSON.stringify(result, null, 2)}\n\n`;
          }
        });
      }
    }
    
    return content;
  };

  const renderMarkdownContent = (content: string): React.JSX.Element => {
    if (!content) return <span>No content available</span>;
    
    // Parse markdown formatting and render as rich text
    const parseMarkdown = (text: string) => {
      return parseMarkdownBoldSections(text);
    };
    
    // Split content by lines and process each
    const lines = content.split('\n');
    
    return (
      <div className="space-y-2">
        {lines.map((line, index) => (
          <div key={index} className="leading-relaxed">
            {parseMarkdown(line)}
          </div>
        ))}
      </div>
    );
  };



  

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'text-green-600';
      case 'in_progress':
        return 'text-yellow-600';
      case 'failed':
        return 'text-red-600';
      default:
        return 'text-blue-600';
    }
  };

  const getDecisionColor = (decision: string) => {
    if (decision.toLowerCase().includes('high') || decision.toLowerCase().includes('suspicious')) {
      return 'text-red-600 bg-red-50 border-red-200';
    }
    if (decision.toLowerCase().includes('medium') || decision.toLowerCase().includes('review')) {
      return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    }
    if (decision.toLowerCase().includes('low') || decision.toLowerCase().includes('approved')) {
      return 'text-green-600 bg-green-50 border-green-200';
    }
    return 'text-blue-600 bg-blue-50 border-blue-200';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-contrast">Investigation Results</h2>
          <p className="text-muted-foreground mt-1">
            Investigation ID: {investigation.investigation_id}
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={onNewInvestigation}
            className="btn-secondary px-4 py-2 rounded-lg font-medium"
          >
            New Investigation
          </button>
        </div>
      </div>

      {/* Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-card p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-primary">{investigation.agents_completed}/4</div>
          <div className="text-sm text-muted-foreground">Agents Completed</div>
        </div>
        
        <div className="bg-card p-4 rounded-lg shadow">
          <div className={`text-2xl font-bold ${getStatusColor(investigation.status)}`}>
            {investigation.status}
          </div>
          <div className="text-sm text-muted-foreground">Status</div>
        </div>
        
        <div className="bg-card p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-primary">{investigation.total_messages}</div>
          <div className="text-sm text-muted-foreground">Messages Processed</div>
        </div>
        
        <div className="bg-card p-4 rounded-lg shadow">
          <div className={`text-sm font-medium ${investigation.all_agents_finished ? 'text-green-600' : 'text-yellow-600'}`}>
            {investigation.all_agents_finished ? '✓ Complete' : '⏳ In Progress'}
          </div>
          <div className="text-sm text-muted-foreground">Investigation</div>
        </div>
      </div>

      {/* Final Decision */}
      <div className="bg-card p-6 rounded-lg shadow-lg">
        <h3 className="text-xl font-bold mb-4 text-contrast">Investigation Report & Final Decision</h3>
        <div className={`p-6 rounded-lg border-2 ${getDecisionColor(investigation.final_decision)}`}>
          <div className="font-bold text-xl mb-3">
            {investigation.final_decision.includes('**FRAUD INVESTIGATION COMPLETE**') 
              ? '🔍 FRAUD INVESTIGATION COMPLETE' 
              : investigation.final_decision.replace(/_/g, ' ').toUpperCase()}
          </div>
          

          
          {investigation.error && (
            <div className="mt-3 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded">
              <div className="text-red-800 dark:text-red-200 font-medium">Error Details:</div>
              <div className="text-red-700 dark:text-red-300 text-sm mt-1">{investigation.error}</div>
            </div>
          )}
          
          {/* Investigation Completion Status */}
          <div className="mt-4 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${investigation.all_agents_finished ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
              <span className="text-sm font-medium">
                {investigation.all_agents_finished ? 'Investigation Complete' : 'Investigation In Progress'}
              </span>
            </div>
            <div className="text-sm text-muted-foreground">
              ID: {investigation.investigation_id}
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Investigation Analysis - TOP PRIORITY DISPLAY */}
      {investigation.full_results ? (
        <div className="bg-gray-900 p-6 rounded-lg shadow-lg border-2 border-cyan-500">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-2xl font-bold text-cyan-300 flex items-center space-x-3">
              <span className="text-3xl">🔍</span>
              <span>Detailed Investigation Analysis</span>
              <span className="px-3 py-1 bg-cyan-900 text-cyan-200 text-sm font-medium rounded border border-cyan-400">
                COMPREHENSIVE REASONING
              </span>
            </h3>
            <div className="flex space-x-3">
              <button
                onClick={() => copyToClipboard(
                  investigation.full_results?.messages?.map((msg: InvestigationMessage) => 
                    `${msg.name?.toUpperCase() || 'AGENT'} ANALYSIS:\n${msg.content}\n\n${'='.repeat(80)}\n\n`
                  ).join('') || investigation.final_decision
                )}
                className={`px-4 py-2 rounded font-mono text-sm transition-all duration-200 flex items-center space-x-2 border ${
                  copySuccess 
                    ? 'bg-green-700 text-green-200 border-green-500' 
                    : 'bg-gray-800 text-cyan-300 border-cyan-500 hover:bg-gray-700 hover:text-cyan-200'
                }`}
                title="Copy detailed analysis to clipboard"
              >
                <span>{copySuccess ? '✅' : '📋'}</span>
                <span>{copySuccess ? 'Copied!' : 'Copy Analysis'}</span>
              </button>
              <button
                onClick={() => {
                  const detailedContent = investigation.full_results?.messages?.map((msg: InvestigationMessage) => 
                    `${'='.repeat(80)}\n${msg.name?.toUpperCase() || 'AGENT'} ANALYSIS\n${'='.repeat(80)}\n\n${msg.content}\n\n`
                  ).join('') || investigation.final_decision;
                  
                  const blob = new Blob([detailedContent], { type: 'text/plain;charset=utf-8' });
                  const url = URL.createObjectURL(blob);
                  const link = document.createElement('a');
                  link.href = url;
                  link.download = `Detailed_Analysis_${investigation.investigation_id}_${new Date().toISOString().slice(0, 10)}.txt`;
                  document.body.appendChild(link);
                  link.click();
                  document.body.removeChild(link);
                  URL.revokeObjectURL(url);
                  setDownloadSuccess(true);
                  setTimeout(() => setDownloadSuccess(false), 2000);
                }}
                className={`px-4 py-2 rounded font-mono text-sm transition-all duration-200 flex items-center space-x-2 border ${
                  downloadSuccess 
                    ? 'bg-green-700 text-green-200 border-green-500' 
                    : 'bg-gray-800 text-cyan-300 border-cyan-500 hover:bg-gray-700 hover:text-cyan-200'
                }`}
                title="Download detailed analysis as text file"
              >
                <span>{downloadSuccess ? '✅' : '📥'}</span>
                <span>{downloadSuccess ? 'Downloaded!' : 'Download Analysis'}</span>
              </button>
            </div>
          </div>
          <EnhancedReportGenerationViewer results={investigation.full_results} />
        </div>
      ) : (
        <div className="bg-card p-6 rounded-lg shadow-lg border-2 border-yellow-500">
          <h3 className="text-xl font-bold mb-4 text-contrast">Investigation Analysis</h3>
          <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
            <div className="flex items-center space-x-2">
              <div className="text-yellow-600 dark:text-yellow-400">⚠️</div>
              <div className="flex-1">
                <p className="text-yellow-800 dark:text-yellow-200 font-medium">
                  Investigation completed but detailed analysis is not available.
                </p>
                <p className="text-yellow-700 dark:text-yellow-300 text-sm mt-1">
                  The investigation finished successfully but the detailed analysis data is missing.
                  Try running a new investigation or check the debug information below.
                </p>
                <button 
                  onClick={onNewInvestigation}
                  className="mt-3 px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-lg text-sm font-medium transition-colors"
                >
                  🔄 Start New Investigation
                </button>
              </div>
            </div>
            
            {/* Debug info */}
            <details className="mt-4">
              <summary className="text-yellow-700 dark:text-yellow-300 cursor-pointer text-sm">
                Show Debug Information
              </summary>
              <pre className="mt-2 p-2 bg-yellow-100 dark:bg-yellow-900/40 rounded text-xs overflow-auto">
                {JSON.stringify(investigation, null, 2)}
              </pre>
            </details>
          </div>
        </div>
      )}

      {/* Comprehensive Final Report - Prominent Display */}
      {investigation.final_report && (
        <div className="bg-card p-6 rounded-lg shadow-lg border-2 border-blue-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-contrast flex items-center space-x-3">
              <span className="text-2xl">📊</span>
              <span>Comprehensive Investigation Report</span>
              <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                DETAILED REASONING
              </span>
            </h3>
            <div className="flex space-x-2">
              <button
                onClick={() => copyToClipboard(investigation.final_report || "")}
                className={`px-3 py-1 text-sm font-medium rounded-md transition-all duration-200 flex items-center space-x-2 ${
                  copySuccess 
                    ? 'bg-green-600 text-white' 
                    : 'bg-gray-600 hover:bg-gray-700 text-white hover:shadow-md'
                }`}
                title="Copy comprehensive report to clipboard"
              >
                <span>{copySuccess ? '✅' : '📋'}</span>
                <span>{copySuccess ? 'Copied!' : 'Copy Report'}</span>
              </button>
            </div>
          </div>
          
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-950 dark:to-indigo-950 rounded-lg p-6 border border-blue-200 dark:border-blue-800">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-600 max-w-none overflow-auto">
              <div className="text-gray-700 dark:text-gray-300 break-words overflow-wrap-anywhere leading-relaxed">
                {renderMarkdownContent(investigation.final_report)}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Transaction Details */}
      <div className="bg-card p-6 rounded-lg shadow-lg">
        <h3 className="text-xl font-bold mb-4 text-contrast">Transaction Details</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <span className="text-muted-foreground">Amount:</span>
            <div className="font-semibold">
              {investigation.transaction_details?.currency || 'USD'} {(investigation.transaction_details?.amount || 0).toLocaleString()}
            </div>
          </div>
          
          <div>
            <span className="text-muted-foreground">Customer:</span>
            <div className="font-semibold">{investigation.transaction_details?.customer_name || 'N/A'}</div>
          </div>
          
          <div>
            <span className="text-muted-foreground">Destination:</span>
            <div className="font-semibold">{investigation.transaction_details?.country_to || 'N/A'}</div>
          </div>
          
          <div>
            <span className="text-muted-foreground">Account Type:</span>
            <div className="font-semibold">{investigation.transaction_details?.account_type || 'N/A'}</div>
          </div>
        </div>
        
        {investigation.transaction_details?.description && (
          <div className="mt-4">
            <span className="text-muted-foreground">Description:</span>
            <div className="mt-1 p-3 bg-muted rounded">
              {investigation.transaction_details.description}
            </div>
          </div>
        )}
      </div>

      {/* Agent Progress */}
      <div className="bg-card p-6 rounded-lg shadow-lg">
        <h3 className="text-xl font-bold mb-4 text-contrast">Investigation Progress</h3>
        <div className="space-y-3">
          {[
            { name: 'Data Analyst Agent', completed: investigation.agents_completed >= 1 },
            { name: 'Regulatory Agent', completed: investigation.agents_completed >= 2 },
            { name: 'Risk Assessment Agent', completed: investigation.agents_completed >= 3 },
            { name: 'Investigation Coordinator', completed: investigation.agents_completed >= 4 }
          ].map((agent, index) => (
            <div key={index} className="flex items-center space-x-3">
              <div className={`w-4 h-4 rounded-full ${agent.completed ? 'bg-green-500' : 'bg-gray-300'}`}></div>
              <span className={`${agent.completed ? 'text-contrast' : 'text-muted-foreground'}`}>
                {agent.name}
              </span>
              {agent.completed && <span className="text-green-600 text-sm">✓</span>}
            </div>
          ))}
        </div>
      </div>

      {/* Additional Agent Analysis - BOTTOM SECTION */}
      {investigation.full_results && (
        <div className="bg-gray-900 p-6 rounded-lg shadow-lg border-2 border-gray-600">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-2xl font-bold text-gray-300 flex items-center space-x-3">
              <span className="text-3xl">🔬</span>
              <span>Additional Agent Analysis</span>
              <span className="px-3 py-1 bg-gray-800 text-gray-300 text-sm font-medium rounded border border-gray-500">
                SUPPORTING EVIDENCE
              </span>
            </h3>
          </div>
          <EnhancedOtherAgentsViewer results={investigation.full_results} />
        </div>
      )}

    </div>
  );
}
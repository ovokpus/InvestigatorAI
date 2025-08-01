'use client';
import { useState } from 'react';

interface MarkdownRendererProps {
  content: string;
}

function MarkdownRenderer({ content }: MarkdownRendererProps) {
  const renderMarkdown = (text: string) => {
    const lines = text.split('\n');
    const processedLines: JSX.Element[] = [];
    let seenTransactionDetails = false;
    let skipUntilNextAgent = false;
    
    lines.forEach((line, index) => {
      // Skip redundant transaction details sections after the first one
      if (line.includes('Transaction Details:') && seenTransactionDetails) {
        skipUntilNextAgent = true;
        return;
      }
      
      // Stop skipping when we hit a new agent or important section
      if (skipUntilNextAgent && (
        line.includes('**Regulatory Research**') ||
        line.includes('**Evidence Collection**') ||
        line.includes('**Compliance Check**') ||
        line.includes('**Report Generation**') ||
        line.includes('**Supervisor**') ||
        line.includes('Regulatory Compliance Assessment') ||
        line.includes('Risk Assessment') ||
        line.includes('Filing Requirements') ||
        line.includes('## Investigation Report') ||
        line.includes('## ') ||
        line.includes('### ')
      )) {
        skipUntilNextAgent = false;
      }
      
      // Continue skipping if we're in a redundant section
      if (skipUntilNextAgent) {
        return;
      }
      
      // Mark that we've seen transaction details
      if (line.includes('Transaction Details:')) {
        seenTransactionDetails = true;
      }
      
      // Handle bold text **text**
      let processedLine = line.replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-blue-800 dark:text-blue-200">$1</strong>');
      
      // Handle headers starting with **
      if (line.startsWith('**') && line.endsWith('**')) {
        const headerText = line.replace(/\*\*/g, '');
        processedLines.push(
          <div key={index} className="text-lg font-bold text-blue-800 dark:text-blue-200 mt-4 mb-2">
            {headerText}
          </div>
        );
        return;
      }
      
      // Handle markdown headers (## and ###)
      if (line.startsWith('### ')) {
        const headerText = line.replace('### ', '');
        processedLines.push(
          <div key={index} className="text-base font-bold text-gray-800 dark:text-gray-200 mt-3 mb-2">
            {headerText}
          </div>
        );
        return;
      }
      
      if (line.startsWith('## ')) {
        const headerText = line.replace('## ', '');
        processedLines.push(
          <div key={index} className="text-lg font-bold text-gray-800 dark:text-gray-200 mt-4 mb-2">
            {headerText}
          </div>
        );
        return;
      }
      
      // Handle KEY FINDINGS header
      if (line.includes('KEY FINDINGS')) {
        processedLines.push(
          <div key={index} className="text-lg font-bold text-green-700 dark:text-green-300 mt-4 mb-2">
            🔍 KEY FINDINGS:
          </div>
        );
        return;
      }
      
      // Handle agent findings (lines starting with **)
      if (processedLine.includes('<strong')) {
        // Determine agent type for color coding
        let bgColor = 'bg-blue-50 dark:bg-blue-950/30';
        let borderColor = 'border-blue-500';
        
        if (line.includes('Regulatory Research')) {
          bgColor = 'bg-purple-50 dark:bg-purple-950/30';
          borderColor = 'border-purple-500';
        } else if (line.includes('Evidence Collection')) {
          bgColor = 'bg-orange-50 dark:bg-orange-950/30';
          borderColor = 'border-orange-500';
        } else if (line.includes('Compliance Check')) {
          bgColor = 'bg-green-50 dark:bg-green-950/30';
          borderColor = 'border-green-500';
        } else if (line.includes('Report Generation')) {
          bgColor = 'bg-red-50 dark:bg-red-950/30';
          borderColor = 'border-red-500';
        } else if (line.includes('Supervisor')) {
          bgColor = 'bg-gray-50 dark:bg-gray-950/30';
          borderColor = 'border-gray-500';
        }
        
        processedLines.push(
          <div 
            key={index} 
            className={`mb-3 p-4 ${bgColor} rounded-lg border-l-4 ${borderColor} shadow-sm break-words overflow-wrap-anywhere`}
            dangerouslySetInnerHTML={{ __html: processedLine }}
          />
        );
        return;
      }
      
      // Handle regular content with indentation
      if (line.trim() && !line.startsWith('**')) {
        processedLines.push(
          <div key={index} className="text-gray-700 dark:text-gray-300 mb-2 ml-4 break-words overflow-wrap-anywhere">
            {line.trim()}
          </div>
        );
        return;
      }
      
      // Empty lines for spacing
      if (!line.trim()) {
        processedLines.push(<div key={index} className="h-2"></div>);
        return;
      }
      
      processedLines.push(
        <div key={index} className="text-gray-800 dark:text-gray-200 mb-1 break-words overflow-wrap-anywhere">
          {line}
        </div>
      );
    });
    
    return processedLines;
  };

  return <div>{renderMarkdown(content)}</div>;
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
}

interface InvestigationResultsProps {
  investigation: Investigation;
  onNewInvestigation: () => void;
}

interface DetailedResultsViewerProps {
  results: FullResults;
}

// Component to parse and display investigation messages
function DetailedResultsViewer({ results }: DetailedResultsViewerProps) {
  const [expandedSections, setExpandedSections] = useState<{ [key: number]: boolean }>({});

  const toggleSection = (index: number) => {
    setExpandedSections(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  // Parse messages from results with debug logging
  console.log('🔍 DetailedResultsViewer - Raw results:', results);
  console.log('🔍 DetailedResultsViewer - Raw messages:', results?.messages);
  
  let messages = results?.messages || [];
  
  // If messages is a string, try to parse it
  if (typeof messages === 'string') {
    try {
      messages = JSON.parse(messages);
      console.log('📝 Parsed messages from string:', messages);
    } catch (e) {
      console.error('❌ Failed to parse messages string:', e);
      messages = [];
    }
  }
  
  // Ensure each message has the correct structure
  const parsedMessages = messages.map((msg: any, index: number) => {
    console.log(`🔍 Message ${index}:`, msg, typeof msg);
    
    // If the message is a string that looks like an object, parse it
    if (typeof msg === 'string' && msg.includes("'content':")) {
      try {
        // Convert Python-like dict syntax to JSON
        const jsonString = msg
          .replace(/'/g, '"')  // Replace single quotes with double quotes
          .replace(/True/g, 'true')  // Replace Python True with JSON true
          .replace(/False/g, 'false')  // Replace Python False with JSON false
          .replace(/None/g, 'null');  // Replace Python None with JSON null
        
        const parsed = JSON.parse(jsonString);
        console.log(`✅ Parsed message ${index}:`, parsed);
        return {
          content: parsed.content || '',
          name: parsed.name || 'unknown',
          type: parsed.type || 'unknown'
        };
      } catch (e) {
        console.error(`❌ Failed to parse message ${index}:`, e);
        return {
          content: msg,
          name: 'unknown',
          type: 'unknown'
        };
      }
    }
    
    // If it's already an object, use it directly
    if (typeof msg === 'object' && msg !== null) {
      return {
        content: msg.content || '',
        name: msg.name || 'unknown',
        type: msg.type || 'unknown'
      };
    }
    
    // Fallback for any other format
    return {
      content: String(msg),
      name: 'unknown',
      type: 'unknown'
    };
  });
  
  console.log('🎯 Final parsed messages:', parsedMessages);

  const formatContent = (content: string) => {
    // For investigation results, don't try to parse sections - display the full content
    // The backend already provides well-formatted agent responses
    return [{
      title: 'Investigation Analysis',
      content: content.trim(),
      type: 'info'
    }];
  };

  const getSectionIcon = (type: string) => {
    switch (type) {
      case 'warning': return '⚠️';
      case 'danger': return '🚨';
      case 'success': return '✅';
      default: return 'ℹ️';
    }
  };

  const getSectionColor = (type: string) => {
    switch (type) {
      case 'warning': return 'border-yellow-200 bg-yellow-50 dark:bg-yellow-900/20';
      case 'danger': return 'border-red-200 bg-red-50 dark:bg-red-900/20';
      case 'success': return 'border-green-200 bg-green-50 dark:bg-green-900/20';
      default: return 'border-blue-200 bg-blue-50 dark:bg-blue-900/20';
    }
  };

  if (!parsedMessages.length) {
    return (
      <div className="text-center p-8 text-muted-foreground">
        <p>No detailed analysis available for this investigation.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {parsedMessages.map((message: InvestigationMessage, messageIndex: number) => {
        if (!message.content || message.type === 'human') return null;

        const sections = formatContent(message.content);
        const formatAgentName = (name: string) => {
          switch (name) {
            case 'system': return 'Investigation System';
            case 'supervisor': return 'Investigation Supervisor';
            case 'regulatory_research': return 'Regulatory Research Agent';
            case 'evidence_collection': return 'Evidence Collection Agent';
            case 'compliance_check': return 'Compliance Check Agent';
            case 'report_generation': return 'Report Generation Agent';
            default: return name ? name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : 'Analysis Agent';
          }
        };
        
        const agentName = formatAgentName(message.name || 'unknown');

        return (
          <div key={messageIndex} className="border border-border rounded-lg overflow-hidden">
            <div 
              className="bg-secondary p-4 cursor-pointer flex items-center justify-between hover:bg-accent transition-colors"
              onClick={() => toggleSection(messageIndex)}
            >
              <div className="flex items-center space-x-3">
                <div className="text-lg">🤖</div>
                <div>
                  <h4 className="font-semibold text-contrast">{agentName}</h4>
                  <p className="text-sm text-muted-foreground">
                    {sections.length} analysis section{sections.length !== 1 ? 's' : ''}
                  </p>
                </div>
              </div>
              <div className="text-muted-foreground">
                {expandedSections[messageIndex] ? '🔽' : '▶️'}
              </div>
            </div>

            {expandedSections[messageIndex] && (
              <div className="p-4 space-y-4">
                {sections.map((section, sectionIndex) => (
                  <div 
                    key={sectionIndex} 
                    className={`border rounded-lg p-4 ${getSectionColor(section.type)}`}
                  >
                    <div className="flex items-center space-x-2 mb-3">
                      <span className="text-lg">{getSectionIcon(section.type)}</span>
                      <h5 className="font-semibold text-contrast">{section.title}</h5>
                    </div>
                    <div className="prose prose-sm max-w-none">
                      <div className="text-sm text-contrast whitespace-pre-wrap leading-relaxed break-words overflow-wrap-anywhere">
                        {section.content}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}

      {/* Summary Statistics */}
      <div className="mt-6 p-4 bg-muted rounded-lg border">
        <h4 className="font-semibold text-contrast mb-2">Investigation Summary</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="text-muted-foreground">Total Messages:</span>
            <div className="font-semibold">{parsedMessages.length}</div>
          </div>
          <div>
            <span className="text-muted-foreground">Analysis Agents:</span>
            <div className="font-semibold">{new Set(parsedMessages.map((m: InvestigationMessage) => m.name).filter(Boolean)).size}</div>
          </div>
          <div>
            <span className="text-muted-foreground">System Messages:</span>
            <div className="font-semibold">{parsedMessages.filter((m: InvestigationMessage) => m.type === 'system').length}</div>
          </div>
          <div>
            <span className="text-muted-foreground">Human Inputs:</span>
            <div className="font-semibold">{parsedMessages.filter((m: InvestigationMessage) => m.type === 'human').length}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function InvestigationResults({ investigation, onNewInvestigation }: InvestigationResultsProps) {
  const [copySuccess, setCopySuccess] = useState(false);

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
        <button
          onClick={onNewInvestigation}
          className="btn-secondary px-4 py-2 rounded-lg font-medium"
        >
          New Investigation
        </button>
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
          
          {/* Display detailed investigation findings */}
          <div className="mt-4 p-6 bg-gradient-to-br from-gray-50 to-blue-50 dark:from-gray-900 dark:to-blue-950 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-lg font-bold text-gray-800 dark:text-gray-200">📊 Investigation Report</h4>
              <button
                onClick={() => copyToClipboard(investigation.final_decision)}
                className={`px-3 py-1 text-sm font-medium rounded-md transition-all duration-200 flex items-center space-x-2 ${
                  copySuccess 
                    ? 'bg-green-600 text-white' 
                    : 'bg-blue-600 hover:bg-blue-700 text-white hover:shadow-md'
                }`}
                title="Copy report to clipboard"
              >
                <span>{copySuccess ? '✅' : '📋'}</span>
                <span>{copySuccess ? 'Copied!' : 'Copy'}</span>
              </button>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-600 max-w-none overflow-auto">
              {investigation.final_decision.includes('**FRAUD INVESTIGATION COMPLETE**') ? (
                <MarkdownRenderer content={investigation.final_decision} />
              ) : (
                <div className="text-gray-700 dark:text-gray-300 break-words overflow-wrap-anywhere whitespace-pre-wrap">{investigation.final_decision}</div>
              )}
            </div>
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

      {/* Detailed Investigation Analysis */}
      {investigation.full_results ? (
        <div className="bg-card p-6 rounded-lg shadow-lg">
          <h3 className="text-xl font-bold mb-4 text-contrast">Detailed Investigation Analysis</h3>
          <DetailedResultsViewer results={investigation.full_results} />
        </div>
      ) : (
        <div className="bg-card p-6 rounded-lg shadow-lg">
          <h3 className="text-xl font-bold mb-4 text-contrast">Investigation Report</h3>
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
    </div>
  );
}
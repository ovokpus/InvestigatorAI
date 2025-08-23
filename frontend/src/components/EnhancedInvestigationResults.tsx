'use client';
import React, { useState } from 'react';



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





interface DetailedResultsViewerProps {
  results: FullResults;
}

// Professional content formatter matching the pasted result format
const renderEnhancedContent = (content: string): React.JSX.Element => {
  if (!content) return <span>No content available</span>;
  
  // Remove ALL markdown notation first
  const cleanContent = content
    .replace(/\*\*([^*]+)\*\*/g, '$1')  // Remove ** bold **
    .replace(/\*([^*]+)\*/g, '$1')      // Remove * italic *
    .replace(/`([^`]+)`/g, '$1')        // Remove ` code `
    .replace(/##+\s*/g, '')             // Remove ### headers
    .trim();
  
  // Split by lines to handle proper formatting
  const lines = cleanContent.split('\n').map(line => line.trim()).filter(line => line);
  
  return (
    <div className="space-y-3 text-gray-100 font-mono leading-relaxed">
      {lines.map((line, index) => {
        // Check if it's a major section header (ALL CAPS with colons)
        if (line === line.toUpperCase() && line.includes(':') && /[A-Z]/.test(line)) {
          return (
            <div key={index} className="font-bold text-white text-lg mb-2 mt-4">
              {highlightImportantTerms(line)}
            </div>
          );
        }
        
        // Check if it's a subsection header (ends with colon, not all caps)
        if (line.endsWith(':') && !line.startsWith('-') && !line.startsWith('✅')) {
          return (
            <div key={index} className="font-bold text-slate-200 mb-1 mt-3">
              {highlightImportantTerms(line)}
            </div>
          );
        }
        
        // Check if it's a bullet point (starts with -)
        if (line.startsWith('-')) {
          return (
            <div key={index} className="ml-2 mb-1">
              <span className="text-cyan-400 mr-2">-</span>
              <span>{highlightImportantTerms(line.substring(1).trim())}</span>
            </div>
          );
        }
        
        // Check if it's a completion status (starts with ✅)
        if (line.startsWith('✅')) {
          return (
            <div key={index} className="font-bold text-green-300 mb-2">
              {line}
            </div>
          );
        }
        
        // Check if it's all caps (like CRITICAL:)
        if (line === line.toUpperCase() && /[A-Z]/.test(line)) {
          return (
            <div key={index} className="font-bold text-yellow-300 mb-2 mt-3">
              {highlightImportantTerms(line)}
            </div>
          );
        }
        
        // Regular line
        return (
          <div key={index} className="mb-1">
            {highlightImportantTerms(line)}
          </div>
        );
      })}
    </div>
  );
  
  function highlightImportantTerms(text: string): React.JSX.Element {
    // Professional highlighting for financial terms with banking-style colors
    const parts = text.split(/(\b(?:OFAC|SAR|AML|KYC|CDD|EDD|Brazil|high-risk|medium-risk|low-risk|\d+\.\d+|HIGH|MEDIUM|LOW)\b)/gi);
    
    return (
      <span>
        {parts.map((part, index) => {
          const lowerPart = part.toLowerCase();
          const upperPart = part.toUpperCase();
          
          // Risk scores and numerical values - professional gold highlight
          if (/^\d+\.\d+$/.test(part)) {
            return <span key={index} className="font-mono text-amber-200 bg-amber-900/20 px-2 py-0.5 rounded border border-amber-800/30 font-bold">{part}</span>;
          }
          
          // Regulatory terms - professional blue with better contrast
          if (['ofac', 'sar', 'aml', 'kyc', 'cdd', 'edd'].includes(lowerPart)) {
            return <span key={index} className="font-semibold text-blue-200 bg-blue-900/30 px-1.5 py-0.5 rounded border border-blue-800/40">{part}</span>;
          }
          
          // Countries - subtle slate highlight with better visibility
          if (lowerPart === 'brazil') {
            return <span key={index} className="font-medium text-blue-300 bg-blue-900/20 px-1.5 py-0.5 rounded">{part}</span>;
          }
          
          // Risk levels - professional color coding
          if (lowerPart.includes('high-risk') || upperPart === 'HIGH') {
            return <span key={index} className="font-bold text-red-200 bg-red-900/30 px-2 py-0.5 rounded border border-red-800/40">{part}</span>;
          }
          if (lowerPart.includes('medium-risk') || upperPart === 'MEDIUM') {
            return <span key={index} className="font-bold text-orange-200 bg-orange-900/30 px-2 py-0.5 rounded border border-orange-800/40">{part}</span>;
          }
          if (lowerPart.includes('low-risk') || upperPart === 'LOW') {
            return <span key={index} className="font-bold text-green-200 bg-green-900/30 px-2 py-0.5 rounded border border-green-800/40">{part}</span>;
          }
          
          return <span key={index}>{part}</span>;
        })}
      </span>
    );
  }
};

// Component to show only Report Generation Agent
function ReportGenerationViewer({ results }: DetailedResultsViewerProps) {
  const messages = results?.messages || [];
  
  // Parse messages and filter for report_generation only
  const parsedMessages = messages
    .map((msg: unknown) => {
      if (typeof msg === 'string' && msg.includes("'content':")) {
        try {
          const jsonString = msg
            .replace(/'/g, '"')
            .replace(/True/g, 'true')
            .replace(/False/g, 'false')
            .replace(/None/g, 'null');
          
          const parsed = JSON.parse(jsonString);
          return {
            content: parsed.content || '',
            name: parsed.name || 'unknown',
            type: parsed.type || 'unknown'
          };
        } catch {
          return {
            content: msg,
            name: 'unknown',
            type: 'unknown'
          };
        }
      }
      
      if (typeof msg === 'object' && msg !== null) {
        const objMsg = msg as { content?: string; name?: string; type?: string };
        return {
          content: objMsg.content || '',
          name: objMsg.name || 'unknown',
          type: objMsg.type || 'unknown'
        };
      }
      
      return {
        content: String(msg),
        name: 'unknown',
        type: 'unknown'
      };
    })
    .filter((message: InvestigationMessage) => message.name === 'report_generation');

  if (!parsedMessages.length) {
    return (
      <div className="text-center p-8 text-muted-foreground">
        <p>No report generation analysis available for this investigation.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {parsedMessages.map((message: InvestigationMessage, messageIndex: number) => {
        if (!message.content || message.type === 'human') return null;

        return (
          <div key={messageIndex} className="border border-cyan-500 rounded-lg overflow-hidden bg-gray-900">
            <div className="bg-gray-800 p-4 border-b border-cyan-500">
              <div className="flex items-center space-x-3">
                <div className="text-lg text-cyan-400">📊</div>
                <div>
                  <h4 className="font-semibold text-cyan-300 font-mono">Report Generation Agent</h4>
                  <p className="text-sm text-cyan-500 font-mono">
                    Investigation Analysis
                  </p>
                </div>
              </div>
            </div>

            <div className="p-6 bg-gray-900">
              {renderEnhancedContent(message.content)}
            </div>
          </div>
        );
      })}
    </div>
  );
}

// Component to show other agents (excluding Report Generation Agent)
function OtherAgentsViewer({ results }: DetailedResultsViewerProps) {
  const [expandedSections, setExpandedSections] = useState<{ [key: number]: boolean }>({});

  const toggleSection = (index: number) => {
    setExpandedSections(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  const messages = results?.messages || [];
  
  const parsedMessages = messages
    .map((msg: unknown) => {
      if (typeof msg === 'string' && msg.includes("'content':")) {
        try {
          const jsonString = msg
            .replace(/'/g, '"')
            .replace(/True/g, 'true')
            .replace(/False/g, 'false')
            .replace(/None/g, 'null');
          
          const parsed = JSON.parse(jsonString);
          return {
            content: parsed.content || '',
            name: parsed.name || 'unknown',
            type: parsed.type || 'unknown'
          };
        } catch {
          return {
            content: msg,
            name: 'unknown',
            type: 'unknown'
          };
        }
      }
      
      if (typeof msg === 'object' && msg !== null) {
        const objMsg = msg as { content?: string; name?: string; type?: string };
        return {
          content: objMsg.content || '',
          name: objMsg.name || 'unknown',
          type: objMsg.type || 'unknown'
        };
      }
      
      return {
        content: String(msg),
        name: 'unknown',
        type: 'unknown'
      };
    })
    .filter((message: InvestigationMessage) => 
      message.name !== 'report_generation' && 
      message.name !== 'unknown' && 
      message.type !== 'human'
    );

  if (!parsedMessages.length) {
    return (
      <div className="text-center p-8 text-muted-foreground">
        <p>No additional agent analysis available for this investigation.</p>
      </div>
    );
  }

  const formatAgentName = (name: string) => {
    switch (name) {
      case 'regulatory_research': return 'Regulatory Research Agent';
      case 'evidence_collection': return 'Evidence Collection Agent';
      case 'compliance_check': return 'Compliance Check Agent';
      default: return name ? name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : 'Analysis Agent';
    }
  };

  return (
    <div className="space-y-4">
      {parsedMessages.map((message: InvestigationMessage, messageIndex: number) => {
        if (!message.content || message.type === 'human') return null;

        const agentName = formatAgentName(message.name || 'unknown');

        return (
          <div key={messageIndex} className="border border-cyan-500 rounded-lg overflow-hidden bg-gray-900">
            <div 
              className="bg-gray-800 p-4 cursor-pointer flex items-center justify-between hover:bg-gray-700 transition-colors border-b border-cyan-500"
              onClick={() => toggleSection(messageIndex)}
            >
              <div className="flex items-center space-x-3">
                <div className="text-lg text-cyan-400">🤖</div>
                <div>
                  <h4 className="font-semibold text-cyan-300 font-mono">{agentName}</h4>
                  <p className="text-sm text-cyan-500 font-mono">
                    Investigation Analysis
                  </p>
                </div>
              </div>
              <div className="text-cyan-400 font-mono">
                {expandedSections[messageIndex] ? '▼' : '▶'}
              </div>
            </div>

            {expandedSections[messageIndex] && (
              <div className="p-6 bg-gray-900">
                {renderEnhancedContent(message.content)}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

export { ReportGenerationViewer, OtherAgentsViewer };

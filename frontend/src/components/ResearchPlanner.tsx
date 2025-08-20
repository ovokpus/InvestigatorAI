'use client';

import { useState } from 'react';

interface ResearchSection {
  name: string;
  description: string;
  research: boolean;
  content: string;
  queries: string[];
  sources: string[];
  iteration_count: number;
  quality_score: number;
}

interface ResearchPlan {
  topic: string;
  sections: ResearchSection[];
  research_depth: number;
  query_count: number;
  created_at: string;
}

export default function ResearchPlanner() {
  const [topic, setTopic] = useState('');
  const [context, setContext] = useState('');
  const [researchPlan, setResearchPlan] = useState<ResearchPlan | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string>('');

  const handleGeneratePlan = async () => {
    if (!topic.trim()) {
      setError('Please enter a research topic');
      return;
    }

    setIsGenerating(true);
    setError('');
    
    try {
      const response = await fetch('http://localhost:8000/research/plan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: topic.trim(),
          context: context.trim()
        }),
      });

      if (!response.ok) {
        throw new Error(`Plan generation failed: ${response.statusText}`);
      }

      const data = await response.json();
      setResearchPlan(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Plan generation failed');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleStartResearch = async (sectionName: string) => {
    if (!researchPlan) return;
    
    // This would trigger the full research process
    alert(`Starting research for section: ${sectionName}\n\nThis would integrate with the enhanced investigation endpoint.`);
  };

  return (
    <div className="space-y-6">
      {/* Plan Generation */}
      <div className="bg-card p-6 rounded-lg shadow-lg">
        <h2 className="text-2xl font-bold mb-4 text-contrast">Research Plan Generator</h2>
        <p className="text-muted-foreground mb-6">
          Generate structured research plans with dynamic sections and quality assessment criteria
        </p>

        <div className="space-y-4">
          {/* Topic Input */}
          <div>
            <label className="block text-sm font-medium text-contrast mb-2">
              Research Topic *
            </label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., Money laundering investigation procedures, Academic research on AI ethics..."
              className="w-full px-3 py-2 border border-input bg-background rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          {/* Context Input */}
          <div>
            <label className="block text-sm font-medium text-contrast mb-2">
              Additional Context (Optional)
            </label>
            <textarea
              value={context}
              onChange={(e) => setContext(e.target.value)}
              placeholder="Provide additional context, specific focus areas, or requirements for the research..."
              rows={3}
              className="w-full px-3 py-2 border border-input bg-background rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-none"
            />
          </div>

          {/* Generate Button */}
          <button
            onClick={handleGeneratePlan}
            disabled={isGenerating}
            className="w-full bg-primary text-primary-foreground py-3 px-6 rounded-lg font-medium hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isGenerating ? 'Generating Research Plan...' : 'Generate Research Plan'}
          </button>

          {error && (
            <div className="p-3 bg-destructive/10 border border-destructive text-destructive rounded-md">
              {error}
            </div>
          )}
        </div>
      </div>

      {/* Generated Plan */}
      {researchPlan && (
        <div className="bg-card p-6 rounded-lg shadow-lg">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className="text-xl font-bold text-contrast">{researchPlan.topic}</h3>
              <p className="text-sm text-muted-foreground">
                Generated {new Date(researchPlan.created_at).toLocaleString()}
              </p>
            </div>
            <div className="text-right text-sm text-muted-foreground">
              <div>Research Depth: {researchPlan.research_depth}</div>
              <div>Queries per Section: {researchPlan.query_count}</div>
            </div>
          </div>

          <div className="space-y-4">
            {researchPlan.sections.map((section, index) => (
              <div
                key={index}
                className={`border rounded-lg p-4 ${
                  section.research ? 'border-primary bg-primary/5' : 'border-input'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <h4 className="font-semibold text-contrast">{section.name}</h4>
                      {section.research && (
                        <span className="bg-primary text-primary-foreground text-xs px-2 py-1 rounded-full">
                          Research Required
                        </span>
                      )}
                    </div>
                    <p className="text-muted-foreground text-sm mt-1">
                      {section.description}
                    </p>
                  </div>
                  
                  {section.research && (
                    <button
                      onClick={() => handleStartResearch(section.name)}
                      className="ml-4 bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90"
                    >
                      Start Research
                    </button>
                  )}
                </div>

                {/* Section Metadata */}
                <div className="flex items-center space-x-4 text-xs text-muted-foreground mt-3">
                  <span>Iterations: {section.iteration_count}</span>
                  {section.quality_score > 0 && (
                    <span>Quality Score: {section.quality_score.toFixed(1)}</span>
                  )}
                  {section.sources.length > 0 && (
                    <span>Sources: {section.sources.length}</span>
                  )}
                </div>

                {/* Section Content Preview */}
                {section.content && (
                  <div className="mt-3 p-3 bg-secondary/20 rounded border">
                    <p className="text-sm text-contrast">
                      {section.content.length > 200 
                        ? `${section.content.substring(0, 200)}...` 
                        : section.content
                      }
                    </p>
                  </div>
                )}

                {/* Generated Queries */}
                {section.queries.length > 0 && (
                  <div className="mt-3">
                    <p className="text-xs font-medium text-contrast mb-2">Planned Queries:</p>
                    <div className="flex flex-wrap gap-1">
                      {section.queries.map((query, qIndex) => (
                        <span
                          key={qIndex}
                          className="bg-secondary text-secondary-foreground text-xs px-2 py-1 rounded"
                        >
                          {query}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Plan Actions */}
          <div className="mt-6 pt-4 border-t border-input">
            <div className="flex space-x-4">
              <button className="flex-1 bg-primary text-primary-foreground py-2 px-4 rounded-lg font-medium hover:bg-primary/90">
                Execute Full Research Plan
              </button>
              <button className="px-4 py-2 bg-secondary text-secondary-foreground rounded-lg font-medium hover:bg-accent">
                Export Plan
              </button>
              <button className="px-4 py-2 bg-secondary text-secondary-foreground rounded-lg font-medium hover:bg-accent">
                Modify Plan
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

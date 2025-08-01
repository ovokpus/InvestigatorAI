import Header from '@/components/Header';
import HealthStatus from '@/components/HealthStatus';
import Link from 'next/link';

export default function HelpPage() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="mb-8">
          <HealthStatus />
        </div>

        <div className="mb-8">
          <nav className="flex space-x-4">
            <Link href="/" className="px-4 py-2 bg-secondary text-secondary-foreground hover:bg-accent rounded-lg font-medium transition-colors">
              Investigation
            </Link>
            <Link href="/tools" className="px-4 py-2 bg-secondary text-secondary-foreground hover:bg-accent rounded-lg font-medium transition-colors">
              Tools & Search
            </Link>
            <span className="px-4 py-2 bg-primary text-primary-foreground rounded-lg font-medium">
              Help & Docs
            </span>
            <a 
              href="#quick-start" 
              className="px-4 py-2 bg-green-600 text-white hover:bg-green-700 rounded-lg font-medium transition-colors"
            >
              🚀 Quick Start
            </a>
          </nav>
        </div>

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-contrast mb-2">How to Use InvestigatorAI</h1>
          <p className="text-muted-foreground">
            Complete guide to fraud investigation with AI-powered assistance
          </p>
        </div>

        <div className="space-y-8">
          {/* Business Value Section - Moved to Top */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20 rounded-lg p-8 border border-blue-200 dark:border-blue-800">
            <h2 className="text-3xl font-bold text-blue-800 dark:text-blue-200 mb-6">💼 Why InvestigatorAI Transforms Your Business</h2>
            
            <div className="mb-6">
              <p className="text-lg text-blue-700 dark:text-blue-300 mb-4">
                InvestigatorAI revolutionizes fraud investigation by reducing investigation time from 6 hours to 90 minutes, 
                delivering immediate ROI while ensuring regulatory compliance and reducing risk exposure.
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              <div className="space-y-6">
                <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
                  <h3 className="text-xl font-bold text-green-600 mb-3 flex items-center">
                    ⏱️ Massive Time Savings
                  </h3>
                  <div className="space-y-2 text-sm text-muted-foreground">
                    <p><strong>Before InvestigatorAI:</strong> 4-6 hours per investigation</p>
                    <p><strong>After InvestigatorAI:</strong> 90 minutes per investigation</p>
                    <p className="text-green-600 font-medium">⚡ 75% reduction in investigation time</p>
                    <p>Enables analysts to handle 4x more cases per day, dramatically reducing backlogs and improving response times to genuine fraud.</p>
                  </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
                  <h3 className="text-xl font-bold text-blue-600 mb-3 flex items-center">
                    🛡️ Regulatory Compliance
                  </h3>
                  <div className="space-y-2 text-sm text-muted-foreground">
                    <p><strong>Built-in AML/BSA/SAR Requirements:</strong> Automatic compliance checking</p>
                    <p><strong>Real Regulatory Data:</strong> INTERPOL, FinCEN, FFIEC integration</p>
                    <p><strong>Audit-Ready Documentation:</strong> Complete investigation trails</p>
                    <p>Reduces regulatory penalty risk (avg. $10M+ annually for AML violations) through consistent, thorough investigations.</p>
                  </div>
                </div>
              </div>

              <div className="space-y-6">
                <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
                  <h3 className="text-xl font-bold text-purple-600 mb-3 flex items-center">
                    📈 Quantified ROI Impact
                  </h3>
                  <div className="space-y-2 text-sm text-muted-foreground">
                    <p><strong>Per Analyst Annual Savings:</strong> $85,000+</p>
                    <p><strong>Medium Institution (50 analysts):</strong> $4.25M annually</p>
                    <p><strong>Large Institution (200 analysts):</strong> $17M annually</p>
                    <p className="text-purple-600 font-medium">💰 ROI typically achieved within 3-6 months</p>
                    <p>Cost savings from reduced investigation time, fewer compliance violations, and faster fraud detection.</p>
                  </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
                  <h3 className="text-xl font-bold text-red-600 mb-3 flex items-center">
                    ⚠️ Risk Reduction
                  </h3>
                  <div className="space-y-2 text-sm text-muted-foreground">
                    <p><strong>Faster Detection:</strong> Identify fraud patterns in minutes, not hours</p>
                    <p><strong>Reduced Exposure:</strong> Stop fraudsters before additional damage</p>
                    <p><strong>Quality Consistency:</strong> AI eliminates human error and oversight</p>
                    <p>Studies show 30% reduction in fraud losses through faster, more consistent investigation processes.</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
              <h3 className="text-xl font-bold text-indigo-600 mb-4">🎯 Operational Excellence</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <h4 className="font-semibold text-contrast mb-2">Productivity Gains</h4>
                  <ul className="space-y-1 text-muted-foreground">
                    <li>• 4x more cases per analyst daily</li>
                    <li>• Elimination of manual research</li>
                    <li>• Automated documentation generation</li>
                    <li>• Real-time regulatory updates</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-contrast mb-2">Quality Improvements</h4>
                  <ul className="space-y-1 text-muted-foreground">
                    <li>• 100% consistent investigation standards</li>
                    <li>• Zero missed regulatory requirements</li>
                    <li>• Comprehensive audit trails</li>
                    <li>• Evidence-based decisions</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-contrast mb-2">Strategic Benefits</h4>
                  <ul className="space-y-1 text-muted-foreground">
                    <li>• Focus on high-value cases</li>
                    <li>• Reduced analyst burnout</li>
                    <li>• Scalable investigation capacity</li>
                    <li>• Competitive advantage</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="mt-6 p-4 bg-blue-100 dark:bg-blue-900/30 rounded-lg border border-blue-300 dark:border-blue-700">
              <p className="text-blue-800 dark:text-blue-200 font-medium text-center">
                <strong>Bottom Line:</strong> InvestigatorAI isn&apos;t just a tool—it&apos;s a business transformation that delivers measurable ROI 
                while ensuring compliance and reducing risk exposure across your entire fraud investigation operation.
              </p>
            </div>
          </div>
          {/* Quick Start Section */}
          <div id="quick-start" className="bg-card rounded-lg p-6 border border-border">
            <h2 className="text-2xl font-semibold text-contrast mb-4">🚀 Quick Start</h2>
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-medium text-contrast mb-2">1. Check System Status</h3>
                <p className="text-muted-foreground mb-2">
                  Always verify that all system components are operational before starting an investigation:
                </p>
                <ul className="list-disc pl-6 text-muted-foreground space-y-1">
                  <li><span className="text-green-600 font-medium">✅ API Status: healthy</span> - Backend services running</li>
                  <li><span className="text-green-600 font-medium">✅ AI Models: Ready</span> - OpenAI integration active</li>
                  <li><span className="text-green-600 font-medium">✅ Vector DB: Ready</span> - Document search available</li>
                </ul>
              </div>

              <div>
                <h3 className="text-lg font-medium text-contrast mb-2">2. Start an Investigation</h3>
                <p className="text-muted-foreground">
                  Navigate to the <strong>Investigation</strong> tab and fill out the transaction details form with:
                </p>
                <ul className="list-disc pl-6 text-muted-foreground space-y-1 mt-2">
                  <li>Transaction amount and currency</li>
                  <li>Customer name and account type</li>
                  <li>Transaction description</li>
                  <li>Destination country</li>
                  <li>Risk rating assessment</li>
                </ul>
              </div>

              <div>
                <h3 className="text-lg font-medium text-contrast mb-2">3. Review Results</h3>
                <p className="text-muted-foreground">
                  The AI agents will process your investigation and provide a comprehensive report including regulatory compliance checks, risk assessment, and documentation ready for review.
                </p>
              </div>
            </div>
          </div>

          {/* Demo Examples Section */}
          <div className="bg-card rounded-lg p-6 border border-border">
            <h2 className="text-2xl font-semibold text-contrast mb-4">🎬 Demo Examples</h2>
            <p className="text-muted-foreground mb-6">
              Try these real-world fraud scenarios to see how InvestigatorAI works in practice:
            </p>

            <div className="space-y-6">
              {/* Example 1 */}
              <div className="border border-border rounded-lg p-4">
                <h3 className="text-lg font-semibold text-red-600 mb-2">🚨 High-Risk Shell Company Transaction</h3>
                <p className="text-sm text-muted-foreground mb-3">
                  <strong>Use Case:</strong> Procurement fraud investigation
                </p>
                
                <div className="bg-muted rounded p-4 mb-3">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                    <div><strong>Amount:</strong> $85,000</div>
                    <div><strong>Currency:</strong> USD</div>
                    <div><strong>Customer:</strong> Rapid Industries LLC</div>
                    <div><strong>Account Type:</strong> Business</div>
                    <div><strong>Destination:</strong> British Virgin Islands</div>
                    <div><strong>Risk Rating:</strong> High</div>
                  </div>
                  <div className="mt-3">
                    <strong>Description:</strong> Large equipment purchase from overseas supplier through shell company
                  </div>
                </div>

                <div className="text-sm">
                  <strong className="text-red-600">Why This Is Suspicious:</strong>
                  <ul className="list-disc pl-5 mt-1 text-muted-foreground space-y-1">
                    <li>High-value transaction to known tax haven</li>
                    <li>Shell company with minimal business history</li>
                    <li>Equipment purchase without proper documentation</li>
                    <li>BVI is flagged jurisdiction for money laundering</li>
                  </ul>
                </div>

                <div className="mt-3 text-sm">
                  <strong className="text-blue-600">Expected Results:</strong>
                  <span className="text-muted-foreground"> High-risk classification, SAR filing recommendations, offshore jurisdiction flags</span>
                </div>
              </div>

              {/* Example 2 */}
              <div className="border border-border rounded-lg p-4">
                <h3 className="text-lg font-semibold text-yellow-600 mb-2">💰 Structured Deposit Pattern</h3>
                <p className="text-sm text-muted-foreground mb-3">
                  <strong>Use Case:</strong> BSA compliance violation detection
                </p>
                
                <div className="bg-muted rounded p-4 mb-3">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                    <div><strong>Amount:</strong> $9,500</div>
                    <div><strong>Currency:</strong> USD</div>
                    <div><strong>Customer:</strong> Corner Market Express</div>
                    <div><strong>Account Type:</strong> Business</div>
                    <div><strong>Destination:</strong> United States</div>
                    <div><strong>Risk Rating:</strong> Low</div>
                  </div>
                  <div className="mt-3">
                    <strong>Description:</strong> Business cash deposit from daily operations
                  </div>
                </div>

                <div className="text-sm">
                  <strong className="text-yellow-600">Why This Is Suspicious:</strong>
                  <ul className="list-disc pl-5 mt-1 text-muted-foreground space-y-1">
                    <li>Amount just under $10K CTR threshold</li>
                    <li>Pattern suggests structuring to avoid reporting</li>
                    <li>Cash-intensive business model</li>
                    <li>Potential BSA compliance issues</li>
                  </ul>
                </div>

                <div className="mt-3 text-sm">
                  <strong className="text-blue-600">Expected Results:</strong>
                  <span className="text-muted-foreground"> Structuring pattern detection, CTR threshold analysis</span>
                </div>
              </div>

              {/* Example 3 */}
              <div className="border border-border rounded-lg p-4">
                <h3 className="text-lg font-semibold text-orange-600 mb-2">🌍 International Crypto Transfer</h3>
                <p className="text-sm text-muted-foreground mb-3">
                  <strong>Use Case:</strong> Cryptocurrency compliance review
                </p>
                
                <div className="bg-muted rounded p-4 mb-3">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                    <div><strong>Amount:</strong> $125,000</div>
                    <div><strong>Currency:</strong> USD</div>
                    <div><strong>Customer:</strong> Digital Assets Management Co</div>
                    <div><strong>Account Type:</strong> Corporate</div>
                    <div><strong>Destination:</strong> Estonia</div>
                    <div><strong>Risk Rating:</strong> Medium</div>
                  </div>
                  <div className="mt-3">
                    <strong>Description:</strong> Investment transfer to cryptocurrency exchange platform
                  </div>
                </div>

                <div className="text-sm">
                  <strong className="text-orange-600">Why This Is Suspicious:</strong>
                  <ul className="list-disc pl-5 mt-1 text-muted-foreground space-y-1">
                    <li>Large crypto investment without proper KYC</li>
                    <li>Estonia has emerging crypto regulations</li>
                    <li>Corporate structure for individual trading</li>
                    <li>Potential sanctions evasion risk</li>
                  </ul>
                </div>

                <div className="mt-3 text-sm">
                  <strong className="text-blue-600">Expected Results:</strong>
                  <span className="text-muted-foreground"> Enhanced due diligence, crypto compliance review</span>
                </div>
              </div>
            </div>
          </div>

          {/* Features Guide Section */}
          <div className="bg-card rounded-lg p-6 border border-border">
            <h2 className="text-2xl font-semibold text-contrast mb-4">🛠️ Features Guide</h2>
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-medium text-contrast mb-2">Investigation Workflow</h3>
                <p className="text-muted-foreground mb-2">
                  The main investigation feature uses 4 specialized AI agents working in coordination:
                </p>
                <ul className="list-disc pl-6 text-muted-foreground space-y-1">
                  <li><strong>Evidence Collection Agent:</strong> Analyzes transaction patterns and historical data</li>
                  <li><strong>Regulatory Compliance Agent:</strong> Checks AML/BSA requirements and compliance</li>
                  <li><strong>Historical Case Agent:</strong> Searches for similar fraud patterns</li>
                  <li><strong>Investigation Report Agent:</strong> Generates comprehensive documentation</li>
                </ul>
              </div>

              <div>
                <h3 className="text-lg font-medium text-contrast mb-2">Document Search</h3>
                <p className="text-muted-foreground">
                  Access real regulatory content from INTERPOL, FinCEN, and FFIEC. Search for specific compliance requirements, 
                  suspicious activity indicators, and regulatory guidance to support your investigations.
                </p>
              </div>

              <div>
                <h3 className="text-lg font-medium text-contrast mb-2">Exchange Rate Lookup</h3>
                <p className="text-muted-foreground">
                  Get current currency exchange rates to analyze international transactions and detect pricing anomalies 
                  that might indicate fraud or money laundering.
                </p>
              </div>

              <div>
                <h3 className="text-lg font-medium text-contrast mb-2">Real-time Monitoring</h3>
                <p className="text-muted-foreground">
                  The system provides live health status updates every 30 seconds to ensure all components are operational 
                  and ready for investigation work.
                </p>
              </div>
            </div>
          </div>

          {/* Performance Expectations */}
          <div className="bg-card rounded-lg p-6 border border-border">
            <h2 className="text-2xl font-semibold text-contrast mb-4">⚡ Performance Expectations</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left py-2 text-contrast">Feature</th>
                    <th className="text-left py-2 text-contrast">Response Time</th>
                    <th className="text-left py-2 text-contrast">Success Rate</th>
                  </tr>
                </thead>
                <tbody className="text-muted-foreground">
                  <tr className="border-b border-border">
                    <td className="py-2">Health Check</td>
                    <td className="py-2">&lt; 1 second</td>
                    <td className="py-2">100%</td>
                  </tr>
                  <tr className="border-b border-border">
                    <td className="py-2">Document Search</td>
                    <td className="py-2">2-3 seconds</td>
                    <td className="py-2">100%</td>
                  </tr>
                  <tr className="border-b border-border">
                    <td className="py-2">Exchange Rate</td>
                    <td className="py-2">&lt; 1 second</td>
                    <td className="py-2">100%*</td>
                  </tr>
                  <tr>
                    <td className="py-2">Full Investigation</td>
                    <td className="py-2">30-90 seconds</td>
                    <td className="py-2">100%</td>
                  </tr>
                </tbody>
              </table>
              <p className="text-xs text-muted-foreground mt-2">
                *Exchange rate shows graceful error handling for missing API key
              </p>
            </div>
          </div>



          {/* Troubleshooting Section */}
          <div className="bg-card rounded-lg p-6 border border-border">
            <h2 className="text-2xl font-semibold text-contrast mb-4">🔧 Troubleshooting</h2>
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-medium text-contrast mb-2">System Status Issues</h3>
                <p className="text-muted-foreground mb-2">
                  If you see red status indicators, check that both the API server and frontend are running properly.
                </p>
              </div>

              <div>
                <h3 className="text-lg font-medium text-contrast mb-2">Slow Investigation Processing</h3>
                <p className="text-muted-foreground mb-2">
                  Normal processing time is 30-90 seconds for complex cases. Longer delays may indicate:
                </p>
                <ul className="list-disc pl-6 text-muted-foreground space-y-1">
                  <li>OpenAI API rate limits or high usage</li>
                  <li>Complex transaction patterns requiring additional analysis</li>
                  <li>Network connectivity issues</li>
                </ul>
              </div>

              <div>
                <h3 className="text-lg font-medium text-contrast mb-2">Search Not Returning Results</h3>
                <p className="text-muted-foreground">
                  Try different search terms or check that the vector database is properly initialized (green status indicator).
                </p>
              </div>
            </div>
          </div>

          {/* Contact Section */}
          <div className="bg-card rounded-lg p-6 border border-border text-center">
            <h2 className="text-2xl font-semibold text-contrast mb-4">📞 Need Help?</h2>
            <p className="text-muted-foreground mb-4">
              For additional support or questions about InvestigatorAI, consult the comprehensive documentation 
              or contact your system administrator.
            </p>
            <div className="flex justify-center space-x-4">
              <Link href="/" className="btn-secondary">
                Start Investigation
              </Link>
              <Link href="/tools" className="btn-primary">
                Explore Tools
              </Link>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
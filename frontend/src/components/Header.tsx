'use client';

export default function Header() {
  return (
    <header className="bg-primary text-primary-foreground shadow-lg">
      <div className="container mx-auto px-4 py-4 sm:py-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between space-y-3 sm:space-y-0">
          <div className="flex-1">
            <h1 className="text-2xl sm:text-3xl font-bold">InvestigatorAI</h1>
            <p className="text-xs sm:text-sm opacity-90 mt-1">Multi-Agent Fraud Investigation System</p>
          </div>
          
          <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-2 sm:space-y-0 sm:space-x-4 w-full sm:w-auto">
            <div className="text-left sm:text-right">
              <div className="text-xs sm:text-sm opacity-90">AI Tooling Powered by</div>
              <div className="font-semibold text-sm sm:text-base">OpenAI, LangChain, LangGraph, Qdrant & RAGAS</div>
            </div>
            
            <div className="w-10 h-10 sm:w-12 sm:h-12 bg-primary-foreground/20 rounded-full flex items-center justify-center flex-shrink-0">
              <svg 
                className="w-5 h-5 sm:w-6 sm:h-6" 
                fill="currentColor" 
                viewBox="0 0 20 20"
              >
                <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
'use client';

import { useState, useEffect } from 'react';

interface ResearchSession {
  research_id: string;
  topic: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'cancelled';
  progress_percentage: number;
  completed_sections: number;
  total_sections: number;
  created_at: string;
  updated_at: string;
  error_message?: string;
  research_type?: string;
}

interface SessionListResponse {
  sessions: ResearchSession[];
  total_count: number;
  page: number;
  page_size: number;
}

export default function ResearchSessions() {
  const [sessions, setSessions] = useState<SessionListResponse | null>(null);
  const [selectedSession, setSelectedSession] = useState<ResearchSession | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    loadSessions();
  }, [currentPage]);

  const loadSessions = async () => {
    setIsLoading(true);
    setError('');
    
    try {
      const response = await fetch(`http://localhost:8000/research/sessions?page=${currentPage}&page_size=10`);
      
      if (!response.ok) {
        throw new Error(`Failed to load sessions: ${response.statusText}`);
      }

      const data = await response.json();
      setSessions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sessions');
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100 dark:bg-green-900/20';
      case 'in_progress': return 'text-blue-600 bg-blue-100 dark:bg-blue-900/20';
      case 'failed': return 'text-red-600 bg-red-100 dark:bg-red-900/20';
      case 'cancelled': return 'text-gray-600 bg-gray-100 dark:bg-gray-900/20';
      default: return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return '✅';
      case 'in_progress': return '🔄';
      case 'failed': return '❌';
      case 'cancelled': return '⏹️';
      default: return '⏳';
    }
  };

  const handleSessionSelect = async (session: ResearchSession) => {
    setSelectedSession(session);
    
    // Load detailed session information
    try {
      const response = await fetch(`http://localhost:8000/research/status/${session.research_id}`);
      if (response.ok) {
        const detailedSession = await response.json();
        setSelectedSession(detailedSession);
      }
    } catch (err) {
      console.error('Failed to load session details:', err);
    }
  };

  const handleDeleteSession = async (researchId: string) => {
    if (!confirm('Are you sure you want to delete this research session?')) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/research/sessions/${researchId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        // Reload sessions after deletion
        loadSessions();
        if (selectedSession?.research_id === researchId) {
          setSelectedSession(null);
        }
      } else {
        throw new Error('Failed to delete session');
      }
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete session');
    }
  };

  const handleCleanupSessions = async () => {
    if (!confirm('This will clean up old and completed research sessions. Continue?')) {
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/research/cleanup', {
        method: 'POST'
      });
      
      if (response.ok) {
        loadSessions();
        setSelectedSession(null);
        alert('Session cleanup completed');
      } else {
        throw new Error('Cleanup failed');
      }
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Cleanup failed');
    }
  };

  return (
    <div className="space-y-6">
      {/* Sessions Header */}
      <div className="bg-card p-6 rounded-lg shadow-lg">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="text-2xl font-bold text-contrast">Research Sessions</h2>
            <p className="text-muted-foreground">
              Manage ongoing and completed research sessions with resumable state
            </p>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={loadSessions}
              disabled={isLoading}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-md font-medium hover:bg-primary/90 disabled:opacity-50"
            >
              {isLoading ? 'Refreshing...' : 'Refresh'}
            </button>
            <button
              onClick={handleCleanupSessions}
              className="px-4 py-2 bg-destructive text-destructive-foreground rounded-md font-medium hover:bg-destructive/90"
            >
              Cleanup Old Sessions
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-destructive/10 border border-destructive text-destructive rounded-md">
            {error}
          </div>
        )}

        {/* Sessions Summary */}
        {sessions && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="text-center p-3 bg-secondary/20 rounded">
              <div className="text-2xl font-bold text-contrast">{sessions.total_count}</div>
              <div className="text-sm text-muted-foreground">Total Sessions</div>
            </div>
            <div className="text-center p-3 bg-secondary/20 rounded">
              <div className="text-2xl font-bold text-blue-600">
                {sessions.sessions.filter(s => s.status === 'in_progress').length}
              </div>
              <div className="text-sm text-muted-foreground">In Progress</div>
            </div>
            <div className="text-center p-3 bg-secondary/20 rounded">
              <div className="text-2xl font-bold text-green-600">
                {sessions.sessions.filter(s => s.status === 'completed').length}
              </div>
              <div className="text-sm text-muted-foreground">Completed</div>
            </div>
            <div className="text-center p-3 bg-secondary/20 rounded">
              <div className="text-2xl font-bold text-red-600">
                {sessions.sessions.filter(s => s.status === 'failed').length}
              </div>
              <div className="text-sm text-muted-foreground">Failed</div>
            </div>
          </div>
        )}

        {/* Sessions List */}
        {sessions && sessions.sessions.length > 0 ? (
          <div className="space-y-3">
            {sessions.sessions.map((session) => (
              <div
                key={session.research_id}
                onClick={() => handleSessionSelect(session)}
                className={`p-4 border rounded-lg cursor-pointer transition-colors hover:bg-accent ${
                  selectedSession?.research_id === session.research_id 
                    ? 'border-primary bg-primary/5' 
                    : 'border-input'
                }`}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="text-lg">{getStatusIcon(session.status)}</span>
                      <h3 className="font-semibold text-contrast">{session.topic}</h3>
                      <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(session.status)}`}>
                        {session.status}
                      </span>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      ID: {session.research_id}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      Created: {new Date(session.created_at).toLocaleString()}
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <div className="text-sm text-contrast font-medium">
                      {session.progress_percentage}% Complete
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {session.completed_sections}/{session.total_sections} sections
                    </div>
                    <div className="w-24 bg-secondary rounded-full h-2 mt-1">
                      <div 
                        className="bg-primary h-2 rounded-full transition-all"
                        style={{ width: `${session.progress_percentage}%` }}
                      ></div>
                    </div>
                  </div>
                </div>

                {session.error_message && (
                  <div className="mt-2 text-sm text-destructive">
                    Error: {session.error_message}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            {isLoading ? 'Loading sessions...' : 'No research sessions found'}
          </div>
        )}

        {/* Pagination */}
        {sessions && sessions.total_count > sessions.page_size && (
          <div className="flex justify-center items-center space-x-4 mt-6">
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage <= 1}
              className="px-4 py-2 bg-secondary text-secondary-foreground rounded-md disabled:opacity-50"
            >
              Previous
            </button>
            <span className="text-muted-foreground">
              Page {sessions.page} of {Math.ceil(sessions.total_count / sessions.page_size)}
            </span>
            <button
              onClick={() => setCurrentPage(currentPage + 1)}
              disabled={currentPage >= Math.ceil(sessions.total_count / sessions.page_size)}
              className="px-4 py-2 bg-secondary text-secondary-foreground rounded-md disabled:opacity-50"
            >
              Next
            </button>
          </div>
        )}
      </div>

      {/* Session Details */}
      {selectedSession && (
        <div className="bg-card p-6 rounded-lg shadow-lg">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className="text-xl font-bold text-contrast">Session Details</h3>
              <p className="text-muted-foreground">
                {selectedSession.research_id}
              </p>
            </div>
            <button
              onClick={() => handleDeleteSession(selectedSession.research_id)}
              className="px-4 py-2 bg-destructive text-destructive-foreground rounded-md font-medium hover:bg-destructive/90"
            >
              Delete Session
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold text-contrast mb-2">Session Information</h4>
              <div className="space-y-2 text-sm">
                <div><span className="text-muted-foreground">Topic:</span> {selectedSession.topic}</div>
                <div><span className="text-muted-foreground">Status:</span> 
                  <span className={`ml-2 px-2 py-1 rounded-full text-xs ${getStatusColor(selectedSession.status)}`}>
                    {selectedSession.status}
                  </span>
                </div>
                <div><span className="text-muted-foreground">Progress:</span> {selectedSession.progress_percentage}%</div>
                <div><span className="text-muted-foreground">Sections:</span> {selectedSession.completed_sections}/{selectedSession.total_sections}</div>
                {selectedSession.research_type && (
                  <div><span className="text-muted-foreground">Type:</span> {selectedSession.research_type}</div>
                )}
              </div>
            </div>

            <div>
              <h4 className="font-semibold text-contrast mb-2">Timeline</h4>
              <div className="space-y-2 text-sm">
                <div><span className="text-muted-foreground">Created:</span> {new Date(selectedSession.created_at).toLocaleString()}</div>
                <div><span className="text-muted-foreground">Updated:</span> {new Date(selectedSession.updated_at).toLocaleString()}</div>
                <div><span className="text-muted-foreground">Duration:</span> 
                  {Math.round((new Date(selectedSession.updated_at).getTime() - new Date(selectedSession.created_at).getTime()) / 60000)} minutes
                </div>
              </div>
            </div>
          </div>

          {selectedSession.error_message && (
            <div className="mt-4 p-3 bg-destructive/10 border border-destructive text-destructive rounded-md">
              <strong>Error:</strong> {selectedSession.error_message}
            </div>
          )}

          {/* Action Buttons */}
          <div className="mt-6 flex space-x-4">
            {selectedSession.status === 'in_progress' && (
              <button className="bg-primary text-primary-foreground px-4 py-2 rounded-md font-medium hover:bg-primary/90">
                Resume Research
              </button>
            )}
            {selectedSession.status === 'completed' && (
              <button className="bg-primary text-primary-foreground px-4 py-2 rounded-md font-medium hover:bg-primary/90">
                View Results
              </button>
            )}
            <button className="bg-secondary text-secondary-foreground px-4 py-2 rounded-md font-medium hover:bg-accent">
              Export Data
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import ResearchForm from '../components/ResearchForm';
import AgentStepsPanel from '../components/AgentStepsPanel';
import FindingsPanel from '../components/FindingsPanel';
import ReportView from '../components/ReportView';
import { startResearch, getRunStatus } from '../services/api';
import '../styles/HomePage.css';

export default function HomePage() {
  const [currentRun, setCurrentRun] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [report, setReport] = useState(null);

  useEffect(() => {
    // Poll for status updates if research is in progress
    if (!currentRun || currentRun.status === 'completed' || currentRun.status === 'failed') {
      return;
    }

    const interval = setInterval(async () => {
      try {
        const status = await getRunStatus(currentRun.run_id);
        setCurrentRun(status);
        
        if (status.status === 'completed') {
          setIsLoading(false);
          // Parse report if available
          if (status.report) {
            setReport(status.report);
          }
        }
      } catch (err) {
        console.error('Error fetching status:', err);
      }
    }, 1000); // Poll every second

    return () => clearInterval(interval);
  }, [currentRun]);

  const handleStartResearch = async (topic) => {
    setIsLoading(true);
    setError(null);
    setReport(null);

    try {
      const result = await startResearch(topic);
      setCurrentRun(result);
      
      // If research completes immediately
      if (result.status === 'completed') {
        setIsLoading(false);
      }
    } catch (err) {
      setError(err.message);
      setIsLoading(false);
    }
  };

  return (
    <div className="home-page">
      <header className="page-header">
        <h1>Autonomous Research Agent</h1>
        <p>Research topics using AI-powered agents</p>
      </header>

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
          <button onClick={() => setError(null)}>Dismiss</button>
        </div>
      )}

      <div className="content-grid">
        <div className="sidebar">
          <ResearchForm onSubmit={handleStartResearch} isLoading={isLoading} />
        </div>

        <div className="main-content">
          <div className="panels-row">
            <AgentStepsPanel 
              steps={currentRun?.steps || []} 
              isLoading={isLoading} 
            />
            <FindingsPanel 
              findings={currentRun?.findings || []} 
            />
          </div>

          <div className="report-section">
            {report ? (
              <ReportView report={report} />
            ) : currentRun && currentRun.summary ? (
              <div className="summary-view">
                <h2>Research Summary</h2>
                <p>{currentRun.summary}</p>
              </div>
            ) : (
              <div className="empty-report">
                <p>Start a research to see the report here.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

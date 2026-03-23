import React, { useState, useEffect } from 'react';
import ReportView from '../components/ReportView';
import { listRuns, getRunStatus, getRunReport, getReportPdfUrl, deleteRun } from '../services/api';
import '../styles/HistoryPage.css';

export default function HistoryPage() {
  const [runs, setRuns] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedRun, setSelectedRun] = useState(null);
  const [selectedReport, setSelectedReport] = useState(null);
  const [selectedDetails, setSelectedDetails] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    const fetchRuns = async () => {
      try {
        const data = await listRuns();
        setRuns(data.runs || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchRuns();
    // Refresh every 5 seconds
    const interval = setInterval(fetchRuns, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleViewRun = async (runId) => {
    setActionLoading(true);
    setError(null);
    try {
      const details = await getRunStatus(runId);
      setSelectedRun(runId);
      setSelectedDetails(details);

      try {
        const report = await getRunReport(runId);
        setSelectedReport(report);
      } catch {
        setSelectedReport(details.report || null);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleDownloadPdf = (runId) => {
    const url = getReportPdfUrl(runId);
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  const handleDeleteRun = async (runId) => {
    const confirmed = window.confirm('Delete this run and its generated PDF?');
    if (!confirmed) return;

    setActionLoading(true);
    setError(null);
    try {
      await deleteRun(runId);
      const data = await listRuns();
      setRuns(data.runs || []);
      if (selectedRun === runId) {
        setSelectedRun(null);
        setSelectedDetails(null);
        setSelectedReport(null);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setActionLoading(false);
    }
  };

  if (isLoading) {
    return <div className="history-page"><p>Loading history...</p></div>;
  }

  if (error) {
    return (
      <div className="history-page error">
        <p>Error loading history: {error}</p>
      </div>
    );
  }

  return (
    <div className="history-page">
      <h1>Research History</h1>

      {runs.length === 0 ? (
        <p className="empty-state">No research runs yet.</p>
      ) : (
        <div className="runs-table">
          <table>
            <thead>
              <tr>
                <th>Topic</th>
                <th>Status</th>
                <th>Created</th>
                <th>Completed</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((run) => (
                <tr key={run.run_id} className={`status-${run.status}`}>
                  <td>{run.topic}</td>
                  <td>
                    <span className={`status-badge status-${run.status}`}>
                      {run.status}
                    </span>
                  </td>
                  <td>{new Date(run.created_at).toLocaleString()}</td>
                  <td>
                    {run.completed_at
                      ? new Date(run.completed_at).toLocaleString()
                      : '-'}
                  </td>
                  <td>
                    <div className="actions-cell">
                      <button
                        onClick={() => handleViewRun(run.run_id)}
                        disabled={actionLoading}
                        className="action-button"
                      >
                        View
                      </button>
                      <button
                        onClick={() => handleDownloadPdf(run.run_id)}
                        disabled={actionLoading || run.status !== 'completed'}
                        className="action-button"
                      >
                        PDF
                      </button>
                      <button
                        onClick={() => handleDeleteRun(run.run_id)}
                        disabled={actionLoading || run.status === 'running' || run.status === 'pending'}
                        className="action-button danger"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {selectedRun && (
        <div className="selected-run-panel">
          <h2>Run Details</h2>
          {selectedDetails && (
            <div className="run-meta">
              <p><strong>Run ID:</strong> {selectedRun}</p>
              <p><strong>Status:</strong> {selectedDetails.status}</p>
              {selectedDetails.error && <p><strong>Error:</strong> {selectedDetails.error}</p>}
            </div>
          )}
          {selectedReport ? (
            <ReportView report={selectedReport} runId={selectedRun} />
          ) : (
            <p className="empty-state">No report available for this run yet.</p>
          )}
        </div>
      )}
    </div>
  );
}

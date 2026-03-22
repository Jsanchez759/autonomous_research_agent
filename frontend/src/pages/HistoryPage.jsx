import React, { useState, useEffect } from 'react';
import { listRuns } from '../services/api';
import '../styles/HistoryPage.css';

export default function HistoryPage() {
  const [runs, setRuns] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

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
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

import React from 'react';
import '../styles/ReportView.css';

export default function ReportView({ report }) {
  if (!report) {
    return (
      <div className="report-view empty">
        <p>No report available. Start a research to generate one.</p>
      </div>
    );
  }

  return (
    <div className="report-view">
      <div className="report-header">
        <h1>{report.topic}</h1>
        <p className="report-date">
          Generated: {new Date(report.generated_at).toLocaleString()}
        </p>
      </div>

      <section className="report-section">
        <h2>Summary</h2>
        <p>{report.summary}</p>
      </section>

      {report.findings && report.findings.length > 0 && (
        <section className="report-section">
          <h2>Findings</h2>
          <ul className="findings-list">
            {report.findings.map((finding, index) => (
              <li key={index}>
                <strong>{finding.title}:</strong> {finding.content}
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="report-section">
        <h2>Conclusion</h2>
        <p>{report.conclusion}</p>
      </section>

      <div className="report-actions">
        <button onClick={() => window.print()} className="print-button">
          Print Report
        </button>
        <button onClick={() => downloadReport(report)} className="download-button">
          Download as JSON
        </button>
      </div>
    </div>
  );
}

function downloadReport(report) {
  const dataStr = JSON.stringify(report, null, 2);
  const dataBlob = new Blob([dataStr], { type: 'application/json' });
  const url = URL.createObjectURL(dataBlob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `report-${report.topic.replace(/\s+/g, '-')}.json`;
  link.click();
  URL.revokeObjectURL(url);
}

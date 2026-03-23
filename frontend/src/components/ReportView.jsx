import React from 'react';
import { getReportPdfUrl } from '../services/api';
import MarkdownContent from './MarkdownContent';
import '../styles/ReportView.css';

export default function ReportView({ report, runId }) {
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
        <MarkdownContent content={report.summary} />
      </section>

      {report.findings && report.findings.length > 0 && (
        <section className="report-section">
          <h2>Insights</h2>
          <ul className="findings-list">
            {report.findings.map((finding, index) => (
              <li key={index}>
                <strong>{finding.title}</strong>
                <MarkdownContent content={finding.content} />
              </li>
            ))}
          </ul>
        </section>
      )}

      <div className="report-actions">
        <button onClick={() => window.print()} className="print-button">
          Print Report
        </button>
        <button
          onClick={() => downloadPdf(runId)}
          className="download-button"
          disabled={!runId}
        >
          Download PDF
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

function downloadPdf(runId) {
  if (!runId) {
    return;
  }
  const url = getReportPdfUrl(runId);
  window.open(url, '_blank', 'noopener,noreferrer');
}

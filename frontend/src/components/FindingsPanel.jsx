import React from 'react';
import MarkdownContent from './MarkdownContent';
import '../styles/FindingsPanel.css';

export default function FindingsPanel({ findings }) {
  return (
    <div className="findings-panel">
      <h2>Key Findings</h2>
      
      {findings.length === 0 ? (
        <p className="empty-state">No findings yet.</p>
      ) : (
        <div className="findings-list">
          {findings.map((finding, index) => (
            <div key={index} className="finding-card">
              <h3>{finding.title}</h3>
              <MarkdownContent content={finding.content} />
              {finding.source && (
                <div className="finding-source">
                  Source: <a href={finding.source} target="_blank" rel="noopener noreferrer">
                    {finding.source}
                  </a>
                </div>
              )}
              <div className="finding-confidence">
                Confidence: {(finding.confidence * 100).toFixed(0)}%
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

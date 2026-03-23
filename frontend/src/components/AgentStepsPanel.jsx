import React from 'react';
import MarkdownContent from './MarkdownContent';
import '../styles/AgentStepsPanel.css';

export default function AgentStepsPanel({ steps, isLoading }) {
  return (
    <div className="steps-panel">
      <h2>Agent Steps</h2>
      
      {steps.length === 0 ? (
        <p className="empty-state">
          {isLoading ? 'Running research...' : 'No steps yet. Start a research to see the agent in action.'}
        </p>
      ) : (
        <div className="steps-list">
          {steps.map((step, index) => (
            <div key={index} className={`step step-${step.status}`}>
              <div className="step-header">
                <span className="step-number">Step {step.step_number}</span>
                <span className={`step-status status-${step.status}`}>
                  {step.status}
                </span>
              </div>
              <div className="step-action">{step.action}</div>
              <div className="step-message">
                <MarkdownContent content={step.message} />
              </div>
              <div className="step-timestamp">
                {new Date(step.timestamp).toLocaleTimeString()}
              </div>
            </div>
          ))}
        </div>
      )}

      {isLoading && (
        <div className="loading-indicator">
          <div className="spinner"></div>
          <p>Processing...</p>
        </div>
      )}
    </div>
  );
}

import React, { useState } from 'react';
import '../styles/ResearchForm.css';

export default function ResearchForm({ onSubmit, isLoading }) {
  const [topic, setTopic] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (topic.trim()) {
      onSubmit(topic);
      setTopic('');
    }
  };

  return (
    <form className="research-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="topic">Research Topic</label>
        <input
          id="topic"
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter a topic to research..."
          disabled={isLoading}
          className="topic-input"
        />
      </div>

      <button
        type="submit"
        disabled={isLoading || !topic.trim()}
        className="submit-button"
      >
        {isLoading ? 'Researching...' : 'Start Research'}
      </button>
    </form>
  );
}

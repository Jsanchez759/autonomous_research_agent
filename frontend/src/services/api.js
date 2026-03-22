// Frontend API service

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

/**
 * Start a new research task
 */
export const startResearch = async (topic) => {
  const response = await fetch(`${API_BASE_URL}/research/start`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      topic,
      max_iterations: 5,
    }),
  });
  
  if (!response.ok) {
    throw new Error(`Research start failed: ${response.statusText}`);
  }
  
  return response.json();
};

/**
 * Get research run status
 */
export const getRunStatus = async (runId) => {
  const response = await fetch(`${API_BASE_URL}/research/run/${runId}`);
  
  if (!response.ok) {
    throw new Error(`Failed to get run status: ${response.statusText}`);
  }
  
  return response.json();
};

/**
 * Get list of all runs
 */
export const listRuns = async () => {
  const response = await fetch(`${API_BASE_URL}/runs/`);
  
  if (!response.ok) {
    throw new Error(`Failed to list runs: ${response.statusText}`);
  }
  
  return response.json();
};

/**
 * Health check
 */
export const healthCheck = async () => {
  const response = await fetch(`${API_BASE_URL}/health`);
  
  if (!response.ok) {
    throw new Error('Health check failed');
  }
  
  return response.json();
};

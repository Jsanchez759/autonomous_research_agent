import React, { useState } from 'react';
import HomePage from './pages/HomePage';
import HistoryPage from './pages/HistoryPage';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('home');

  return (
    <div className="app">
      <nav className="navigation">
        <div className="nav-brand">🔬 Research Agent</div>
        <div className="nav-links">
          <button
            className={`nav-link ${currentPage === 'home' ? 'active' : ''}`}
            onClick={() => setCurrentPage('home')}
          >
            Research
          </button>
          <button
            className={`nav-link ${currentPage === 'history' ? 'active' : ''}`}
            onClick={() => setCurrentPage('history')}
          >
            History
          </button>
        </div>
      </nav>

      <main className="page-container">
        {currentPage === 'home' && <HomePage />}
        {currentPage === 'history' && <HistoryPage />}
      </main>

      <footer className="app-footer">
        <p>Autonomous Research Agent v0.1.0</p>
      </footer>
    </div>
  );
}

export default App;

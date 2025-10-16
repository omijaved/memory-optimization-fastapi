import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import PerformanceMonitor from './components/PerformanceMonitor';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>Memory & Concurrency Optimization Dashboard</h1>
          <p>Real-time monitoring of memory leaks, race conditions, and GIL limitations</p>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/performance" element={<PerformanceMonitor />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
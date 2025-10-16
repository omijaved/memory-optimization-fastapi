import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const API_BASE_URL = 'http://localhost:8000';

const Dashboard = () => {
  const [fibonacciResult, setFibonacciResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [nValue, setNValue] = useState(40);
  const [useOptimized, setUseOptimized] = useState(false);
  const [performanceData, setPerformanceData] = useState({
    labels: [],
    datasets: [
      {
        label: 'Execution Time (ms)',
        data: [],
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
      },
      {
        label: 'Memory Usage (MB)',
        data: [],
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
      },
    ],
  });
  const [stats, setStats] = useState(null);
  const [testResults, setTestResults] = useState([]);

  const calculateFibonacci = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const endpoint = useOptimized ? '/fibonacci-optimized' : '/fibonacci';
      const response = await axios.post(`${API_BASE_URL}${endpoint}`, {
        n: nValue,
        use_optimized: useOptimized
      });
      
      const result = response.data;
      setFibonacciResult(result);
      
      // Update performance chart
      setPerformanceData(prev => {
        const newLabels = [...prev.labels, new Date().toLocaleTimeString()];
        const newTimeData = [...prev.datasets[0].data, result.execution_time * 1000];
        const newMemoryData = [...prev.datasets[1].data, result.memory_usage];
        
        // Keep only last 20 data points
        if (newLabels.length > 20) {
          newLabels.shift();
          newTimeData.shift();
          newMemoryData.shift();
        }
        
        return {
          labels: newLabels,
          datasets: [
            {
              ...prev.datasets[0],
              data: newTimeData,
            },
            {
              ...prev.datasets[1],
              data: newMemoryData,
            },
          ],
        };
      });
      
      // Add to test results
      setTestResults(prev => [
        ...prev.slice(-9), // Keep only last 9 results
        {
          timestamp: new Date().toISOString(),
          result: result.result,
          executionTime: result.execution_time,
          memoryUsage: result.memory_usage,
          success: result.success,
          error: result.error_message
        }
      ]);
      
    } catch (err) {
      setError('Error calculating Fibonacci: ' + err.message);
      setFibonacciResult(null);
    } finally {
      setLoading(false);
    }
  };

  const getStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/stats`);
      setStats(response.data);
    } catch (err) {
      console.error('Error getting stats:', err);
    }
  };

  const clearMemory = async () => {
    try {
      await axios.post(`${API_BASE_URL}/clear-memory`);
      alert('Memory cleared successfully');
    } catch (err) {
      alert('Error clearing memory: ' + err.message);
    }
  };

  const resetCounter = async () => {
    try {
      await axios.post(`${API_BASE_URL}/reset-counter`);
      alert('Counter reset successfully');
    } catch (err) {
      alert('Error resetting counter: ' + err.message);
    }
  };

  const triggerGC = async () => {
    try {
      await axios.post(`${API_BASE_URL}/trigger-gc`);
      alert('Garbage collection triggered');
    } catch (err) {
      alert('Error triggering GC: ' + err.message);
    }
  };

  // Auto-refresh stats every 5 seconds
  useEffect(() => {
    const statsInterval = setInterval(getStats, 5000);
    return () => clearInterval(statsInterval);
  }, []);

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Performance Metrics',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  return (
    <div className="dashboard">
      <div className="controls">
        <h2>Fibonacci Calculator</h2>
        <div className="input-group">
          <label>
            n value:
            <input
              type="number"
              value={nValue}
              onChange={(e) => setNValue(parseInt(e.target.value) || 40)}
              min="1"
              max="50"
            />
          </label>
          <label>
            <input
              type="checkbox"
              checked={useOptimized}
              onChange={(e) => setUseOptimized(e.target.checked)}
            />
            Use Optimized Version
          </label>
        </div>
        <div className="button-group">
          <button
            onClick={calculateFibonacci}
            disabled={loading}
            className={useOptimized ? 'optimized' : ''}
          >
            {loading ? 'Calculating...' : 'Calculate Fibonacci'}
          </button>
          <button onClick={clearMemory}>Clear Memory</button>
          <button onClick={resetCounter}>Reset Counter</button>
          <button onClick={triggerGC}>Trigger GC</button>
        </div>
      </div>

      {error && <div className="error">{error}</div>}

      {fibonacciResult && (
        <div className="result">
          <h3>Result</h3>
          <p><strong>Fibonacci({nValue}) =</strong> {fibonacciResult.result}</p>
          <p><strong>Execution Time:</strong> {fibonacciResult.execution_time.toFixed(4)} seconds</p>
          <p><strong>Memory Usage:</strong> {fibonacciResult.memory_usage.toFixed(2)} MB</p>
          <p><strong>Counter Value:</strong> {fibonacciResult.counter_value}</p>
          <p><strong>Threads:</strong> {fibonacciResult.thread_count}</p>
          <p><strong>Processes:</strong> {fibonacciResult.process_count}</p>
          <p><strong>Success:</strong> {fibonacciResult.success ? 'Yes' : 'No'}</p>
          {fibonacciResult.error_message && (
            <p><strong>Error:</strong> {fibonacciResult.error_message}</p>
          )}
        </div>
      )}

      <div className="chart-container">
        <h3>Performance Metrics</h3>
        <Line options={chartOptions} data={performanceData} />
      </div>

      <div className="stats">
        <h3>System Statistics</h3>
        {stats ? (
          <div className="stats-grid">
            <div className="stat-item">
              <strong>GC Count:</strong> {stats.gc_count.join(', ')}
            </div>
            <div className="stat-item">
              <strong>Memory Leak Size:</strong> {stats.memory_leak_size} objects
            </div>
            <div className="stat-item">
              <strong>Active Threads:</strong> {stats.active_threads}
            </div>
            <div className="stat-item">
              <strong>CPU Count:</strong> {stats.cpu_count}
            </div>
            <div className="stat-item">
              <strong>Switch Interval:</strong> {stats.switch_interval}s
            </div>
            <div className="stat-item">
              <strong>Tracemalloc:</strong> {stats.tracemalloc_stats}
            </div>
          </div>
        ) : (
          <p>Loading stats...</p>
        )}
      </div>

      <div className="test-results">
        <h3>Recent Test Results</h3>
        <div className="results-table">
          <table>
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Result</th>
                <th>Time (s)</th>
                <th>Memory (MB)</th>
                <th>Success</th>
              </tr>
            </thead>
            <tbody>
              {testResults.map((result, index) => (
                <tr key={index} className={result.success ? '' : 'error'}>
                  <td>{new Date(result.timestamp).toLocaleTimeString()}</td>
                  <td>{result.result}</td>
                  <td>{result.executionTime.toFixed(4)}</td>
                  <td>{result.memoryUsage.toFixed(2)}</td>
                  <td>{result.success ? '✓' : '✗'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
import React, { useState, useEffect } from 'react';
import axios from 'axios';
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
import { Line } from 'react-chartjs-2';

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

const PerformanceMonitor = () => {
  const [systemStats, setSystemStats] = useState(null);
  const [cpuData, setCpuData] = useState({
    labels: [],
    datasets: [{
      label: 'CPU Usage (%)',
      data: [],
      borderColor: 'rgb(54, 162, 235)',
      backgroundColor: 'rgba(54, 162, 235, 0.5)',
    }]
  });
  const [memoryData, setMemoryData] = useState({
    labels: [],
    datasets: [{
      label: 'Memory Usage (MB)',
      data: [],
      borderColor: 'rgb(255, 99, 132)',
      backgroundColor: 'rgba(255, 99, 132, 0.5)',
    }]
  });
  const [testLog, setTestLog] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [testConfig, setTestConfig] = useState({
    numRequests: 100,
    concurrent: 10,
    useOptimized: false
  });

  const fetchSystemStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/stats`);
      setSystemStats(response.data);
      return response.data;
    } catch (error) {
      console.error('Error fetching system stats:', error);
      return null;
    }
  };

  const runLoadTest = async () => {
    if (isRunning) return;
    
    setIsRunning(true);
    const startTime = Date.now();
    const log = [];
    
    try {
      log.push(`Starting load test at ${new Date().toISOString()}`);
      log.push(`Config: ${testConfig.numRequests} requests, ${testConfig.concurrent} concurrent`);
      
      const endpoint = testConfig.useOptimized ? '/fibonacci-optimized' : '/fibonacci';
      const url = `${API_BASE_URL}${endpoint}`;
      
      const promises = [];
      const results = [];
      
      // Create concurrent requests
      for (let i = 0; i < testConfig.concurrent; i++) {
        const batchPromises = [];
        for (let j = 0; j < Math.ceil(testConfig.numRequests / testConfig.concurrent); j++) {
          const promise = axios.post(url, { n: 40, use_optimized: testConfig.useOptimized })
            .then(response => {
              results.push({ success: true, data: response.data, time: Date.now() - startTime });
              return response.data;
            })
            .catch(error => {
              results.push({ success: false, error: error.message, time: Date.now() - startTime });
              throw error;
            });
          batchPromises.push(promise);
        }
        promises.push(...batchPromises);
      }
      
      // Execute all requests
      await Promise.allSettled(promises);
      
      const endTime = Date.now();
      const totalTime = (endTime - startTime) / 1000;
      
      const successful = results.filter(r => r.success).length;
      const failed = results.filter(r => !r.success).length;
      const avgTime = results.reduce((sum, r) => sum + r.time, 0) / results.length / 1000;
      
      log.push(`Load test completed in ${totalTime.toFixed(2)} seconds`);
      log.push(`Successful: ${successful}, Failed: ${failed}`);
      log.push(`Average time per request: ${avgTime.toFixed(4)}s`);
      log.push(`Requests per second: ${(testConfig.numRequests / totalTime).toFixed(2)}`);
      
      // Log individual failures
      results.filter(r => !r.success).forEach((result, index) => {
        log.push(`Failure ${index + 1}: ${result.error}`);
      });
      
    } catch (error) {
      log.push(`Load test failed: ${error.message}`);
    } finally {
      setIsRunning(false);
      setTestLog(prev => [...prev, ...log]);
      
      // Auto-scroll to bottom
      setTimeout(() => {
        const logElement = document.querySelector('.test-log');
        if (logElement) {
          logElement.scrollTop = logElement.scrollHeight;
        }
      }, 100);
    }
  };

  // Auto-refresh system stats
  useEffect(() => {
    const interval = setInterval(fetchSystemStats, 2000);
    return () => clearInterval(interval);
  }, []);

  // Update charts when stats change
  useEffect(() => {
    if (systemStats) {
      const now = new Date().toLocaleTimeString();
      
      // Update CPU chart
      setCpuData(prev => {
        const newLabels = [...prev.labels, now];
        const newData = [...prev.datasets[0].data, systemStats.cpu_percent || 0];
        
        if (newLabels.length > 20) {
          newLabels.shift();
          newData.shift();
        }
        
        return {
          labels: newLabels,
          datasets: [{
            ...prev.datasets[0],
            data: newData
          }]
        };
      });
      
      // Update memory chart
      setMemoryData(prev => {
        const newLabels = [...prev.labels, now];
        const memoryUsage = (systemStats.memory_leak_size * 8) || 0; // Rough estimate
        const newData = [...prev.datasets[0].data, memoryUsage];
        
        if (newLabels.length > 20) {
          newLabels.shift();
          newData.shift();
        }
        
        return {
          labels: newLabels,
          datasets: [{
            ...prev.datasets[0],
            data: newData
          }]
        };
      });
    }
  }, [systemStats]);

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Real-time Performance',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  return (
    <div className="performance-monitor">
      <h2>Performance Monitor</h2>
      
      <div className="test-controls">
        <h3>Load Test Configuration</h3>
        <div className="config-grid">
          <div>
            <label>Number of Requests:</label>
            <input
              type="number"
              value={testConfig.numRequests}
              onChange={(e) => setTestConfig(prev => ({ ...prev, numRequests: parseInt(e.target.value) || 100 }))}
              min="1"
              max="10000"
            />
          </div>
          <div>
            <label>Concurrent Requests:</label>
            <input
              type="number"
              value={testConfig.concurrent}
              onChange={(e) => setTestConfig(prev => ({ ...prev, concurrent: parseInt(e.target.value) || 10 }))}
              min="1"
              max="100"
            />
          </div>
          <div>
            <label>
              <input
                type="checkbox"
                checked={testConfig.useOptimized}
                onChange={(e) => setTestConfig(prev => ({ ...prev, useOptimized: e.target.checked }))}
              />
              Use Optimized Version
            </label>
          </div>
        </div>
        <button
          onClick={runLoadTest}
          disabled={isRunning}
          className="run-test-button"
        >
          {isRunning ? 'Running Test...' : 'Run Load Test'}
        </button>
      </div>

      <div className="charts-container">
        <div className="chart">
          <h3>CPU Usage</h3>
          <Line options={chartOptions} data={cpuData} />
        </div>
        <div className="chart">
          <h3>Memory Usage</h3>
          <Line options={chartOptions} data={memoryData} />
        </div>
      </div>

      <div className="system-stats">
        <h3>System Statistics</h3>
        {systemStats ? (
          <div className="stats-grid">
            <div className="stat-item">
              <strong>GC Count:</strong> {systemStats.gc_count.join(', ')}
            </div>
            <div className="stat-item">
              <strong>Memory Leak Size:</strong> {systemStats.memory_leak_size} objects
            </div>
            <div className="stat-item">
              <strong>Active Threads:</strong> {systemStats.active_threads}
            </div>
            <div className="stat-item">
              <strong>CPU Count:</strong> {systemStats.cpu_count}
            </div>
            <div className="stat-item">
              <strong>Switch Interval:</strong> {systemStats.switch_interval}s
            </div>
            <div className="stat-item">
              <strong>Tracemalloc:</strong> {systemStats.tracemalloc_stats}
            </div>
            <div className="stat-item">
              <strong>CPU Usage:</strong> {systemStats.cpu_percent}%
            </div>
            <div className="stat-item">
              <strong>Memory Usage:</strong> {systemStats.memory_percent}%
            </div>
          </div>
        ) : (
          <p>Loading system stats...</p>
        )}
      </div>

      <div className="test-log-container">
        <h3>Test Log</h3>
        <div className="test-log">
          {testLog.map((log, index) => (
            <div key={index} className={log.startsWith('Failure') ? 'error' : ''}>
              {log}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PerformanceMonitor;
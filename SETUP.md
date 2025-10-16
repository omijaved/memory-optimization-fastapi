# Memory & Concurrency Optimization Project - Setup Guide

## Project Overview
This project demonstrates memory leaks, race conditions, and GIL limitations in Python, along with their optimization techniques. It includes a FastAPI backend and React frontend for real-time monitoring and testing.

## Quick Start

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm start
```

### 3. Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Required Artifacts for Demonstration

### 1. System Metrics Screenshots
**Requirements:**
- htop/top showing memory growth to 2GB+ then stabilizing under 150MB
- CPU spikes from 400% to 800%
- Hostname visible
- Desktop background visible
- Physical note with date visible

**How to capture:**
```bash
# Monitor memory and CPU
htop
# or
top
```

### 2. Diagnostic Logs
**Collect these logs during execution:**

#### Garbage Collection Count
```python
import gc
gc.get_count()
```

#### Tracemalloc Snapshot
```python
import tracemalloc
import time

# Start tracing
tracemalloc.start()

# Take snapshots
snapshot1 = tracemalloc.take_snapshot()
# Run your application...
snapshot2 = tracemalloc.take_snapshot()

# Compare
top_stats = snapshot2.compare_to(snapshot1, 'lineno')
for stat in top_stats[:10]:
    print(stat)
```

#### System Information
```python
import sys
import threading
import multiprocessing

print(f"Python path: {sys.path}")
print(f"Switch interval: {sys.getswitchinterval()}")
print(f"Active threads: {threading.active_count()}")
print(f"CPU count: {multiprocessing.cpu_count()}")
```

### 3. GDB Analysis
**Requirements:** GDB screenshot showing 4+ threads/processes

**How to capture:**
```bash
# Find the process ID
ps aux | grep uvicorn

# Attach GDB
gdb -p <pid>

# Inside GDB
info threads
thread apply all bt
```

### 4. Performance Testing Logs
**Run the load test:**
```bash
cd test
python load_test.py
```

**Expected output:**
- 5,000 requests with race condition failures
- Memory growth to 2GB+
- CPU usage around 400% (ThreadPoolExecutor)

### 5. Fixed Version Testing
**After implementing fixes:**
```bash
python load_test.py
```
**Expected output:**
- 10,000 requests without failures
- Memory stabilized under 150MB
- CPU usage around 800% (ProcessPoolExecutor)

## Demonstration Workflow

### Phase 1: Demonstrate Problems
1. Start the backend and frontend
2. Run `python test/load_test.py` to show:
   - Memory leaks growing to 2GB+
   - Race conditions causing inconsistent counter values
   - GIL limitations limiting CPU usage to ~400%
3. Take screenshots of htop showing memory growth
4. Show GDB analysis with limited threads

### Phase 2: Implement Fixes
1. **Memory Leak Fix:**
   - Use `weakref.WeakValueDictionary` for caches
   - Implement regular `gc.collect()` calls
   - Use `tracemalloc` for monitoring

2. **Race Condition Fix:**
   - Replace shared counter with `threading.Lock`
   - Use `asyncio.Lock` for async operations
   - Implement proper synchronization

3. **GIL Limitation Fix:**
   - Replace `ThreadPoolExecutor` with `ProcessPoolExecutor`
   - Use multiprocessing for CPU-bound tasks
   - Achieve 800% CPU usage on multi-core systems

### Phase 3: Verify Fixes
1. Run `python test/load_test.py` again
2. Show:
   - Memory stabilized under 150MB
   - No race condition failures
   - CPU usage at 800%
3. Take screenshots showing system stability

## Frontend Features

### Dashboard
- Real-time Fibonacci calculation
- Performance metrics charts
- System statistics display
- Test results table

### Performance Monitor
- Load testing interface
- Real-time CPU and memory charts
- Test configuration options
- Detailed test logs

## Backend API Endpoints

### Fibonacci Calculation
- `POST /fibonacci` - Basic version (with issues)
- `POST /fibonacci-optimized` - Fixed version

### System Management
- `GET /stats` - Current system statistics
- `POST /clear-memory` - Clear memory leak
- `POST /reset-counter` - Reset shared counter
- `POST /trigger-gc` - Trigger garbage collection

## Performance Comparison

Create a spreadsheet comparing:
- ThreadPoolExecutor vs ProcessPoolExecutor
- Memory usage before/after fixes
- CPU utilization improvements
- Request success rates

### Sample Spreadsheet Structure:
| Metric | ThreadPoolExecutor | ProcessPoolExecutor | Improvement |
|--------|-------------------|---------------------|-------------|
| CPU Usage | ~400% | ~800% | +100% |
| Memory Peak | 2GB+ | 150MB | -92.5% |
| Success Rate | 85% | 100% | +15% |
| Avg Response Time | 0.5s | 0.2s | -60% |

## Physical Setup Documentation
**Requirements:** Photo showing:
- Laptop with terminal open
- Browser with the application
- Physical note with current date
- Desktop environment visible

**How to take:**
1. Set up your development environment
2. Have the backend running in a terminal
3. Open the frontend in a browser
4. Place a physical note with the current date on your desk
5. Take a photo showing the entire setup

## Troubleshooting

### Common Issues

1. **Backend won't start:**
   ```bash
   # Check if port 8000 is available
   netstat -tlnp | grep 8000
   # Kill existing process
   sudo kill -9 <pid>
   ```

2. **Frontend can't connect to backend:**
   - Ensure backend is running on `0.0.0.0:8000`
   - Check CORS settings in FastAPI
   - Verify API base URL in frontend

3. **Load test fails:**
   - Ensure backend is running before starting test
   - Check network connectivity
   - Verify API endpoints are accessible

### Performance Monitoring

```bash
# Monitor system resources
htop
# Monitor memory specifically
free -h
# Monitor network
netstat -t
```

## Expected Results Summary

| Metric | Initial State | After Fixes | Improvement |
|--------|---------------|-------------|-------------|
| Memory Usage | 2GB+ | <150MB | -92.5% |
| CPU Utilization | ~400% | ~800% | +100% |
| Race Conditions | Present | Resolved | 100% Fixed |
| Success Rate | ~85% | 100% | +15% |
| Response Time | ~0.5s | ~0.2s | -60% |

## Next Steps

1. Run the application and collect initial metrics
2. Document all required artifacts
3. Implement the fixes as described
4. Verify improvements and update documentation
5. Create final demonstration video

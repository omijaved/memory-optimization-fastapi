# Full-Stack Memory and Concurrency Optimization Project

## Project Overview
A FastAPI backend integrated with React frontend for demonstrating memory leaks, race conditions, GIL limitations, and their optimization through various techniques.

## Features
- **Backend (FastAPI)**: Intentional memory leak and race condition simulation
- **Frontend (React)**: Real-time dashboard for processing and displaying results
- **CPU-bound operations**: Recursive Fibonacci sequences with memoization
- **Performance testing**: 5,000+ requests with Apache Bench
- **Optimization**: Memory leak fixes, race condition resolution, GIL bypass

## Project Structure
```
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # Main FastAPI application
│   │   ├── models.py       # Pydantic models
│   │   ├── services.py     # Business logic with intentional issues
│   │   └── utils.py        # Utility functions
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── Dockerfile
└── test/                   # Testing and benchmarking scripts
    ├── load_test.py
    └── analyze_results.py
```

## Getting Started

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Running Tests
```bash
# Start backend first
python test/load_test.py
```

## Performance Metrics to Collect

### Memory and CPU
- htop/top screenshots showing:
  - Memory growth to 2GB+ then stabilizing under 150MB
  - CPU spikes from 400% to 800%
  - Hostname, desktop background, physical note with date visible

### Logs and Diagnostics
- `gc.get_count()` output
- `tracemalloc` snapshot diff (.txt)
- `sys.getswitchinterval()`
- `threading.active_count()`
- `multiprocessing.cpu_count()`
- Python path: `python -c "import sys; print(sys.path)"`

### GDB Analysis
- GDB screenshot with `gdb -p <pid>` and `info threads` showing 4+ threads/processes

### Performance Comparison
- Spreadsheet comparing ProcessPoolExecutor vs ThreadPoolExecutor timings (5 runs each)

## Expected Results
1. **Initial State**: Memory leaks causing growth to 2GB+, race conditions causing inconsistent results
2. **After Fixes**: Memory stabilized under 150MB, race conditions resolved, CPU usage optimized
3. **Performance**: 10,000 successful requests without failures

## Artifacts Required
- Video/screenshots of system metrics during execution
- Logs from all diagnostic tools
- Full log of loop runs with timestamps
- Photos of physical setup
- Frontend UI screenshots during execution
- Performance comparison spreadsheet
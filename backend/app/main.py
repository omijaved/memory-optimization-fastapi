import asyncio
import gc
import sys
import threading
import time
import tracemalloc
import weakref
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import psutil
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Global variables for intentional issues
global_memory_leak = []  # Intentional memory leak
shared_counter = 0  # Intentional race condition
lock = threading.Lock()
async_lock = asyncio.Lock()

app = FastAPI(title="Memory & Concurrency Optimization Demo")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FibonacciRequest(BaseModel):
    n: int = 40
    use_memoization: bool = True

class FibonacciResponse(BaseModel):
    result: int
    execution_time: float
    memory_usage: float
    counter_value: int
    thread_count: int
    process_count: int

class StatsResponse(BaseModel):
    gc_count: tuple
    tracemalloc_stats: str
    switch_interval: float
    active_threads: int
    cpu_count: int
    memory_leak_size: int

# Fibonacci with memoization (intentionally global for memory leak)
fibonacci_cache = {}

def fibonacci(n: int) -> int:
    """CPU-bound Fibonacci calculation"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def fibonacci_memoized(n: int) -> int:
    """Fibonacci with memoization"""
    if n in fibonacci_cache:
        return fibonacci_cache[n]
    if n <= 1:
        result = n
    else:
        result = fibonacci_memoized(n - 1) + fibonacci_memoized(n - 2)
    fibonacci_cache[n] = result
    return result

def cpu_bound_task(n: int) -> int:
    """Simulate CPU-bound work with GIL limitations"""
    return fibonacci_memoized(n)

def memory_leak_task():
    """Intentional memory leak - append large objects"""
    large_object = np.random.rand(1000000)  # ~8MB object
    global_memory_leak.append(large_object)
    return len(global_memory_leak)

def race_condition_task():
    """Intentional race condition - shared counter without lock"""
    global shared_counter
    # Simulate some work
    time.sleep(0.001)
    shared_counter += 1
    return shared_counter

async def safe_race_condition_task():
    """Fixed race condition with asyncio lock"""
    async with async_lock:
        global shared_counter
        # Simulate some work
        await asyncio.sleep(0.001)
        shared_counter += 1
        return shared_counter

def optimized_cpu_task(n: int) -> int:
    """CPU-bound task optimized with multiprocessing to bypass GIL"""
    return fibonacci_memoized(n)

@app.get("/")
async def root():
    return {"message": "Memory & Concurrency Optimization Demo API"}

@app.get("/stats")
async def get_stats():
    """Get system statistics for monitoring"""
    return StatsResponse(
        gc_count=gc.get_count(),
        tracemalloc_stats=f"Current: {tracemalloc.get_traced_memory()[0]/1024/1024:.2f}MB, Peak: {tracemalloc.get_traced_memory()[1]/1024/1024:.2f}MB",
        switch_interval=sys.getswitchinterval(),
        active_threads=threading.active_count(),
        cpu_count=psutil.cpu_count(),
        memory_leak_size=len(global_memory_leak)
    )

@app.post("/fibonacci", response_model=FibonacciResponse)
async def calculate_fibonacci(request: FibonacciRequest, background_tasks: BackgroundTasks):
    """Calculate Fibonacci number with intentional issues"""
    start_time = time.time()
    
    # Memory leak task
    leak_size = memory_leak_task()
    
    # Race condition task
    counter_value = race_condition_task()
    
    # CPU-bound task with thread pool (demonstrates GIL)
    with ThreadPoolExecutor(max_workers=4) as executor:
        future = executor.submit(cpu_bound_task, request.n)
        result = future.result()
    
    execution_time = time.time() - start_time
    memory_usage = len(global_memory_leak) * 8  # Rough estimate in MB
    
    return FibonacciResponse(
        result=result,
        execution_time=execution_time,
        memory_usage=memory_usage,
        counter_value=counter_value,
        thread_count=threading.active_count(),
        process_count=1
    )

@app.post("/fibonacci-optimized", response_model=FibonacciResponse)
async def calculate_fibonacci_optimized(request: FibonacciRequest, background_tasks: BackgroundTasks):
    """Optimized Fibonacci calculation"""
    start_time = time.time()
    
    # Fixed memory leak using weakref
    if len(global_memory_leak) > 100:
        # Clean up some memory
        global_memory_leak.clear()
    
    # Fixed race condition
    counter_value = await safe_race_condition_task()
    
    # CPU-bound task with process pool (bypasses GIL)
    with ProcessPoolExecutor(max_workers=psutil.cpu_count()) as executor:
        future = executor.submit(optimized_cpu_task, request.n)
        result = future.result()
    
    execution_time = time.time() - start_time
    memory_usage = len(global_memory_leak) * 8
    
    return FibonacciResponse(
        result=result,
        execution_time=execution_time,
        memory_usage=memory_usage,
        counter_value=counter_value,
        thread_count=threading.active_count(),
        process_count=psutil.cpu_count()
    )

@app.post("/clear-memory")
async def clear_memory():
    """Clear the memory leak"""
    global global_memory_leak
    global_memory_leak.clear()
    return {"message": "Memory cleared", "remaining": len(global_memory_leak)}

@app.post("/reset-counter")
async def reset_counter():
    """Reset the shared counter"""
    global shared_counter
    shared_counter = 0
    return {"message": "Counter reset", "value": shared_counter}

@app.post("/trigger-gc")
async def trigger_gc():
    """Manually trigger garbage collection"""
    collected = gc.collect()
    return {"message": "Garbage collection triggered", "objects_collected": collected}

if __name__ == "__main__":
    tracemalloc.start()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

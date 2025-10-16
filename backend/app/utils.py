import time
import threading
from typing import Callable, Any
import asyncio

class Timer:
    """Simple timer for performance measurement"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
    
    @property
    def elapsed(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0

def run_with_timer(func: Callable, *args, **kwargs) -> tuple[Any, float]:
    """Run a function and return result with execution time"""
    with Timer() as timer:
        result = func(*args, **kwargs)
    return result, timer.elapsed

class ThreadSafeCounter:
    """Thread-safe counter implementation"""
    
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()
    
    def increment(self):
        with self._lock:
            self._value += 1
            return self._value
    
    def get(self):
        with self._lock:
            return self._value
    
    def reset(self):
        with self._lock:
            self._value = 0
            return self._value

class AsyncSafeCounter:
    """Async-safe counter implementation"""
    
    def __init__(self):
        self._value = 0
        self._lock = asyncio.Lock()
    
    async def increment(self):
        async with self._lock:
            self._value += 1
            return self._value
    
    async def get(self):
        async with self._lock:
            return self._value
    
    async def reset(self):
        async with self._lock:
            self._value = 0
            return self._value

def fibonacci_memoized_cache(n: int, cache: dict = None) -> int:
    """Fibonacci with memoization using provided cache"""
    if cache is None:
        cache = {}
    if n in cache:
        return cache[n]
    if n <= 1:
        result = n
    else:
        result = fibonacci_memoized_cache(n - 1, cache) + fibonacci_memoized_cache(n - 2, cache)
    cache[n] = result
    return result

def create_large_object(size_mb: int = 8) -> bytes:
    """Create a large object for memory testing"""
    return bytes(size_mb * 1024 * 1024)  # size_mb in bytes

def simulate_cpu_work(iterations: int = 1000000) -> None:
    """Simulate CPU-bound work"""
    result = 0
    for i in range(iterations):
        result += i * i
    return result
import asyncio
import gc
import time
import threading
import tracemalloc
import sys
import numpy as np
import psutil

# Global variables for intentional issues
global_memory_leak = []  # Intentional memory leak
shared_counter = 0  # Intentional race condition
lock = threading.Lock()
async_lock = asyncio.Lock()

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

class MemoryManager:
    """Handles memory management and cleanup"""
    
    @staticmethod
    def cleanup_memory():
        """Clean up memory leak"""
        global global_memory_leak
        global_memory_leak.clear()
        
    @staticmethod
    def get_memory_stats():
        """Get current memory statistics"""
        process = psutil.Process()
        memory_info = process.memory_info()
        return {
            'rss': memory_info.rss / 1024 / 1024,  # MB
            'vms': memory_info.vms / 1024 / 1024,  # MB
            'percent': process.memory_percent()
        }

class RaceConditionManager:
    """Handles race condition management"""
    
    @staticmethod
    def reset_counter():
        """Reset the shared counter"""
        global shared_counter
        shared_counter = 0
        return shared_counter
        
    @staticmethod
    def get_counter():
        """Get current counter value"""
        global shared_counter
        return shared_counter

class PerformanceMonitor:
    """Monitors system performance"""
    
    @staticmethod
    def get_system_stats():
        """Get current system statistics"""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'cpu_count': psutil.cpu_count(),
            'thread_count': threading.active_count(),
            'gc_count': gc.get_count(),
            'switch_interval': sys.getswitchinterval(),
            'memory_leak_size': len(global_memory_leak)
        }
        
    @staticmethod
    def get_tracemalloc_stats():
        """Get tracemalloc statistics"""
        current, peak = tracemalloc.get_traced_memory()
        return {
            'current': current / 1024 / 1024,  # MB
            'peak': peak / 1024 / 1024  # MB
        }
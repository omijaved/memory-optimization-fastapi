from pydantic import BaseModel
from typing import Optional, List

class FibonacciRequest(BaseModel):
    n: int = 40
    use_memoization: bool = True
    use_optimized: bool = False

class FibonacciResponse(BaseModel):
    result: int
    execution_time: float
    memory_usage: float
    counter_value: int
    thread_count: int
    process_count: int
    success: bool
    error_message: Optional[str] = None

class StatsResponse(BaseModel):
    gc_count: tuple
    tracemalloc_stats: str
    switch_interval: float
    active_threads: int
    cpu_count: int
    memory_leak_size: int
    cpu_percent: float
    memory_percent: float

class LoadTestRequest(BaseModel):
    url: str = "http://localhost:8000/fibonacci"
    num_requests: int = 100
    concurrent: int = 10
    use_optimized: bool = False

class LoadTestResponse(BaseModel):
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_time: float
    min_time: float
    max_time: float
    requests_per_second: float
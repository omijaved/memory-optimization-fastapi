#!/usr/bin/env python3
"""
Load testing script for Memory & Concurrency Optimization Demo

This script performs load testing on the FastAPI backend to demonstrate:
1. Memory leaks and their optimization
2. Race conditions and their resolution
3. GIL limitations and multiprocessing optimization
"""

import asyncio
import csv
import gc
import json
import os
import sys
import time
import tracemalloc
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import List, Dict, Any
import requests
import statistics
import psutil

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_CONFIGS = [
    {
        "name": "Basic Fibonacci",
        "endpoint": "/fibonacci",
        "num_requests": 100,
        "concurrent": 10,
        "use_optimized": False
    },
    {
        "name": "Optimized Fibonacci",
        "endpoint": "/fibonacci-optimized",
        "num_requests": 100,
        "concurrent": 10,
        "use_optimized": True
    }
]

class LoadTest:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results = []
        self.start_time = None
        self.end_time = None
        self.pid = os.getpid()
        
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system statistics"""
        process = psutil.Process(self.pid)
        memory_info = process.memory_info()
        cpu_percent = process.cpu_percent()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "pid": self.pid,
            "cpu_percent": cpu_percent,
            "memory_rss": memory_info.rss / 1024 / 1024,  # MB
            "memory_vms": memory_info.vms / 1024 / 1024,  # MB
            "gc_count": gc.get_count(),
            "thread_count": threading.active_count(),
            "memory_leak_size": len(get_memory_leak_size())
        }
    
    def make_request(self, session: requests.Session) -> Dict[str, Any]:
        """Make a single request to the API"""
        url = f"{API_BASE_URL}{self.config['endpoint']}"
        payload = {"n": 40, "use_optimized": self.config['use_optimized']}
        
        try:
            start_time = time.time()
            response = session.post(url, json=payload, timeout=30)
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "result": data.get("result"),
                    "execution_time": data.get("execution_time", 0),
                    "memory_usage": data.get("memory_usage", 0),
                    "counter_value": data.get("counter_value", 0),
                    "response_time": end_time - start_time,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "response_time": end_time - start_time,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": 0,
                "timestamp": datetime.now().isoformat()
            }
    
    def run_concurrent_requests(self) -> List[Dict[str, Any]]:
        """Run concurrent requests"""
        results = []
        
        with requests.Session() as session:
            with ThreadPoolExecutor(max_workers=self.config['concurrent']) as executor:
                futures = [executor.submit(self.make_request, session) 
                          for _ in range(self.config['num_requests'])]
                
                for future in futures:
                    results.append(future.result())
        
        return results
    
    def run_test(self) -> Dict[str, Any]:
        """Run the complete load test"""
        print(f"Starting test: {self.config['name']}")
        print(f"Config: {self.config['num_requests']} requests, {self.config['concurrent']} concurrent")
        
        self.start_time = time.time()
        
        # Get initial stats
        initial_stats = self.get_system_stats()
        print(f"Initial stats: {initial_stats}")
        
        # Run concurrent requests
        results = self.run_concurrent_requests()
        
        self.end_time = time.time()
        
        # Get final stats
        final_stats = self.get_system_stats()
        print(f"Final stats: {final_stats}")
        
        # Analyze results
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        response_times = [r['response_time'] for r in successful]
        execution_times = [r['execution_time'] for r in successful]
        memory_usages = [r['memory_usage'] for r in successful]
        counter_values = [r['counter_value'] for r in successful]
        
        test_summary = {
            "test_name": self.config['name'],
            "config": self.config,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time": datetime.fromtimestamp(self.end_time).isoformat(),
            "total_duration": self.end_time - self.start_time,
            "total_requests": len(results),
            "successful_requests": len(successful),
            "failed_requests": len(failed),
            "success_rate": len(successful) / len(results) * 100,
            "requests_per_second": len(results) / (self.end_time - self.start_time),
            "average_response_time": statistics.mean(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "average_execution_time": statistics.mean(execution_times) if execution_times else 0,
            "average_memory_usage": statistics.mean(memory_usages) if memory_usages else 0,
            "average_counter_value": statistics.mean(counter_values) if counter_values else 0,
            "initial_stats": initial_stats,
            "final_stats": final_stats,
            "results": results
        }
        
        # Log failures
        if failed:
            print(f"\nFailures ({len(failed)}):")
            for failure in failed[:5]:  # Show first 5 failures
                print(f"  - {failure['error']}")
            if len(failed) > 5:
                print(f"  ... and {len(failed) - 5} more")
        
        print(f"\nTest completed: {len(successful)}/{len(results)} successful")
        print(f"Success rate: {test_summary['success_rate']:.2f}%")
        print(f"Requests per second: {test_summary['requests_per_second']:.2f}")
        
        return test_summary

def get_memory_leak_size():
    """Get current memory leak size from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/stats")
        if response.status_code == 200:
            return response.json().get("memory_leak_size", 0)
    except:
        pass
    return 0

def run_stress_test():
    """Run stress test to demonstrate race conditions"""
    print("\n=== Running Stress Test ===")
    
    stress_config = {
        "name": "Stress Test",
        "endpoint": "/fibonacci",
        "num_requests": 1000,
        "concurrent": 50,
        "use_optimized": False
    }
    
    stress_test = LoadTest(stress_config)
    stress_test.run_test()

def run_optimized_comparison():
    """Compare optimized vs non-optimized performance"""
    print("\n=== Performance Comparison ===")
    
    results = {}
    
    for config in TEST_CONFIGS:
        test = LoadTest(config)
        result = test.run_test()
        results[config['name']] = result
    
    # Print comparison
    print("\n=== Performance Comparison ===")
    print(f"{'Test':<20} {'Success Rate':<12} {'RPS':<8} {'Avg Time':<12} {'Avg Memory':<12}")
    print("-" * 65)
    
    for name, result in results.items():
        print(f"{name:<20} {result['success_rate']:<12.2f} {result['requests_per_second']:<8.2f} "
              f"{result['average_response_time']:<12.4f} {result['average_memory_usage']:<12.2f}")
    
    return results

def save_results_to_csv(results: Dict[str, Any], filename: str = "load_test_results.csv"):
    """Save test results to CSV"""
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['test_name', 'timestamp', 'success', 'response_time', 'execution_time', 
                     'memory_usage', 'counter_value', 'error']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for test_name, result in results.items():
            for item in result['results']:
                writer.writerow({
                    'test_name': test_name,
                    'timestamp': item['timestamp'],
                    'success': item['success'],
                    'response_time': item.get('response_time', 0),
                    'execution_time': item.get('execution_time', 0),
                    'memory_usage': item.get('memory_usage', 0),
                    'counter_value': item.get('counter_value', 0),
                    'error': item.get('error', '')
                })
    
    print(f"Results saved to {filename}")

def main():
    print("Memory & Concurrency Optimization - Load Testing")
    print("=" * 50)
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL}/stats", timeout=5)
        if response.status_code != 200:
            print(f"API not responding properly: {response.status_code}")
            return
    except requests.exceptions.RequestException:
        print(f"API not available at {API_BASE_URL}")
        print("Please start the FastAPI backend first:")
        print("  cd backend && uvicorn app.main:app --reload")
        return
    
    # Run tests
    comparison_results = run_optimized_comparison()
    run_stress_test()
    
    # Save results
    save_results_to_csv(comparison_results)
    
    print("\n=== Test Summary ===")
    print("Load testing completed. Check the CSV file for detailed results.")
    print("\nNext steps:")
    print("1. Monitor memory usage with htop/top")
    print("2. Check for race conditions in counter values")
    print("3. Compare performance between optimized and non-optimized versions")
    print("4. Run GDB analysis: gdb -p <pid> and 'info threads'")

if __name__ == "__main__":
    main()
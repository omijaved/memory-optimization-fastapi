#!/usr/bin/env python3
"""
Automated artifact collection for Memory & Concurrency Optimization Project

This script collects all required artifacts for demonstration:
1. System metrics screenshots
2. Diagnostic logs
3. Performance test results
4. GDB analysis
5. Physical setup documentation
"""
import gc
import os
import sys
import time
import subprocess
import json
import datetime
import psutil
import threading
import requests
from pathlib import Path

class ArtifactCollector:
    def __init__(self, output_dir="artifacts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.api_base_url = "http://localhost:8000"
        self.collection_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = self.output_dir / f"session_{self.collection_time}"
        self.session_dir.mkdir(exist_ok=True)
        
    def check_api_health(self):
        """Check if the API is running"""
        try:
            response = requests.get(f"{self.api_base_url}/stats", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def collect_system_info(self):
        """Collect basic system information"""
        print("Collecting system information...")
        
        system_info = {
            "timestamp": datetime.datetime.now().isoformat(),
            "hostname": os.uname().nodename,
            "platform": os.uname().sysname,
            "architecture": os.uname().machine,
            "python_version": sys.version,
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total / (1024**3),  # GB
            "disk_usage": {
                "total": psutil.disk_usage('/').total / (1024**3),  # GB
                "used": psutil.disk_usage('/').used / (1024**3),  # GB
                "free": psutil.disk_usage('/').free / (1024**3)  # GB
            }
        }
        
        with open(self.session_dir / "system_info.json", 'w') as f:
            json.dump(system_info, f, indent=2)
        
        return system_info
    
    def collect_diagnostic_logs(self):
        """Collect diagnostic logs"""
        print("Collecting diagnostic logs...")
        
        # Garbage collection count
        gc_count = gc.get_count()
        
        # Tracemalloc snapshot
        import tracemalloc
        tracemalloc.start()
        time.sleep(1)  # Allow some allocation
        snapshot = tracemalloc.take_snapshot()
        
        # System information
        switch_interval = sys.getswitchinterval()
        active_threads = threading.active_count()
        cpu_count = os.cpu_count()
        
        diagnostic_data = {
            "gc_count": gc_count,
            "switch_interval": switch_interval,
            "active_threads": active_threads,
            "cpu_count": cpu_count,
            "python_path": sys.path,
            "tracemalloc_stats": {
                "current": tracemalloc.get_traced_memory()[0] / (1024**2),  # MB
                "peak": tracemalloc.get_traced_memory()[1] / (1024**2)  # MB
            },
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        with open(self.session_dir / "diagnostic_logs.json", 'w') as f:
            json.dump(diagnostic_data, f, indent=2)
        
        # Save tracemalloc diff
        top_stats = snapshot.statistics('lineno')
        with open(self.session_dir / "tracemalloc_stats.txt", 'w') as f:
            f.write(f"Tracemalloc Statistics - {datetime.datetime.now()}\n")
            f.write("=" * 50 + "\n\n")
            for stat in top_stats[:20]:
                f.write(f"{stat}\n")
        
        return diagnostic_data
    
    def run_performance_test(self, num_requests=1000, use_optimized=False):
        """Run performance test and collect results"""
        print(f"Running performance test ({num_requests} requests, optimized={use_optimized})...")
        
        endpoint = "/fibonacci-optimized" if use_optimized else "/fibonacci"
        
        results = []
        start_time = time.time()
        
        for i in range(num_requests):
            try:
                response = requests.post(
                    f"{self.api_base_url}{endpoint}",
                    json={"n": 40, "use_optimized": use_optimized},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results.append({
                        "success": True,
                        "result": data.get("result"),
                        "execution_time": data.get("execution_time", 0),
                        "memory_usage": data.get("memory_usage", 0),
                        "counter_value": data.get("counter_value", 0),
                        "thread_count": data.get("thread_count", 0),
                        "process_count": data.get("process_count", 0)
                    })
                else:
                    results.append({
                        "success": False,
                        "error": f"HTTP {response.status_code}: {response.text}"
                    })
            except Exception as e:
                results.append({
                    "success": False,
                    "error": str(e)
                })
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        test_summary = {
            "test_config": {
                "num_requests": num_requests,
                "use_optimized": use_optimized,
                "endpoint": endpoint
            },
            "execution_time": total_time,
            "total_requests": len(results),
            "successful_requests": len(successful),
            "failed_requests": len(failed),
            "success_rate": len(successful) / len(results) * 100 if results else 0,
            "requests_per_second": len(results) / total_time if total_time > 0 else 0,
            "average_execution_time": sum(r.get('execution_time', 0) for r in successful) / len(successful) if successful else 0,
            "average_memory_usage": sum(r.get('memory_usage', 0) for r in successful) / len(successful) if successful else 0,
            "results": results
        }
        
        # Save results
        filename = f"performance_test_{num_requests}_requests{'_optimized' if use_optimized else ''}.json"
        with open(self.session_dir / filename, 'w') as f:
            json.dump(test_summary, f, indent=2)
        
        return test_summary
    
    def collect_memory_monitoring(self, duration=60):
        """Monitor memory usage over time"""
        print(f"Monitoring memory usage for {duration} seconds...")
        
        memory_data = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            process = psutil.Process()
            memory_info = process.memory_info()
            cpu_percent = process.cpu_percent()
            
            memory_data.append({
                "timestamp": datetime.datetime.now().isoformat(),
                "memory_rss": memory_info.rss / (1024**2),  # MB
                "memory_vms": memory_info.vms / (1024**2),  # MB
                "cpu_percent": cpu_percent,
                "thread_count": threading.active_count(),
                "gc_count": gc.get_count()
            })
            
            time.sleep(1)
        
        with open(self.session_dir / "memory_monitoring.json", 'w') as f:
            json.dump(memory_data, f, indent=2)
        
        return memory_data
    
    def generate_screenshot_commands(self):
        """Generate commands for taking screenshots"""
        print("Generating screenshot commands...")
        
        commands = []
        
        # htop screenshot
        commands.append({
            "name": "htop_screenshot",
            "description": "Screenshot of htop showing memory and CPU usage",
            "command": "htop",
            "instructions": "Take screenshot while htop is running, showing memory growth and CPU usage"
        })
        
        # GDB analysis
        commands.append({
            "name": "gdb_analysis",
            "description": "GDB analysis showing thread information",
            "command": "gdb -p $(pgrep -f uvicorn)",
            "gdb_commands": ["info threads", "thread apply all bt"],
            "instructions": "Run GDB, execute 'info threads' and take screenshot"
        })
        
        # System information
        commands.append({
            "name": "system_info",
            "description": "System information including hostname and date",
            "command": "uname -a && date",
            "instructions": "Run in terminal and include screenshot showing hostname and current date"
        })
        
        with open(self.session_dir / "screenshot_commands.json", 'w') as f:
            json.dump(commands, f, indent=2)
        
        return commands
    
    def collect_all_artifacts(self):
        """Collect all required artifacts"""
        print("Starting artifact collection...")
        print(f"Output directory: {self.session_dir}")
        
        # Check API health
        if not self.check_api_health():
            print("ERROR: API is not running. Please start the backend first.")
            return False
        
        # Collect all artifacts
        try:
            self.collect_system_info()
            self.collect_diagnostic_logs()
            
            # Run performance tests
            print("\nRunning initial performance test (with issues)...")
            self.run_performance_test(num_requests=1000, use_optimized=False)
            
            print("\nRunning optimized performance test...")
            self.run_performance_test(num_requests=1000, use_optimized=True)
            
            # Monitor memory
            self.collect_memory_monitoring(duration=30)
            
            # Generate screenshot commands
            self.generate_screenshot_commands()
            
            # Create summary
            self.create_summary()
            
            print(f"\nArtifact collection completed successfully!")
            print(f"All artifacts saved to: {self.session_dir}")
            
            return True
            
        except Exception as e:
            print(f"ERROR during artifact collection: {e}")
            return False
    
    def create_summary(self):
        """Create a summary of collected artifacts"""
        summary = {
            "collection_time": self.collection_time,
            "session_directory": str(self.session_dir),
            "collected_artifacts": [
                "system_info.json",
                "diagnostic_logs.json",
                "tracemalloc_stats.txt",
                "memory_monitoring.json",
                "screenshot_commands.json",
                "performance_test_1000_requests.json",
                "performance_test_1000_requests_optimized.json"
            ],
            "next_steps": [
                "Take screenshots as specified in screenshot_commands.json",
                "Take photo of physical setup with date note",
                "Run GDB analysis and take screenshot",
                "Analyze performance test results",
                "Compare before/after performance metrics"
            ]
        }
        
        with open(self.session_dir / "collection_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Collect artifacts for Memory & Concurrency Optimization Project')
    parser.add_argument('--output-dir', default='artifacts', help='Output directory for artifacts')
    parser.add_argument('--requests', type=int, default=1000, help='Number of requests for performance test')
    
    args = parser.parse_args()
    
    collector = ArtifactCollector(args.output_dir)
    success = collector.collect_all_artifacts()
    
    if success:
        print("\n" + "=" * 60)
        print("ARTIFACT COLLECTION COMPLETE")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Review collected artifacts in the session directory")
        print("2. Take screenshots as specified in screenshot_commands.json")
        print("3. Document physical setup with date")
        print("4. Analyze performance test results")
        print("5. Create comparison spreadsheet")
    else:
        print("\nArtifact collection failed. Please check error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
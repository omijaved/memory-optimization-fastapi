#!/usr/bin/env python3
"""
Analyze load test results and generate performance reports

This script analyzes the CSV output from load_test.py and generates:
1. Performance comparison charts
2. Memory usage analysis
3. Race condition detection
4. Optimization recommendations
"""

import csv
import json
import statistics
from datetime import datetime
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from collections import defaultdict

class ResultsAnalyzer:
    def __init__(self, csv_file: str):
        self.csv_file = csv_file
        self.data = self.load_data()
        
    def load_data(self) -> List[Dict[str, Any]]:
        """Load data from CSV file"""
        data = []
        try:
            with open(self.csv_file, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Convert numeric fields
                    row['response_time'] = float(row.get('response_time', 0))
                    row['execution_time'] = float(row.get('execution_time', 0))
                    row['memory_usage'] = float(row.get('memory_usage', 0))
                    row['counter_value'] = float(row.get('counter_value', 0))
                    row['success'] = row.get('success', 'false').lower() == 'true'
                    data.append(row)
        except FileNotFoundError:
            print(f"Error: File {self.csv_file} not found")
            exit(1)
        
        return data
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get overall test summary"""
        if not self.data:
            return {}
        
        total_requests = len(self.data)
        successful_requests = len([d for d in self.data if d['success']])
        failed_requests = total_requests - successful_requests
        
        response_times = [d['response_time'] for d in self.data if d['success']]
        execution_times = [d['execution_time'] for d in self.data if d['success']]
        memory_usages = [d['memory_usage'] for d in self.data if d['success']]
        counter_values = [d['counter_value'] for d in self.data if d['success']]
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": (successful_requests / total_requests) * 100 if total_requests > 0 else 0,
            "average_response_time": statistics.mean(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "average_execution_time": statistics.mean(execution_times) if execution_times else 0,
            "average_memory_usage": statistics.mean(memory_usages) if memory_usages else 0,
            "max_memory_usage": max(memory_usages) if memory_usages else 0,
            "counter_range": (min(counter_values) if counter_values else 0, max(counter_values) if counter_values else 0),
            "counter_std": statistics.stdev(counter_values) if len(counter_values) > 1 else 0
        }
    
    def get_test_comparison(self) -> Dict[str, Dict[str, Any]]:
        """Compare different test configurations"""
        test_groups = defaultdict(list)
        
        for row in self.data:
            test_name = row.get('test_name', 'Unknown')
            test_groups[test_name].append(row)
        
        comparison = {}
        for test_name, test_data in test_groups.items():
            successful = [d for d in test_data if d['success']]
            
            comparison[test_name] = {
                "total_requests": len(test_data),
                "successful_requests": len(successful),
                "success_rate": (len(successful) / len(test_data)) * 100 if test_data else 0,
                "average_response_time": statistics.mean([d['response_time'] for d in successful]) if successful else 0,
                "average_execution_time": statistics.mean([d['execution_time'] for d in successful]) if successful else 0,
                "average_memory_usage": statistics.mean([d['memory_usage'] for d in successful]) if successful else 0,
                "counter_std": statistics.stdev([d['counter_value'] for d in successful]) if len(successful) > 1 else 0
            }
        
        return comparison
    
    def detect_race_conditions(self) -> Dict[str, Any]:
        """Detect potential race conditions in counter values"""
        if not self.data:
            return {}
        
        # Group by test name and analyze counter values
        test_groups = defaultdict(list)
        for row in self.data:
            test_name = row.get('test_name', 'Unknown')
            test_groups[test_name].append(row)
        
        race_conditions = {}
        for test_name, test_data in test_groups.items():
            successful = [d for d in test_data if d['success']]
            
            if successful:
                counter_values = [d['counter_value'] for d in successful]
                expected_values = list(range(1, len(successful) + 1))
                
                # Check if counter values follow expected pattern
                is_sequential = all(counter_values[i] == expected_values[i] 
                                  for i in range(len(counter_values)))
                
                # Check for duplicates
                has_duplicates = len(set(counter_values)) != len(counter_values)
                
                # Calculate variance
                variance = statistics.variance(counter_values) if len(counter_values) > 1 else 0
                
                race_conditions[test_name] = {
                    "is_sequential": is_sequential,
                    "has_duplicates": has_duplicates,
                    "variance": variance,
                    "expected_range": (min(expected_values), max(expected_values)),
                    "actual_range": (min(counter_values), max(counter_values))
                }
        
        return race_conditions
    
    def generate_performance_report(self) -> str:
        """Generate a comprehensive performance report"""
        summary = self.get_test_summary()
        comparison = self.get_test_comparison()
        race_conditions = self.detect_race_conditions()
        
        report = []
        report.append("=" * 60)
        report.append("MEMORY & CONCURRENCY OPTIMIZATION - PERFORMANCE REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Data file: {self.csv_file}")
        report.append("")
        
        # Overall Summary
        report.append("OVERALL TEST SUMMARY")
        report.append("-" * 30)
        report.append(f"Total Requests: {summary['total_requests']}")
        report.append(f"Successful Requests: {summary['successful_requests']}")
        report.append(f"Failed Requests: {summary['failed_requests']}")
        report.append(f"Success Rate: {summary['success_rate']:.2f}%")
        report.append(f"Average Response Time: {summary['average_response_time']:.4f}s")
        report.append(f"Average Execution Time: {summary['average_execution_time']:.4f}s")
        report.append(f"Average Memory Usage: {summary['average_memory_usage']:.2f}MB")
        report.append(f"Max Memory Usage: {summary['max_memory_usage']:.2f}MB")
        report.append("")
        
        # Test Comparison
        report.append("TEST COMPARISON")
        report.append("-" * 30)
        report.append(f"{'Test Name':<20} {'Success Rate':<12} {'Avg Time':<12} {'Memory':<10} {'Race Risk':<10}")
        report.append("-" * 65)
        
        for test_name, metrics in comparison.items():
            race_risk = "High" if race_conditions.get(test_name, {}).get('variance', 0) > 1 else "Low"
            report.append(f"{test_name:<20} {metrics['success_rate']:<12.2f} {metrics['average_response_time']:<12.4f} "
                         f"{metrics['average_memory_usage']:<10.2f} {race_risk:<10}")
        
        report.append("")
        
        # Race Condition Analysis
        report.append("RACE CONDITION ANALYSIS")
        report.append("-" * 30)
        for test_name, analysis in race_conditions.items():
            report.append(f"\nTest: {test_name}")
            report.append(f"  Sequential: {analysis['is_sequential']}")
            report.append(f"  Duplicates: {analysis['has_duplicates']}")
            report.append(f"  Variance: {analysis['variance']:.4f}")
            report.append(f"  Expected Range: {analysis['expected_range']}")
            report.append(f"  Actual Range: {analysis['actual_range']}")
            
            if analysis['variance'] > 0.5:
                report.append("  ⚠️  HIGH RISK OF RACE CONDITIONS DETECTED!")
        
        report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS")
        report.append("-" * 30)
        
        # Check for memory issues
        if summary['max_memory_usage'] > 1000:  # > 1GB
            report.append("🔴 MEMORY LEAK DETECTED:")
            report.append("   - Implement regular garbage collection")
            report.append("   - Use weakref.WeakValueDictionary for caches")
            report.append("   - Monitor memory usage with tracemalloc")
        
        # Check for race conditions
        high_risk_tests = [name for name, analysis in race_conditions.items() 
                          if analysis.get('variance', 0) > 0.5]
        if high_risk_tests:
            report.append("🔴 RACE CONDITIONS DETECTED:")
            for test in high_risk_tests:
                report.append(f"   - {test}: Use threading.Lock or asyncio.Lock")
        
        # Performance recommendations
        if comparison:
            basic_test = next((metrics for name, metrics in comparison.items() 
                             if 'Basic' in name), None)
            optimized_test = next((metrics for name, metrics in comparison.items() 
                                 if 'Optimized' in name), None)
            
            if basic_test and optimized_test:
                basic_time = basic_test['average_response_time']
                optimized_time = optimized_test['average_response_time']
                improvement = ((basic_time - optimized_time) / basic_time) * 100 if basic_time > 0 else 0
                
                report.append(f"📊 PERFORMANCE IMPROVEMENT: {improvement:.1f}%")
                report.append("   - Multiprocessing effectively bypasses GIL limitations")
                report.append("   - Consider using ProcessPoolExecutor for CPU-bound tasks")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def save_report(self, filename: str = "performance_report.txt"):
        """Save the performance report to a file"""
        report = self.generate_performance_report()
        with open(filename, 'w') as f:
            f.write(report)
        print(f"Performance report saved to {filename}")
        return report

def create_performance_charts(csv_file: str, output_dir: str = "charts"):
    """Create performance comparison charts"""
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        # Read data
        df = pd.read_csv(csv_file)
        
        # Filter successful requests
        df_success = df[df['success'] == True]
        
        # Create comparison charts
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Response time comparison
        test_groups = df_success.groupby('test_name')['response_time'].agg(['mean', 'std']).reset_index()
        axes[0, 0].bar(test_groups['test_name'], test_groups['mean'], yerr=test_groups['std'])
        axes[0, 0].set_title('Average Response Time by Test')
        axes[0, 0].set_ylabel('Response Time (s)')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 2. Memory usage comparison
        memory_groups = df_success.groupby('test_name')['memory_usage'].agg(['mean', 'std']).reset_index()
        axes[0, 1].bar(memory_groups['test_name'], memory_groups['mean'], yerr=memory_groups['std'])
        axes[0, 1].set_title('Average Memory Usage by Test')
        axes[0, 1].set_ylabel('Memory Usage (MB)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 3. Success rate
        success_rates = df.groupby('test_name')['success'].mean() * 100
        axes[1, 0].bar(success_rates.index, success_rates.values)
        axes[1, 0].set_title('Success Rate by Test')
        axes[1, 0].set_ylabel('Success Rate (%)')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 4. Counter values (race condition indicator)
        if 'counter_value' in df_success.columns:
            counter_groups = df_success.groupby('test_name')['counter_value'].agg(['mean', 'std']).reset_index()
            axes[1, 1].bar(counter_groups['test_name'], counter_groups['mean'], yerr=counter_groups['std'])
            axes[1, 1].set_title('Average Counter Value by Test')
            axes[1, 1].set_ylabel('Counter Value')
            axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/performance_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Performance charts saved to {output_dir}/performance_comparison.png")
        
    except Exception as e:
        print(f"Error creating charts: {e}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze load test results')
    parser.add_argument('csv_file', help='Path to the CSV file with test results')
    parser.add_argument('--output-dir', default='analysis', help='Output directory for reports')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Analyze results
    analyzer = ResultsAnalyzer(args.csv_file)
    
    # Generate and save report
    report = analyzer.save_report(f'{args.output_dir}/performance_report.txt')
    
    # Print report
    print(report)
    
    # Create charts
    create_performance_charts(args.csv_file, args.output_dir)
    
    print(f"\nAnalysis complete! Check the '{args.output_dir}' directory for:")
    print("- performance_report.txt")
    print("- charts/performance_comparison.png")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Comprehensive Stress Testing Suite
Extended validation beyond basic scalability testing.
"""

import asyncio
import gc
import json
import psutil
import random
import statistics
import sys
import time
import os
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from src.mcp_standards.memory.v2.test_hybrid_memory import create_test_hybrid_memory

class StressTestMetrics:
    """Comprehensive metrics collection for stress testing"""

    def __init__(self):
        self.start_time = time.time()
        self.operations = []
        self.memory_samples = []
        self.error_log = []
        self.performance_samples = []

    def record_operation(self, operation_type: str, duration: float, success: bool, details: Dict = None):
        """Record a single operation"""
        self.operations.append({
            'type': operation_type,
            'duration': duration,
            'success': success,
            'timestamp': time.time(),
            'details': details or {}
        })

    def record_memory_sample(self):
        """Record current memory usage"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            cpu_percent = process.cpu_percent()

            self.memory_samples.append({
                'timestamp': time.time(),
                'rss_mb': memory_info.rss / 1024 / 1024,
                'vms_mb': memory_info.vms / 1024 / 1024,
                'cpu_percent': cpu_percent,
                'num_fds': process.num_fds() if hasattr(process, 'num_fds') else 0
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    def record_error(self, error_type: str, message: str, context: Dict = None):
        """Record an error occurrence"""
        self.error_log.append({
            'type': error_type,
            'message': message,
            'timestamp': time.time(),
            'context': context or {}
        })

    def get_summary(self) -> Dict[str, Any]:
        """Generate comprehensive test summary"""
        total_time = time.time() - self.start_time

        # Operation statistics
        successful_ops = [op for op in self.operations if op['success']]
        failed_ops = [op for op in self.operations if not op['success']]

        # Performance statistics
        durations = [op['duration'] for op in successful_ops]

        # Memory statistics
        if self.memory_samples:
            memory_growth = (
                self.memory_samples[-1]['rss_mb'] - self.memory_samples[0]['rss_mb']
                if len(self.memory_samples) > 1 else 0
            )
            max_memory = max(sample['rss_mb'] for sample in self.memory_samples)
            avg_cpu = statistics.mean(sample['cpu_percent'] for sample in self.memory_samples)
        else:
            memory_growth = 0
            max_memory = 0
            avg_cpu = 0

        return {
            'test_duration_seconds': total_time,
            'total_operations': len(self.operations),
            'successful_operations': len(successful_ops),
            'failed_operations': len(failed_ops),
            'success_rate': len(successful_ops) / len(self.operations) if self.operations else 0,
            'operations_per_second': len(self.operations) / total_time if total_time > 0 else 0,
            'performance': {
                'avg_duration_ms': statistics.mean(durations) * 1000 if durations else 0,
                'min_duration_ms': min(durations) * 1000 if durations else 0,
                'max_duration_ms': max(durations) * 1000 if durations else 0,
                'p95_duration_ms': statistics.quantiles(durations, n=20)[18] * 1000 if len(durations) > 20 else 0,
                'p99_duration_ms': statistics.quantiles(durations, n=100)[98] * 1000 if len(durations) > 100 else 0,
            },
            'memory': {
                'growth_mb': memory_growth,
                'max_usage_mb': max_memory,
                'avg_cpu_percent': avg_cpu,
                'samples_collected': len(self.memory_samples)
            },
            'errors': {
                'total_errors': len(self.error_log),
                'error_types': list(set(error['type'] for error in self.error_log)),
                'error_rate': len(self.error_log) / len(self.operations) if self.operations else 0
            }
        }

async def stress_test_large_dataset(memory_router, metrics: StressTestMetrics, num_patterns: int = 1000):
    """Test system with large dataset of patterns"""
    print(f"📊 Large Dataset Stress Test: {num_patterns} patterns...")

    # Generate diverse patterns
    pattern_templates = [
        "File operation: {action} on {file_type} file {filename} in {directory}",
        "Database query: {operation} {table} with {condition} filter returning {count} results",
        "API request: {method} {endpoint} with {params} parameters taking {duration}ms",
        "System command: {command} executed with {args} arguments in {context} environment",
        "User interaction: {user} performed {action} on {component} at {timestamp}",
        "Network operation: {protocol} connection to {host}:{port} with {status} status",
        "Cache operation: {operation} {key} in {cache_type} cache with {result} outcome",
        "Configuration change: {setting} modified from {old_value} to {new_value} by {user}",
        "Performance metric: {metric} measured at {value} {unit} on {component}",
        "Error handling: {error_type} caught in {module} with {severity} severity"
    ]

    start_time = time.time()
    batch_size = 50

    for batch_start in range(0, num_patterns, batch_size):
        batch_end = min(batch_start + batch_size, num_patterns)
        batch_patterns = []

        # Generate batch of patterns
        for i in range(batch_start, batch_end):
            template = random.choice(pattern_templates)

            # Fill template with random data
            pattern_content = template.format(
                action=random.choice(['create', 'update', 'delete', 'read', 'modify']),
                file_type=random.choice(['json', 'xml', 'csv', 'txt', 'log']),
                filename=f"file_{i}_{random.randint(1000, 9999)}",
                directory=random.choice(['/tmp', '/var/log', '/home/user', '/opt/app']),
                operation=random.choice(['SELECT', 'INSERT', 'UPDATE', 'DELETE']),
                table=f"table_{random.choice(['users', 'orders', 'products', 'logs'])}",
                condition=f"id = {random.randint(1, 1000)}",
                count=random.randint(0, 100),
                method=random.choice(['GET', 'POST', 'PUT', 'DELETE']),
                endpoint=f"/api/v1/{random.choice(['users', 'orders', 'products'])}",
                params=random.randint(0, 10),
                duration=random.randint(10, 1000),
                command=random.choice(['ls', 'grep', 'find', 'awk', 'sed']),
                args=f"--{random.choice(['verbose', 'recursive', 'force'])}",
                context=random.choice(['development', 'staging', 'production']),
                user=f"user_{random.randint(1, 100)}",
                component=random.choice(['button', 'form', 'menu', 'dialog']),
                timestamp=datetime.now().isoformat(),
                protocol=random.choice(['HTTP', 'HTTPS', 'TCP', 'UDP']),
                host=f"server_{random.randint(1, 10)}",
                port=random.choice([80, 443, 8080, 3000]),
                status=random.choice(['success', 'failed', 'timeout']),
                key=f"cache_key_{i}",
                cache_type=random.choice(['redis', 'memcache', 'local']),
                result=random.choice(['hit', 'miss', 'expired']),
                setting=f"config_{random.choice(['timeout', 'retries', 'pool_size'])}",
                old_value=random.randint(1, 100),
                new_value=random.randint(1, 100),
                metric=random.choice(['cpu_usage', 'memory_usage', 'response_time']),
                value=random.uniform(0.1, 99.9),
                unit=random.choice(['%', 'MB', 'ms']),
                error_type=random.choice(['TypeError', 'ValueError', 'ConnectionError']),
                module=f"module_{random.choice(['auth', 'db', 'api', 'cache'])}",
                severity=random.choice(['low', 'medium', 'high', 'critical'])
            )

            batch_patterns.append({
                'content': pattern_content,
                'context': {
                    'batch': batch_start // batch_size,
                    'pattern_id': i,
                    'test_type': 'large_dataset_stress',
                    'complexity': random.choice(['simple', 'medium', 'complex']),
                    'priority': random.choice(['low', 'medium', 'high']),
                    'source': random.choice(['user', 'system', 'api', 'batch'])
                },
                'category': f"stress_test_category_{i % 10}"
            })

        # Store batch concurrently
        batch_start_time = time.time()
        tasks = []

        for pattern in batch_patterns:
            async def store_pattern(p):
                op_start = time.time()
                try:
                    pattern_id = await memory_router.store_pattern(
                        p['content'], p['context'], p['category']
                    )
                    duration = time.time() - op_start
                    metrics.record_operation('store', duration, True, {'pattern_id': pattern_id})
                    return True
                except Exception as e:
                    duration = time.time() - op_start
                    metrics.record_operation('store', duration, False)
                    metrics.record_error('store_error', str(e), {'pattern': p})
                    return False

            tasks.append(store_pattern(pattern))

        # Execute batch
        results = await asyncio.gather(*tasks, return_exceptions=True)
        batch_time = time.time() - batch_start_time

        successful = sum(1 for r in results if r is True)
        batch_num = batch_start // batch_size + 1
        total_batches = (num_patterns + batch_size - 1) // batch_size

        print(f"  Batch {batch_num}/{total_batches}: {successful}/{len(batch_patterns)} patterns stored in {batch_time:.3f}s")

        # Memory sampling
        metrics.record_memory_sample()

        # Brief pause between batches
        await asyncio.sleep(0.1)

    total_time = time.time() - start_time
    print(f"✅ Large Dataset Test: {num_patterns} patterns processed in {total_time:.3f}s")
    return True

async def stress_test_concurrent_load(memory_router, metrics: StressTestMetrics, max_concurrent: int = 20):
    """Test system under extreme concurrent load"""
    print(f"⚡ Extreme Concurrent Load Test: {max_concurrent} concurrent operations...")

    async def concurrent_user(user_id: int, duration_seconds: int = 60):
        """Simulate a single concurrent user"""
        end_time = time.time() + duration_seconds
        operation_count = 0

        while time.time() < end_time:
            # Randomly choose operation (70% search, 30% store)
            if random.random() < 0.7:
                # Search operation
                queries = [
                    "file operation database",
                    "user interaction system",
                    "API request performance",
                    "network connection cache",
                    "error handling configuration"
                ]
                query = random.choice(queries)

                op_start = time.time()
                try:
                    results = await memory_router.search_patterns(
                        query,
                        top_k=random.randint(3, 10),
                        threshold=random.uniform(0.3, 0.8)
                    )
                    duration = time.time() - op_start
                    metrics.record_operation(
                        'search', duration, True,
                        {'user': user_id, 'results': len(results) if results else 0}
                    )
                except Exception as e:
                    duration = time.time() - op_start
                    metrics.record_operation('search', duration, False)
                    metrics.record_error('search_error', str(e), {'user': user_id})
            else:
                # Store operation
                content = f"Concurrent user {user_id} operation {operation_count}: " + \
                         f"Testing system under load at {datetime.now().isoformat()}"
                context = {
                    'user_id': user_id,
                    'operation_count': operation_count,
                    'test_phase': 'concurrent_load'
                }
                category = f"concurrent_user_{user_id % 5}"

                op_start = time.time()
                try:
                    pattern_id = await memory_router.store_pattern(content, context, category)
                    duration = time.time() - op_start
                    metrics.record_operation(
                        'store', duration, True,
                        {'user': user_id, 'pattern_id': pattern_id}
                    )
                except Exception as e:
                    duration = time.time() - op_start
                    metrics.record_operation('store', duration, False)
                    metrics.record_error('store_error', str(e), {'user': user_id})

            operation_count += 1

            # Brief pause between operations for this user
            await asyncio.sleep(random.uniform(0.1, 0.5))

    # Launch concurrent users
    user_tasks = []
    for user_id in range(max_concurrent):
        task = asyncio.create_task(concurrent_user(user_id, 30))  # 30 seconds per user
        user_tasks.append(task)

        # Stagger user startup
        await asyncio.sleep(0.1)

    # Monitor progress
    start_time = time.time()
    while not all(task.done() for task in user_tasks):
        await asyncio.sleep(5)
        metrics.record_memory_sample()

        # Progress update
        elapsed = time.time() - start_time
        completed_tasks = sum(1 for task in user_tasks if task.done())
        print(f"  Progress: {completed_tasks}/{max_concurrent} users completed, {elapsed:.1f}s elapsed")

    # Wait for all users to complete
    await asyncio.gather(*user_tasks, return_exceptions=True)

    total_time = time.time() - start_time
    print(f"✅ Concurrent Load Test: {max_concurrent} users completed in {total_time:.3f}s")
    return True

async def stress_test_memory_stability(memory_router, metrics: StressTestMetrics, duration_minutes: int = 10):
    """Test for memory leaks and stability over extended period"""
    print(f"🧠 Memory Stability Test: {duration_minutes} minutes duration...")

    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)

    operation_count = 0
    gc_count = 0

    while time.time() < end_time:
        # Mixed operations to stress memory
        operations = []

        # Create batch of operations
        for _ in range(20):
            if random.random() < 0.6:
                # Store operation
                content = f"Memory stability test pattern {operation_count}: " + \
                         f"Testing for memory leaks with large content " + \
                         f"{'x' * random.randint(100, 1000)}"  # Variable content size

                operations.append(('store', content, {
                    'operation_count': operation_count,
                    'test_phase': 'memory_stability',
                    'content_size': len(content)
                }, f"memory_category_{operation_count % 3}"))
            else:
                # Search operation
                queries = [
                    "memory stability test pattern",
                    "testing for memory leaks",
                    "large content memory test",
                    "stability pattern operation"
                ]
                operations.append(('search', random.choice(queries), {}, {}))

            operation_count += 1

        # Execute operations
        for op_type, content_or_query, context, category in operations:
            op_start = time.time()
            try:
                if op_type == 'store':
                    result = await memory_router.store_pattern(content_or_query, context, category)
                    duration = time.time() - op_start
                    metrics.record_operation('store', duration, True)
                else:
                    result = await memory_router.search_patterns(content_or_query, top_k=5)
                    duration = time.time() - op_start
                    metrics.record_operation('search', duration, True)
            except Exception as e:
                duration = time.time() - op_start
                metrics.record_operation(op_type, duration, False)
                metrics.record_error(f'{op_type}_error', str(e))

        # Memory monitoring
        metrics.record_memory_sample()

        # Periodic garbage collection
        if operation_count % 200 == 0:
            gc.collect()
            gc_count += 1
            print(f"  Memory check: {operation_count} operations, GC run #{gc_count}")

        # Brief pause
        await asyncio.sleep(0.1)

    # Final garbage collection and memory sample
    gc.collect()
    metrics.record_memory_sample()

    total_time = time.time() - start_time
    print(f"✅ Memory Stability Test: {operation_count} operations in {total_time:.3f}s")
    return True

async def run_comprehensive_stress_tests():
    """Run all stress tests and generate comprehensive report"""
    print("🚀 Comprehensive Stress Testing Suite")
    print("=" * 60)

    metrics = StressTestMetrics()

    try:
        # Initialize memory router
        print("🔧 Initializing test memory router...")
        memory_router = await create_test_hybrid_memory()
        print("✅ Memory router initialized")

        # Initial memory baseline
        metrics.record_memory_sample()

        # Test suite
        tests = [
            ("Large Dataset Stress Test", lambda: stress_test_large_dataset(memory_router, metrics, 1000)),
            ("Extreme Concurrent Load Test", lambda: stress_test_concurrent_load(memory_router, metrics, 15)),
            ("Memory Stability Test", lambda: stress_test_memory_stability(memory_router, metrics, 5)),
        ]

        for test_name, test_func in tests:
            print(f"\n🧪 Running {test_name}...")
            test_start = time.time()

            try:
                success = await test_func()
                test_time = time.time() - test_start
                print(f"✅ {test_name} completed in {test_time:.3f}s")

            except Exception as e:
                test_time = time.time() - test_start
                print(f"❌ {test_name} failed: {e}")
                metrics.record_error('test_failure', str(e), {'test': test_name})

        # Generate comprehensive report
        print(f"\n📊 Comprehensive Stress Test Results")
        print("=" * 60)

        summary = metrics.get_summary()

        print(f"🕒 Test Duration: {summary['test_duration_seconds']:.1f} seconds")
        print(f"📈 Operations: {summary['total_operations']:,} total")
        print(f"✅ Success Rate: {summary['success_rate']:.1%}")
        print(f"⚡ Throughput: {summary['operations_per_second']:.1f} ops/second")

        print(f"\n⏱️ Performance Metrics:")
        perf = summary['performance']
        print(f"   Average: {perf['avg_duration_ms']:.1f}ms")
        print(f"   95th percentile: {perf['p95_duration_ms']:.1f}ms")
        print(f"   99th percentile: {perf['p99_duration_ms']:.1f}ms")
        print(f"   Min/Max: {perf['min_duration_ms']:.1f}ms / {perf['max_duration_ms']:.1f}ms")

        print(f"\n🧠 Memory Analysis:")
        mem = summary['memory']
        print(f"   Memory Growth: {mem['growth_mb']:.1f} MB")
        print(f"   Peak Usage: {mem['max_usage_mb']:.1f} MB")
        print(f"   Average CPU: {mem['avg_cpu_percent']:.1f}%")
        print(f"   Samples: {mem['samples_collected']} collected")

        print(f"\n❌ Error Analysis:")
        errors = summary['errors']
        print(f"   Total Errors: {errors['total_errors']}")
        print(f"   Error Rate: {errors['error_rate']:.1%}")
        print(f"   Error Types: {', '.join(errors['error_types']) if errors['error_types'] else 'None'}")

        # Performance assessment
        print(f"\n🎯 Performance Assessment:")
        if summary['success_rate'] >= 0.95:
            print("✅ Excellent reliability (≥95% success rate)")
        elif summary['success_rate'] >= 0.90:
            print("⚠️ Good reliability (≥90% success rate)")
        else:
            print("❌ Poor reliability (<90% success rate)")

        if perf['p95_duration_ms'] <= 100:
            print("✅ Excellent response times (≤100ms p95)")
        elif perf['p95_duration_ms'] <= 200:
            print("⚠️ Good response times (≤200ms p95)")
        else:
            print("❌ Poor response times (>200ms p95)")

        if mem['growth_mb'] <= 50:
            print("✅ Excellent memory efficiency (≤50MB growth)")
        elif mem['growth_mb'] <= 100:
            print("⚠️ Good memory efficiency (≤100MB growth)")
        else:
            print("❌ Poor memory efficiency (>100MB growth)")

        # Overall assessment
        overall_score = (
            (1 if summary['success_rate'] >= 0.95 else 0.5 if summary['success_rate'] >= 0.90 else 0) +
            (1 if perf['p95_duration_ms'] <= 100 else 0.5 if perf['p95_duration_ms'] <= 200 else 0) +
            (1 if mem['growth_mb'] <= 50 else 0.5 if mem['growth_mb'] <= 100 else 0)
        ) / 3

        print(f"\n🏆 Overall Assessment:")
        if overall_score >= 0.9:
            print("🎉 EXCELLENT - System exceeds all stress testing requirements!")
        elif overall_score >= 0.7:
            print("✅ GOOD - System performs well under stress with minor concerns")
        elif overall_score >= 0.5:
            print("⚠️ ACCEPTABLE - System functions under stress but needs improvement")
        else:
            print("❌ POOR - System struggles under stress, requires optimization")

        return overall_score >= 0.7

    except Exception as e:
        print(f"❌ Stress testing suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(run_comprehensive_stress_tests())
    sys.exit(0 if success else 1)
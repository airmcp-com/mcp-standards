#!/usr/bin/env python3
"""
Quick Additional Stress Testing
Focused stress tests that complete within time limits.
"""

import asyncio
import gc
import json
import random
import statistics
import sys
import time
import os
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from src.mcp_standards.memory.v2.test_hybrid_memory import create_test_hybrid_memory

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

async def stress_test_large_batch(memory_router, batch_size: int = 100):
    """Test storing large batches of patterns"""
    print(f"📊 Large Batch Test: {batch_size} patterns in single batch...")

    # Generate diverse test patterns
    patterns = []
    for i in range(batch_size):
        patterns.append({
            'content': f"Stress test pattern {i}: " +
                      f"Complex operation involving {random.choice(['file', 'database', 'network', 'cache'])} " +
                      f"with {random.choice(['high', 'medium', 'low'])} priority " +
                      f"{'x' * random.randint(50, 200)}",  # Variable length content
            'context': {
                'test_id': i,
                'batch_size': batch_size,
                'complexity': random.choice(['simple', 'complex']),
                'priority': random.randint(1, 10)
            },
            'category': f'stress_batch_{i % 5}'
        })

    # Store all patterns concurrently
    start_time = time.time()

    async def store_single_pattern(pattern, index):
        op_start = time.time()
        try:
            pattern_id = await memory_router.store_pattern(
                pattern['content'],
                pattern['context'],
                pattern['category']
            )
            duration = time.time() - op_start
            return {'success': True, 'duration': duration, 'index': index, 'pattern_id': pattern_id}
        except Exception as e:
            duration = time.time() - op_start
            return {'success': False, 'duration': duration, 'index': index, 'error': str(e)}

    # Execute all stores concurrently
    tasks = [store_single_pattern(pattern, i) for i, pattern in enumerate(patterns)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    total_time = time.time() - start_time
    successful = sum(1 for r in results if isinstance(r, dict) and r.get('success', False))
    failed = len(results) - successful

    durations = [r['duration'] for r in results if isinstance(r, dict) and 'duration' in r]
    avg_duration = statistics.mean(durations) if durations else 0
    max_duration = max(durations) if durations else 0

    print(f"✅ Large Batch Test Results:")
    print(f"   Success: {successful}/{batch_size} patterns ({successful/batch_size:.1%})")
    print(f"   Total time: {total_time:.3f}s")
    print(f"   Rate: {successful/total_time:.1f} patterns/second")
    print(f"   Avg latency: {avg_duration*1000:.1f}ms")
    print(f"   Max latency: {max_duration*1000:.1f}ms")

    return {
        'success': successful >= batch_size * 0.8,  # 80% success required
        'total_patterns': batch_size,
        'successful_patterns': successful,
        'failed_patterns': failed,
        'total_time': total_time,
        'avg_latency_ms': avg_duration * 1000,
        'max_latency_ms': max_duration * 1000,
        'throughput': successful / total_time
    }

async def stress_test_rapid_search(memory_router, num_searches: int = 100):
    """Test rapid succession of search operations"""
    print(f"🔍 Rapid Search Test: {num_searches} searches...")

    # Diverse search queries
    queries = [
        "stress test pattern",
        "complex operation involving",
        "file database network",
        "high priority simple",
        "batch size complexity",
        "concurrent operations",
        "performance testing",
        "memory patterns",
        "system validation",
        "error handling"
    ]

    start_time = time.time()
    results = []

    # Execute searches rapidly
    for i in range(num_searches):
        query = random.choice(queries)
        top_k = random.randint(3, 10)
        threshold = random.uniform(0.3, 0.8)

        search_start = time.time()
        try:
            search_results = await memory_router.search_patterns(
                query, top_k=top_k, threshold=threshold
            )
            duration = time.time() - search_start
            results.append({
                'success': True,
                'duration': duration,
                'results_count': len(search_results) if search_results else 0,
                'query': query
            })
        except Exception as e:
            duration = time.time() - search_start
            results.append({
                'success': False,
                'duration': duration,
                'error': str(e),
                'query': query
            })

        # Minimal delay between searches
        await asyncio.sleep(0.01)

    total_time = time.time() - start_time
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful

    durations = [r['duration'] for r in results if 'duration' in r]
    avg_duration = statistics.mean(durations) if durations else 0
    total_results = sum(r.get('results_count', 0) for r in results if r['success'])

    print(f"✅ Rapid Search Test Results:")
    print(f"   Success: {successful}/{num_searches} searches ({successful/num_searches:.1%})")
    print(f"   Total time: {total_time:.3f}s")
    print(f"   Rate: {successful/total_time:.1f} searches/second")
    print(f"   Avg latency: {avg_duration*1000:.1f}ms")
    print(f"   Total results found: {total_results}")

    return {
        'success': successful >= num_searches * 0.9,  # 90% success required
        'total_searches': num_searches,
        'successful_searches': successful,
        'failed_searches': failed,
        'total_time': total_time,
        'avg_latency_ms': avg_duration * 1000,
        'search_rate': successful / total_time,
        'total_results_found': total_results
    }

async def stress_test_concurrent_mixed(memory_router, concurrent_operations: int = 50):
    """Test concurrent mixed read/write operations"""
    print(f"⚡ Concurrent Mixed Operations Test: {concurrent_operations} concurrent ops...")

    async def mixed_operation(op_id: int):
        """Single mixed operation (store or search)"""
        op_start = time.time()

        if random.random() < 0.5:  # 50% store, 50% search
            # Store operation
            try:
                content = f"Concurrent operation {op_id}: mixed workload stress test"
                context = {'op_id': op_id, 'test_type': 'concurrent_mixed'}
                category = f'concurrent_{op_id % 3}'

                pattern_id = await memory_router.store_pattern(content, context, category)
                duration = time.time() - op_start
                return {
                    'type': 'store',
                    'success': True,
                    'duration': duration,
                    'op_id': op_id,
                    'pattern_id': pattern_id
                }
            except Exception as e:
                duration = time.time() - op_start
                return {
                    'type': 'store',
                    'success': False,
                    'duration': duration,
                    'op_id': op_id,
                    'error': str(e)
                }
        else:
            # Search operation
            try:
                queries = ["concurrent operation", "mixed workload", "stress test"]
                query = random.choice(queries)

                results = await memory_router.search_patterns(query, top_k=5)
                duration = time.time() - op_start
                return {
                    'type': 'search',
                    'success': True,
                    'duration': duration,
                    'op_id': op_id,
                    'results_count': len(results) if results else 0
                }
            except Exception as e:
                duration = time.time() - op_start
                return {
                    'type': 'search',
                    'success': False,
                    'duration': duration,
                    'op_id': op_id,
                    'error': str(e)
                }

    # Execute all operations concurrently
    start_time = time.time()
    tasks = [mixed_operation(i) for i in range(concurrent_operations)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    total_time = time.time() - start_time

    # Analyze results
    successful_ops = [r for r in results if isinstance(r, dict) and r.get('success', False)]
    failed_ops = [r for r in results if isinstance(r, dict) and not r.get('success', False)]

    store_ops = [r for r in successful_ops if r.get('type') == 'store']
    search_ops = [r for r in successful_ops if r.get('type') == 'search']

    durations = [r['duration'] for r in successful_ops if 'duration' in r]
    avg_duration = statistics.mean(durations) if durations else 0

    print(f"✅ Concurrent Mixed Operations Test Results:")
    print(f"   Success: {len(successful_ops)}/{concurrent_operations} operations ({len(successful_ops)/concurrent_operations:.1%})")
    print(f"   Store ops: {len(store_ops)}, Search ops: {len(search_ops)}")
    print(f"   Total time: {total_time:.3f}s")
    print(f"   Rate: {len(successful_ops)/total_time:.1f} ops/second")
    print(f"   Avg latency: {avg_duration*1000:.1f}ms")

    return {
        'success': len(successful_ops) >= concurrent_operations * 0.8,  # 80% success required
        'total_operations': concurrent_operations,
        'successful_operations': len(successful_ops),
        'failed_operations': len(failed_ops),
        'store_operations': len(store_ops),
        'search_operations': len(search_ops),
        'total_time': total_time,
        'avg_latency_ms': avg_duration * 1000,
        'operations_rate': len(successful_ops) / total_time
    }

async def stress_test_memory_usage():
    """Test memory usage patterns"""
    print(f"🧠 Memory Usage Analysis...")

    if not HAS_PSUTIL:
        print("⚠️ psutil not available, skipping detailed memory analysis")
        return {'success': True, 'memory_analysis': 'skipped'}

    try:
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        initial_cpu = process.cpu_percent()

        # Create memory router and perform operations
        memory_router = await create_test_hybrid_memory()

        # Store some patterns to create memory load
        for i in range(50):
            content = f"Memory test pattern {i}: " + "x" * 100  # Small patterns
            context = {'memory_test': True, 'pattern_id': i}
            await memory_router.store_pattern(content, context, f'memory_cat_{i%3}')

        # Force garbage collection
        gc.collect()

        # Measure memory after operations
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        final_cpu = process.cpu_percent()

        memory_growth = final_memory - initial_memory

        print(f"✅ Memory Usage Analysis Results:")
        print(f"   Initial memory: {initial_memory:.1f} MB")
        print(f"   Final memory: {final_memory:.1f} MB")
        print(f"   Memory growth: {memory_growth:.1f} MB")
        print(f"   CPU usage: {final_cpu:.1f}%")

        return {
            'success': memory_growth < 100,  # Less than 100MB growth acceptable
            'initial_memory_mb': initial_memory,
            'final_memory_mb': final_memory,
            'memory_growth_mb': memory_growth,
            'cpu_percent': final_cpu
        }

    except Exception as e:
        print(f"❌ Memory analysis failed: {e}")
        return {'success': False, 'error': str(e)}

async def run_quick_stress_tests():
    """Run quick additional stress tests"""
    print("🚀 Quick Additional Stress Testing")
    print("=" * 50)

    try:
        # Initialize memory router
        print("🔧 Initializing memory router...")
        memory_router = await create_test_hybrid_memory()
        print("✅ Memory router ready")

        # Test suite
        tests = [
            ("Large Batch Stress", lambda: stress_test_large_batch(memory_router, 100)),
            ("Rapid Search Stress", lambda: stress_test_rapid_search(memory_router, 100)),
            ("Concurrent Mixed Ops", lambda: stress_test_concurrent_mixed(memory_router, 30)),
            ("Memory Usage Analysis", stress_test_memory_usage),
        ]

        results = {}
        total_start_time = time.time()

        for test_name, test_func in tests:
            print(f"\n🧪 Running {test_name}...")
            test_start = time.time()

            try:
                result = await test_func()
                test_time = time.time() - test_start
                results[test_name] = {**result, 'test_time': test_time}

                status = "✅ PASS" if result['success'] else "❌ FAIL"
                print(f"{status} {test_name} completed in {test_time:.3f}s")

            except Exception as e:
                test_time = time.time() - test_start
                results[test_name] = {
                    'success': False,
                    'test_time': test_time,
                    'error': str(e)
                }
                print(f"❌ {test_name}: ERROR - {e}")

        total_time = time.time() - total_start_time

        # Generate summary
        print(f"\n📊 Quick Stress Test Summary")
        print("=" * 50)

        passed = sum(1 for r in results.values() if r.get('success', False))
        total = len(results)
        success_rate = (passed / total) * 100

        print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        print(f"Total Time: {total_time:.3f}s")
        print()

        for test_name, result in results.items():
            status = "✅" if result.get('success', False) else "❌"
            print(f"{status} {test_name}: {result['test_time']:.3f}s")

            # Show key metrics for each test
            if 'throughput' in result:
                print(f"   Throughput: {result['throughput']:.1f} patterns/second")
            elif 'search_rate' in result:
                print(f"   Search Rate: {result['search_rate']:.1f} searches/second")
            elif 'operations_rate' in result:
                print(f"   Operations Rate: {result['operations_rate']:.1f} ops/second")

            if 'avg_latency_ms' in result:
                print(f"   Avg Latency: {result['avg_latency_ms']:.1f}ms")

            if 'memory_growth_mb' in result:
                print(f"   Memory Growth: {result['memory_growth_mb']:.1f}MB")

            if 'error' in result:
                print(f"   Error: {result['error']}")

        # Overall assessment
        print(f"\n🎯 Additional Testing Assessment:")
        if success_rate >= 75:
            print("🎉 EXCELLENT - System handles additional stress scenarios well!")
            assessment = "excellent"
        elif success_rate >= 50:
            print("✅ GOOD - System shows resilience with some areas for improvement")
            assessment = "good"
        else:
            print("⚠️ NEEDS IMPROVEMENT - System struggles under additional stress")
            assessment = "needs_improvement"

        # Performance insights
        print(f"\n💡 Key Insights:")

        # Analyze throughput across tests
        throughputs = []
        if 'Large Batch Stress' in results and 'throughput' in results['Large Batch Stress']:
            throughputs.append(f"Batch processing: {results['Large Batch Stress']['throughput']:.1f} patterns/sec")
        if 'Rapid Search Stress' in results and 'search_rate' in results['Rapid Search Stress']:
            throughputs.append(f"Search operations: {results['Rapid Search Stress']['search_rate']:.1f} searches/sec")
        if 'Concurrent Mixed Ops' in results and 'operations_rate' in results['Concurrent Mixed Ops']:
            throughputs.append(f"Mixed operations: {results['Concurrent Mixed Ops']['operations_rate']:.1f} ops/sec")

        for insight in throughputs:
            print(f"   • {insight}")

        print(f"\n🚀 System Status: Additional stress testing {'PASSED' if success_rate >= 75 else 'NEEDS WORK'}")
        return success_rate >= 75

    except Exception as e:
        print(f"❌ Additional stress testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(run_quick_stress_tests())
    sys.exit(0 if success else 1)
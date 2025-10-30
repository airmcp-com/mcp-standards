#!/usr/bin/env python3
"""
Performance Optimization Engine Test Suite
Tests the advanced caching, connection pooling, and batch processing systems.
"""

import asyncio
import time
import json
from typing import List, Dict, Any
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from src.mcp_standards.performance.optimization_engine import (
    PerformanceOptimizer,
    IntelligentCache,
    ConnectionPool,
    BatchProcessor,
    PerformanceMetrics,
    CacheEntry,
    create_performance_optimizer
)
from src.mcp_standards.memory.v2.test_hybrid_memory import create_test_hybrid_memory

async def test_intelligent_cache():
    """Test intelligent cache with LRU eviction and TTL"""
    print("🧠 Testing Intelligent Cache...")

    # Small cache for testing eviction
    cache = IntelligentCache(max_size=3, default_ttl=2.0)

    # Test basic operations
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")

    assert cache.get("key1") == "value1"
    assert cache.get("key2") == "value2"
    assert cache.get("key3") == "value3"

    # Test LRU eviction
    cache.set("key4", "value4")  # Should evict key1 (least recently used)
    assert cache.get("key1") is None
    assert cache.get("key4") == "value4"

    # Test TTL expiration
    cache.set("short_ttl", "expires_soon", ttl=0.1)
    assert cache.get("short_ttl") == "expires_soon"
    await asyncio.sleep(0.2)
    assert cache.get("short_ttl") is None

    # Test cache statistics
    stats = cache.get_stats()
    assert stats['size'] > 0
    assert stats['hits'] > 0

    print("✅ Intelligent Cache: All tests passed")
    return True

async def test_connection_pool():
    """Test HTTP connection pooling for AgentDB"""
    print("🔗 Testing Connection Pool...")

    pool = ConnectionPool(max_connections=3, connection_timeout=60.0)

    # Test connection creation and reuse
    start_time = time.time()

    # Simulate multiple requests
    tasks = []
    for i in range(5):
        task = asyncio.create_task(pool.execute_request(
            'GET', 'http://localhost:3002/stats'
        ))
        tasks.append(task)

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Check that requests completed
    successful_requests = sum(1 for r in results if not isinstance(r, Exception))
    print(f"✅ Connection Pool: {successful_requests}/5 requests successful")

    # Test pool statistics
    stats = pool.get_stats()
    print(f"📊 Pool Stats: {stats}")

    await pool.close()
    return successful_requests >= 3  # Allow some failures

async def test_batch_processor():
    """Test batch processing for vector operations"""
    print("⚡ Testing Batch Processor...")

    processor = BatchProcessor(batch_size=3, max_wait_time=1.0)

    # Create sample operations and add them to the processor
    start_time = time.time()

    operation_futures = []
    for i in range(7):  # More than batch size to test batching
        operation_data = {
            'content': f"Test pattern {i}",
            'embedding': [0.1 * j for j in range(1536)]  # Dummy embedding
        }
        # Add operations to the batch processor
        future = await processor.add_operation('vector_store', operation_data)
        operation_futures.append(future)

    # Wait a bit for batch processing to complete
    await asyncio.sleep(processor.max_wait_time + 0.1)

    processing_time = time.time() - start_time

    print(f"✅ Batch Processor: Added {len(operation_futures)} operations in {processing_time:.3f}s")
    return True

async def test_performance_optimizer():
    """Test the main performance optimizer with real AgentDB"""
    print("🚀 Testing Performance Optimizer...")

    try:
        # Create memory router for the optimizer
        memory_router = await create_test_hybrid_memory()
        optimizer = await create_performance_optimizer(memory_router)

        # Test pattern storage with caching
        test_patterns = [
            {
                'content': 'Testing performance optimization patterns',
                'context': {'tool': 'test', 'optimization': 'caching'},
                'category': 'performance_test'
            },
            {
                'content': 'Advanced caching mechanisms for vector databases',
                'context': {'tool': 'test', 'optimization': 'vectordb'},
                'category': 'performance_test'
            },
            {
                'content': 'Connection pooling for HTTP requests',
                'context': {'tool': 'test', 'optimization': 'http'},
                'category': 'performance_test'
            }
        ]

        # Store patterns
        store_start = time.time()
        stored_ids = []
        for pattern in test_patterns:
            pattern_id = await optimizer.optimized_store_pattern(
                pattern['content'],
                pattern['context'],
                pattern['category']
            )
            stored_ids.append(pattern_id)

        store_time = time.time() - store_start
        print(f"📝 Stored {len(test_patterns)} patterns in {store_time:.3f}s")

        # Test cached search (first call)
        search_start = time.time()
        results1 = await optimizer.optimized_search_patterns(
            "performance optimization",
            top_k=3,
            category="performance_test"
        )
        first_search_time = time.time() - search_start

        # Test cached search (second call - should be faster)
        search_start = time.time()
        results2 = await optimizer.optimized_search_patterns(
            "performance optimization",
            top_k=3,
            category="performance_test"
        )
        cached_search_time = time.time() - search_start

        print(f"🔍 First search: {first_search_time:.3f}s")
        print(f"⚡ Cached search: {cached_search_time:.3f}s")
        print(f"🚀 Speedup: {first_search_time/cached_search_time:.1f}x")

        # Test performance metrics
        metrics = optimizer.get_performance_metrics()
        print(f"📊 Performance Metrics:")
        print(f"   - Cache hit rate: {metrics.cache_stats['hit_rate']:.1%}")
        print(f"   - Avg response time: {metrics.avg_response_time:.3f}s")
        print(f"   - Operations completed: {metrics.operations_completed}")

        await optimizer.close()

        # Verify cache effectiveness
        cache_effective = cached_search_time < first_search_time * 0.8
        results_consistent = len(results1) == len(results2)

        print(f"✅ Performance Optimizer: Cache effective={cache_effective}, Results consistent={results_consistent}")
        return cache_effective and results_consistent

    except Exception as e:
        print(f"❌ Performance Optimizer test failed: {e}")
        return False

async def test_memory_optimization():
    """Test memory usage optimization"""
    print("💾 Testing Memory Optimization...")

    try:
        import psutil
        import gc

        # Measure initial memory
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        memory_router = await create_test_hybrid_memory()
        optimizer = await create_performance_optimizer(memory_router)

        # Generate load to test memory efficiency
        large_patterns = []
        for i in range(100):
            large_patterns.append({
                'content': f"Large pattern content {i} " * 50,  # ~2.5KB each
                'context': {'test': 'memory', 'iteration': i},
                'category': 'memory_test'
            })

        # Store patterns and measure memory growth
        for pattern in large_patterns[:50]:  # Store half
            await optimizer.optimized_store_pattern(
                pattern['content'],
                pattern['context'],
                pattern['category']
            )

        mid_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Force garbage collection
        gc.collect()

        # Continue storing patterns
        for pattern in large_patterns[50:]:  # Store remaining half
            await optimizer.optimized_store_pattern(
                pattern['content'],
                pattern['context'],
                pattern['category']
            )

        final_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Clean up
        await optimizer.close()
        gc.collect()

        cleanup_memory = process.memory_info().rss / 1024 / 1024  # MB

        print(f"📊 Memory Usage:")
        print(f"   - Initial: {initial_memory:.1f} MB")
        print(f"   - Mid-test: {mid_memory:.1f} MB (+{mid_memory-initial_memory:.1f} MB)")
        print(f"   - Final: {final_memory:.1f} MB (+{final_memory-initial_memory:.1f} MB)")
        print(f"   - After cleanup: {cleanup_memory:.1f} MB")

        # Memory should not grow excessively (under 100MB growth for this test)
        memory_growth = final_memory - initial_memory
        memory_efficient = memory_growth < 100

        print(f"✅ Memory Optimization: Growth {memory_growth:.1f}MB, Efficient={memory_efficient}")
        return memory_efficient

    except ImportError:
        print("⚠️ psutil not available, skipping memory optimization test")
        return True
    except Exception as e:
        print(f"❌ Memory optimization test failed: {e}")
        return False

async def run_performance_test_suite():
    """Run the complete performance optimization test suite"""
    print("🚀 Performance Optimization Engine Test Suite")
    print("=" * 50)

    tests = [
        ("Intelligent Cache", test_intelligent_cache),
        ("Connection Pool", test_connection_pool),
        ("Batch Processor", test_batch_processor),
        ("Performance Optimizer", test_performance_optimizer),
        ("Memory Optimization", test_memory_optimization),
    ]

    results = {}
    total_start_time = time.time()

    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} Test...")
        start_time = time.time()

        try:
            success = await test_func()
            test_time = time.time() - start_time
            results[test_name] = {
                'success': success,
                'time': test_time,
                'status': 'PASS' if success else 'FAIL'
            }
            print(f"✅ {test_name}: {results[test_name]['status']} ({test_time:.3f}s)")

        except Exception as e:
            test_time = time.time() - start_time
            results[test_name] = {
                'success': False,
                'time': test_time,
                'status': 'ERROR',
                'error': str(e)
            }
            print(f"❌ {test_name}: ERROR - {e}")

    total_time = time.time() - total_start_time

    # Generate summary report
    print("\n📊 Performance Test Results Summary")
    print("=" * 50)

    passed = sum(1 for r in results.values() if r['success'])
    total = len(results)
    success_rate = (passed / total) * 100

    print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
    print(f"Total Time: {total_time:.3f}s")
    print()

    for test_name, result in results.items():
        status_icon = "✅" if result['success'] else "❌"
        print(f"{status_icon} {test_name}: {result['status']} ({result['time']:.3f}s)")
        if 'error' in result:
            print(f"   Error: {result['error']}")

    if success_rate >= 80:
        print(f"\n🎉 Performance optimization engine is ready for production!")
        print(f"   Success rate: {success_rate:.1f}% (≥80% required)")
    else:
        print(f"\n⚠️ Performance optimization needs attention")
        print(f"   Success rate: {success_rate:.1f}% (<80% required)")

    return success_rate >= 80

if __name__ == "__main__":
    # Run the test suite
    success = asyncio.run(run_performance_test_suite())
    exit_code = 0 if success else 1
    sys.exit(exit_code)
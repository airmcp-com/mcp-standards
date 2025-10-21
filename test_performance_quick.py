#!/usr/bin/env python3
"""
Quick Performance Optimization Test
Fast validation of performance optimization components.
"""

import asyncio
import time
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from src.mcp_standards.performance.optimization_engine import (
    IntelligentCache,
    ConnectionPool,
    BatchProcessor,
    create_performance_optimizer
)
from src.mcp_standards.memory.v2.test_hybrid_memory import create_test_hybrid_memory

async def test_cache_basic():
    """Quick cache test"""
    print("🧠 Testing Cache...")

    cache = IntelligentCache(max_size=5, default_ttl=10.0)

    # Basic operations
    cache.set("test1", "value1")
    cache.set("test2", "value2")

    assert cache.get("test1") == "value1"
    assert cache.get("test2") == "value2"
    assert cache.get("missing") is None

    stats = cache.get_stats()
    assert stats['size'] == 2
    assert stats['hits'] == 2
    assert stats['misses'] == 1

    print("✅ Cache: Basic operations working")
    return True

async def test_connection_pool_basic():
    """Quick connection pool test"""
    print("🔗 Testing Connection Pool...")

    pool = ConnectionPool(max_connections=2, connection_timeout=5.0)

    # Test simple HTTP request to AgentDB
    try:
        result = await pool.execute_request('GET', 'http://localhost:3002/health')
        success = result is not None
        print(f"✅ Connection Pool: Health check {'passed' if success else 'failed'}")
        await pool.close()
        return success
    except Exception as e:
        print(f"❌ Connection Pool: {e}")
        return False

async def test_batch_processor_basic():
    """Quick batch processor test"""
    print("⚡ Testing Batch Processor...")

    processor = BatchProcessor(batch_size=2, max_wait_time=0.1)

    # Add a few operations
    try:
        future1 = await processor.add_operation('test', {'data': 'test1'})
        future2 = await processor.add_operation('test', {'data': 'test2'})

        # Wait a bit for processing
        await asyncio.sleep(0.2)

        print("✅ Batch Processor: Operations added successfully")
        return True
    except Exception as e:
        print(f"❌ Batch Processor: {e}")
        return False

async def test_optimizer_basic():
    """Quick optimizer test"""
    print("🚀 Testing Performance Optimizer...")

    try:
        memory_router = await create_test_hybrid_memory()
        optimizer = await create_performance_optimizer(memory_router)

        # Test simple pattern storage
        pattern_id = await optimizer.optimized_store_pattern(
            "Quick test pattern for performance validation",
            {"tool": "quick_test", "type": "validation"},
            "test_category"
        )

        # Test search with caching
        results = await optimizer.optimized_search_patterns(
            "test pattern validation",
            top_k=1
        )

        # Test cached search (should be faster)
        cached_results = await optimizer.optimized_search_patterns(
            "test pattern validation",
            top_k=1
        )

        await optimizer.close()

        success = (pattern_id is not None and
                  len(results) > 0 and
                  len(cached_results) > 0)

        print(f"✅ Performance Optimizer: {'Working' if success else 'Failed'}")
        return success

    except Exception as e:
        print(f"❌ Performance Optimizer: {e}")
        return False

async def run_quick_tests():
    """Run quick performance validation tests"""
    print("🚀 Quick Performance Optimization Test")
    print("=" * 40)

    tests = [
        ("Cache", test_cache_basic),
        ("Connection Pool", test_connection_pool_basic),
        ("Batch Processor", test_batch_processor_basic),
        ("Performance Optimizer", test_optimizer_basic),
    ]

    results = {}
    start_time = time.time()

    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}...")
        test_start = time.time()

        try:
            success = await test_func()
            test_time = time.time() - test_start
            results[test_name] = {
                'success': success,
                'time': test_time
            }
        except Exception as e:
            test_time = time.time() - test_start
            results[test_name] = {
                'success': False,
                'time': test_time,
                'error': str(e)
            }
            print(f"❌ {test_name}: {e}")

    total_time = time.time() - start_time

    # Summary
    print(f"\n📊 Quick Test Results")
    print("=" * 40)

    passed = sum(1 for r in results.values() if r['success'])
    total = len(results)
    success_rate = (passed / total) * 100

    print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
    print(f"Total Time: {total_time:.3f}s")

    for test_name, result in results.items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{status} {test_name}: {result['time']:.3f}s")
        if 'error' in result:
            print(f"   Error: {result['error']}")

    print()
    if success_rate >= 75:
        print("🎉 Performance optimization components are working!")
        return True
    else:
        print("⚠️ Some performance components need attention")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_quick_tests())
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Direct Scalability Test for V2 System
Tests AgentDB and V2 memory system performance under load without optimization engine.
"""

import asyncio
import time
import random
import sys
import os
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from src.mcp_standards.memory.v2.test_hybrid_memory import create_test_hybrid_memory

async def test_concurrent_pattern_storage(memory_router, num_patterns: int = 50, concurrency: int = 10):
    """Test storing patterns concurrently"""
    print(f"📝 Testing concurrent storage: {num_patterns} patterns, {concurrency} concurrent")

    # Generate test patterns
    patterns = []
    for i in range(num_patterns):
        patterns.append({
            'content': f"Scalability test pattern {i}: " + " ".join([
                f"operation_{j}" for j in range(random.randint(5, 15))
            ]),
            'context': {
                'tool': f'scalability_test_{i % 5}',
                'user': f'test_user_{i % 3}',
                'session': f'session_{i // 10}',
                'timestamp': time.time(),
                'test_batch': i // concurrency
            },
            'category': f'scalability_category_{i % 3}'
        })

    # Store patterns concurrently
    start_time = time.time()

    async def store_pattern(pattern):
        try:
            pattern_id = await memory_router.store_pattern(
                pattern['content'],
                pattern['context'],
                pattern['category']
            )
            return {'success': True, 'pattern_id': pattern_id, 'content': pattern['content']}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # Process in batches for controlled concurrency
    results = []
    for i in range(0, len(patterns), concurrency):
        batch = patterns[i:i+concurrency]
        batch_start = time.time()

        # Run batch concurrently
        batch_tasks = [store_pattern(pattern) for pattern in batch]
        batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

        batch_time = time.time() - batch_start
        successful = sum(1 for r in batch_results if isinstance(r, dict) and r.get('success', False))

        print(f"  Batch {i//concurrency + 1}: {successful}/{len(batch)} patterns stored in {batch_time:.3f}s")
        results.extend(batch_results)

    total_time = time.time() - start_time
    successful_patterns = sum(1 for r in results if isinstance(r, dict) and r.get('success', False))

    print(f"✅ Storage Test: {successful_patterns}/{num_patterns} patterns stored")
    print(f"   Total time: {total_time:.3f}s")
    print(f"   Rate: {successful_patterns/total_time:.1f} patterns/second")

    return {
        'success': successful_patterns >= num_patterns * 0.8,  # 80% success rate required
        'total_patterns': num_patterns,
        'successful_patterns': successful_patterns,
        'total_time': total_time,
        'patterns_per_second': successful_patterns / total_time,
        'results': results
    }

async def test_concurrent_pattern_search(memory_router, num_searches: int = 30, concurrency: int = 5):
    """Test searching patterns concurrently"""
    print(f"🔍 Testing concurrent search: {num_searches} searches, {concurrency} concurrent")

    # Generate diverse search queries
    search_queries = [
        "scalability test pattern",
        "operation_1 operation_2",
        "test_user_0",
        "session_1",
        "scalability_category_0",
        "concurrent operations",
        "pattern storage",
        "test batch processing",
        "user session data",
        "category classification"
    ]

    # Create search tasks
    searches = []
    for i in range(num_searches):
        query = random.choice(search_queries)
        top_k = random.randint(3, 10)
        threshold = random.uniform(0.5, 0.8)

        searches.append({
            'query': query,
            'top_k': top_k,
            'threshold': threshold,
            'search_id': i
        })

    start_time = time.time()

    async def search_patterns(search_spec):
        try:
            search_start = time.time()
            results = await memory_router.search_patterns(
                search_spec['query'],
                top_k=search_spec['top_k'],
                threshold=search_spec['threshold']
            )
            search_time = time.time() - search_start

            return {
                'success': True,
                'search_id': search_spec['search_id'],
                'query': search_spec['query'],
                'results_count': len(results) if results else 0,
                'search_time': search_time
            }
        except Exception as e:
            return {
                'success': False,
                'search_id': search_spec['search_id'],
                'error': str(e)
            }

    # Process searches in batches
    results = []
    for i in range(0, len(searches), concurrency):
        batch = searches[i:i+concurrency]
        batch_start = time.time()

        # Run batch concurrently
        batch_tasks = [search_patterns(search) for search in batch]
        batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

        batch_time = time.time() - batch_start
        successful = sum(1 for r in batch_results if isinstance(r, dict) and r.get('success', False))

        total_results = sum(r.get('results_count', 0) for r in batch_results if isinstance(r, dict) and r.get('success', False))
        avg_search_time = sum(r.get('search_time', 0) for r in batch_results if isinstance(r, dict) and r.get('success', False)) / max(successful, 1)

        print(f"  Batch {i//concurrency + 1}: {successful}/{len(batch)} searches completed in {batch_time:.3f}s")
        print(f"    Avg search time: {avg_search_time:.3f}s, Total results: {total_results}")

        results.extend(batch_results)

    total_time = time.time() - start_time
    successful_searches = sum(1 for r in results if isinstance(r, dict) and r.get('success', False))

    print(f"✅ Search Test: {successful_searches}/{num_searches} searches completed")
    print(f"   Total time: {total_time:.3f}s")
    print(f"   Rate: {successful_searches/total_time:.1f} searches/second")

    return {
        'success': successful_searches >= num_searches * 0.8,  # 80% success rate required
        'total_searches': num_searches,
        'successful_searches': successful_searches,
        'total_time': total_time,
        'searches_per_second': successful_searches / total_time,
        'results': results
    }

async def test_mixed_workload(memory_router, duration_seconds: int = 30):
    """Test mixed read/write workload for sustained period"""
    print(f"⚡ Testing mixed workload for {duration_seconds} seconds...")

    start_time = time.time()
    end_time = start_time + duration_seconds

    operations = []
    operation_id = 0

    async def store_operation():
        nonlocal operation_id
        op_id = operation_id
        operation_id += 1

        content = f"Mixed workload pattern {op_id}: continuous operation testing"
        context = {
            'operation_type': 'mixed_workload',
            'operation_id': op_id,
            'timestamp': time.time()
        }
        category = f'mixed_category_{op_id % 5}'

        try:
            pattern_id = await memory_router.store_pattern(content, context, category)
            return {'type': 'store', 'success': True, 'operation_id': op_id}
        except Exception as e:
            return {'type': 'store', 'success': False, 'operation_id': op_id, 'error': str(e)}

    async def search_operation():
        queries = ["mixed workload", "continuous operation", "pattern testing", "sustained load"]
        query = random.choice(queries)

        try:
            results = await memory_router.search_patterns(query, top_k=5, threshold=0.6)
            return {'type': 'search', 'success': True, 'results_count': len(results) if results else 0}
        except Exception as e:
            return {'type': 'search', 'success': False, 'error': str(e)}

    # Run mixed operations
    while time.time() < end_time:
        # Create a batch of mixed operations
        batch_operations = []
        for _ in range(10):  # 10 operations per batch
            if random.random() < 0.7:  # 70% store, 30% search
                batch_operations.append(store_operation())
            else:
                batch_operations.append(search_operation())

        # Execute batch
        batch_results = await asyncio.gather(*batch_operations, return_exceptions=True)
        operations.extend(batch_results)

        # Brief pause between batches
        await asyncio.sleep(0.1)

    total_time = time.time() - start_time
    successful_ops = sum(1 for op in operations if isinstance(op, dict) and op.get('success', False))
    store_ops = sum(1 for op in operations if isinstance(op, dict) and op.get('type') == 'store' and op.get('success', False))
    search_ops = sum(1 for op in operations if isinstance(op, dict) and op.get('type') == 'search' and op.get('success', False))

    print(f"✅ Mixed Workload: {successful_ops} operations in {total_time:.3f}s")
    print(f"   Store operations: {store_ops}")
    print(f"   Search operations: {search_ops}")
    print(f"   Rate: {successful_ops/total_time:.1f} operations/second")

    return {
        'success': successful_ops > 0 and total_time <= duration_seconds + 5,  # Allow some buffer
        'total_operations': len(operations),
        'successful_operations': successful_ops,
        'store_operations': store_ops,
        'search_operations': search_ops,
        'total_time': total_time,
        'operations_per_second': successful_ops / total_time
    }

async def run_scalability_tests():
    """Run comprehensive scalability tests"""
    print("🚀 V2 System Scalability Tests")
    print("=" * 50)

    try:
        # Create memory router
        print("🔧 Initializing test memory router...")
        memory_router = await create_test_hybrid_memory()
        print("✅ Memory router initialized")

        # Run scalability tests
        tests = [
            ("Concurrent Storage", lambda: test_concurrent_pattern_storage(memory_router, 50, 10)),
            ("Concurrent Search", lambda: test_concurrent_pattern_search(memory_router, 30, 5)),
            ("Mixed Workload", lambda: test_mixed_workload(memory_router, 15)),
        ]

        results = {}
        total_start_time = time.time()

        for test_name, test_func in tests:
            print(f"\n🧪 Running {test_name}...")
            test_start = time.time()

            try:
                result = await test_func()
                test_time = time.time() - test_start
                results[test_name] = {
                    **result,
                    'test_time': test_time
                }

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

        # Generate summary report
        print(f"\n📊 Scalability Test Results")
        print("=" * 50)

        passed = sum(1 for r in results.values() if r.get('success', False))
        total = len(results)
        success_rate = (passed / total) * 100

        print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        print(f"Total Test Time: {total_time:.3f}s")
        print()

        for test_name, result in results.items():
            status = "✅" if result.get('success', False) else "❌"
            print(f"{status} {test_name}: {result['test_time']:.3f}s")

            if 'patterns_per_second' in result:
                print(f"   Performance: {result['patterns_per_second']:.1f} patterns/second")
            elif 'searches_per_second' in result:
                print(f"   Performance: {result['searches_per_second']:.1f} searches/second")
            elif 'operations_per_second' in result:
                print(f"   Performance: {result['operations_per_second']:.1f} operations/second")

            if 'error' in result:
                print(f"   Error: {result['error']}")

        print()
        if success_rate >= 80:
            print("🎉 V2 system shows excellent scalability characteristics!")
            print("   Ready for high-load production environments")
        else:
            print("⚠️ Scalability needs improvement")
            print("   Consider optimization before production deployment")

        return success_rate >= 80

    except Exception as e:
        print(f"❌ Scalability test suite failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_scalability_tests())
    sys.exit(0 if success else 1)
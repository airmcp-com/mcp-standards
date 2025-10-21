#!/usr/bin/env python3
"""
Debug Search Functionality
Simple test to identify why search operations are failing.
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from src.mcp_standards.memory.v2.test_hybrid_memory import create_test_hybrid_memory

async def debug_search():
    """Debug search functionality step by step"""
    print("🔍 Debugging Search Functionality")
    print("=" * 40)

    try:
        # Create memory router
        print("1. Creating memory router...")
        memory_router = await create_test_hybrid_memory()
        print("✅ Memory router created")

        # Store a simple pattern first
        print("\n2. Storing test pattern...")
        pattern_id = await memory_router.store_pattern(
            "This is a simple test pattern for search debugging",
            {"test": "search_debug", "type": "simple"},
            "debug_category"
        )
        print(f"✅ Pattern stored with ID: {pattern_id}")

        # Try basic search
        print("\n3. Testing basic search...")
        try:
            results = await memory_router.search_patterns(
                "simple test pattern",
                top_k=5,
                threshold=0.1  # Very low threshold
            )
            print(f"✅ Search completed, found {len(results) if results else 0} results")
            if results:
                for i, result in enumerate(results):
                    print(f"   Result {i+1}: {result}")
            else:
                print("   No results found")

        except Exception as e:
            print(f"❌ Search failed: {e}")
            import traceback
            traceback.print_exc()

        # Test AgentDB search directly
        print("\n4. Testing AgentDB search directly...")
        try:
            agentdb_results = await memory_router.agentdb.search_patterns(
                "simple test pattern",
                top_k=5,
                threshold=0.1
            )
            print(f"✅ AgentDB search: {len(agentdb_results) if agentdb_results else 0} results")
            if agentdb_results:
                for i, result in enumerate(agentdb_results):
                    print(f"   AgentDB Result {i+1}: {result}")

        except Exception as e:
            print(f"❌ AgentDB search failed: {e}")
            import traceback
            traceback.print_exc()

        # Test SQLite search directly
        print("\n5. Testing SQLite search directly...")
        try:
            sqlite_results = await memory_router.sqlite.search_patterns(
                "simple test pattern",
                top_k=5
            )
            print(f"✅ SQLite search: {len(sqlite_results) if sqlite_results else 0} results")
            if sqlite_results:
                for i, result in enumerate(sqlite_results):
                    print(f"   SQLite Result {i+1}: {result}")

        except Exception as e:
            print(f"❌ SQLite search failed: {e}")
            import traceback
            traceback.print_exc()

        print("\n6. Checking pattern storage status...")
        # Check if patterns are actually stored
        try:
            # Check AgentDB statistics
            stats = await memory_router.agentdb.get_stats()
            print(f"✅ AgentDB stats: {stats}")
        except Exception as e:
            print(f"❌ Failed to get AgentDB stats: {e}")

    except Exception as e:
        print(f"❌ Overall test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_search())
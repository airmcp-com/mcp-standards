#!/usr/bin/env python3
"""
Test Production AgentDB Adapter

Test the new HTTP-based AgentDB adapter
"""

import asyncio
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.mcp_standards.memory.v2.agentdb_adapter_new import AgentDBAdapter, AgentDBConfig, VectorSearchResult


async def test_production_agentdb():
    """Test the production AgentDB adapter"""
    print("🔬 Testing Production AgentDB Adapter")
    print("=" * 50)

    # Create adapter with configuration
    config = AgentDBConfig(
        http_host="localhost",
        http_port=3002,
        timeout=10,
        vector_dimension=1536
    )

    adapter = AgentDBAdapter(config)

    try:
        # Test initialization
        print("⚡ Initializing AgentDB adapter...")
        success = await adapter.initialize()

        if not success:
            print("❌ Failed to initialize AgentDB adapter")
            return

        print("✅ AgentDB adapter initialized successfully")

        # Test vector storage
        print("\n📥 Testing vector storage...")
        test_vector = [0.1] * 1536  # Create 1536-dimensional test vector
        test_metadata = {
            "pattern_type": "correction",
            "category": "package-management",
            "description": "test pattern",
            "confidence": 0.8
        }

        stored_id = await adapter.store_vector(test_vector, test_metadata)
        print(f"✅ Vector stored with ID: {stored_id}")

        # Test vector search
        print("\n🔍 Testing vector search...")
        search_results = await adapter.search_vectors(
            query_vector=test_vector,
            top_k=5,
            similarity_threshold=0.0
        )

        print(f"✅ Found {len(search_results)} similar vectors")
        for i, result in enumerate(search_results):
            print(f"   {i+1}. ID: {result.vector_id}")
            print(f"      Similarity: {result.similarity_score:.3f}")
            print(f"      Metadata: {result.metadata}")

        # Test statistics
        print("\n📊 Testing statistics...")
        stats = await adapter.get_statistics()
        print(f"✅ Database statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")

        # Test multiple vectors
        print("\n📦 Testing multiple vectors...")
        for i in range(3):
            vector = [0.1 + i * 0.1] * 1536
            metadata = {
                "pattern_type": "test",
                "index": i,
                "description": f"test pattern {i}"
            }
            vector_id = await adapter.store_vector(vector, metadata)
            print(f"   Stored vector {i+1}: {vector_id}")

        # Search again to see all vectors
        print("\n🔍 Searching all patterns...")
        all_results = await adapter.search_vectors(
            query_vector=test_vector,
            top_k=10,
            similarity_threshold=0.0
        )

        print(f"✅ Total vectors found: {len(all_results)}")
        for result in all_results:
            print(f"   • {result.vector_id}: {result.metadata.get('description')} (sim: {result.similarity_score:.3f})")

        print("\n✅ Production AgentDB adapter test completed successfully!")

    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await adapter.close()


if __name__ == "__main__":
    asyncio.run(test_production_agentdb())
#!/usr/bin/env python3
"""
Quick Test - V2 Memory System

Simple script to quickly test the V2 memory system with realistic patterns.
"""

import asyncio
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mcp_standards.hooks.pattern_extractor_v2 import create_pattern_extractor_v2


async def quick_test():
    """Quick test of V2 pattern extraction"""
    print("🧪 Quick V2 Memory System Test")
    print("=" * 40)

    # Initialize V2 system
    print("⚡ Initializing V2 system...")
    extractor = await create_pattern_extractor_v2()

    try:
        # Test 1: Package management correction
        print("\n📦 Test 1: Package management correction")
        patterns = await extractor.extract_patterns(
            "Bash",
            {"command": "pip install requests"},
            "Actually, use uv not pip for better performance"
        )
        print(f"   Detected {len(patterns)} patterns:")
        for p in patterns:
            print(f"   • {p.pattern_type}: {p.description} (confidence: {p.confidence:.2f})")

        # Test 2: Testing workflow
        print("\n🧪 Test 2: Testing workflow")
        # First edit a file
        await extractor.extract_patterns("Edit", {"file_path": "src/app.py"}, "File updated")
        # Then run tests
        patterns = await extractor.extract_patterns(
            "Bash",
            {"command": "pytest tests/"},
            "Tests passed: 12 passed in 1.5s"
        )
        print(f"   Detected {len(patterns)} patterns:")
        for p in patterns:
            print(f"   • {p.pattern_type}: {p.description} (confidence: {p.confidence:.2f})")

        # Test 3: Semantic search
        print("\n🔍 Test 3: Semantic search")
        results = await extractor.find_similar_patterns(
            "package management tools",
            min_confidence=0.2,
            top_k=3
        )
        print(f"   Found {len(results)} similar patterns:")
        for r in results:
            print(f"   • {r['pattern_text']} (similarity: {r['similarity']:.3f})")

        # Test 4: Multiple corrections of same type
        print("\n🔄 Test 4: Multiple similar corrections")
        corrections = [
            "Prefer uv over pip for dependency management",
            "Use uv instead of pip for faster installs",
            "Switch from yarn to npm for better performance"
        ]

        for correction in corrections:
            patterns = await extractor.extract_patterns("Bash", {"command": "install"}, correction)
            print(f"   '{correction}' → {len(patterns)} patterns")

        # Test 5: Search for learned patterns
        print("\n📚 Test 5: Search learned patterns")
        search_queries = ["python packaging", "dependency management", "package tools"]
        for query in search_queries:
            results = await extractor.find_similar_patterns(query, min_confidence=0.2, top_k=2)
            print(f"   '{query}' → {len(results)} results")

        print("\n✅ Quick test completed successfully!")

    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await extractor.close()


if __name__ == "__main__":
    asyncio.run(quick_test())
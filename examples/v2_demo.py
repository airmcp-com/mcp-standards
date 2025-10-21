#!/usr/bin/env python3
"""
V2 Memory System Local Demo

This script demonstrates how to use the new V2 memory system locally
with semantic pattern clustering and hybrid memory storage.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to Python path for local imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mcp_standards.hooks.pattern_extractor_v2 import (
    PatternExtractorV2,
    create_pattern_extractor_v2
)
from src.mcp_standards.memory.v2.test_hybrid_memory import create_test_hybrid_memory


class V2DemoRunner:
    """Interactive demo of V2 memory system"""

    def __init__(self):
        self.extractor = None
        self.memory_router = None

    async def setup(self):
        """Initialize V2 memory system"""
        print("🚀 Initializing V2 Memory System...")
        print("   📊 Setting up hybrid memory (AgentDB + SQLite)")
        print("   🧠 Loading semantic pattern extractor")

        # Create V2 pattern extractor with hybrid memory
        self.extractor = await create_pattern_extractor_v2()
        self.memory_router = self.extractor.memory_router

        print("✅ V2 Memory System ready!")
        print()

    async def demo_pattern_extraction(self):
        """Demonstrate pattern extraction with semantic clustering"""
        print("=" * 60)
        print("🔍 DEMO 1: Pattern Extraction with Semantic Clustering")
        print("=" * 60)

        # Test scenarios that would create patterns
        test_scenarios = [
            # Correction patterns
            {
                "tool": "Bash",
                "args": {"command": "pip install requests"},
                "result": "Actually, use uv not pip for better package management",
                "description": "Package manager correction"
            },
            {
                "tool": "Bash",
                "args": {"command": "yarn install lodash"},
                "result": "Prefer npm over yarn for this project",
                "description": "JavaScript package manager preference"
            },
            {
                "tool": "Bash",
                "args": {"command": "python setup.py install"},
                "result": "Switch to uv from pip for dependency management",
                "description": "Python packaging tool correction"
            },
            # Workflow patterns
            {
                "tool": "Edit",
                "args": {"file_path": "src/app.py"},
                "result": "File updated successfully",
                "description": "Code change"
            },
            {
                "tool": "Bash",
                "args": {"command": "pytest tests/"},
                "result": "Tests passed: 15 passed in 2.1s",
                "description": "Testing after code change"
            },
            # Tool preferences
            {
                "tool": "Bash",
                "args": {"command": "uv add fastapi"},
                "result": "Package installed successfully",
                "description": "Using preferred package manager"
            }
        ]

        all_patterns = []
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n📝 Scenario {i}: {scenario['description']}")
            print(f"   Tool: {scenario['tool']}")
            print(f"   Args: {scenario['args']}")
            print(f"   Result: {scenario['result']}")

            # Extract patterns
            patterns = await self.extractor.extract_patterns(
                scenario['tool'],
                scenario['args'],
                scenario['result']
            )

            print(f"   🎯 Detected {len(patterns)} pattern(s):")
            for pattern in patterns:
                print(f"      • Type: {pattern.pattern_type}")
                print(f"        Category: {pattern.category}")
                print(f"        Description: {pattern.description}")
                print(f"        Confidence: {pattern.confidence:.2f}")

            all_patterns.extend(patterns)

        print(f"\n✅ Total patterns extracted: {len(all_patterns)}")
        return all_patterns

    async def demo_semantic_search(self):
        """Demonstrate semantic search capabilities"""
        print("\n" + "=" * 60)
        print("🔎 DEMO 2: Semantic Pattern Search")
        print("=" * 60)

        # Test semantic searches
        search_queries = [
            "package management tools",
            "python dependency management",
            "testing workflow",
            "code quality tools",
            "javascript package managers"
        ]

        for query in search_queries:
            print(f"\n🔍 Searching for: '{query}'")

            try:
                results = await self.extractor.find_similar_patterns(
                    query,
                    min_confidence=0.2,  # Lower threshold for demo
                    top_k=3
                )

                print(f"   Found {len(results)} relevant patterns:")
                for result in results:
                    print(f"      • {result['pattern_text']}")
                    print(f"        Similarity: {result['similarity']:.3f}")
                    print(f"        Category: {result['category']}")

            except Exception as e:
                print(f"   ⚠️  Search error: {e}")

    async def demo_learned_preferences(self):
        """Demonstrate learned preferences retrieval"""
        print("\n" + "=" * 60)
        print("🎓 DEMO 3: Learned Preferences")
        print("=" * 60)

        categories = ["package-management", "testing", "general"]

        for category in categories:
            print(f"\n📚 Learned preferences for '{category}':")

            try:
                preferences = await self.extractor.get_learned_preferences(
                    category=category,
                    min_confidence=0.3
                )

                if preferences:
                    for pref in preferences:
                        print(f"      • {pref['pattern_text']}")
                        print(f"        Confidence: {pref['confidence']:.3f}")
                else:
                    print("      (No preferences learned yet)")

            except Exception as e:
                print(f"   ⚠️  Error: {e}")

    async def demo_performance_stats(self):
        """Show performance statistics"""
        print("\n" + "=" * 60)
        print("📊 DEMO 4: Performance Statistics")
        print("=" * 60)

        try:
            stats = await self.extractor.get_pattern_statistics()

            print("🔧 Memory System Status:")
            memory_stats = stats.get('memory_stats', {})
            system_status = memory_stats.get('system_status', {})

            print(f"   AgentDB Available: {'✅' if system_status.get('agentdb_available') else '❌'}")
            print(f"   SQLite Available: {'✅' if system_status.get('sqlite_available') else '❌'}")

            print("\n📈 Pattern Statistics:")
            pattern_stats = stats.get('pattern_stats', {})
            print(f"   Total Patterns: {pattern_stats.get('total_patterns', 0)}")
            print(f"   Pattern Types: {pattern_stats.get('pattern_types', [])}")
            print(f"   Categories: {pattern_stats.get('categories', [])}")

            print("\n⚡ Performance Metrics:")
            router_stats = memory_stats.get('router_stats', {})
            print(f"   Total Queries: {router_stats.get('queries_total', 0)}")
            print(f"   Avg Query Time: {router_stats.get('avg_query_time_ms', 0):.2f}ms")

        except Exception as e:
            print(f"⚠️  Stats error: {e}")

    async def interactive_test(self):
        """Interactive testing mode"""
        print("\n" + "=" * 60)
        print("🎮 INTERACTIVE MODE")
        print("=" * 60)
        print("Test your own patterns! Enter tool executions and see what patterns are detected.")
        print("Type 'quit' to exit, 'search <query>' to search patterns, or 'stats' for statistics.\n")

        while True:
            try:
                # Get user input
                tool_name = input("🔧 Tool name (e.g., 'Bash', 'Edit'): ").strip()
                if tool_name.lower() == 'quit':
                    break
                elif tool_name.lower().startswith('search '):
                    query = tool_name[7:].strip()
                    await self._search_interactive(query)
                    continue
                elif tool_name.lower() == 'stats':
                    await self.demo_performance_stats()
                    continue

                command = input("💻 Command/args (e.g., 'pip install requests'): ").strip()
                result = input("📄 Result/feedback (e.g., 'use uv not pip'): ").strip()

                if not tool_name or not result:
                    print("⚠️  Please provide at least tool name and result.")
                    continue

                # Process the input
                print(f"\n🔄 Processing...")
                args = {"command": command} if command else {}

                # Debug information
                print(f"🔧 Debug info:")
                print(f"   Tool: '{tool_name}'")
                print(f"   Args: {args}")
                print(f"   Result: '{result}'")

                try:
                    patterns = await self.extractor.extract_patterns(tool_name, args, result)

                    print(f"🎯 Detected {len(patterns)} pattern(s):")
                    for pattern in patterns:
                        print(f"   • {pattern.pattern_type}: {pattern.description}")
                        print(f"     Category: {pattern.category}, Confidence: {pattern.confidence:.2f}")

                except Exception as pattern_error:
                    print(f"❌ Pattern extraction error: {pattern_error}")
                    import traceback
                    traceback.print_exc()
                    continue

                print()

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"⚠️  Unexpected error: {e}")
                import traceback
                traceback.print_exc()

    async def _search_interactive(self, query):
        """Handle interactive search"""
        print(f"\n🔍 Searching for: '{query}'")
        try:
            results = await self.extractor.find_similar_patterns(query, min_confidence=0.2, top_k=5)
            if results:
                for result in results:
                    print(f"   • {result['pattern_text']} (similarity: {result['similarity']:.3f})")
            else:
                print("   No patterns found.")
        except Exception as e:
            print(f"   ⚠️  Search error: {e}")
        print()

    async def cleanup(self):
        """Clean up resources"""
        if self.extractor:
            await self.extractor.close()
        print("🧹 Cleanup completed.")

    async def run_full_demo(self):
        """Run the complete demo"""
        try:
            await self.setup()
            await self.demo_pattern_extraction()
            await self.demo_semantic_search()
            await self.demo_learned_preferences()
            await self.demo_performance_stats()

            # Ask if user wants interactive mode
            print("\n" + "=" * 60)
            print("🎯 Demo completed! Would you like to try interactive mode? (y/n)")
            choice = input("Choice: ").strip().lower()

            if choice in ['y', 'yes']:
                await self.interactive_test()

        finally:
            await self.cleanup()


async def main():
    """Main demo function"""
    print("🌟 Welcome to the V2 Memory System Demo!")
    print("This demo shows the new semantic pattern clustering capabilities.\n")

    demo = V2DemoRunner()
    await demo.run_full_demo()


if __name__ == "__main__":
    asyncio.run(main())
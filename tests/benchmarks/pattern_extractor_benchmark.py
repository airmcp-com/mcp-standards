"""
Performance Benchmark: Pattern Extractor V1 vs V2

Compares performance and accuracy between the current regex-based
pattern extractor and the new semantic clustering implementation.
"""

import asyncio
import time
import tempfile
from pathlib import Path
from typing import List, Dict, Any
import statistics

# Import V1 (current) pattern extractor
from src.mcp_standards.hooks.pattern_extractor import PatternExtractor as PatternExtractorV1

# Import V2 (semantic) pattern extractor
from src.mcp_standards.hooks.pattern_extractor_v2 import (
    PatternExtractorV2,
    create_pattern_extractor_v2
)


class PatternExtractorBenchmark:
    """Benchmark suite for pattern extractors"""

    def __init__(self):
        self.test_scenarios = [
            # Correction patterns
            ("Bash", {"command": "pip install requests"}, "Actually use uv not pip for package management"),
            ("Bash", {"command": "npm install"}, "Should prefer yarn over npm for this project"),
            ("Bash", {"command": "pip install"}, "Use poetry instead of pip for dependency management"),
            ("Bash", {"command": "pytest"}, "Switch to jest from pytest for JavaScript testing"),
            ("Bash", {"command": "git add ."}, "Always create feature branches, never commit to main"),

            # Workflow patterns
            ("Edit", {"file_path": "src/app.py"}, "File edited successfully"),
            ("Bash", {"command": "pytest tests/"}, "Tests passed: 15 tests in 2.3s"),
            ("Write", {"file_path": "README.md"}, "Documentation updated"),
            ("Bash", {"command": "git commit -m 'Add feature'"}, "Committed successfully"),
            ("Bash", {"command": "docker build ."}, "Build completed successfully"),

            # Tool preferences
            ("Bash", {"command": "uv add fastapi"}, "Package installed successfully"),
            ("Bash", {"command": "yarn build"}, "Build completed in 12.3s"),
            ("Bash", {"command": "poetry run pytest"}, "Test suite completed"),
            ("Bash", {"command": "npx create-react-app"}, "React app created"),
            ("Bash", {"command": "cargo test"}, "All tests passed"),

            # Complex scenarios
            ("Edit", {"file_path": "src/database.py"}, "Database connection updated"),
            ("Bash", {"command": "mypy src/"}, "Type checking completed with 0 errors"),
            ("Bash", {"command": "black src/"}, "Code formatted successfully"),
            ("Bash", {"command": "isort src/"}, "Imports sorted"),
            ("Bash", {"command": "flake8 src/"}, "Linting completed"),
        ]

    async def benchmark_v1_extractor(self) -> Dict[str, Any]:
        """Benchmark V1 (regex-based) pattern extractor"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            extractor = PatternExtractorV1(db_path)

            # Warm up
            extractor.extract_patterns("Bash", {"command": "test"}, "warm up")

            # Benchmark
            start_time = time.time()
            all_patterns = []

            for tool_name, args, result in self.test_scenarios:
                patterns = extractor.extract_patterns(tool_name, args, result)
                all_patterns.extend(patterns)

            total_time = time.time() - start_time

            return {
                "version": "V1 (Regex)",
                "total_time_ms": total_time * 1000,
                "avg_time_per_scenario_ms": (total_time / len(self.test_scenarios)) * 1000,
                "total_patterns": len(all_patterns),
                "patterns_per_scenario": len(all_patterns) / len(self.test_scenarios),
                "unique_patterns": len(set(p.description for p in all_patterns if hasattr(p, 'description'))),
                "stats": {"type": "V1_regex_based", "db_path": str(db_path)}
            }

    async def benchmark_v2_extractor(self) -> Dict[str, Any]:
        """Benchmark V2 (semantic clustering) pattern extractor"""
        extractor = await create_pattern_extractor_v2()

        try:
            # Warm up
            await extractor.extract_patterns("Bash", {"command": "test"}, "warm up")

            # Benchmark
            start_time = time.time()
            all_patterns = []

            for tool_name, args, result in self.test_scenarios:
                patterns = await extractor.extract_patterns(tool_name, args, result)
                all_patterns.extend(patterns)

            total_time = time.time() - start_time

            # Get statistics
            stats = await extractor.get_pattern_statistics()

            return {
                "version": "V2 (Semantic)",
                "total_time_ms": total_time * 1000,
                "avg_time_per_scenario_ms": (total_time / len(self.test_scenarios)) * 1000,
                "total_patterns": len(all_patterns),
                "patterns_per_scenario": len(all_patterns) / len(self.test_scenarios),
                "unique_patterns": len(set(p.description for p in all_patterns)),
                "stats": stats
            }

        finally:
            await extractor.close()

    async def benchmark_semantic_search_accuracy(self) -> Dict[str, Any]:
        """Test semantic search accuracy in V2"""
        extractor = await create_pattern_extractor_v2()

        try:
            # Add test patterns
            test_patterns = [
                ("use uv not pip for packages", "python-package"),
                ("prefer poetry over pip", "python-package"),
                ("always use pytest for testing", "testing"),
                ("use npm for JavaScript packages", "javascript-package"),
                ("implement error handling", "general")
            ]

            for text, category in test_patterns:
                await extractor.extract_patterns(
                    "Bash",
                    {"command": "test"},
                    text
                )

            # Test semantic searches
            search_tests = [
                ("package management with uv", ["uv", "pip", "poetry"]),
                ("testing framework", ["pytest", "testing"]),
                ("dependency management", ["package", "pip", "poetry", "uv"]),
                ("error handling", ["error", "handling"])
            ]

            search_results = {}
            for query, expected_terms in search_tests:
                results = await extractor.find_similar_patterns(
                    query,
                    min_confidence=0.3,
                    top_k=5
                )

                # Check if expected terms appear in results
                found_terms = []
                for result in results:
                    text = result['pattern_text'].lower()
                    for term in expected_terms:
                        if term in text:
                            found_terms.append(term)

                search_results[query] = {
                    "results_count": len(results),
                    "found_expected_terms": list(set(found_terms)),
                    "accuracy": len(set(found_terms)) / len(expected_terms) if expected_terms else 0
                }

            avg_accuracy = statistics.mean([r["accuracy"] for r in search_results.values()])

            return {
                "search_tests": search_results,
                "average_accuracy": avg_accuracy,
                "total_searches": len(search_tests)
            }

        finally:
            await extractor.close()

    async def run_full_benchmark(self) -> Dict[str, Any]:
        """Run complete benchmark suite"""
        print("🚀 Starting Pattern Extractor Benchmark...")
        print(f"📊 Testing {len(self.test_scenarios)} scenarios")
        print()

        # Benchmark V1
        print("⏱️  Running V1 (Regex) benchmark...")
        v1_results = await self.benchmark_v1_extractor()

        # Benchmark V2
        print("⏱️  Running V2 (Semantic) benchmark...")
        v2_results = await self.benchmark_v2_extractor()

        # Test semantic accuracy
        print("🎯 Testing semantic search accuracy...")
        accuracy_results = await self.benchmark_semantic_search_accuracy()

        # Calculate improvements
        time_improvement = ((v1_results["total_time_ms"] - v2_results["total_time_ms"]) / v1_results["total_time_ms"]) * 100
        pattern_improvement = v2_results["total_patterns"] - v1_results["total_patterns"]

        results = {
            "test_scenarios": len(self.test_scenarios),
            "v1_results": v1_results,
            "v2_results": v2_results,
            "semantic_accuracy": accuracy_results,
            "performance_comparison": {
                "time_improvement_percent": time_improvement,
                "pattern_detection_improvement": pattern_improvement,
                "v2_faster": time_improvement > 0,
                "v2_more_patterns": pattern_improvement > 0
            }
        }

        return results

    def print_results(self, results: Dict[str, Any]):
        """Print formatted benchmark results"""
        print("\n" + "="*60)
        print("📈 PATTERN EXTRACTOR BENCHMARK RESULTS")
        print("="*60)

        v1 = results["v1_results"]
        v2 = results["v2_results"]
        comp = results["performance_comparison"]
        acc = results["semantic_accuracy"]

        print(f"\n📊 Performance Comparison:")
        print(f"  V1 (Regex):     {v1['total_time_ms']:.1f}ms total ({v1['avg_time_per_scenario_ms']:.2f}ms/scenario)")
        print(f"  V2 (Semantic):  {v2['total_time_ms']:.1f}ms total ({v2['avg_time_per_scenario_ms']:.2f}ms/scenario)")

        if comp['v2_faster']:
            print(f"  🚀 V2 is {comp['time_improvement_percent']:.1f}% faster!")
        else:
            print(f"  ⚠️  V2 is {abs(comp['time_improvement_percent']):.1f}% slower")

        print(f"\n🔍 Pattern Detection:")
        print(f"  V1 patterns:    {v1['total_patterns']} total ({v1['patterns_per_scenario']:.1f}/scenario)")
        print(f"  V2 patterns:    {v2['total_patterns']} total ({v2['patterns_per_scenario']:.1f}/scenario)")
        print(f"  Unique V1:      {v1['unique_patterns']}")
        print(f"  Unique V2:      {v2['unique_patterns']}")

        if comp['v2_more_patterns']:
            print(f"  📈 V2 detected {comp['pattern_detection_improvement']} more patterns")
        else:
            print(f"  📉 V2 detected {abs(comp['pattern_detection_improvement'])} fewer patterns")

        print(f"\n🎯 Semantic Search Accuracy:")
        print(f"  Average accuracy: {acc['average_accuracy']:.1%}")
        print(f"  Test queries:     {acc['total_searches']}")

        for query, result in acc['search_tests'].items():
            print(f"    '{query}': {result['accuracy']:.1%} ({result['results_count']} results)")

        print(f"\n✅ Benchmark completed successfully!")


async def main():
    """Run the benchmark"""
    benchmark = PatternExtractorBenchmark()
    results = await benchmark.run_full_benchmark()
    benchmark.print_results(results)

    return results


if __name__ == "__main__":
    asyncio.run(main())
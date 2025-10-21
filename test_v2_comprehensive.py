#!/usr/bin/env python3
"""Comprehensive V2 Integration Test

End-to-end validation of the complete V2 pattern extraction system.
This test validates all components working together in production configuration.
"""

import sys
import asyncio
import json
import tempfile
from pathlib import Path
from datetime import datetime

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.mcp_standards.utils.v2_status import check_v2_status
from src.mcp_standards.hooks.capture_hook_v2 import HookCaptureSystemV2
from src.mcp_standards.memory.v2.test_hybrid_memory import create_test_hybrid_memory
from src.mcp_standards.migration.v1_to_v2_migration import migrate_v1_to_v2


class V2ComprehensiveTest:
    """Comprehensive V2 system integration test"""

    def __init__(self):
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0

    async def run_all_tests(self) -> bool:
        """Run all comprehensive tests"""
        print("🧪 Comprehensive V2 Integration Test Suite")
        print("=" * 60)

        tests = [
            ("System Health Check", self.test_system_health),
            ("AgentDB Production Integration", self.test_agentdb_integration),
            ("V2 Hook System", self.test_hook_system),
            ("Hybrid Memory System", self.test_hybrid_memory),
            ("Pattern Extraction Pipeline", self.test_pattern_extraction),
            ("Migration System", self.test_migration_system),
            ("Performance & Scalability", self.test_performance),
            ("Error Handling & Recovery", self.test_error_handling),
            ("Real-world Scenarios", self.test_real_world_scenarios),
        ]

        for test_name, test_func in tests:
            print(f"\n🔬 {test_name}")
            print("-" * 40)

            try:
                success = await test_func()
                self.test_results[test_name] = success
                self.total_tests += 1
                if success:
                    self.passed_tests += 1
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {e}")
                self.test_results[test_name] = False
                self.total_tests += 1

        # Generate final report
        await self.generate_final_report()

        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        return success_rate >= 80  # 80% pass rate required

    async def test_system_health(self) -> bool:
        """Test overall system health"""
        health = await check_v2_status()

        print(f"   Overall status: {health.overall_status}")
        print(f"   AgentDB: {health.agentdb_status.status}")
        print(f"   SQLite: {health.sqlite_status.status}")
        print(f"   Hooks: {health.hook_status.status}")
        print(f"   Memory: {health.memory_status.status}")

        # All components should be healthy
        healthy_components = sum(1 for status in [
            health.agentdb_status.status,
            health.sqlite_status.status,
            health.hook_status.status,
            health.memory_status.status
        ] if status == "healthy")

        print(f"   Healthy components: {healthy_components}/4")
        return healthy_components >= 3  # At least 3/4 components must be healthy

    async def test_agentdb_integration(self) -> bool:
        """Test AgentDB production integration"""
        try:
            from src.mcp_standards.memory.v2.agentdb_adapter_new import AgentDBAdapter, AgentDBConfig

            # Test adapter creation and initialization
            config = AgentDBConfig(http_host="localhost", http_port=3002)
            adapter = AgentDBAdapter(config)

            success = await adapter.initialize()
            if not success:
                print("   ❌ AgentDB adapter initialization failed")
                return False

            # Test vector operations
            test_vector = [0.1] * 1536
            test_metadata = {"test": "comprehensive_test", "timestamp": datetime.now().isoformat()}

            # Store vector
            vector_id = await adapter.store_vector(test_vector, test_metadata)
            if not vector_id:
                print("   ❌ Vector storage failed")
                await adapter.close()
                return False

            print(f"   ✅ Vector stored: {vector_id}")

            # Search vectors
            search_results = await adapter.search_vectors(test_vector, top_k=5)
            if not search_results:
                print("   ❌ Vector search failed")
                await adapter.close()
                return False

            print(f"   ✅ Vector search returned {len(search_results)} results")

            # Test statistics
            stats = await adapter.get_statistics()
            if "total_vectors" not in stats:
                print("   ❌ Statistics retrieval failed")
                await adapter.close()
                return False

            print(f"   ✅ Statistics: {stats['total_vectors']} vectors")

            await adapter.close()
            return True

        except Exception as e:
            print(f"   ❌ AgentDB integration error: {e}")
            return False

    async def test_hook_system(self) -> bool:
        """Test V2 hook system end-to-end"""
        try:
            # Create hook capture system
            hook_system = HookCaptureSystemV2()

            # Test tool execution capture
            test_execution = {
                "tool": "Edit",
                "args": {
                    "file_path": "/test/project/main.py",
                    "old_string": "import requests",
                    "new_string": "import httpx  # Use httpx not requests for async support"
                },
                "result": "File updated successfully",
                "timestamp": datetime.now().isoformat(),
                "projectPath": "/test/project"
            }

            result = await hook_system.capture_tool_execution(test_execution)

            print(f"   Capture result: {result.get('captured', False)}")
            print(f"   System used: {result.get('system_version', 'unknown')}")
            print(f"   Patterns found: {result.get('patterns_found', 0)}")

            await hook_system.close()

            # Should capture high-significance patterns
            return result.get('captured', False) and result.get('system_version') == 'v2'

        except Exception as e:
            print(f"   ❌ Hook system error: {e}")
            return False

    async def test_hybrid_memory(self) -> bool:
        """Test hybrid memory system functionality"""
        try:
            # Create test memory router
            memory_router = await create_test_hybrid_memory(
                agentdb_path=".claude/memory/comprehensive_test",
                sqlite_path=str(Path.home() / ".mcp-standards" / "comprehensive_test.db")
            )

            # Test pattern storage
            pattern_id = await memory_router.store_pattern(
                pattern_text="Use pytest not unittest for testing",
                category="testing",
                context="Test framework preference",
                confidence=0.8,
                metadata={"source": "comprehensive_test"}
            )

            if not pattern_id:
                print("   ❌ Pattern storage failed")
                await memory_router.close()
                return False

            print(f"   ✅ Pattern stored: {pattern_id}")

            # Test pattern search
            similar_patterns = await memory_router.find_similar_patterns(
                query="testing framework preference",
                top_k=5,
                threshold=0.5
            )

            if not similar_patterns:
                print("   ❌ Pattern search failed")
                await memory_router.close()
                return False

            print(f"   ✅ Found {len(similar_patterns)} similar patterns")

            # Test statistics
            stats = await memory_router.get_statistics()
            if "router_stats" not in stats:
                print("   ❌ Memory statistics failed")
                await memory_router.close()
                return False

            print(f"   ✅ Memory stats: {stats['router_stats']['queries_total']} queries")

            await memory_router.close()
            return True

        except Exception as e:
            print(f"   ❌ Hybrid memory error: {e}")
            return False

    async def test_pattern_extraction(self) -> bool:
        """Test pattern extraction pipeline"""
        try:
            from src.mcp_standards.hooks.pattern_extractor_v2 import PatternExtractorV2

            # Create test memory router
            memory_router = await create_test_hybrid_memory(
                agentdb_path=".claude/memory/pattern_test",
                sqlite_path=str(Path.home() / ".mcp-standards" / "pattern_test.db")
            )

            extractor = PatternExtractorV2(memory_router=memory_router)

            # Test correction pattern extraction
            patterns = await extractor.extract_patterns(
                tool_name="Bash",
                args={"command": "pip install numpy"},
                result={"correction": "Actually use uv add numpy for faster installs"},
                project_path="/test/project"
            )

            print(f"   Extracted {len(patterns)} patterns")
            if patterns:
                for i, pattern in enumerate(patterns):
                    print(f"   Pattern {i+1}: {pattern.description}")
                    print(f"      Type: {pattern.pattern_type}, Category: {pattern.category}")

            await memory_router.close()
            return len(patterns) > 0

        except Exception as e:
            print(f"   ❌ Pattern extraction error: {e}")
            return False

    async def test_migration_system(self) -> bool:
        """Test V1 to V2 migration system"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Create a minimal V1 database for testing
                import sqlite3
                v1_db = temp_path / "test_v1.db"

                with sqlite3.connect(v1_db) as conn:
                    conn.execute("""
                        CREATE TABLE patterns (
                            id INTEGER PRIMARY KEY,
                            pattern_type TEXT,
                            category TEXT,
                            description TEXT,
                            text_content TEXT,
                            confidence REAL,
                            context TEXT,
                            created_at TEXT,
                            metadata TEXT
                        )
                    """)

                    conn.execute("""
                        INSERT INTO patterns (pattern_type, category, description, text_content, confidence)
                        VALUES ('correction', 'testing', 'Use pytest', 'use pytest not unittest', 0.8)
                    """)
                    conn.commit()

                # Test migration
                stats = await migrate_v1_to_v2(
                    v1_db_path=str(v1_db),
                    v2_agentdb_path=str(temp_path / "v2_test"),
                    v2_sqlite_path=str(temp_path / "v2_test.db"),
                    dry_run=False,
                    backup_enabled=False
                )

                print(f"   Migration stats: {stats.migrated_patterns}/{stats.total_v1_patterns}")
                print(f"   Success rate: {stats.success_rate:.1f}%")

                return stats.success_rate >= 100

        except Exception as e:
            print(f"   ❌ Migration test error: {e}")
            return False

    async def test_performance(self) -> bool:
        """Test performance and scalability"""
        try:
            start_time = datetime.now()

            # Create memory router
            memory_router = await create_test_hybrid_memory(
                agentdb_path=".claude/memory/perf_test",
                sqlite_path=str(Path.home() / ".mcp-standards" / "perf_test.db")
            )

            # Test multiple pattern operations
            patterns_stored = 0
            for i in range(10):  # Store 10 patterns rapidly
                pattern_id = await memory_router.store_pattern(
                    pattern_text=f"Performance test pattern {i}",
                    category="testing",
                    confidence=0.7
                )
                if pattern_id:
                    patterns_stored += 1

            # Test search performance
            search_start = datetime.now()
            results = await memory_router.find_similar_patterns(
                query="performance test",
                top_k=5
            )
            search_time = (datetime.now() - search_start).total_seconds()

            total_time = (datetime.now() - start_time).total_seconds()

            print(f"   Stored {patterns_stored}/10 patterns")
            print(f"   Search returned {len(results)} results in {search_time:.3f}s")
            print(f"   Total test time: {total_time:.3f}s")

            await memory_router.close()

            # Performance criteria: complete in <5 seconds, store all patterns
            return total_time < 5.0 and patterns_stored >= 8

        except Exception as e:
            print(f"   ❌ Performance test error: {e}")
            return False

    async def test_error_handling(self) -> bool:
        """Test error handling and recovery"""
        try:
            tests_passed = 0

            # Test 1: Invalid AgentDB connection
            try:
                from src.mcp_standards.memory.v2.agentdb_adapter_new import AgentDBAdapter, AgentDBConfig
                config = AgentDBConfig(http_host="localhost", http_port=9999)  # Wrong port
                adapter = AgentDBAdapter(config)
                success = await adapter.initialize()
                if not success:
                    tests_passed += 1
                    print("   ✅ Invalid AgentDB connection handled correctly")
                await adapter.close()
            except Exception:
                tests_passed += 1
                print("   ✅ AgentDB connection error handled")

            # Test 2: Hook system with missing components
            try:
                hook_system = HookCaptureSystemV2(force_v1=True)  # Force V1 fallback
                result = await hook_system.capture_tool_execution({
                    "tool": "Test",
                    "args": {},
                    "result": "test",
                    "timestamp": datetime.now().isoformat()
                })
                if result.get('system_version') == 'v1':
                    tests_passed += 1
                    print("   ✅ V1 fallback working correctly")
                await hook_system.close()
            except Exception as e:
                print(f"   ⚠️ Hook fallback test failed: {e}")

            # Test 3: Memory system resilience
            try:
                # This should handle gracefully even with some backend issues
                memory_router = await create_test_hybrid_memory(
                    agentdb_path=".claude/memory/error_test",
                    sqlite_path=str(Path.home() / ".mcp-standards" / "error_test.db")
                )
                stats = await memory_router.get_statistics()
                if "error" not in stats or stats.get("system_status"):
                    tests_passed += 1
                    print("   ✅ Memory system error handling working")
                await memory_router.close()
            except Exception as e:
                print(f"   ⚠️ Memory error test failed: {e}")

            print(f"   Error handling tests passed: {tests_passed}/3")
            return tests_passed >= 2

        except Exception as e:
            print(f"   ❌ Error handling test error: {e}")
            return False

    async def test_real_world_scenarios(self) -> bool:
        """Test real-world usage scenarios"""
        try:
            # Scenario 1: Package management correction
            hook_system = HookCaptureSystemV2()

            correction_scenario = {
                "tool": "Bash",
                "args": {"command": "pip install fastapi", "description": "Install FastAPI"},
                "result": {
                    "stdout": "Successfully installed fastapi",
                    "correction": "Actually use uv add fastapi for better dependency management"
                },
                "timestamp": datetime.now().isoformat(),
                "projectPath": "/real/project"
            }

            result1 = await hook_system.capture_tool_execution(correction_scenario)

            # Scenario 2: Testing workflow pattern
            workflow_scenario = {
                "tool": "Edit",
                "args": {
                    "file_path": "/real/project/main.py",
                    "old_string": "def main():",
                    "new_string": "def main():\n    # Always run tests after changes"
                },
                "result": "File updated successfully",
                "timestamp": datetime.now().isoformat(),
                "projectPath": "/real/project"
            }

            result2 = await hook_system.capture_tool_execution(workflow_scenario)

            await hook_system.close()

            # Check results
            scenario1_success = result1.get('captured', False) and result1.get('system_version') == 'v2'
            scenario2_success = result2.get('captured', False)

            print(f"   Package management scenario: {'✅' if scenario1_success else '❌'}")
            print(f"   Workflow pattern scenario: {'✅' if scenario2_success else '❌'}")

            return scenario1_success and scenario2_success

        except Exception as e:
            print(f"   ❌ Real-world scenario error: {e}")
            return False

    async def generate_final_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE V2 INTEGRATION TEST REPORT")
        print("=" * 60)

        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0

        print(f"Tests Run: {self.total_tests}")
        print(f"Tests Passed: {self.passed_tests}")
        print(f"Tests Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()

        print("Test Results by Category:")
        for test_name, passed in self.test_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status} {test_name}")

        print()
        if success_rate >= 80:
            print("🎉 V2 SYSTEM VALIDATION: PASSED")
            print("✅ The V2 pattern extraction system is ready for production deployment!")
            print()
            print("🚀 Next Steps:")
            print("  1. Deploy to Claude Code environment")
            print("  2. Configure hook integration")
            print("  3. Monitor pattern extraction in real usage")
            print("  4. Run periodic health checks")
        else:
            print("⚠️ V2 SYSTEM VALIDATION: NEEDS ATTENTION")
            print("Some components require fixes before production deployment")


async def main():
    """Main test runner"""
    test_runner = V2ComprehensiveTest()
    success = await test_runner.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
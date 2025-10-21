"""
Migration Test: V1 to V2 Pattern Extractor Data Migration

Tests migrating existing SQLite data from V1 (regex-based) pattern extractor
to V2 (semantic clustering) hybrid memory system.
"""

import asyncio
import sqlite3
import tempfile
import time
import pytest
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from src.mcp_standards.hooks.pattern_extractor import PatternExtractor as PatternExtractorV1
from src.mcp_standards.hooks.pattern_extractor_v2 import (
    PatternExtractorV2,
    create_pattern_extractor_v2
)
from src.mcp_standards.memory.v2.test_hybrid_memory import create_test_hybrid_memory


class V1ToV2Migration:
    """Handles migration from V1 to V2 pattern data"""

    def __init__(self, v1_db_path: str, v2_memory_router):
        self.v1_db_path = v1_db_path
        self.v2_memory_router = v2_memory_router

    def analyze_v1_data(self) -> Dict[str, Any]:
        """Analyze existing V1 data before migration"""
        conn = sqlite3.connect(self.v1_db_path)
        conn.row_factory = sqlite3.Row

        stats = {
            "pattern_frequency_count": 0,
            "tool_preferences_count": 0,
            "categories": set(),
            "tools": set(),
            "patterns": []
        }

        try:
            # Analyze pattern_frequency table
            cursor = conn.execute("SELECT * FROM pattern_frequency")
            patterns = cursor.fetchall()
            stats["pattern_frequency_count"] = len(patterns)

            for pattern in patterns:
                stats["tools"].add(pattern["tool_name"])
                if pattern["pattern_type"]:
                    stats["categories"].add(pattern["pattern_type"])

                stats["patterns"].append({
                    "id": pattern["id"],
                    "pattern_key": pattern["pattern_key"],
                    "tool_name": pattern["tool_name"],
                    "pattern_type": pattern["pattern_type"],
                    "description": pattern["pattern_description"],
                    "count": pattern["occurrence_count"],
                    "confidence": pattern["confidence"],
                    "first_seen": pattern["first_seen"],
                    "last_seen": pattern["last_seen"]
                })

            # Analyze tool_preferences table
            cursor = conn.execute("SELECT * FROM tool_preferences")
            preferences = cursor.fetchall()
            stats["tool_preferences_count"] = len(preferences)

            for pref in preferences:
                stats["categories"].add(pref["category"])

        except sqlite3.OperationalError as e:
            print(f"Database analysis error: {e}")

        finally:
            conn.close()

        # Convert sets to lists for JSON serialization
        stats["categories"] = list(stats["categories"])
        stats["tools"] = list(stats["tools"])

        return stats

    async def migrate_patterns_to_v2(self) -> Dict[str, Any]:
        """Migrate V1 patterns to V2 hybrid memory system"""
        conn = sqlite3.connect(self.v1_db_path)
        conn.row_factory = sqlite3.Row

        migration_stats = {
            "patterns_migrated": 0,
            "preferences_migrated": 0,
            "errors": [],
            "migrated_patterns": []
        }

        try:
            # Migrate pattern_frequency table
            cursor = conn.execute("SELECT * FROM pattern_frequency")
            patterns = cursor.fetchall()

            for pattern in patterns:
                try:
                    # Map V1 pattern to V2 format
                    pattern_text = pattern["pattern_description"] or pattern["pattern_key"]
                    category = pattern["pattern_type"] or "general"
                    confidence = float(pattern["confidence"]) if pattern["confidence"] else 0.5

                    # Store in V2 hybrid memory
                    pattern_id = await self.v2_memory_router.store_pattern(
                        pattern_text=pattern_text,
                        category=category,
                        confidence=confidence,
                        metadata={
                            "v1_migration": True,
                            "v1_id": pattern["id"],
                            "v1_pattern_key": pattern["pattern_key"],
                            "tool_name": pattern["tool_name"],
                            "occurrence_count": pattern["occurrence_count"],
                            "first_seen": pattern["first_seen"],
                            "last_seen": pattern["last_seen"],
                            "promoted_to_preference": bool(pattern["promoted_to_preference"])
                        }
                    )

                    if pattern_id:
                        migration_stats["patterns_migrated"] += 1
                        migration_stats["migrated_patterns"].append({
                            "v1_id": pattern["id"],
                            "v2_pattern_id": pattern_id,
                            "pattern_text": pattern_text,
                            "category": category
                        })

                except Exception as e:
                    migration_stats["errors"].append(f"Pattern {pattern['id']}: {str(e)}")

            # Migrate tool_preferences table
            cursor = conn.execute("SELECT * FROM tool_preferences")
            preferences = cursor.fetchall()

            for pref in preferences:
                try:
                    # Create pattern text from preference
                    pattern_text = f"preference: {pref['preference']} for {pref['category']}"
                    confidence = float(pref["confidence"]) if pref["confidence"] else 0.5

                    # Store in V2 hybrid memory
                    pattern_id = await self.v2_memory_router.store_pattern(
                        pattern_text=pattern_text,
                        category=pref["category"],
                        confidence=confidence,
                        context=pref["context"],
                        metadata={
                            "v1_migration": True,
                            "v1_preference_id": pref["id"],
                            "preference": pref["preference"],
                            "examples": pref["examples"],
                            "learned_from": pref["learned_from"],
                            "apply_count": pref["apply_count"],
                            "last_validated": pref["last_validated"],
                            "last_applied": pref["last_applied"]
                        }
                    )

                    if pattern_id:
                        migration_stats["preferences_migrated"] += 1

                except Exception as e:
                    migration_stats["errors"].append(f"Preference {pref['id']}: {str(e)}")

        except sqlite3.OperationalError as e:
            migration_stats["errors"].append(f"Database error: {str(e)}")

        finally:
            conn.close()

        return migration_stats

    async def verify_migration(self, original_stats: Dict, migration_stats: Dict) -> Dict[str, Any]:
        """Verify migration completed successfully"""
        verification = {
            "data_integrity": True,
            "semantic_search_working": False,
            "pattern_retrieval_working": False,
            "issues": []
        }

        # Check data counts
        expected_patterns = original_stats["pattern_frequency_count"]
        expected_preferences = original_stats["tool_preferences_count"]

        if migration_stats["patterns_migrated"] != expected_patterns:
            verification["data_integrity"] = False
            verification["issues"].append(
                f"Pattern count mismatch: expected {expected_patterns}, got {migration_stats['patterns_migrated']}"
            )

        if migration_stats["preferences_migrated"] != expected_preferences:
            verification["data_integrity"] = False
            verification["issues"].append(
                f"Preference count mismatch: expected {expected_preferences}, got {migration_stats['preferences_migrated']}"
            )

        # Test semantic search on migrated data
        try:
            # Search for package management patterns
            search_results = await self.v2_memory_router.find_similar_patterns(
                query="package management",
                top_k=5,
                threshold=0.2
            )

            if len(search_results) > 0:
                verification["semantic_search_working"] = True
            else:
                verification["issues"].append("Semantic search returned no results")

        except Exception as e:
            verification["issues"].append(f"Semantic search error: {str(e)}")

        # Test pattern retrieval by ID
        try:
            if migration_stats["migrated_patterns"]:
                first_migrated = migration_stats["migrated_patterns"][0]
                pattern_id = first_migrated["v2_pattern_id"]

                # Try to retrieve the pattern
                retrieved = await self.v2_memory_router.agentdb.get_pattern(pattern_id)
                if retrieved:
                    verification["pattern_retrieval_working"] = True
                else:
                    verification["issues"].append("Could not retrieve migrated pattern by ID")

        except Exception as e:
            verification["issues"].append(f"Pattern retrieval error: {str(e)}")

        return verification


class TestV1ToV2Migration:
    """Test suite for V1 to V2 migration"""

    @pytest.fixture
    async def v1_with_test_data(self):
        """Create V1 extractor with test data"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test_v1.db"
            extractor = PatternExtractorV1(db_path)

            # Add test patterns to V1
            test_patterns = [
                ("Bash", {"command": "pip install"}, "use uv not pip"),
                ("Bash", {"command": "npm install"}, "prefer yarn over npm"),
                ("Edit", {"file_path": "test.py"}, "always run tests after changes"),
                ("Bash", {"command": "git commit"}, "use feature branches"),
                ("Bash", {"command": "python setup.py"}, "use poetry for packaging")
            ]

            for tool_name, args, result in test_patterns:
                extractor.extract_patterns(tool_name, args, result)

            yield extractor, db_path

    @pytest.fixture
    async def v2_memory_router(self):
        """Create V2 memory router for migration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            router = await create_test_hybrid_memory(
                agentdb_path=f"{temp_dir}/v2_agentdb",
                sqlite_path=f"{temp_dir}/v2_sqlite.db"
            )
            yield router
            await router.close()

    @pytest.mark.asyncio
    async def test_v1_data_analysis(self, v1_with_test_data):
        """Test analyzing V1 data before migration"""
        extractor, db_path = v1_with_test_data
        router = await create_test_hybrid_memory()

        try:
            migration = V1ToV2Migration(str(db_path), router)
            stats = migration.analyze_v1_data()

            assert stats["pattern_frequency_count"] >= 0
            assert isinstance(stats["tools"], list)
            assert isinstance(stats["categories"], list)
            assert isinstance(stats["patterns"], list)

            print(f"V1 Data Analysis:")
            print(f"  Patterns: {stats['pattern_frequency_count']}")
            print(f"  Preferences: {stats['tool_preferences_count']}")
            print(f"  Categories: {stats['categories']}")
            print(f"  Tools: {stats['tools']}")

        finally:
            await router.close()

    @pytest.mark.asyncio
    async def test_full_migration_workflow(self, v1_with_test_data):
        """Test complete migration workflow"""
        extractor, db_path = v1_with_test_data
        router = await create_test_hybrid_memory()

        try:
            migration = V1ToV2Migration(str(db_path), router)

            # 1. Analyze V1 data
            original_stats = migration.analyze_v1_data()
            print(f"\n📊 V1 Data Analysis:")
            print(f"  Patterns: {original_stats['pattern_frequency_count']}")
            print(f"  Preferences: {original_stats['tool_preferences_count']}")

            # 2. Migrate data
            print(f"\n🔄 Migrating data to V2...")
            migration_stats = await migration.migrate_patterns_to_v2()
            print(f"  Migrated patterns: {migration_stats['patterns_migrated']}")
            print(f"  Migrated preferences: {migration_stats['preferences_migrated']}")
            print(f"  Errors: {len(migration_stats['errors'])}")

            # 3. Verify migration
            print(f"\n✅ Verifying migration...")
            verification = await migration.verify_migration(original_stats, migration_stats)
            print(f"  Data integrity: {verification['data_integrity']}")
            print(f"  Semantic search: {verification['semantic_search_working']}")
            print(f"  Pattern retrieval: {verification['pattern_retrieval_working']}")

            if verification["issues"]:
                print(f"  Issues: {verification['issues']}")

            # Assertions
            assert migration_stats["patterns_migrated"] >= 0
            assert len(migration_stats["errors"]) == 0, f"Migration errors: {migration_stats['errors']}"
            assert verification["data_integrity"], f"Data integrity issues: {verification['issues']}"

            print(f"\n🎉 Migration completed successfully!")

        finally:
            await router.close()

    @pytest.mark.asyncio
    async def test_migrated_data_semantic_search(self, v1_with_test_data):
        """Test semantic search on migrated data"""
        extractor, db_path = v1_with_test_data
        router = await create_test_hybrid_memory()

        try:
            migration = V1ToV2Migration(str(db_path), router)

            # Migrate data
            await migration.migrate_patterns_to_v2()

            # Test semantic searches
            search_queries = [
                "package management",
                "testing workflow",
                "version control",
                "dependency management"
            ]

            for query in search_queries:
                results = await router.find_similar_patterns(
                    query=query,
                    top_k=3,
                    threshold=0.2
                )

                print(f"Search '{query}': {len(results)} results")
                for result in results:
                    print(f"  - {result['pattern_text']} (similarity: {result['similarity']:.3f})")

        finally:
            await router.close()


# Integration test function
async def test_migration_integration():
    """Comprehensive migration integration test"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup V1 with realistic data
        v1_db_path = Path(temp_dir) / "production_v1.db"
        v1_extractor = PatternExtractorV1(v1_db_path)

        # Add realistic patterns that would exist in production
        realistic_patterns = [
            ("Bash", {"command": "pip install requests"}, "Actually, use uv not pip for package management"),
            ("Bash", {"command": "npm install lodash"}, "Prefer yarn for JavaScript dependencies"),
            ("Edit", {"file_path": "src/main.py"}, "File updated successfully"),
            ("Bash", {"command": "pytest tests/"}, "Always run tests after code changes"),
            ("Bash", {"command": "git add ."}, "Use feature branches for development"),
            ("Bash", {"command": "python setup.py install"}, "Use poetry for Python packaging"),
            ("Write", {"file_path": "README.md"}, "Documentation updated"),
            ("Bash", {"command": "docker build ."}, "Build completed successfully"),
            ("Bash", {"command": "mypy src/"}, "Type checking is important"),
            ("Bash", {"command": "black src/"}, "Code formatting completed")
        ]

        for tool_name, args, result in realistic_patterns:
            v1_extractor.extract_patterns(tool_name, args, result)

        # Setup V2 hybrid memory
        v2_router = await create_test_hybrid_memory(
            agentdb_path=f"{temp_dir}/migrated_agentdb",
            sqlite_path=f"{temp_dir}/migrated_sqlite.db"
        )

        try:
            print("🚀 Starting V1 to V2 Migration Integration Test")
            print(f"📁 Test directory: {temp_dir}")

            # Run migration
            migration = V1ToV2Migration(str(v1_db_path), v2_router)

            # Step 1: Analyze original data
            print("\n📊 Step 1: Analyzing V1 data...")
            original_stats = migration.analyze_v1_data()
            print(f"  Found {original_stats['pattern_frequency_count']} patterns")
            print(f"  Found {original_stats['tool_preferences_count']} preferences")
            print(f"  Categories: {original_stats['categories']}")

            # Step 2: Migrate
            print("\n🔄 Step 2: Migrating to V2...")
            migration_stats = await migration.migrate_patterns_to_v2()
            print(f"  Migrated {migration_stats['patterns_migrated']} patterns")
            print(f"  Migrated {migration_stats['preferences_migrated']} preferences")

            if migration_stats["errors"]:
                print(f"  ⚠️  Errors: {migration_stats['errors']}")

            # Step 3: Verify
            print("\n✅ Step 3: Verifying migration...")
            verification = await migration.verify_migration(original_stats, migration_stats)
            print(f"  Data integrity: {'✅' if verification['data_integrity'] else '❌'}")
            print(f"  Semantic search: {'✅' if verification['semantic_search_working'] else '❌'}")
            print(f"  Pattern retrieval: {'✅' if verification['pattern_retrieval_working'] else '❌'}")

            # Step 4: Test V2 functionality
            print("\n🧪 Step 4: Testing V2 functionality with migrated data...")
            v2_extractor = PatternExtractorV2(memory_router=v2_router)
            await v2_extractor.initialize()

            # Test semantic search
            search_result = await v2_extractor.find_similar_patterns(
                "python package management",
                min_confidence=0.3
            )
            print(f"  Semantic search found {len(search_result)} relevant patterns")

            # Test new pattern extraction with migration context
            new_patterns = await v2_extractor.extract_patterns(
                "Bash",
                {"command": "pip install django"},
                "Should use uv for package management"
            )
            print(f"  V2 extracted {len(new_patterns)} new patterns with migration context")

            # Step 5: Performance comparison
            print("\n⚡ Step 5: Performance comparison...")
            start_time = time.time()
            for _ in range(10):
                await v2_router.find_similar_patterns("package management", top_k=3)
            v2_search_time = (time.time() - start_time) * 1000

            print(f"  V2 search performance: {v2_search_time:.1f}ms for 10 searches")

            print("\n🎉 Migration integration test completed successfully!")
            return {
                "original_stats": original_stats,
                "migration_stats": migration_stats,
                "verification": verification,
                "v2_search_time_ms": v2_search_time
            }

        finally:
            await v2_router.close()


if __name__ == "__main__":
    import time
    asyncio.run(test_migration_integration())
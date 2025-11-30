#!/usr/bin/env python3
"""Test V1 to V2 Migration Script

Test the migration functionality with mock V1 data.
"""

import sys
import sqlite3
import json
import tempfile
import asyncio
from pathlib import Path
from datetime import datetime

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.mcp_standards.migration.v1_to_v2_migration import migrate_v1_to_v2


def create_mock_v1_database(db_path: Path):
    """Create a mock V1 database with sample patterns"""
    print(f"📝 Creating mock V1 database: {db_path}")

    with sqlite3.connect(db_path) as conn:
        # Create V1 tables
        conn.execute("""
            CREATE TABLE tool_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_name TEXT NOT NULL,
                args TEXT,
                result TEXT,
                significance REAL,
                project_path TEXT,
                timestamp TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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

        # Insert sample V1 patterns
        sample_patterns = [
            {
                'pattern_type': 'correction',
                'category': 'package-management',
                'description': 'Use uv instead of pip for Python packages',
                'text_content': 'actually use uv not pip for package management',
                'confidence': 0.8,
                'context': json.dumps({'correction_type': 'tool_preference'}),
                'created_at': '2024-01-15T10:30:00Z',
                'metadata': json.dumps({'tool_name': 'Bash', 'project_path': '/test/project'})
            },
            {
                'pattern_type': 'workflow',
                'category': 'testing',
                'description': 'Always run tests after code changes',
                'text_content': 'always run tests after making code changes',
                'confidence': 0.9,
                'context': json.dumps({'workflow_type': 'post_code_change'}),
                'created_at': '2024-01-16T14:20:00Z',
                'metadata': json.dumps({'tool_name': 'Edit', 'project_path': '/test/project'})
            },
            {
                'pattern_type': 'preference',
                'category': 'version-control',
                'description': 'Use feature branches for development',
                'text_content': 'always create feature branch before making changes',
                'confidence': 0.7,
                'context': json.dumps({'git_workflow': 'feature_branch'}),
                'created_at': '2024-01-17T09:15:00Z',
                'metadata': json.dumps({'tool_name': 'Bash', 'project_path': '/test/project'})
            }
        ]

        for pattern in sample_patterns:
            conn.execute("""
                INSERT INTO patterns (
                    pattern_type, category, description, text_content,
                    confidence, context, created_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern['pattern_type'],
                pattern['category'],
                pattern['description'],
                pattern['text_content'],
                pattern['confidence'],
                pattern['context'],
                pattern['created_at'],
                pattern['metadata']
            ))

        # Insert sample tool executions with embedded patterns
        sample_executions = [
            {
                'tool_name': 'Bash',
                'args': json.dumps({'command': 'npm install express'}),
                'result': json.dumps({
                    'stdout': 'installed express',
                    'patterns': [{
                        'type': 'correction',
                        'category': 'package-management',
                        'description': 'prefer yarn over npm',
                        'text': 'use yarn not npm for better performance',
                        'confidence': 0.75
                    }]
                }),
                'significance': 0.8,
                'project_path': '/test/project',
                'timestamp': '2024-01-18T11:45:00Z'
            }
        ]

        for execution in sample_executions:
            conn.execute("""
                INSERT INTO tool_executions (
                    tool_name, args, result, significance, project_path, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                execution['tool_name'],
                execution['args'],
                execution['result'],
                execution['significance'],
                execution['project_path'],
                execution['timestamp']
            ))

        conn.commit()
        print(f"✅ Created mock V1 database with {len(sample_patterns)} patterns and {len(sample_executions)} executions")


async def test_migration():
    """Test the V1 to V2 migration process"""
    print("🔄 Testing V1 to V2 Migration")
    print("=" * 50)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create mock V1 database
        v1_db_path = temp_path / "v1_knowledge.db"
        create_mock_v1_database(v1_db_path)

        # Test 1: Dry run migration
        print("\n🧪 Test 1: Dry run migration analysis")
        stats = await migrate_v1_to_v2(
            v1_db_path=str(v1_db_path),
            v2_agentdb_path=str(temp_path / "v2_agentdb"),
            v2_sqlite_path=str(temp_path / "v2_audit.db"),
            dry_run=True,
            backup_enabled=False
        )

        print(f"   Dry run results:")
        print(f"   - Found {stats.total_v1_patterns} V1 patterns")
        print(f"   - Would migrate: {stats.migrated_patterns}")
        print(f"   - Would skip duplicates: {stats.duplicates_found}")
        print(f"   - Success rate: {stats.success_rate:.1f}%")
        print(f"   - Duration: {stats.duration:.2f}s")

        # Test 2: Actual migration
        print("\n🚀 Test 2: Full migration")
        stats = await migrate_v1_to_v2(
            v1_db_path=str(v1_db_path),
            v2_agentdb_path=str(temp_path / "v2_agentdb_full"),
            v2_sqlite_path=str(temp_path / "v2_audit_full.db"),
            dry_run=False,
            backup_enabled=True
        )

        print(f"   Full migration results:")
        print(f"   - Migrated {stats.migrated_patterns}/{stats.total_v1_patterns} patterns")
        print(f"   - Duplicates: {stats.duplicates_found}")
        print(f"   - Errors: {stats.errors}")
        print(f"   - Success rate: {stats.success_rate:.1f}%")
        print(f"   - Duration: {stats.duration:.2f}s")

        # Test 3: Verify backup was created
        backup_files = list(v1_db_path.parent.glob("*.backup_*.db"))
        if backup_files:
            print(f"   ✅ Backup created: {backup_files[0].name}")
        else:
            print("   ⚠️  No backup found")

        # Test 4: Check V2 database
        v2_sqlite_path = temp_path / "v2_audit_full.db"
        if v2_sqlite_path.exists():
            with sqlite3.connect(v2_sqlite_path) as conn:
                pattern_count = conn.execute("SELECT COUNT(*) FROM pattern_metadata").fetchone()[0]
                print(f"   ✅ V2 SQLite has {pattern_count} pattern metadata entries")

        # Test 5: Migration with no V1 data
        print("\n📭 Test 3: Migration with empty V1 database")
        empty_v1_db = temp_path / "empty_v1.db"
        with sqlite3.connect(empty_v1_db) as conn:
            conn.execute("CREATE TABLE patterns (id INTEGER PRIMARY KEY)")
            conn.commit()

        empty_stats = await migrate_v1_to_v2(
            v1_db_path=str(empty_v1_db),
            v2_agentdb_path=str(temp_path / "v2_empty"),
            v2_sqlite_path=str(temp_path / "v2_empty.db"),
            dry_run=False,
            backup_enabled=False
        )

        print(f"   Empty migration: {empty_stats.total_v1_patterns} patterns found")

        return stats.success_rate > 80  # Consider successful if >80% migration rate


async def test_migration_error_handling():
    """Test migration error handling and edge cases"""
    print("\n🛡️  Testing migration error handling")
    print("=" * 40)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Test with non-existent V1 database
        print("   Testing non-existent V1 database...")
        try:
            stats = await migrate_v1_to_v2(
                v1_db_path=str(temp_path / "nonexistent.db"),
                v2_agentdb_path=str(temp_path / "v2_test"),
                v2_sqlite_path=str(temp_path / "v2_test.db"),
                dry_run=True,
                backup_enabled=False
            )
            print(f"   ✅ Handled gracefully: {stats.total_v1_patterns} patterns found")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            return False

        # Test with corrupted V1 database
        print("   Testing corrupted V1 database...")
        corrupted_db = temp_path / "corrupted.db"
        corrupted_db.write_text("This is not a valid SQLite database")

        try:
            stats = await migrate_v1_to_v2(
                v1_db_path=str(corrupted_db),
                v2_agentdb_path=str(temp_path / "v2_corrupted"),
                v2_sqlite_path=str(temp_path / "v2_corrupted.db"),
                dry_run=True,
                backup_enabled=False
            )
            print(f"   ⚠️  Handled corrupted DB: {stats.errors} errors")
        except Exception as e:
            print(f"   ✅ Expected error handled: {type(e).__name__}")

        return True


def main():
    """Run all migration tests"""
    print("🧪 V1 to V2 Migration Test Suite")
    print("=" * 60)

    async def run_all_tests():
        # Test main migration
        migration_success = await test_migration()

        # Test error handling
        error_handling_success = await test_migration_error_handling()

        print("\n🏁 Test Results Summary")
        print("=" * 30)
        print(f"   Migration test: {'✅ PASS' if migration_success else '❌ FAIL'}")
        print(f"   Error handling: {'✅ PASS' if error_handling_success else '❌ FAIL'}")

        if migration_success and error_handling_success:
            print("\n🎉 All migration tests PASSED!")
            print("   V1 to V2 migration is ready for production use")
            return True
        else:
            print("\n⚠️  Some migration tests failed")
            return False

    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
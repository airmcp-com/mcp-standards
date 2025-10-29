"""
Test suite for Simple Personal Memory MCP setup validation
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_imports():
    """Test that all modules can be imported"""
    try:
        # Test AgentDB client import
        from mcp_standards.agentdb_client import AgentDBClient, remember_preference, recall_preferences
        print("✓ AgentDB client imports successfully")

        # Test auto memory hook import
        from mcp_standards.hooks.auto_memory import AutoMemoryHook, detect_and_store
        print("✓ Auto memory hook imports successfully")

        # Test simple server import (this might fail due to MCP dependencies)
        try:
            from mcp_standards import server_simple
            print("✓ Simple server imports successfully")
        except ImportError as e:
            print(f"⚠️  Simple server import failed (may need MCP installed): {e}")

        return True

    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False


def test_agentdb_client_init():
    """Test AgentDB client initialization"""
    try:
        from mcp_standards.agentdb_client import AgentDBClient

        # Create client (should not fail even if AgentDB not installed)
        client = AgentDBClient()
        print(f"✓ AgentDB client initialized at: {client.db_path}")

        # Check directory creation
        assert client.db_path.exists(), "AgentDB directory should exist"
        print(f"✓ AgentDB directory created: {client.db_path}")

        return True

    except Exception as e:
        print(f"✗ AgentDB client init test failed: {e}")
        return False


def test_auto_memory_patterns():
    """Test pattern detection without AgentDB dependency"""
    try:
        from mcp_standards.hooks.auto_memory import AutoMemoryHook
        from mcp_standards.agentdb_client import AgentDBClient

        # Create mock client
        client = AgentDBClient()
        hook = AutoMemoryHook(client)

        # Test correction detection
        test_cases = [
            {
                "tool_name": "Bash",
                "args": {"command": "use uv not pip"},
                "result": "success",
                "expected": True
            },
            {
                "tool_name": "Write",
                "args": {"content": "actually, use TypeScript instead of JavaScript"},
                "result": "success",
                "expected": True
            },
            {
                "tool_name": "Read",
                "args": {"file_path": "test.py"},
                "result": "file contents",
                "expected": False  # No correction pattern
            }
        ]

        for i, test in enumerate(test_cases):
            correction = hook.detect_correction(
                test["tool_name"],
                test["args"],
                test["result"]
            )

            has_correction = correction is not None
            if has_correction == test["expected"]:
                print(f"✓ Pattern detection test {i+1} passed")
            else:
                print(f"✗ Pattern detection test {i+1} failed: expected {test['expected']}, got {has_correction}")
                return False

        # Test stats
        stats = hook.get_stats()
        assert "total_detections" in stats
        assert "patterns_count" in stats
        print(f"✓ Hook stats: {stats['patterns_count']} patterns defined")

        return True

    except Exception as e:
        print(f"✗ Auto memory pattern test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_directory_structure():
    """Test that required directories exist"""
    project_root = Path(__file__).parent.parent

    required_dirs = [
        "src/mcp_standards",
        "src/mcp_standards/hooks",
        ".claude/skills",
        "docs",
        "scripts"
    ]

    all_exist = True
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"✓ Directory exists: {dir_path}")
        else:
            print(f"✗ Directory missing: {dir_path}")
            all_exist = False

    return all_exist


def test_required_files():
    """Test that all required files exist"""
    project_root = Path(__file__).parent.parent

    required_files = [
        "src/mcp_standards/agentdb_client.py",
        "src/mcp_standards/hooks/auto_memory.py",
        "src/mcp_standards/server_simple.py",
        ".claude/skills/remember-preferences.md",
        "scripts/setup-agentdb.js",
        "docs/SIMPLE_V2_PLAN.md",
        "docs/QUICKSTART_SIMPLE.md",
        "README_SIMPLE.md",
        "package.json"
    ]

    all_exist = True
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"✓ File exists: {file_path} ({size} bytes)")
        else:
            print(f"✗ File missing: {file_path}")
            all_exist = False

    return all_exist


def run_all_tests():
    """Run all validation tests"""
    print("=" * 60)
    print("MCP Standards Simple - Setup Validation Tests")
    print("=" * 60)
    print()

    tests = [
        ("Directory Structure", test_directory_structure),
        ("Required Files", test_required_files),
        ("Module Imports", test_imports),
        ("AgentDB Client Init", test_agentdb_client_init),
        ("Auto Memory Patterns", test_auto_memory_patterns),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print(f"{'='*60}")

        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print(f"{'='*60}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*60}")

    if passed == total:
        print("\n🎉 All tests passed! System is ready for dev testing.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. See details above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

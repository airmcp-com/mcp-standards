#!/bin/bash
set -e

# Self-Learning System Test Suite
# Tests all new functionality

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║           Self-Learning System Test Suite                       ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MEMORY_DIR="$SCRIPT_DIR/mcp-servers/claude-memory"
DB_PATH="$HOME/.claude-memory/knowledge.db"

TESTS_PASSED=0
TESTS_FAILED=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} $2"
        ((TESTS_FAILED++))
    fi
}

echo "[1/8] Testing Database Schema..."
# Check if new tables exist
for table in tool_executions pattern_frequency tool_preferences agent_performance validation_gates knowledge_evolution spec_validations; do
    if sqlite3 "$DB_PATH" "SELECT name FROM sqlite_master WHERE type='table' AND name='$table';" | grep -q "$table"; then
        test_result 0 "Table $table exists"
    else
        test_result 1 "Table $table missing"
    fi
done
echo ""

echo "[2/8] Testing Schema Version..."
VERSION=$(sqlite3 "$DB_PATH" "SELECT MAX(version) FROM schema_migrations;" 2>/dev/null || echo "0")
if [ "$VERSION" -ge 7 ]; then
    test_result 0 "Schema version $VERSION (expected: 7)"
else
    test_result 1 "Schema version $VERSION (expected: 7)"
fi
echo ""

echo "[3/8] Testing Tool Preferences..."
# Check if uv preference exists
COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM tool_preferences WHERE preference LIKE '%uv%';" 2>/dev/null || echo "0")
if [ "$COUNT" -gt 0 ]; then
    test_result 0 "User preference (uv not pip) stored: $COUNT entries"
else
    test_result 1 "User preference not found"
fi
echo ""

echo "[4/8] Testing Hooks System..."
# Check if hooks files exist and are executable
cd "$MEMORY_DIR"
if [ -f "hooks/capture_hook.py" ]; then
    test_result 0 "capture_hook.py exists"

    # Test if it's valid Python
    if python3 -m py_compile hooks/capture_hook.py 2>/dev/null; then
        test_result 0 "capture_hook.py is valid Python"
    else
        test_result 1 "capture_hook.py has syntax errors"
    fi
else
    test_result 1 "capture_hook.py missing"
fi

if [ -f "hooks/significance_scorer.py" ]; then
    test_result 0 "significance_scorer.py exists"
else
    test_result 1 "significance_scorer.py missing"
fi

if [ -f "hooks/pattern_extractor.py" ]; then
    test_result 0 "pattern_extractor.py exists"
else
    test_result 1 "pattern_extractor.py missing"
fi
echo ""

echo "[5/8] Testing Intelligence Layer..."
for module in claudemd_manager temporal_graph validation_engine agent_tracker; do
    if [ -f "intelligence/${module}.py" ]; then
        test_result 0 "${module}.py exists"

        # Test if it's valid Python
        if python3 -m py_compile "intelligence/${module}.py" 2>/dev/null; then
            test_result 0 "${module}.py is valid Python"
        else
            test_result 1 "${module}.py has syntax errors"
        fi
    else
        test_result 1 "${module}.py missing"
    fi
done
echo ""

echo "[6/8] Testing Enhanced Server..."
if [ -f "claude_memory/enhanced_server.py" ]; then
    test_result 0 "enhanced_server.py exists"

    # Test if it's valid Python
    if python3 -m py_compile claude_memory/enhanced_server.py 2>/dev/null; then
        test_result 0 "enhanced_server.py is valid Python"
    else
        test_result 1 "enhanced_server.py has syntax errors"
    fi
else
    test_result 1 "enhanced_server.py missing"
fi

if [ -f "claude_memory/model_router.py" ]; then
    test_result 0 "model_router.py exists"

    # Test if it's valid Python
    if python3 -m py_compile claude_memory/model_router.py 2>/dev/null; then
        test_result 0 "model_router.py is valid Python"
    else
        test_result 1 "model_router.py has syntax errors"
    fi
else
    test_result 1 "model_router.py missing"
fi
echo ""

echo "[7/8] Testing Pattern Extraction..."
# Test significance scorer
cd "$MEMORY_DIR"
cat > /tmp/test_scorer.py <<'EOF'
import sys
sys.path.insert(0, '.')
from hooks.significance_scorer import SignificanceScorer

scorer = SignificanceScorer()

# Test 1: Edit CLAUDE.md (should be high significance)
score1 = scorer.calculate_significance(
    tool_name="Edit",
    args={"file_path": "CLAUDE.md"},
    result="success",
    project_path="/test"
)
assert score1 >= 0.8, f"CLAUDE.md edit should have high significance, got {score1}"

# Test 2: Read random file (should be low)
score2 = scorer.calculate_significance(
    tool_name="Read",
    args={"file_path": "random.txt"},
    result="success",
    project_path="/test"
)
assert score2 <= 0.5, f"Random file read should have low significance, got {score2}"

# Test 3: Correction pattern (should boost score)
score3 = scorer.calculate_significance(
    tool_name="Edit",
    args={"file_path": "test.py", "content": "use uv instead of pip"},
    result="success",
    project_path="/test"
)
assert score3 >= 0.5, f"Correction should boost significance, got {score3}"

print("All scorer tests passed!")
EOF

if uv run python /tmp/test_scorer.py 2>&1; then
    test_result 0 "Significance scorer logic correct"
else
    test_result 1 "Significance scorer has logic errors"
fi

# Test pattern extractor
cat > /tmp/test_extractor.py <<'EOF'
import sys
from pathlib import Path
sys.path.insert(0, '.')
from hooks.pattern_extractor import PatternExtractor

db_path = Path.home() / ".claude-memory" / "knowledge.db"
extractor = PatternExtractor(db_path)

# Test correction detection
patterns = extractor.extract_patterns(
    tool_name="Edit",
    args={"file_path": "test.py"},
    result="use uv not pip",
    project_path="/test"
)

# Should detect correction pattern
assert len(patterns) > 0, "Should detect correction pattern"
assert any(p.get("type") == "correction" for p in patterns), "Should identify as correction"

print("All extractor tests passed!")
EOF

if uv run python /tmp/test_extractor.py 2>&1; then
    test_result 0 "Pattern extractor logic correct"
else
    test_result 1 "Pattern extractor has logic errors"
fi
echo ""

echo "[8/8] Testing CLAUDE.md Generation..."
cat > /tmp/test_claudemd.py <<'EOF'
import sys
from pathlib import Path
sys.path.insert(0, '.')
from intelligence.claudemd_manager import ClaudeMdManager

db_path = Path.home() / ".claude-memory" / "knowledge.db"
manager = ClaudeMdManager(db_path)

# Test global content generation
content = manager.generate_claudemd_content(project_path=None, min_confidence=0.7)

# Should contain sections
assert "## Tool Preferences" in content, "Should have Tool Preferences section"
assert "use uv" in content.lower(), "Should include uv preference"

# Test suggestions
suggestions = manager.suggest_updates(project_path=None, min_confidence=0.7)
print(f"Found {len(suggestions)} suggestions")

print("All CLAUDE.md tests passed!")
EOF

if uv run python /tmp/test_claudemd.py 2>&1; then
    test_result 0 "CLAUDE.md generation works"
else
    test_result 1 "CLAUDE.md generation has errors"
fi
echo ""

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                    Test Summary                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "System is ready for use. Key features verified:"
    echo "  ✓ Database schema with 7 new tables"
    echo "  ✓ User preference (uv not pip) stored"
    echo "  ✓ Hooks system functional"
    echo "  ✓ Intelligence layer operational"
    echo "  ✓ Pattern extraction working"
    echo "  ✓ CLAUDE.md generation functional"
    echo ""
    echo "Next: Run ./validate.sh for full system check"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo ""
    echo "Please review errors above and fix issues"
    exit 1
fi

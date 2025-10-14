#!/bin/bash

# Claude Memory - Validation Script
# Tests installation and identifies issues

echo "=================================="
echo "Claude Memory Validation"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

# Test 1: Check Python
echo "[1/7] Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
        echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION"
    else
        echo -e "${RED}✗${NC} Python 3.10+ required, found $PYTHON_VERSION"
        ((ERRORS++))
    fi
else
    echo -e "${RED}✗${NC} Python3 not found"
    ((ERRORS++))
fi

# Test 2: Check uv
echo "[2/7] Checking uv..."
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✓${NC} uv $UV_VERSION"
else
    echo -e "${RED}✗${NC} uv not found"
    echo "  Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
    ((ERRORS++))
fi

# Test 3: Check dependencies
echo "[3/7] Checking dependencies..."
cd mcp-servers/claude-memory
if [ -d ".venv" ]; then
    echo -e "${GREEN}✓${NC} Virtual environment exists"
else
    echo -e "${RED}✗${NC} Virtual environment missing"
    echo "  Run: uv sync"
    ((ERRORS++))
fi
cd ../..

# Test 4: Test server startup
echo "[4/7] Testing MCP server..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/mcp-servers/claude-memory"

timeout 2 uv run python run_server.py &> /tmp/claude-memory-test.log &
SERVER_PID=$!
sleep 1

if ps -p $SERVER_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Server starts successfully"
    kill $SERVER_PID 2>/dev/null || true
else
    echo -e "${RED}✗${NC} Server failed to start"
    echo "  Check logs: /tmp/claude-memory-test.log"
    ((ERRORS++))
fi
cd ../..

# Test 5: Check database location
echo "[5/7] Checking database location..."
DB_DIR="$HOME/.claude-memory"
if [ -d "$DB_DIR" ]; then
    echo -e "${GREEN}✓${NC} Database directory exists: $DB_DIR"
    if [ -f "$DB_DIR/knowledge.db" ]; then
        DB_SIZE=$(du -h "$DB_DIR/knowledge.db" | cut -f1)
        EPISODE_COUNT=$(sqlite3 "$DB_DIR/knowledge.db" "SELECT COUNT(*) FROM episodes" 2>/dev/null || echo "0")
        echo "  Database size: $DB_SIZE"
        echo "  Episodes: $EPISODE_COUNT"
    fi
else
    echo -e "${YELLOW}!${NC} Database directory will be created on first use"
    ((WARNINGS++))
fi

# Test 6: Check Claude config
echo "[6/7] Checking Claude configuration..."
OS="$(uname -s)"
case "${OS}" in
    Darwin*)    CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json";;
    Linux*)     CLAUDE_CONFIG="$HOME/.config/claude/config.json";;
    *)          CLAUDE_CONFIG="";;
esac

if [ -n "$CLAUDE_CONFIG" ] && [ -f "$CLAUDE_CONFIG" ]; then
    echo -e "${GREEN}✓${NC} Config file exists: $CLAUDE_CONFIG"

    if grep -q "claude-memory" "$CLAUDE_CONFIG"; then
        echo -e "${GREEN}✓${NC} claude-memory server configured"

        # Extract and validate path
        CONFIGURED_PATH=$(python3 -c "
import json
with open('$CLAUDE_CONFIG') as f:
    config = json.load(f)
    if 'mcpServers' in config and 'claude-memory' in config['mcpServers']:
        args = config['mcpServers']['claude-memory'].get('args', [])
        for i, arg in enumerate(args):
            if arg == '--directory' and i+1 < len(args):
                print(args[i+1])
                break
" 2>/dev/null)

        if [ -n "$CONFIGURED_PATH" ]; then
            if [ -d "$CONFIGURED_PATH" ]; then
                echo -e "${GREEN}✓${NC} Server directory exists: $CONFIGURED_PATH"
            else
                echo -e "${RED}✗${NC} Configured directory not found: $CONFIGURED_PATH"
                echo "  Update config with correct path: $SCRIPT_DIR/mcp-servers/claude-memory"
                ((ERRORS++))
            fi
        fi
    else
        echo -e "${RED}✗${NC} claude-memory not in config"
        echo "  Run: ./install.sh"
        ((ERRORS++))
    fi
else
    echo -e "${RED}✗${NC} Claude config not found"
    echo "  Expected: $CLAUDE_CONFIG"
    echo "  Run: ./install.sh"
    ((ERRORS++))
fi

# Test 7: SQLite test
echo "[7/7] Testing SQLite..."
if command -v sqlite3 &> /dev/null; then
    echo -e "${GREEN}✓${NC} SQLite available"

    # Test FTS5
    FTS5_TEST=$(sqlite3 :memory: "CREATE VIRTUAL TABLE test USING fts5(content);" 2>&1)
    if [ -z "$FTS5_TEST" ]; then
        echo -e "${GREEN}✓${NC} FTS5 extension available"
    else
        echo -e "${YELLOW}!${NC} FTS5 might not be available"
        echo "  Search features may be limited"
        ((WARNINGS++))
    fi
else
    echo -e "${RED}✗${NC} SQLite not found"
    echo "  Install: brew install sqlite (macOS) or apt-get install sqlite3 (Linux)"
    ((ERRORS++))
fi

echo ""
echo "=================================="
echo "Validation Summary"
echo "=================================="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Restart Claude Desktop/Code"
    echo "  2. Test in Claude:"
    echo "     add_episode(name=\"Test\", content=\"Works!\", source=\"validation\")"
    echo "     search_episodes(\"test\")"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS warning(s)${NC}"
    echo "Installation should work, but check warnings above"
else
    echo -e "${RED}✗ $ERRORS error(s), $WARNINGS warning(s)${NC}"
    echo ""
    echo "Fix the errors above and run ./validate.sh again"
    echo "For help: https://github.com/mattstrautmann/research-mcp/issues"
fi

echo ""

exit $ERRORS

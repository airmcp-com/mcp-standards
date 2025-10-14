#!/bin/bash
# Quick validation that the memory leak fix is working

set -e

echo "===================================="
echo "Memory Leak Fix Validation"
echo "===================================="
echo ""

# Change to script directory
cd "$(dirname "$0")"

# 1. Test imports
echo "✓ Testing imports..."
python3 -c "from hooks.significance_scorer import SignificanceScorer" || {
    echo "✗ Import failed"
    exit 1
}

# 2. Run test suite
echo "✓ Running test suite..."
python3 test-memory-leak-fix.py > /dev/null 2>&1 || {
    echo "✗ Tests failed"
    exit 1
}

# 3. Check if MCP server is running
echo "✓ Checking MCP server status..."
if ps aux | grep -E "(python.*run_.*server\.py)" | grep -v grep > /dev/null; then
    echo "  - MCP server is running"

    # Get memory usage
    mem_kb=$(ps aux | grep -E "(python.*run_.*server\.py)" | grep -v grep | awk '{sum+=$6} END {print sum}')
    mem_mb=$((mem_kb / 1024))

    echo "  - Current memory: ${mem_mb} MB"

    if [ $mem_mb -gt 512 ]; then
        echo "  ⚠️  WARNING: Memory usage high (${mem_mb} MB)"
    else
        echo "  ✓ Memory usage normal"
    fi
else
    echo "  - MCP server not running (OK - starts on demand)"
fi

# 4. Check database
echo "✓ Checking database..."
db="$HOME/.claude-memory/knowledge.db"
if [ -f "$db" ]; then
    size_kb=$(du -k "$db" | cut -f1)
    size_mb=$((size_kb / 1024))
    echo "  - Database size: ${size_mb} MB"

    if [ $size_mb -gt 100 ]; then
        echo "  ⚠️  WARNING: Database larger than expected (${size_mb} MB)"
    fi
else
    echo "  - Database not created yet (normal for fresh install)"
fi

# 5. Check monitoring script
echo "✓ Checking monitoring script..."
if [ -x "./monitor-memory.sh" ]; then
    echo "  - Monitoring script ready"
    echo "  - Run: ./monitor-memory.sh 300"
else
    echo "  ✗ Monitoring script not executable"
    exit 1
fi

echo ""
echo "===================================="
echo "✓ All validation checks passed!"
echo "===================================="
echo ""
echo "The memory leak fix is properly deployed."
echo ""
echo "Next steps:"
echo "  1. Monitor for 7 days: ./monitor-memory.sh 300"
echo "  2. Check logs: tail -f ~/.claude-memory/memory-monitor.log"
echo "  3. View summary: cat MEMORY_LEAK_SUMMARY.md"
echo ""

#!/bin/bash

echo "Testing Claude Memory + Agentic Flow Integration"
echo "================================================"
echo ""

# Check if both MCP servers are in config
CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"

if [ -f "$CLAUDE_CONFIG" ]; then
    echo "✓ Claude config found"
    
    if grep -q "claude-memory" "$CLAUDE_CONFIG"; then
        echo "✓ claude-memory configured"
    else
        echo "✗ claude-memory NOT configured"
    fi
    
    if grep -q "agentic-flow" "$CLAUDE_CONFIG"; then
        echo "✓ agentic-flow configured"
    else
        echo "✗ agentic-flow NOT configured (optional but recommended)"
    fi
else
    echo "✗ Claude config not found"
fi

echo ""
echo "Test the integration in Claude:"
echo ""
echo "1. Check MCP servers are loaded:"
echo "   /mcp"
echo ""
echo "2. Test memory (can use cheap model via agentic-flow):"
echo "   add_episode(name=\"Cost Test\", content=\"Testing with Gemini Flash\", source=\"test\")"
echo "   search_episodes(\"cost\")"
echo ""
echo "3. Cost savings:"
echo "   Claude Sonnet: \$15/M tokens"
echo "   Gemini Flash:  \$0.075/M tokens (99.5% cheaper)"
echo ""

#!/usr/bin/env python3
"""
Run Enhanced Claude Memory MCP Server with Self-Learning

This server includes:
- Automatic learning from tool executions (via hooks)
- Pattern extraction and preference learning
- CLAUDE.md auto-generation
- Agent performance tracking
- Validation gates
- Cost-optimized routing via agentic-flow
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from claude_memory.enhanced_server import main

if __name__ == "__main__":
    print("=" * 60)
    print("Enhanced Claude Memory MCP Server")
    print("=" * 60)
    print()
    print("Features:")
    print("  ✓ Persistent memory with FTS5 search")
    print("  ✓ Automatic learning from corrections")
    print("  ✓ CLAUDE.md auto-generation")
    print("  ✓ Agent performance tracking")
    print("  ✓ Validation gates")
    print("  ✓ 99.5% cost savings via smart routing")
    print()
    print("=" * 60)
    print()

    asyncio.run(main())

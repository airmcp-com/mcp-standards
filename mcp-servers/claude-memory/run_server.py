#!/usr/bin/env python3
"""Run Claude Memory MCP Server"""
import asyncio
from claude_memory.server import main

if __name__ == "__main__":
    asyncio.run(main())
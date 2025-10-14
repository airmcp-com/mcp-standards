# Claude Memory MCP Server

Persistent memory for Claude using SQLite with full-text search.

## Quick Start

From the project root:
```bash
./install.sh
```

Or manually:
```bash
cd mcp-servers/claude-memory
uv sync
uv run python run_server.py
```

## Configuration

The server stores data in `~/.claude-memory/knowledge.db` by default.

To use a custom location, set the environment variable:
```bash
export CLAUDE_MEMORY_DB="/custom/path/knowledge.db"
```

## Tools

- `add_episode(name, content, source)` - Save knowledge
- `search_episodes(query, limit=10)` - Search with FTS5
- `list_recent(limit=10)` - List recent episodes
- `log_tool_execution(tool_name, args, result)` - Log tool usage
- `export_to_markdown(export_path)` - Export to markdown files

## Development

```bash
# Install dependencies
uv sync

# Run server
uv run python run_server.py

# Test database
sqlite3 ~/.claude-memory/knowledge.db "SELECT * FROM episodes;"
```

## License

MIT

# Claude Memory - AI Coding Standards Made Easy

**Auto-generate AI assistant instructions from your existing coding standards**

Stop manually writing `CLAUDE.md`, `.github/copilot-instructions.md`, and `.cursor/rules` files. Extract your standards once from existing config files, use everywhere.

---

## The Problem

AI coding assistants IGNORE your existing coding standards:
- ❌ Don't respect `.editorconfig`
- ❌ Don't respect `.prettierrc`
- ❌ Don't respect ESLint rules
- ❌ Generate code that fails linting

**Current "solutions" require manual work:**
- Write `.github/copilot-instructions.md` by hand
- Write `.cursor/rules/*.mdc` by hand
- Write `CLAUDE.md` by hand
- Keep them all in sync manually

**This tool automates all of that.**

---

## What It Does

1. **Reads your existing standards** (`.editorconfig`, `.prettierrc`, ESLint, `pyproject.toml`, `package.json`, `Cargo.toml`)
2. **Extracts your conventions** (package manager, test commands, project structure)
3. **Generates instruction files** for Claude, Copilot, and Cursor automatically
4. **Stores in memory** for instant recall across conversations

### Before vs After

**BEFORE (Manual - 2-3 hours):**
```markdown
# You write this in CLAUDE.md by hand:
- Use 2 spaces for indentation
- Use single quotes for strings
- Use uv for Python package management
- Run `uv run pytest` before committing
- Max line length: 88 characters
```

**AFTER (Automatic - 5 minutes):**
```python
# Run once in Claude:
generate_ai_standards(project_path=".")

# Auto-generated CLAUDE.md includes:
## Code Style (from .prettierrc, .editorconfig)
- Indentation: 2 spaces (editorconfig)
- Quotes: single (prettier)
- Line length: 88 chars (black)

## Project Standards (from pyproject.toml)
- Package manager: uv (detected from uv.lock)
- Testing: pytest (from dependencies)
- Test command: uv run pytest
```

**All generated automatically from your existing config files.**

---

## Core Features

### 🎯 Automatic Standards Extraction
Reads and parses:
- `.editorconfig` → Indentation, line endings, charset
- `.prettierrc` / `.prettierrc.json` → Formatting rules, quote style
- `.eslintrc` / `.eslintrc.json` → Linting rules, max line length
- `pyproject.toml` → Python project info, Black/Ruff config
- `Cargo.toml` → Rust project info
- `package.json` → JavaScript/TypeScript dependencies, scripts
- `README.md` → Project-specific conventions

### 🌐 Universal AI Support
Generates instructions for:
- ✅ **Claude Desktop/Code** (`CLAUDE.md`)
- ✅ **GitHub Copilot** (`.github/copilot-instructions.md`)
- ✅ **Cursor** (`.cursor/rules/standards.mdc`)

### 📦 Project Intelligence
Auto-detects:
- **Project type**: Python, JavaScript, TypeScript, Rust, Go, Ruby, PHP, Java, C#
- **Package manager**: uv, poetry, pip, npm, yarn, pnpm, bun, cargo, go
- **Test framework**: pytest, jest, vitest, mocha, cargo test, go test
- **Build process**: Scripts from `package.json`, project structure

### 🧠 Persistent Memory
- Stores extracted standards in local SQLite database
- Full-text search with FTS5
- Recall standards instantly in any conversation
- Export to markdown for documentation

### 🔒 Local-First Privacy
All data stays on your machine. No cloud dependencies.

---

## 30-Minute Setup

### Prerequisites (5 minutes)

**Required:**
- Python 3.10+
- Claude Desktop or Claude Code

**Install uv** (Python package manager):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Installation (10 minutes)

**1. Clone and configure:**
```bash
git clone https://github.com/mattstrautmann/research-mcp
cd research-mcp

# Optional: Setup cost optimization (99.5% savings)
cp .env.example .env
# Edit .env and add your Gemini API key (get free at https://aistudio.google.com/app/apikey)
```

**2. Run installer:**
```bash
./install.sh
```

The script will:
- Install dependencies via `uv`
- Check for `.env` file and Gemini API key
- If found, configure **both** claude-memory and agentic-flow for cost optimization
- If not found, configure just claude-memory (you can add Gemini later)
- Detect your Claude config location
- Offer to update your Claude config automatically

**2. Restart Claude Desktop/Code**

When Claude Desktop restarts, it automatically spawns the MCP server as a local child process. No separate startup scripts needed - the server runs on your machine and communicates with Claude via standard I/O pipes.

**How it works:**
- Claude Desktop reads your config file on startup
- When MCP tools are needed, Claude spawns the server process locally
- The server runs on your machine with full file system access
- Your data stays local (SQLite at `~/.claude-memory/knowledge.db`)
- When Claude quits, the MCP server process also terminates

That's it! The installation script handles everything.

### Manual Installation (if needed)

If the automatic script doesn't work, here's the manual process:

**1. Install dependencies:**
```bash
cd mcp-servers/claude-memory
uv sync
```

**2. Get absolute path:**
```bash
pwd
# Copy this path, you'll need it for config
```

**3. Update Claude config:**

**For Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "claude-memory": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/research-mcp/mcp-servers/claude-memory",
        "run",
        "run_server.py"
      ]
    }
  }
}
```

**For Claude Code** (`~/.claude/config.json`):
```json
{
  "mcpServers": {
    "claude-memory": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/research-mcp/mcp-servers/claude-memory",
        "run",
        "run_server.py"
      ]
    }
  }
}
```

**4. Restart Claude completely**

### Validation (5 minutes)

Open Claude and test:

```
# Check MCP server is loaded
/mcp
# Should show: claude-memory

# Add your first memory
add_episode(
    name="Setup Complete",
    content="Claude Memory is working! Installation successful.",
    source="setup-test"
)

# Search for it
search_episodes("setup")
# Should return your episode

# List recent memories
list_recent(limit=5)
```

**Success!** Claude now has persistent memory.

---

## Usage

### Core Tools

**add_episode** - Save important information:
```python
add_episode(
    name="API Decision",
    content="Using FastAPI for REST endpoints, better async support than Flask",
    source="technical-review"
)
```

**search_episodes** - Find relevant context:
```python
search_episodes("api framework")
# Returns episodes matching "api framework"
```

**list_recent** - See recent memories:
```python
list_recent(limit=10)
# Returns 10 most recent episodes
```

### Common Patterns

**Architecture Decisions:**
```python
add_episode(
    name="Cache Strategy",
    content="Redis for session data, CDN for static assets. Decided against Memcached due to persistence needs.",
    source="architecture"
)
```

**Code Discoveries:**
```python
add_episode(
    name="Auth Bug Fix",
    content="JWT tokens were expiring too quickly. Changed expiry from 1h to 24h in config/auth.py line 42",
    source="debugging"
)
```

**Meeting Notes:**
```python
add_episode(
    name="Client Feedback - Dashboard",
    content="Client wants real-time updates on dashboard. Considering WebSockets vs polling.",
    source="meeting-2025-01-11"
)
```

---

## Features

### Automatic Logging (Optional)

Enable automatic capture of significant tool executions:

```python
# Claude can automatically log important actions
# Examples: File edits, git commits, API calls
log_tool_execution(
    tool_name="edit_file",
    args={"file": "server.py"},
    result={"success": true}
)
```

### Export to Markdown

Backup your knowledge base:

```python
export_to_markdown(export_path="~/claude-memory-backup")
# Creates organized markdown files of all episodes
```

### Storage

- **Location**: `~/.claude-memory/knowledge.db`
- **Format**: SQLite with FTS5 full-text search
- **Backup**: Just copy the `.db` file

---

## Troubleshooting

### Understanding MCP Server Behavior

**Remember:** MCP servers are **local processes spawned by Claude Desktop**, not standalone services or cloud applications.

- ✅ Server runs on your machine as a child process of Claude
- ✅ Starts automatically when Claude needs MCP tools
- ✅ Stops automatically when Claude quits
- ❌ Not a background service/daemon that runs independently
- ❌ Not a cloud service - everything stays local

### "MCP server not found"

**Check Claude config location:**
```bash
# macOS
ls -la ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Linux
ls -la ~/.config/claude/config.json
```

**Verify absolute path in config:**
```bash
cd research-mcp/mcp-servers/claude-memory
pwd
# Use this exact path in your config
```

**Restart Claude completely** (Cmd+Q, then reopen)

**Verify MCP server is loaded:**
```
# In Claude interface
/mcp
# Should show: claude-memory (connected)
```

### "uv: command not found"

Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # or ~/.zshrc
```

### "Database locked" error

Close all Claude instances and try again. SQLite doesn't allow concurrent writes.

### Server won't start

**Important:** You don't need to start the server manually - Claude Desktop starts it automatically. However, you can test if it would start correctly:

```bash
cd mcp-servers/claude-memory
uv run python run_server.py
# Should output: "✓ Claude Memory MCP Server initialized"
# Press Ctrl+C to stop
```

**Note:** When running manually like this, the server waits for MCP protocol messages on stdin. It's meant to be spawned by Claude Desktop, not run standalone.

If this fails, check Python version:
```bash
python3 --version  # Should be 3.10+
```

### "Where is the MCP server running?"

The server runs **locally on your machine** as a child process of Claude Desktop:

```bash
# Check if Claude Desktop is running with MCP server
ps aux | grep -E "Claude|uv.*run_server"

# You should see something like:
# your_user    1234  Claude Desktop
# your_user    5678  uv run run_server.py (child of Claude)
```

The server is **not** a standalone service - it only exists while Claude Desktop is running and has spawned it.

### Memory Leak Fixed (2025-10-13)

✅ **Fixed**: Resolved unbounded memory growth in pattern tracking that could cause system restarts after several days.

**Details**: The `SignificanceScorer` maintained an unbounded cache that grew indefinitely. Now implements:
- Size limit (max 1000 entries) with LRU eviction
- 24-hour time-based expiry
- Automatic hourly cleanup

**No functional impact** - all learning preserved. See [MEMORY_LEAK_SUMMARY.md](mcp-servers/claude-memory/MEMORY_LEAK_SUMMARY.md) for details.

Monitor memory usage:
```bash
cd mcp-servers/claude-memory
./monitor-memory.sh 300  # Check every 5 minutes
```

---

## How It Works

### MCP Server Architecture

**On-Demand Process Spawning:**
- MCP servers run **locally on your machine**, not in the cloud
- Claude Desktop spawns the server as a **child process** when needed
- Communication happens via **stdio pipes** (standard input/output), not network/HTTP
- Process lifecycle is managed by Claude - starts with Claude, stops with Claude

**Process hierarchy:**
```
Claude Desktop (parent process)
  └─ uv run run_server.py (child process - your MCP server)
```

**This means:**
- ✅ Full file system access on your local machine
- ✅ All data stays local (no cloud dependencies)
- ✅ No separate startup/shutdown scripts needed
- ✅ Automatic lifecycle management
- ✅ Zero configuration after initial setup

### Data Storage & Search

1. **SQLite Database**: Lightweight, file-based storage at `~/.claude-memory/knowledge.db`
2. **FTS5 Search**: Full-text search index for fast retrieval
3. **MCP Protocol**: Standard Claude integration via Model Context Protocol
4. **uv Package Manager**: Fast, reliable Python dependency management

**Data flow:**
```
User → Claude Desktop → MCP Server (local process) → SQLite database
User → Claude Desktop → MCP Server → FTS5 index → Results
```

---

## Advanced

### Custom Database Location

Set environment variable:
```bash
export CLAUDE_MEMORY_DB="/custom/path/knowledge.db"
```

### Query the Database Directly

```bash
sqlite3 ~/.claude-memory/knowledge.db
sqlite> SELECT * FROM episodes WHERE source = 'architecture';
```

### Integration with Other MCP Servers

Claude Memory works alongside other MCP servers. Example config with multiple servers:

```json
{
  "mcpServers": {
    "claude-memory": {
      "command": "uv",
      "args": ["--directory", "/path/to/claude-memory", "run", "run_server.py"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/files"]
    }
  }
}
```

### 💰 Cost Optimization with Agentic Flow

Memory operations are simple CRUD tasks perfect for cheap models. The installer automatically configures cost optimization if you have a Gemini API key.

**Setup Methods:**

**Method 1: Environment File (Recommended)**
```bash
# Before running ./install.sh
cp .env.example .env
# Edit .env and add your Gemini API key
# The installer will automatically detect and configure both servers
```

**Method 2: Manual Configuration**
If you didn't set up `.env` before installation, add to your Claude config:
```json
{
  "mcpServers": {
    "agentic-flow": {
      "command": "npx",
      "args": ["-y", "agentic-flow", "mcp"],
      "env": {
        "GEMINI_API_KEY": "your_gemini_key",
        "DEFAULT_MODEL": "gemini-1.5-flash",
        "COST_OPTIMIZATION": "true",
        "FALLBACK_MODEL": "deepseek-chat"
      }
    },
    "claude-memory": {
      "command": "uv",
      "args": ["--directory", "/path/to/claude-memory", "run", "run_server.py"]
    }
  }
}
```

**How it works:**
- Simple operations (memory CRUD, searches) → **Gemini 1.5 Flash** automatically
- Complex operations (code generation, analysis) → **Claude** for quality
- Fallback to DeepSeek if Gemini fails

**Cost comparison for 1M tokens:**
- Claude Sonnet: $15.00
- Gemini 1.5 Flash: $0.075 (99.5% savings)
- DeepSeek Chat: $0.14 (99% savings)

**Example `.env` file:**
```bash
# Get free key at: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Override defaults
DEFAULT_MODEL=gemini-1.5-flash
COST_OPTIMIZATION=true
FALLBACK_MODEL=deepseek-chat
```

Memory operations like `add_episode()` and `search_episodes()` work perfectly with cheap models, saving you significant costs on high-volume usage.

**📘 Detailed guide:** See [docs/COST-OPTIMIZATION.md](docs/COST-OPTIMIZATION.md) for setup, examples, and monitoring.

---

## Philosophy

**Local-First**: Your data stays on your machine. No cloud dependencies.

**Simple**: One thing well—persistent memory. No feature creep.

**Fast**: SQLite + FTS5 = sub-50ms searches on 1M+ episodes.

**Extensible**: Python codebase, easy to customize for your workflow.

---

## What's Next?

Once setup is working, explore:

1. **Build your knowledge base**: Add key decisions, patterns, discoveries
2. **Try automatic learning**: System learns from corrections after 3 occurrences
3. **Multi-tool integration**: Enable cross-tool config updates (see [INTEGRATION_GUIDE.md](docs/INTEGRATION_GUIDE.md))
4. **Claude Projects**: Export learned preferences to Claude.ai knowledge base
5. **Custom workflows**: Extend the code for domain-specific memory patterns

**📘 Complete setup guide**: See [docs/INTEGRATION_GUIDE.md](docs/INTEGRATION_GUIDE.md) for Claude Desktop, Claude Code, Cursor, Copilot, and other AI assistants.

---

## Roadmap

### Current Status: Core Memory (✅ Complete)
- Persistent episode storage with SQLite + FTS5
- Fast full-text search (<50ms on 1M+ episodes)
- MCP server integration
- Export to markdown

### Upcoming: Universal Learning System (🔄 In Progress)
**Week 1: Universal Config Discovery** (Planned)
- Read and parse all AI assistant config formats
- Priority-based config merging
- Config validation and testing

**Week 2: Enhanced Pattern Learning** (Planned)
- 5-layer pattern detection (explicit, implicit, violations, behavioral, semantic)
- Confidence scoring and promotion
- Cross-session pattern tracking

**Week 3: Auto-Update Orchestration** (Planned)
- Event-driven CLAUDE.md updates
- Smart file selection (project vs global)
- Cross-tool config updates (optional)
- Backup-first atomic writes

**Week 4: Integration & Documentation** (Planned)
- Claude Projects export automation
- Team sharing workflows
- Comprehensive testing
- Video tutorials

### Future Enhancements
See [docs/CONFIG_STANDARDS.md](docs/CONFIG_STANDARDS.md) and [docs/INTEGRATION_GUIDE.md](docs/INTEGRATION_GUIDE.md) for detailed architecture.

**Planned features:**
- Claude Projects API integration (when available)
- Real-time cross-tool sync
- Learning analytics dashboard
- Conflict resolution UI
- Team knowledge base sync

---

## Contributing

We welcome contributions to the universal learning system!

**High-priority areas:**
- Universal config discovery implementation
- Enhanced pattern learning algorithms
- Cross-tool compatibility testing
- Documentation and examples

**Research areas:**
- Semantic clustering for similar corrections
- Temporal knowledge graphs (Zep/Graphiti integration)
- RLHF-style learning from corrections
- Natural language query improvements

See [docs/CONFIG_STANDARDS.md](docs/CONFIG_STANDARDS.md) for complete technical reference.

---

## Support

- **Issues**: [GitHub Issues](https://github.com/mattstrautmann/research-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mattstrautmann/research-mcp/discussions)

---

## License

MIT License - see LICENSE file

---

**Auto-generate AI assistant instructions from your existing coding standards. 5-minute setup.**

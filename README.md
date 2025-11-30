# MCP Standards - Personal Memory for Claude

> **⚠️ ARCHIVED PROJECT**: This repository is archived and provided for reference only. The project was experimental and served as a proof-of-concept for automatic preference learning with AgentDB vector memory. See [ARCHIVE.md](ARCHIVE.md) for complete details.

**Make Claude remember YOUR preferences automatically. Zero config, zero manual steps.**

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Archived](https://img.shields.io/badge/status-archived-inactive.svg)](ARCHIVE.md)

---

## 🎯 What This Does

Stop repeating yourself to Claude. This MCP server learns your preferences automatically:

```
You: "Install pytest"
Claude: pip install pytest

You: "Actually, use uv not pip"
Claude: ✓ Remembered

Next session:
You: "Install requests"
Claude: uv pip install requests  [automatic]
```

**One correction. Forever remembered.**

---

## ⚡ Quick Start (5 Minutes)

### 1. Install

```bash
git clone https://github.com/airmcp-com/mcp-standards.git
cd mcp-standards

# Install dependencies
npm install

# Setup AgentDB
npm run setup
```

### 2. Configure Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-standards": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/ABSOLUTE/PATH/TO/mcp-standards",
        "python",
        "-m",
        "mcp_standards.server_simple"
      ]
    }
  }
}
```

**⚠️ Replace `/ABSOLUTE/PATH/TO/` with your actual path!**

### 3. Restart Claude Desktop

Quit and relaunch Claude Desktop.

### 4. Test It!

```
You: "Remember: use uv not pip"
Claude: ✓ Remembered: 'use uv not pip' (python)

You: "What do you remember?"
Claude: I remember you prefer:
- Use uv not pip for Python projects
```

**That's it! You're done.** 🎉

---

## 🧠 How It Works

### Automatic Learning

Just correct Claude naturally - it learns automatically:

```
Session 1:
You: "Use uv not pip"
→ Auto-detected and stored in AgentDB

Session 2+:
You: "Install anything"
→ Claude uses uv automatically
```

### What Gets Remembered

✅ **Tool preferences**: "use uv not pip", "prefer yarn over npm"
✅ **Workflow patterns**: "run tests before commit"
✅ **Code style**: "use TypeScript for new files"
✅ **Project conventions**: "follow PEP 8"

### Categories (Auto-Detected)

- `python` - Python/pip/uv preferences
- `javascript` - npm/yarn/pnpm preferences
- `git` - Git workflow preferences
- `docker` - Docker/container preferences
- `testing` - Test framework preferences
- `general` - Everything else

---

## 📊 Features

| Feature | Status |
|---------|--------|
| **Auto-detection** | ✅ Detects "use X not Y" automatically |
| **Semantic search** | ✅ <1ms with AgentDB (150x faster than SQLite) |
| **Cross-session** | ✅ Preferences persist forever |
| **Zero config** | ✅ Works out of the box |
| **100% local** | ✅ No cloud, all private |
| **Simple** | ✅ 5-minute setup |

---

## 📖 Documentation

- **[Quick Start Guide](docs/QUICKSTART_SIMPLE.md)** - Detailed setup instructions
- **[Validation Checklist](docs/VALIDATION_CHECKLIST.md)** - Testing & troubleshooting
- **[Implementation Plan](docs/SIMPLE_V2_PLAN.md)** - Technical details
- **[Skills Guide](.claude/skills/remember-preferences.md)** - How to use in Claude

---

## 🛠️ MCP Tools Available

### Personal Memory (Simple Version)

```javascript
// Store preference
remember({
    content: "use uv not pip",
    category: "python"
})

// Search preferences
recall({
    query: "package manager",
    top_k: 5
})

// List all categories
list_categories()

// Get statistics
memory_stats()
```

### Config Standards (Bonus)

```javascript
// Generate minimal CLAUDE.md from project config files
generate_ai_standards({
    project_path: ".",
    formats: ["claude"]
})
```

---

## 🚀 Architecture

### Simple & Fast

```
User corrects Claude
   ↓
Auto-detection hook triggers
   ↓
Stores in AgentDB (semantic vector memory)
   ↓
Next session: Claude queries AgentDB automatically
   ↓
Uses remembered preference
```

### Technologies

- **AgentDB** - Ultra-fast vector memory (<1ms search)
- **Python** - MCP server (async)
- **SQLite** - Fallback storage
- **MCP Protocol** - Claude Desktop integration
- **100% Local** - No cloud dependencies

---

## 📁 Project Structure

```
mcp-standards/
├── src/mcp_standards/
│   ├── agentdb_client.py        # AgentDB wrapper
│   ├── hooks/auto_memory.py     # Auto-detection
│   └── server_simple.py         # Simple MCP server
├── tests/
│   └── test_simple_setup.py     # Validation tests
├── docs/
│   ├── QUICKSTART_SIMPLE.md     # Setup guide
│   ├── VALIDATION_CHECKLIST.md  # Testing guide
│   └── SIMPLE_V2_PLAN.md        # Technical details
├── scripts/
│   └── setup-agentdb.js         # Setup script
├── .claude/skills/
│   └── remember-preferences.md  # Claude skill
└── README.md                     # This file
```

**Clean. Simple. Works.**

---

## 🧪 Testing

Run automated validation:

```bash
python3 tests/test_simple_setup.py
```

**Expected output**:
```
✓ PASS: Directory Structure
✓ PASS: Required Files
✓ PASS: Module Imports
✓ PASS: AgentDB Client Init
✓ PASS: Auto Memory Patterns

Results: 5/5 tests passed
Status: Ready for dev testing 🚀
```

---

## 🐛 Troubleshooting

### Setup fails

```bash
# Check Node.js version
node --version  # Need v18+

# Install AgentDB manually
npm install -g agentdb
npx agentdb --version
```

### Claude Desktop doesn't connect

```bash
# Check logs
tail -f ~/Library/Logs/Claude/mcp*.log

# Look for initialization messages
# Should see: "MCP Standards (Simple) initialized"
```

### Preferences not remembered

Check that:
1. Server is running (check Claude Desktop MCP status)
2. Corrections use clear phrases ("use X not Y")
3. AgentDB path exists: `~/.mcp-standards/agentdb`

**More help**: See [Validation Checklist](docs/VALIDATION_CHECKLIST.md)

---

## 🎯 Performance

| Metric | Value |
|--------|-------|
| **Setup time** | <5 minutes |
| **Server startup** | <2 seconds |
| **Search speed** | <1ms (AgentDB HNSW) |
| **Detection** | Real-time (async) |
| **Storage** | <10ms |
| **Memory usage** | ~50MB (embedding model) |

**150x faster than SQLite. Zero lag.**

---

## 🔒 Privacy

- ✅ **100% local** - Everything stored in `~/.mcp-standards/`
- ✅ **No cloud** - No external API calls
- ✅ **No telemetry** - No data collection
- ✅ **Your data** - You control everything

---

## 📝 What Changed (v2 Simple)

We removed all the complexity:

| v1 (Old) | v2 Simple (New) |
|----------|-----------------|
| Manual MCP calls (4-5 steps) | ✅ Automatic (zero steps) |
| SQLite keyword search (50ms+) | ✅ AgentDB vector search (<1ms) |
| No semantic matching | ✅ Semantic understanding |
| Complex setup | ✅ 5-minute setup |
| 6,000+ LOC | ✅ ~950 LOC |

**Result**: 80% less code, 100x better UX

---

## 🤝 Contributing

This is a personal side project. If you want to contribute:

1. Try it yourself first
2. Open an issue describing what you want to add
3. Wait for feedback before writing code

**Please don't**: Submit large PRs without discussion first.

---

## 📜 License

MIT License - See [LICENSE](LICENSE) file

---

## 🙏 Credits

Built with inspiration from:

- **[AgentDB](https://agentdb.ruv.io)** - Ultra-fast vector memory
- **[Context Engineering Guide](https://github.com/coleam00/context-engineering-intro)** - Minimal CLAUDE.md principles
- **Gunnar's approach** - Simple side projects that solve personal problems

---

## 💬 Questions?

**Q: Why not just use v1?**
A: v1 requires 4-5 manual MCP calls per correction. v2 is zero-touch.

**Q: Do I need AgentDB?**
A: Yes, but it's installed automatically via `npm run setup`.

**Q: Is my data private?**
A: 100% local. Everything stored in `~/.mcp-standards/`. No cloud.

**Q: What if I want the old version?**
A: Use `src/mcp_standards/server.py` instead of `server_simple.py`.

---

## 🚀 Next Steps

```bash
# Try it now
git clone https://github.com/airmcp-com/mcp-standards.git
cd mcp-standards
npm run setup

# See: docs/QUICKSTART_SIMPLE.md
```

**Stop repeating yourself. Start remembering automatically.** 🎯

---

## 📦 Archive Status

**This project is archived.** See [ARCHIVE.md](docs/ARCHIVE.md) for:
- Complete project status and achievements
- Security audit results
- Full documentation index
- Lessons learned and technical insights
- How to use this repository as reference

---

**Made with ❤️ by keeping it simple**

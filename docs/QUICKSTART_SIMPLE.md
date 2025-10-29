# Quick Start: Simple Personal Memory MCP

**Goal**: Make Claude remember YOUR preferences automatically. Zero config, zero manual steps.

## Installation (5 Minutes)

### Step 1: Setup AgentDB

```bash
cd /path/to/mcp-standards

# Install dependencies
npm install

# Setup AgentDB
npm run setup
```

This will:
- ✓ Install AgentDB
- ✓ Create ~/.mcp-standards/agentdb directory
- ✓ Test AgentDB functionality

### Step 2: Configure Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-standards-simple": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/ABSOLUTE/PATH/TO/mcp-standards",
        "python",
        "src/mcp_standards/server_simple.py"
      ]
    }
  }
}
```

**Replace `/ABSOLUTE/PATH/TO/` with your actual path!**

### Step 3: Restart Claude Desktop

```bash
# Quit Claude Desktop completely
# Restart it
```

### Step 4: Test It!

Open Claude Desktop and try:

```
You: Remember: use uv not pip for Python projects
Claude: ✓ Remembered: 'use uv not pip for Python projects' (python)

You: What do you remember about Python?
Claude: I remember you prefer:
- Use uv not pip for Python projects
```

**That's it! You're done!**

---

## Daily Usage

### Automatic Learning (Recommended)

Just correct Claude naturally - it learns automatically:

```
You: "Install pytest"
Claude: pip install pytest

You: "Actually, use uv not pip"
Claude: ✓ Remembered

Next time:
You: "Install pytest"
Claude: uv pip install pytest  [uses remembered preference]
```

### Manual Memory (Optional)

You can also explicitly tell Claude to remember:

```
Remember: Always run tests before committing
Remember: Use TypeScript for new JavaScript files
Remember: Prefer functional components in React
```

### Query Memory

```
What preferences have you remembered?
What do you remember about Git?
Show me memory stats
List all categories
```

---

## How It Works

### Architecture

```
User corrects Claude
   ↓
Auto-detection hook triggers
   ↓
Stores in AgentDB (semantic vector memory)
   ↓
Next session: Claude queries AgentDB before responding
   ↓
Uses remembered preference automatically
```

### What Gets Remembered

✅ **Tool preferences**: "use uv not pip", "prefer yarn over npm"
✅ **Workflow patterns**: "run tests before commit"
✅ **Code style**: "use TypeScript", "prefer functional components"
✅ **Project conventions**: "follow PEP 8"

### Categories (Auto-Detected)

- `python` - Python-related preferences
- `javascript` - JavaScript/Node.js preferences
- `git` - Git workflow preferences
- `docker` - Docker/container preferences
- `testing` - Testing preferences
- `general` - Everything else

---

## MCP Tools Available

### Personal Memory (NEW)

```javascript
// Store preference
remember({
    content: "use uv not pip",
    category: "python"
})

// Search preferences
recall({
    query: "package manager",
    category: "python",
    top_k: 5
})

// List all categories
list_categories()

// Get statistics
memory_stats()
```

### Config Standards (EXISTING)

```javascript
// Generate minimal CLAUDE.md from project config
generate_ai_standards({
    project_path: ".",
    formats: ["claude", "copilot", "cursor"]
})
```

---

## Troubleshooting

### AgentDB not found

```bash
# Install manually
npm install -g agentdb

# Verify
npx agentdb --version
```

### Preferences not being remembered

Check logs in Claude Desktop:
- Look for "🎯 Detected correction" messages
- Look for "✓ Remembered" confirmations

### AgentDB slow on first startup

First startup loads the embedding model (~23MB). Subsequent startups are <10ms.

### Want to reset memory

```bash
# Delete AgentDB data
rm -rf ~/.mcp-standards/agentdb/*

# Restart Claude Desktop
```

---

## Performance

- **Startup**: <10ms (after first model load)
- **Search**: <1ms (HNSW vector index)
- **Storage**: 100% local (no cloud)
- **Memory**: ~50MB (embedding model)

---

## What's Different from v1?

| Feature | v1 (Old) | v2 Simple (New) |
|---------|----------|-----------------|
| **Memory storage** | SQLite keyword search | AgentDB vector search |
| **Detection** | Manual MCP calls | Automatic hooks |
| **Search speed** | 50ms+ | <1ms |
| **Semantic matching** | ❌ No | ✅ Yes |
| **Setup** | Complex | 5 minutes |
| **Workflow** | 4-5 manual steps | Zero steps |

---

## Next Steps

### Week 1: Use It Yourself

Just use Claude normally. Correct it when needed. Watch it learn.

### Week 2: Refinement

```
What preferences have you remembered?
```

Review and see what it learned. The system improves as you use it.

### Future Features (Coming)

- ✨ Confidence scoring (promote after 2-3 corrections)
- ✨ Cross-project learning (global vs local)
- ✨ Preference conflicts detection
- ✨ Web dashboard for memory management

---

## Questions?

- **Documentation**: See `docs/SIMPLE_V2_PLAN.md`
- **Skill Guide**: See `.claude/skills/remember-preferences.md`
- **Architecture**: AgentDB + Simple hooks + Minimal CLAUDE.md
- **Inspiration**: Gunnar's simple side projects + context engineering

---

**Remember**: The best preference is the one you only have to correct once.

🚀 **Ready to try it? Run `npm run setup` now!**

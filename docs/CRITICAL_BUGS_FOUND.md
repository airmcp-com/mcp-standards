# Critical Bugs Found - 2025-10-30

## Bug #1: AgentDB Client Using Non-Existent CLI Commands

**Severity**: CRITICAL - Memory system completely non-functional

**Location**: `src/mcp_standards/agentdb_client.py:103-166`

### The Problem

The AgentDB client is calling CLI commands that don't exist:

```python
# ❌ WRONG - These commands don't exist in AgentDB CLI
cmd = [
    "npx", "agentdb",
    "store",  # ❌ Not a valid command
    "--key", f"{category}:{hash(content)}",
    "--value", content,
    "--metadata", json.dumps(meta),
    "--path", str(self.db_path)
]

cmd = [
    "npx", "agentdb",
    "query",  # ❌ Wrong syntax - requires <db> argument
    "--query", query,
    "--top-k", str(top_k),
    "--threshold", str(min_similarity),
    "--path", str(self.db_path)
]
```

### Actual AgentDB CLI Commands

```bash
$ npx agentdb --help

CORE COMMANDS
  init <path>       Initialize vector database
  mcp               Start MCP server for Claude Code
  benchmark         Run performance benchmarks
  version           Show version information

DATABASE COMMANDS
  import <file>     Import vectors from file
  export <file>     Export vectors to file
  query <db>        Query vector database (requires DB file path)
  stats <db>        Show database statistics
```

**No `store` command exists!**
**The `query` command requires a `<db>` file path, not `--query` text**

### Impact

1. **`remember` tool**: Silently fails - never stores anything
2. **`recall` tool**: Silently fails - returns empty results
3. **User preferences**: NEVER saved, NEVER retrieved
4. **Memory stats**: Would fail if called

### Why It Wasn't Caught

1. Commands run via `subprocess` - errors suppressed
2. No validation tests actually calling AgentDB
3. Assumed CLI API from documentation without testing
4. Error logging doesn't bubble up to MCP response

### Evidence

```bash
$ npx agentdb store --key "test" --value "data" --path ~/test
❌ Unknown command: store

$ npx agentdb query --query "test" --path ~/test
❌ Error: Missing required argument: db
```

### Root Cause

AgentDB has **two different interfaces**:

1. **CLI** - For command-line operations (init, mcp server, benchmark)
2. **JavaScript/TypeScript API** - For programmatic usage (store, query, search)

The Python client is trying to use the JS API via CLI commands, which don't exist.

---

## Bug #2: MCP Tool Auto-Discovery Not Working in Claude Desktop

**Severity**: HIGH - User experience issue

**Status**: Tool descriptions are correct, but Claude Desktop doesn't auto-trigger

### The Problem

Even with enhanced tool descriptions following best practices:

```python
description=(
    "Store user preferences, corrections, and workflow rules in semantic memory. "
    "Use when user explicitly shares preferences or corrects your suggestions. "
    "**Trigger phrases**: 'remember', 'I prefer', 'always use', 'never use'..."
)
```

Claude Desktop **does not** auto-trigger the tools when users say:
- "Remember: use uv not pip" → Tool NOT called
- "What Python package manager?" → `recall` tool NOT called
- "use uv not pip" → `remember` tool NOT called

### Evidence

User testing in Claude Desktop showed:
1. User: "what python package manager?"
2. Claude: Responded without calling `recall` tool
3. User: "install pytest"
4. Claude: Used `uv add` without checking `recall`
5. User: "use uv not pip"
6. Claude: Acknowledged but didn't call `remember` tool

### Logs Confirm

```bash
$ tail -f ~/Library/Logs/Claude/mcp*.log | grep "tools/call"
# No tool invocations despite trigger phrases
```

### Theories

1. **Claude Desktop vs Claude Code difference**: Desktop may have stricter auto-trigger thresholds
2. **Description length**: Very long descriptions may reduce effectiveness
3. **Markdown formatting**: `**Bold**` syntax may interfere with parsing
4. **Multiple tools competing**: 7 tools available, Claude may be conservative
5. **Context window**: Other instructions may take priority over tool descriptions

### What DOES Work

Manual tool invocation works perfectly:
```
User: "Use the remember tool to store: use uv not pip"
Claude: ✓ [Calls tool successfully]
```

---

## Recommended Fixes

### Fix #1: AgentDB Client (URGENT)

**Option A: Use AgentDB JavaScript API via Node**

Create a Node.js bridge script that uses the actual AgentDB API:

```javascript
// scripts/agentdb-bridge.js
import { AgentDB } from 'agentdb';

const db = new AgentDB({ path: process.argv[2] });

switch (process.argv[3]) {
  case 'store':
    await db.store(JSON.parse(process.argv[4]));
    break;
  case 'query':
    const results = await db.query(JSON.parse(process.argv[5]));
    console.log(JSON.stringify(results));
    break;
}
```

Then call from Python:
```python
cmd = ["node", "scripts/agentdb-bridge.js", str(self.db_path), "store", json.dumps(data)]
```

**Option B: Use SQLite Directly for Now**

Remove AgentDB dependency temporarily, use existing SQLite backend:

```python
# Use the working SQLite implementation instead
# Save to knowledge.db with FTS5 for semantic search
```

**Option C: Use AgentDB MCP Server Tools**

Since AgentDB has an MCP server (`npx agentdb mcp`), use its tools instead of CLI:

```json
{
  "mcpServers": {
    "agentdb": {
      "command": "npx",
      "args": ["agentdb", "mcp"]
    }
  }
}
```

Then delegate to AgentDB's MCP tools from our server.

### Fix #2: MCP Auto-Discovery (MEDIUM PRIORITY)

**Short-term**: Document actual UX in README

Update README to show users need explicit tool calls:
```markdown
# ❌ Doesn't work yet
"Remember: use uv not pip"

# ✅ Current syntax
"Use the remember tool to store: use uv not pip"
```

**Medium-term**: Test description variations

Try:
1. Shorter, more focused descriptions
2. Remove markdown formatting
3. Add imperative "CALL THIS TOOL WHEN" language
4. Test with only 2-3 tools (reduce competition)

**Long-term**: Consider MCP Prompts

While prompts don't auto-trigger, they could provide a better UX:
```
/remember use uv not pip
```

---

## Testing Required

### AgentDB Client Testing

```bash
# 1. Test actual CLI
npx agentdb init ~/.mcp-standards/test.db
npx agentdb query ~/.mcp-standards/test.db

# 2. Test Node API directly
node -e "import('agentdb').then(m => console.log(m))"

# 3. Verify MCP server
npx agentdb mcp
# Check what tools it provides
```

### MCP Tool Testing

```bash
# Monitor tool calls in real-time
tail -f ~/Library/Logs/Claude/mcp*.log | grep "tools/call"

# Test variations in Claude Desktop:
# 1. "Remember: use uv not pip"
# 2. "Use the remember tool: use uv not pip"
# 3. "Store this preference: use uv not pip"
```

---

## Priority

1. **FIX AGENTDB CLIENT IMMEDIATELY** - System is completely broken
2. Test which AgentDB interface actually works
3. Update README with honest UX (manual tool calls required)
4. Continue researching auto-discovery (but don't block on it)

---

**Found**: 2025-10-30 22:00 PST
**Reporter**: User testing in Claude Desktop
**Impact**: Complete memory system failure (no storage/retrieval working)

# QA Findings - Critical Inconsistencies

**Date**: 2025-10-14
**Status**: ❌ CRITICAL ISSUES FOUND

---

## Critical Issues

### 1. ❌ Non-Existent Install Script in README

**Location**: README.md lines 123-124

**Current (WRONG)**:
```bash
# 2. Run installer (auto-configures Claude Desktop/Code)
./install.sh
```

**Issue**: `install.sh` does not exist in the repository

**Fix Required**: Replace with actual installation instructions using `uv`

---

### 2. ❌ Server Name Inconsistency

**Location**: `src/mcp_standards/server.py` line 30

**Current**:
```python
self.server = Server("claude-memory")
```

**Should Be**:
```python
self.server = Server("mcp-standards")
```

**Impact**: Server registers with wrong name in Claude Desktop

---

### 3. ❌ Database Path Inconsistency

**Location**: `src/mcp_standards/server.py` line 33

**Current**:
```python
self.db_path = Path.home() / ".claude-memory" / "knowledge.db"
```

**Should Be**:
```python
self.db_path = Path.home() / ".mcp-standards" / "knowledge.db"
```

**Impact**: Database stored in wrong directory with old naming

---

### 4. ⚠️ Missing Tool in README

**Issue**: README doesn't document `log_tool_execution` tool

**Actual Tools in server.py**:
1. add_episode ✅ (documented)
2. search_episodes ✅ (documented)
3. list_recent ✅ (documented)
4. log_tool_execution ❌ (NOT documented)
5. export_to_markdown ✅ (documented)
6. generate_ai_standards ✅ (documented)
7. get_learned_preferences ✅ (documented)
8. suggest_claudemd_update ✅ (documented)
9. update_claudemd ✅ (documented)

**Decision**: `log_tool_execution` is an internal tool, don't document it publicly

---

## Fixes Required

### Priority 1: README.md

Replace install instructions (lines 116-127):

```bash
### Install (3 commands)

```bash
# 1. Clone repository
git clone https://github.com/airmcp-com/mcp-standards.git
cd mcp-standards

# 2. Install dependencies
uv sync

# 3. Configure Claude Desktop
# Add to ~/.claude/config/claude_desktop_config.json:
{
  "mcpServers": {
    "mcp-standards": {
      "command": "uv",
      "args": ["run", "python", "/ABSOLUTE/PATH/TO/mcp-standards/run_server.py"]
    }
  }
}

# 4. Restart Claude Desktop - you're done!
```

### Priority 1: server.py

**Fix 1 - Server Name** (line 30):
```python
# OLD
self.server = Server("claude-memory")
# NEW
self.server = Server("mcp-standards")
```

**Fix 2 - Database Path** (line 33):
```python
# OLD
self.db_path = Path.home() / ".claude-memory" / "knowledge.db"
# NEW
self.db_path = Path.home() / ".mcp-standards" / "knowledge.db"
```

---

## Files to Update

1. ✅ README.md - Installation instructions
2. ✅ src/mcp_standards/server.py - Server name and database path
3. Check: Any other files referencing `.claude-memory` directory

---

## Verification Steps After Fix

1. Search entire codebase for `.claude-memory` references
2. Search entire codebase for `Server("claude-memory")`
3. Test fresh installation following new README
4. Verify database creates at `~/.mcp-standards/knowledge.db`
5. Verify server registers as `mcp-standards` in Claude Desktop

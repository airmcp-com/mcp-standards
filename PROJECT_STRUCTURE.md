# MCP Standards - Clean Project Structure

**Last Updated**: 2025-10-29

---

## 📁 Clean Directory Structure

```
mcp-standards/
├── 📄 README.md                     # ⭐ START HERE - Main documentation
├── 📄 CLAUDE.md                     # Project configuration for Claude Code
├── 📄 package.json                  # npm dependencies and scripts
├── 📄 pyproject.toml               # Python dependencies
│
├── 📂 src/mcp_standards/           # ✨ Core implementation
│   ├── agentdb_client.py           # AgentDB wrapper (200 LOC)
│   ├── server_simple.py            # Simple MCP server (350 LOC)
│   ├── hooks/
│   │   └── auto_memory.py          # Auto-detection (250 LOC)
│   ├── server.py                   # Legacy v1 server (keep for compatibility)
│   ├── standards.py                # Config parser (keep)
│   └── ...                         # Other legacy files
│
├── 📂 tests/                       # ✅ All tests here
│   ├── test_simple_setup.py        # Main validation suite
│   ├── test_*.py                   # Other test files (moved from root)
│   └── ...
│
├── 📂 docs/                        # 📖 Documentation
│   ├── QUICKSTART_SIMPLE.md        # 5-minute setup guide
│   ├── VALIDATION_CHECKLIST.md     # Testing & troubleshooting
│   ├── SIMPLE_V2_PLAN.md           # Technical implementation plan
│   └── archive/                    # Old docs (kept for reference)
│       ├── UAT_READINESS_REPORT.md
│       ├── USAGE_V2.md
│       └── README_SIMPLE.md
│
├── 📂 scripts/                     # 🔧 Setup & utility scripts
│   ├── setup-agentdb.js            # AgentDB installation
│   └── run_server.py               # Legacy server runner
│
├── 📂 .claude/                     # Claude Code integration
│   ├── skills/
│   │   └── remember-preferences.md # Main skill for personal memory
│   ├── agents/                     # Claude Code agents
│   ├── commands/                   # Claude Code commands
│   └── helpers/                    # Claude Code helpers
│
└── 📂 node_modules/                # npm dependencies (auto-generated)
```

---

## 🎯 What Each Directory Does

### `/src/mcp_standards/` - Core Code

**Simple v2 (NEW - Use This)**:
- `agentdb_client.py` - Wrapper for AgentDB vector memory
- `hooks/auto_memory.py` - Auto-detection of corrections
- `server_simple.py` - Simple MCP server with 4 tools

**Legacy v1 (OLD - Keep for compatibility)**:
- `server.py` - Complex v1 server (9 tools, manual)
- `standards.py` - Config file parser (still useful)
- `export.py` - Markdown export (still useful)
- Other files - Legacy intelligence layers

**Total LOC**:
- Simple v2: ~950 LOC (what you want)
- Legacy v1: ~6,000 LOC (keep but ignore)

### `/tests/` - All Tests

**Clean organization**:
- `test_simple_setup.py` - Main validation (5 tests, all passing)
- `test_*.py` - Other tests (moved from root for cleanliness)
- All test files now in one place

### `/docs/` - Documentation

**Active docs** (read these):
- `QUICKSTART_SIMPLE.md` - Setup instructions
- `VALIDATION_CHECKLIST.md` - Testing guide
- `SIMPLE_V2_PLAN.md` - Technical details

**Archived docs** (reference only):
- `archive/` - Old v1 docs, kept for history

### `/scripts/` - Setup & Tools

- `setup-agentdb.js` - Main setup script (npm run setup)
- `run_server.py` - Legacy server runner

### `/.claude/` - Claude Code Integration

- `skills/remember-preferences.md` - Main skill
- Other directories - Claude Code system files

---

## 🗑️ What Got Cleaned Up

### Moved to `/tests/` (12 files)
```
test_*.py files (all moved from root)
deploy_v2.py (moved from root)
```

### Moved to `/docs/archive/` (4 files)
```
UAT_READINESS_REPORT.md
USAGE_V2.md
v2_plan_draft.md
README_SIMPLE.md (consolidated into main README)
```

### Moved to `/scripts/` (1 file)
```
run_server.py
```

### Kept in Root (4 files - essential)
```
README.md          # ⭐ Main documentation (UPDATED)
CLAUDE.md          # Project config (KEEP)
package.json       # npm config (KEEP)
pyproject.toml     # Python config (KEEP)
```

---

## 🎯 Quick Navigation

**Want to get started?**
→ Read `README.md` (main docs)
→ Run `npm run setup` (5 minutes)
→ See `docs/QUICKSTART_SIMPLE.md` (detailed steps)

**Want to understand the code?**
→ Start with `src/mcp_standards/server_simple.py` (350 LOC)
→ Then read `src/mcp_standards/agentdb_client.py` (200 LOC)
→ Finally check `src/mcp_standards/hooks/auto_memory.py` (250 LOC)
→ **Total**: ~950 LOC for the entire simple system

**Want to test?**
→ Run `python3 tests/test_simple_setup.py`
→ See `docs/VALIDATION_CHECKLIST.md` for details

**Want technical details?**
→ Read `docs/SIMPLE_V2_PLAN.md` (implementation plan)
→ Check `docs/VALIDATION_CHECKLIST.md` (testing plan)

**Need help?**
→ See `README.md` (troubleshooting section)
→ Check `docs/VALIDATION_CHECKLIST.md` (known issues)

---

## 📊 File Count Summary

| Directory | Files | Purpose |
|-----------|-------|---------|
| `/` (root) | 4 | Essential configs only |
| `/src/mcp_standards/` | 15+ | Core code (v1 + v2) |
| `/tests/` | 15+ | All tests (organized) |
| `/docs/` | 10+ | Documentation + archive |
| `/scripts/` | 2 | Setup & utilities |
| `/.claude/` | 50+ | Claude Code integration |

**Total**: Clean, organized, easy to navigate

---

## 🚀 Using the Clean Structure

### For Users (Just want it to work)
1. Read `README.md`
2. Run `npm run setup`
3. Done!

### For Contributors (Want to understand)
1. Read `README.md`
2. Read `docs/SIMPLE_V2_PLAN.md`
3. Look at `src/mcp_standards/server_simple.py`
4. Check `tests/test_simple_setup.py`

### For Maintainers (Deep dive)
1. Everything above, plus:
2. Read `docs/VALIDATION_CHECKLIST.md`
3. Review `src/mcp_standards/` architecture
4. Check legacy v1 files if needed

---

## 🎉 Result: Clean & Simple

**Before cleanup**:
- 12 test files in root ❌
- 8 README/docs in root ❌
- Unclear structure ❌
- Confusing navigation ❌

**After cleanup**:
- Tests in `/tests/` ✅
- Docs in `/docs/` ✅
- Clear structure ✅
- Easy navigation ✅

**One README. One setup command. One simple system.**

---

**Last Updated**: 2025-10-29
**Structure Version**: v2 Simple
**Status**: Clean & Ready for Development 🚀

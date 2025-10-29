# MCP Standards v2: Simple Personal Memory

**Philosophy**: Make Claude remember MY preferences automatically. Zero config, zero manual steps.

## What We're Building

A simple MCP server that:
1. ✅ Auto-detects corrections ("use uv not pip")
2. ✅ Stores in AgentDB (semantic vector memory)
3. ✅ Retrieves before responding (automatic context)
4. ✅ Parses config files → minimal CLAUDE.md
5. ✅ ONE skill to enable it all

## Architecture (Simple)

```
┌─────────────────────────────────────────┐
│         Claude Desktop/Code             │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │  MCP: personal-memory             │  │
│  │                                   │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │  AgentDB Client             │  │  │
│  │  │  (npx agentdb)              │  │  │
│  │  │  - Vector storage           │  │  │
│  │  │  - Semantic search          │  │  │
│  │  │  - <10ms startup            │  │  │
│  │  └─────────────────────────────┘  │  │
│  │                                   │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │  Auto Memory Hook           │  │  │
│  │  │  - Detects corrections      │  │  │
│  │  │  - Auto-stores patterns     │  │  │
│  │  │  - Zero manual calls        │  │  │
│  │  └─────────────────────────────┘  │  │
│  │                                   │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │  Config Parser (existing)   │  │  │
│  │  │  - Reads .editorconfig      │  │  │
│  │  │  - Minimal CLAUDE.md        │  │  │
│  │  └─────────────────────────────┘  │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## Implementation

### Phase 1: AgentDB Integration (Days 1-3)
- Install AgentDB via npm
- Create simple Python client wrapper
- Test store/retrieve operations
- Performance benchmark (<10ms startup, <1ms search)

### Phase 2: Auto-Detection (Days 4-6)
- Hook into MCP tool execution
- Detect correction patterns
- Auto-store in AgentDB (no manual calls)
- Test detection accuracy

### Phase 3: Skill Creation (Day 7)
- Create `remember-preferences.md` skill
- Auto-query AgentDB before responding
- Test memory retrieval in conversations

### Phase 4: Polish (Days 8-10)
- Simplify codebase (remove complex layers)
- Optimize for minimal CLAUDE.md output
- End-to-end testing
- Documentation

## What We're NOT Building

❌ Custom vector database (use AgentDB)
❌ Complex confidence scoring (trust AgentDB)
❌ Manual promotion system (auto-detect everything)
❌ Event-driven architecture (overkill)
❌ Hybrid memory tiers (AgentDB handles it)

## Success Criteria

1. **Zero Manual Steps**: User corrects Claude → automatically remembered
2. **Fast**: <1ms to retrieve preferences
3. **Accurate**: Semantic matching (>80% recall)
4. **Minimal CLAUDE.md**: <1000 tokens, not 23K
5. **Works Cross-Project**: Personal knowledge graph

## Files to Create (New)

```
/src/mcp_standards/agentdb_client.py       # AgentDB wrapper (100 LOC)
/src/mcp_standards/hooks/auto_memory.py    # Correction detector (150 LOC)
/.claude/skills/remember-preferences.md    # The skill (50 LOC)
/docs/SIMPLE_V2_PLAN.md                    # This file
```

## Files to Keep (Simplified)

```
/src/mcp_standards/standards.py            # Config parser ✅
/src/mcp_standards/server.py               # MCP server ✅
/src/mcp_standards/export.py               # Markdown export ✅
```

## Files to Remove (Complexity)

```
/src/intelligence/context/                 # Over-engineered
/src/intelligence/reasoning/               # Use AgentDB RL
/src/mcp_standards/intelligence/temporal_graph.py
/docs/architecture/v2-*.md                 # Old complex plans
```

## Timeline

- **Week 1**: Core system working (auto-detect + store)
- **Week 2**: Polish + test + document
- **Week 3**: Use it myself, iterate

## Inspiration

- **Gunnar's approach**: Simple side projects that solve personal problems
- **Context engineering**: Minimal CLAUDE.md, dynamic loading
- **AgentDB**: 150x faster semantic search, built-in learning

## Next Steps

1. ✅ Create this plan
2. Install AgentDB: `npm install agentdb`
3. Build AgentDB client wrapper
4. Create correction detection hook
5. Build remember-preferences skill
6. Test end-to-end

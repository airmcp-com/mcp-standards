# V2 Implementation Roadmap: Quick Start Guide

**Ready-to-Execute Development Plan**
**Start Date**: 2025-10-20
**Target Completion**: 4-5 weeks

---

## Overview

This roadmap translates the [V2 AgentDB Integration Specification](./v2-agentdb-integration-spec.md) into actionable development tasks with clear priorities, dependencies, and acceptance criteria.

---

## Week 1: AgentDB Foundation

### Day 1-2: Environment Setup & Dependencies

**Tasks**:
```bash
# 1. Create feature branch
git checkout -b feature/v2-agentdb-integration

# 2. Install dependencies
npm install agentdb
pip install watchdog>=3.0.0

# 3. Create directory structure
mkdir -p src/mcp_standards/memory
mkdir -p src/mcp_standards/events
mkdir -p src/mcp_standards/migration
mkdir -p src/mcp_standards/benchmarks
mkdir -p tests/unit/memory
mkdir -p tests/integration/v2
mkdir -p tests/performance

# 4. Update pyproject.toml
# Add new dependencies (see spec section 9.2)
```

**Files to Create**:
- `src/mcp_standards/memory/__init__.py`
- `src/mcp_standards/events/__init__.py`
- `src/mcp_standards/migration/__init__.py`
- `src/mcp_standards/benchmarks/__init__.py`

**Acceptance Criteria**:
- ✅ Branch created and dependencies installed
- ✅ Directory structure matches specification
- ✅ No import errors when running `python -c "import mcp_standards"`

---

### Day 3-4: AgentDB Adapter Implementation

**Priority**: 🔴 Critical Path

**Implementation Order**:

1. **Create `agentdb_adapter.py`** (4-6 hours)
   ```python
   # File: src/mcp_standards/memory/agentdb_adapter.py
   # Reference: Spec Section 2.2
   ```
   - Implement `AgentDBAdapter.__init__()` with HNSW configuration
   - Implement `store()` method with embedding generation
   - Implement `search()` method with vector similarity
   - Add error handling and logging

2. **Create AgentDB subprocess wrapper** (2-3 hours)
   ```python
   # File: src/mcp_standards/memory/agentdb_wrapper.py
   # Fallback when native bindings unavailable
   ```

3. **Write unit tests** (2-3 hours)
   ```python
   # File: tests/unit/memory/test_agentdb_adapter.py
   ```

**Acceptance Criteria**:
- ✅ AgentDB adapter can store vectors
- ✅ Search returns results with similarity scores
- ✅ Embeddings generated correctly via EmbeddingManager
- ✅ Unit tests pass with >80% coverage

**Testing Commands**:
```bash
pytest tests/unit/memory/test_agentdb_adapter.py -v
pytest --cov=src/mcp_standards/memory/agentdb_adapter.py
```

---

### Day 5: SQLite Adapter Enhancement

**Priority**: 🟡 High

**Implementation Order**:

1. **Create `sqlite_adapter.py`** (3-4 hours)
   ```python
   # File: src/mcp_standards/memory/sqlite_adapter.py
   # Reference: Spec Section 2.3
   ```
   - Add `agentdb_synced` column to existing tables
   - Implement `store_metadata()` method
   - Implement `query_audit_log()` method
   - Create `reasoning_episodes` table schema

2. **Write migration SQL** (1-2 hours)
   ```sql
   -- File: src/mcp_standards/migrations/v2_schema.sql
   ALTER TABLE pattern_frequency ADD COLUMN agentdb_synced BOOLEAN DEFAULT FALSE;
   CREATE TABLE reasoning_episodes (...);
   CREATE TABLE sync_metadata (...);
   ```

**Acceptance Criteria**:
- ✅ SQLite adapter implements metadata storage
- ✅ New tables created successfully
- ✅ Backward compatible with v1 schema
- ✅ Migration SQL tested on copy of production DB

---

### Day 6-7: Memory Router Implementation

**Priority**: 🔴 Critical Path

**Implementation Order**:

1. **Create `router.py`** (6-8 hours)
   ```python
   # File: src/mcp_standards/memory/router.py
   # Reference: Spec Section 2.1
   ```
   - Implement `MemoryRouter.__init__()`
   - Implement `store_pattern()` (dual storage)
   - Implement `search_patterns()` with query type routing
   - Implement `_merge_results()` for hybrid queries

2. **Integration tests** (3-4 hours)
   ```python
   # File: tests/integration/v2/test_memory_router.py
   ```
   - Test semantic search routing
   - Test exact match routing
   - Test hybrid query merging
   - Test error handling

**Acceptance Criteria**:
- ✅ Router correctly dispatches to AgentDB vs SQLite
- ✅ Hybrid queries merge results properly
- ✅ All query types working (SEMANTIC, EXACT, AUDIT, TEMPORAL, HYBRID)
- ✅ Integration tests pass

**Testing Commands**:
```bash
pytest tests/integration/v2/test_memory_router.py -v --log-cli-level=INFO
```

---

## Week 2: Pattern Extractor Integration

### Day 8-9: Pattern Extractor Modification

**Priority**: 🔴 Critical Path

**Tasks**:

1. **Modify `pattern_extractor.py`** (6-8 hours)
   - Replace direct SQLite calls with `memory_router` calls
   - Add `_store_pattern_hybrid()` method
   - Implement `_check_semantic_promotion()` with clustering
   - Reduce promotion threshold from 3 → 2

2. **Update tests** (2-3 hours)
   ```python
   # File: tests/integration/test_pattern_learning.py
   ```
   - Test semantic clustering promotion
   - Test that 2 similar patterns trigger promotion
   - Verify AgentDB storage

**Acceptance Criteria**:
- ✅ Patterns stored in both AgentDB (vector) and SQLite (metadata)
- ✅ Semantic clustering triggers promotion at threshold 2
- ✅ Existing v1 pattern detection logic unchanged
- ✅ All pattern learning tests pass

**Migration Note**:
Existing `pattern_extractor.py` is 513 LOC. Changes are additive (not rewrite):
- Add `memory_router` parameter to `__init__` (~5 lines)
- Replace `_update_pattern_frequency()` call with `_store_pattern_hybrid()` (~20 lines)
- Add `_check_semantic_promotion()` method (~50 lines)
- Add `_promote_pattern_cluster()` method (~30 lines)

---

### Day 10-11: Benchmarking & Performance Tuning

**Priority**: 🟢 Medium

**Tasks**:

1. **Create benchmark suite** (4-5 hours)
   ```python
   # File: src/mcp_standards/benchmarks/performance.py
   # Reference: Spec Section 6.2
   ```
   - Implement `benchmark_startup()`
   - Implement `benchmark_search()`
   - Implement `benchmark_pattern_extraction()`

2. **Run benchmarks and optimize** (3-4 hours)
   ```bash
   python -m mcp_standards.benchmarks.performance --output results.json
   ```
   - Tune HNSW parameters (M, ef_construction, ef_search)
   - Test memory vs disk mode
   - Profile slow operations

**Acceptance Criteria**:
- ✅ Startup time <10ms (disk mode)
- ✅ Search time <1ms (P95)
- ✅ Pattern extraction <5ms average
- ✅ Benchmark results documented

**Performance Tuning Checklist**:
```yaml
HNSW Parameters:
  - M: 16 (default) → Test: 12, 16, 24
  - ef_construction: 200 → Test: 150, 200, 300
  - ef_search: 50 → Test: 30, 50, 100

Mode Selection:
  - disk: <10ms startup ✅
  - memory: ~100ms startup, faster search

Embedding Batch Size:
  - Test: 16, 32, 64, 128
```

---

### Day 12-13: Server Integration & MCP Tools

**Priority**: 🔴 Critical Path

**Tasks**:

1. **Update `server.py`** (4-5 hours)
   - Initialize `MemoryRouter` in `__init__`
   - Add new MCP tools: `semantic_search_patterns`, `cluster_related_patterns`
   - Update existing tools to use router
   - Add tool handlers

2. **Test MCP integration** (2-3 hours)
   ```python
   # File: tests/integration/test_mcp_tools_v2.py
   ```
   - Test semantic search tool
   - Test clustering tool
   - Verify backward compatibility with v1 tools

**New MCP Tools**:
```python
# semantic_search_patterns
# cluster_related_patterns
# record_reasoning_outcome (Phase 3)
# get_pattern_success_rate (Phase 3)
```

**Acceptance Criteria**:
- ✅ MCP server starts without errors
- ✅ New tools callable via MCP protocol
- ✅ Existing v1 tools still work
- ✅ Integration tests pass

---

### Day 14: Week 2 Review & Testing

**Tasks**:
- Run full test suite
- Fix any failing tests
- Code review (self-review using checklist)
- Update documentation for completed features

**Testing Commands**:
```bash
# Run all tests
pytest tests/ -v --cov=src/mcp_standards

# Run only v2 tests
pytest tests/integration/v2/ tests/unit/memory/ -v

# Benchmark
python -m mcp_standards.benchmarks.performance
```

---

## Week 3: Event-Driven Architecture

### Day 15-16: Event Bus Implementation

**Priority**: 🟡 High

**Tasks**:

1. **Create `event_bus.py`** (3-4 hours)
   ```python
   # File: src/mcp_standards/events/event_bus.py
   # Reference: Spec Section 3.3
   ```
   - Implement `Event` dataclass
   - Implement `EventBus` with subscribe/emit
   - Add async event processing loop
   - Add event type enum

2. **Create event types** (1-2 hours)
   ```python
   # File: src/mcp_standards/events/types.py

   class EventType(Enum):
       PATTERN_PROMOTED = "pattern_promoted"
       CONFIG_CHANGED = "config_changed"
       CLAUDEMD_UPDATED = "claudemd_updated"
       REASONING_OUTCOME = "reasoning_outcome"
   ```

3. **Unit tests** (2-3 hours)
   ```python
   # File: tests/unit/events/test_event_bus.py
   ```

**Acceptance Criteria**:
- ✅ Event bus can emit events
- ✅ Subscribers receive events asynchronously
- ✅ Event processing loop handles errors gracefully
- ✅ Unit tests pass

---

### Day 17-18: File Watcher & Config Monitor

**Priority**: 🟡 High

**Tasks**:

1. **Create `config_watcher.py`** (4-5 hours)
   ```python
   # File: src/mcp_standards/events/config_watcher.py
   # Uses: watchdog library
   ```
   - Implement file system monitoring (inotify/FSEvents)
   - Watch for changes to: `.editorconfig`, `pyproject.toml`, etc.
   - Emit `config_changed` events

2. **Integration with event bus** (2-3 hours)
   - Connect watcher to event bus
   - Add event handlers
   - Test end-to-end flow

**Acceptance Criteria**:
- ✅ File watcher detects config file changes
- ✅ Events emitted on file modification
- ✅ No memory leaks from file watching
- ✅ Cross-platform support (macOS, Linux, Windows)

**Testing**:
```bash
# Manual test
echo "# test" >> .editorconfig
# Should see event emitted in logs
```

---

### Day 19-20: CLAUDE.md Manager Enhancement

**Priority**: 🟡 High

**Tasks**:

1. **Enhance `claudemd_manager.py`** (5-6 hours)
   - Add event bus subscription
   - Implement `_on_pattern_promoted()` handler
   - Implement `_generate_content_semantic()` using AgentDB
   - Implement `_cluster_patterns_semantically()`

2. **Create `diff_learner.py`** (3-4 hours)
   ```python
   # File: src/mcp_standards/intelligence/diff_learner.py
   ```
   - Analyze CLAUDE.md backups
   - Extract user-added preferences
   - Learn from manual edits

**Acceptance Criteria**:
- ✅ CLAUDE.md auto-updates when patterns promoted
- ✅ No manual trigger needed
- ✅ Backup created before each update
- ✅ Semantic grouping improves organization

---

### Day 21: Proactive Suggester

**Priority**: 🟢 Medium

**Tasks**:

1. **Create `proactive_suggester.py`** (3-4 hours)
   ```python
   # File: src/mcp_standards/intelligence/proactive_suggester.py
   ```
   - Background job (runs every 5 minutes)
   - Checks for patterns ready for promotion
   - Sends MCP notifications

2. **MCP notification integration** (2-3 hours)
   - Research MCP notification protocol
   - Implement notification sender
   - Test notifications in Claude Desktop

**Acceptance Criteria**:
- ✅ Background job runs periodically
- ✅ Detects patterns ready for CLAUDE.md
- ✅ Notifications appear in Claude Desktop
- ✅ No performance impact from background job

---

## Week 4: ReasoningBank & Polish

### Day 22-23: ReasoningBank Implementation

**Priority**: 🟢 Medium

**Tasks**:

1. **Create `reasoning_bank.py`** (4-5 hours)
   ```python
   # File: src/mcp_standards/intelligence/reasoning_bank.py
   # Reference: Spec Section 5.2
   ```
   - Implement `record_outcome()`
   - Implement `get_pattern_success_rate()`
   - Implement Bayesian confidence adjustment

2. **Add MCP tools** (2-3 hours)
   - `record_reasoning_outcome`
   - `get_pattern_success_rate`

3. **Integration** (2-3 hours)
   - Hook into pattern application flow
   - Auto-detect outcomes (success/failure)
   - Update confidence scores

**Acceptance Criteria**:
- ✅ Outcomes recorded in `reasoning_episodes` table
- ✅ Confidence adjusts based on success rate
- ✅ Failed patterns demoted automatically
- ✅ MCP tools working

---

### Day 24-25: Migration Tool

**Priority**: 🔴 Critical Path (for v2 release)

**Tasks**:

1. **Create `v2_migrator.py`** (6-8 hours)
   ```python
   # File: src/mcp_standards/migration/v2_migrator.py
   # Reference: Spec Section 4.1
   ```
   - Implement backup creation
   - Implement schema migration
   - Implement pattern migration with embeddings
   - Implement verification

2. **Create migration CLI** (2-3 hours)
   ```python
   # File: src/mcp_standards/cli/migrate.py
   ```
   - CLI interface using `click`
   - Progress reporting
   - Dry-run mode

**Acceptance Criteria**:
- ✅ Migrates v1 database to v2 successfully
- ✅ All patterns have embeddings in AgentDB
- ✅ Data integrity verified
- ✅ Rollback works if migration fails

**Testing**:
```bash
# Dry run
mcp-standards migrate --db-path ~/.mcp-standards/knowledge.db --dry-run

# Actual migration
mcp-standards migrate --db-path ~/.mcp-standards/knowledge.db
```

---

### Day 26-27: Testing & Bug Fixes

**Priority**: 🔴 Critical Path

**Tasks**:

1. **Re-enable disabled tests** (4-6 hours)
   - Migrate tests from `tests/_disabled/`
   - Update for v2 architecture
   - Fix any breaking changes

2. **Integration testing** (3-4 hours)
   - End-to-end workflow tests
   - Test migration on real v1 database
   - Test MCP server with Claude Desktop

3. **Bug fixes** (4-6 hours)
   - Fix any issues found during testing
   - Address edge cases
   - Performance optimizations

**Acceptance Criteria**:
- ✅ Test coverage >80%
- ✅ All tests passing
- ✅ No critical bugs
- ✅ Migration tested on production data

---

### Day 28: Documentation & Release

**Priority**: 🟡 High

**Tasks**:

1. **Update documentation** (4-5 hours)
   - Update README.md
   - Update ARCHITECTURE.md
   - Create MIGRATION.md guide
   - Update API documentation

2. **Create release notes** (2-3 hours)
   ```markdown
   # v2.0.0 Release Notes

   ## Breaking Changes
   - Migration required from v1
   - New dependency: agentdb

   ## New Features
   - Semantic pattern matching
   - Event-driven CLAUDE.md updates
   - ReasoningBank outcome tracking
   - <10ms startup, <1ms search

   ## Migration Guide
   [Link to MIGRATION.md]
   ```

3. **Prepare release** (1-2 hours)
   - Tag release: `v2.0.0`
   - Create GitHub release
   - Update PyPI package

---

## Week 5: Optional Enhancements

### Stretch Goals (If Time Permits)

1. **Multi-Agent Coordination** (3-5 days)
   - Swarm memory layer
   - Cross-project pattern sharing
   - Reference: Spec Section 1.1 (optional component)

2. **Predictive Corrections** (2-3 days)
   - Predict next likely correction
   - Proactive suggestions
   - Reference: Spec Section 5.1 (new tool)

3. **Web UI for Pattern Management** (3-5 days)
   - View learned patterns
   - Manage confidence scores
   - Visualize pattern clusters

---

## Daily Checklist

Each day, before committing code:

```markdown
- [ ] All unit tests pass locally
- [ ] Code formatted with ruff
- [ ] Type hints added (mypy compatible)
- [ ] Docstrings updated
- [ ] No TODO comments in committed code
- [ ] Benchmark tests run (if performance-related)
- [ ] Git commit follows conventional commits format
- [ ] No secrets or credentials in code
```

---

## Git Workflow

```bash
# Daily workflow
git checkout feature/v2-agentdb-integration
git pull origin feature/v2-agentdb-integration

# Make changes...

# Before commit
pytest tests/ -v --cov=src/mcp_standards
ruff check src/ tests/
mypy src/

# Commit
git add .
git commit -m "feat(memory): implement AgentDB adapter with HNSW search

- Add AgentDBAdapter class with vector storage
- Implement semantic search with <1ms target
- Add embedding generation via EmbeddingManager
- Include unit tests with >80% coverage

Refs: #123"

# Push daily
git push origin feature/v2-agentdb-integration
```

---

## Success Metrics Tracking

Track these metrics throughout development:

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Startup Time | <10ms | - | ⏳ |
| Search Time (P95) | <1ms | - | ⏳ |
| Pattern Extraction | <5ms | - | ⏳ |
| Test Coverage | >80% | - | ⏳ |
| Semantic Match Accuracy | >85% | - | ⏳ |
| Promotion Threshold | 2 patterns | 3 | ⏳ |

Update daily in project tracking board.

---

## Troubleshooting Common Issues

### AgentDB Installation Issues

```bash
# If npm install agentdb fails
# Try:
npm cache clean --force
npm install agentdb

# If Python bindings unavailable
# Fallback to subprocess wrapper (implemented in spec)
```

### Performance Not Meeting Targets

```python
# Checklist:
# 1. HNSW parameters tuned?
#    - M=16, ef_construction=200, ef_search=50
# 2. Using disk mode for <10ms startup?
# 3. Embeddings cached?
# 4. SQLite WAL mode enabled?
# 5. Proper indexes on SQLite tables?
```

### Migration Failures

```bash
# Always create backup first
cp ~/.mcp-standards/knowledge.db ~/.mcp-standards/knowledge.backup.db

# If migration fails, rollback
mv ~/.mcp-standards/knowledge.backup.db ~/.mcp-standards/knowledge.db
```

---

## Resources

- [V2 AgentDB Integration Spec](./v2-agentdb-integration-spec.md) - Complete technical specification
- [V2 System Analysis](../v2-system-analysis.md) - Gap analysis and requirements
- [AgentDB Documentation](https://agentdb.ruv.io) - AgentDB API reference
- [Context Engineering Guide](https://github.com/coleam00/context-engineering-intro) - Token optimization principles

---

## Questions & Support

**Technical Questions**:
- Review spec sections for implementation details
- Check existing v1 code for patterns
- Reference AgentDB documentation

**Architecture Decisions**:
- Refer to Architecture Decision Records (ADRs) in spec
- Consult with team lead

**Blocked?**:
- Create GitHub issue with "blocked" label
- Document blocking issue and alternatives considered

---

**Ready to Start**: ✅

**First Command**:
```bash
git checkout -b feature/v2-agentdb-integration
mkdir -p src/mcp_standards/memory
code src/mcp_standards/memory/agentdb_adapter.py
```

**Let's build v2! 🚀**

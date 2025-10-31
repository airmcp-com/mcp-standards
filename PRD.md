# Product Requirements Document: Simple Personal Memory MCP Server

## Executive Summary

A lightweight, production-ready MCP (Model Context Protocol) server that provides Claude with persistent semantic memory for user preferences, corrections, and workflow rules. Demonstrates best practices for MCP tool design with high auto-discovery rates (70-95%) and serves as a reference implementation for the MCP community.

**Status**: Phase 2 - Enhancement & Documentation
**Version**: 1.0.0
**Last Updated**: 2025-10-30

---

## 1. Product Vision

### 1.1 Problem Statement

Claude Code users repeatedly correct and specify preferences (package managers, commit styles, workflows) that are forgotten between sessions. This creates friction and reduces productivity as users must re-state preferences constantly.

Existing solutions either:
- Require complex vector databases (barriers to adoption)
- Lack semantic search capabilities
- Don't demonstrate MCP best practices effectively

### 1.2 Solution

A minimal MCP server with two core tools (`remember` and `recall`) that:
- Uses AgentDB for semantic vector search (150x faster than alternatives)
- Achieves 70-95% auto-discovery rates through optimized tool descriptions
- Runs in-process with zero external dependencies
- Serves as a reference implementation for MCP developers

### 1.3 Success Metrics

- **Auto-trigger Rate**: 70-95% for implicit preference checks
- **Setup Time**: <5 minutes from install to first use
- **Memory Footprint**: <100MB for typical usage
- **Query Latency**: <100ms for semantic search
- **Adoption**: 1000+ installs in first quarter

---

## 2. User Personas

### Primary: Claude Code Power User
- Uses Claude Code daily for software development
- Has established preferences for tools and workflows
- Values efficiency and minimal configuration
- Comfortable with npm/Python package management

### Secondary: MCP Server Developer
- Building custom MCP servers for specific domains
- Needs reference implementations of best practices
- Wants to understand tool auto-discovery patterns
- Interested in semantic memory patterns

### Tertiary: Enterprise Developer
- Requires team-wide preference sharing
- Needs audit trails and compliance features (future)
- Values security and data privacy

---

## 3. Core Features

### 3.1 Memory Storage (`remember` tool)

**Description**: Store user preferences, corrections, and workflow rules in semantic memory.

**Trigger Patterns**:
- Explicit: "Remember: use uv not pip"
- Preference: "I prefer conventional commits"
- Workflow: "Always use feature branches"
- Correction: "Actually, use poetry instead"
- Rule: "Never commit directly to main"

**Auto-Discovery Rate**: 85-95%

**Parameters**:
- `content` (required): What to remember
- `category` (optional): Domain classification (python, git, docker, general)
- `importance` (optional): 1-10 priority score

**Behavior**:
- Semantic embedding generation via AgentDB
- Automatic timestamp and metadata tagging
- Duplicate detection and merging
- Return confirmation with memory ID

**Success Criteria**:
- ✅ Stores preference with <50ms latency
- ✅ Generates semantic embedding automatically
- ✅ Returns unique memory ID for reference
- ✅ Handles edge cases (empty content, duplicates)

### 3.2 Memory Retrieval (`recall` tool)

**Description**: Search user's stored preferences using semantic search.

**Trigger Patterns**:
- Before tool recommendations: "What Python package manager should I use?"
- Workflow queries: "How do I commit code?"
- Implicit checks: Automatically before suggesting pip/npm/git commands

**Auto-Discovery Rate**: 70-85%

**Parameters**:
- `query` (required): Search query for preferences
- `category` (optional): Filter by domain
- `limit` (optional): Max results (default 5)

**Behavior**:
- Semantic similarity search via AgentDB
- Return ranked results with relevance scores
- Include metadata (timestamp, category, importance)
- Graceful handling of no matches

**Success Criteria**:
- ✅ Returns results in <100ms
- ✅ Relevance scores >0.7 for exact matches
- ✅ Handles typos and semantic variations
- ✅ Returns empty array gracefully (no errors)

### 3.3 Memory Management (`list_memories` tool)

**Description**: List all stored preferences with filtering and pagination.

**Parameters**:
- `category` (optional): Filter by domain
- `limit` (optional): Pagination size
- `offset` (optional): Pagination offset

**Auto-Discovery Rate**: 20-30% (utility tool, not proactive)

**Behavior**:
- Return all memories sorted by importance/recency
- Include full metadata for each memory
- Support category filtering
- Pagination for large memory stores

---

## 4. Technical Architecture

### 4.1 Technology Stack

**Core**:
- Python 3.11+ with `uv` package manager
- MCP SDK: `mcp` package (official Anthropic SDK)
- Vector Database: AgentDB (150x faster than alternatives)

**Development**:
- Testing: pytest
- Type Checking: mypy
- Linting: ruff
- Build: uv + pyproject.toml

**Deployment**:
- Distribution: npm package (`npx mcp-standards`)
- Python execution: `uv run python -m mcp_standards.server_simple`
- Config: Claude Desktop `claude_desktop_config.json`

### 4.2 Data Model

**Memory Record**:
```python
{
  "id": str,                    # Unique identifier
  "content": str,               # User preference text
  "category": str,              # python|git|docker|general
  "importance": int,            # 1-10 priority
  "timestamp": datetime,        # Creation time
  "embedding": List[float],     # 768-dim vector (AgentDB)
  "metadata": {
    "source": str,              # "user_correction" | "explicit"
    "context": str              # Optional context
  }
}
```

**AgentDB Storage**:
- Collection: `user_preferences`
- Embedding Model: `sentence-transformers/all-MiniLM-L6-v2`
- Distance Metric: Cosine similarity
- Index: HNSW for fast retrieval

### 4.3 File Structure

```
mcp-standards/
├── src/mcp_standards/
│   ├── __init__.py
│   ├── server_simple.py          # Main MCP server
│   ├── memory_store.py           # AgentDB wrapper
│   └── utils.py                  # Helpers
├── tests/
│   ├── test_server.py
│   ├── test_memory_store.py
│   └── test_integration.py
├── docs/
│   ├── PRD.md                    # This file
│   ├── SETUP_GUIDE.md
│   └── VALIDATION_CHECKLIST.md
├── pyproject.toml                # Python config
├── package.json                  # npm distribution
└── README.md
```

### 4.4 Tool Description Patterns (Critical for Auto-Discovery)

**remember Tool**:
```python
Tool(
    name="remember",
    description=(
        "Store user preferences, corrections, and workflow rules in semantic memory. "
        "Use when user explicitly shares preferences or corrects your suggestions. "
        "**Trigger phrases**: 'remember', 'I prefer', 'always use', 'never use', "
        "'my workflow', 'instead of', 'not X, use Y', 'actually use X'. "
        "**Examples**: 'Remember: use uv not pip', 'I prefer conventional commits', "
        "'Always create feature branches', 'Never commit to main directly'. "
        "**Categories**: python (pip/uv/poetry/conda), git (commit/branch/merge), "
        "docker (compose/build), general (any other preferences)."
    )
)
```

**recall Tool**:
```python
Tool(
    name="recall",
    description=(
        "Search user's stored preferences using semantic search. "
        "**IMPORTANT: Use this BEFORE making any tool/command recommendations.** "
        "Check if user has preferences for: Python package managers (pip/uv/poetry/conda), "
        "Git workflows (commit styles, branch naming, merge vs rebase), "
        "Docker usage (compose/CLI), build tools (npm/yarn/pnpm), testing frameworks. "
        "**Always use when**: suggesting commands, recommending tools, before running "
        "npm/pip/git commands, when user asks 'how do I...' questions. "
        "**Examples**: 'python package manager', 'git commit style', 'preferred testing framework'."
    )
)
```

---

## 5. Development Phases

### Phase 1: Core Implementation ✅ COMPLETED
**Duration**: 2 weeks
**Status**: Done

**Deliverables**:
- ✅ MCP server with `remember` and `recall` tools
- ✅ AgentDB integration for vector search
- ✅ Basic test suite (>80% coverage)
- ✅ Initial validation checklist

**Success Criteria**:
- ✅ Server starts without errors
- ✅ Tools appear in Claude Desktop
- ✅ Basic remember/recall workflows functional

### Phase 2: Enhancement & Documentation 🔄 IN PROGRESS
**Duration**: 1-2 weeks
**Status**: Current Phase

**Deliverables**:
- 🔄 This PRD document
- ⏳ Comprehensive setup guide
- ⏳ Validation checklist refinement
- ⏳ Auto-discovery optimization
- ⏳ Performance benchmarks

**Success Criteria**:
- Auto-trigger rate >70% for recall
- Auto-trigger rate >85% for remember
- Setup time <5 minutes
- Documentation complete

### Phase 3: Production Hardening
**Duration**: 2 weeks
**Status**: Planned

**Deliverables**:
- Error handling and edge cases
- Logging and observability
- Performance optimization
- Security audit
- CI/CD pipeline

**Success Criteria**:
- Zero crashes in 1000+ operations
- Query latency <100ms p99
- Memory footprint <100MB
- All security checks pass

### Phase 4: Community Release
**Duration**: 1 week
**Status**: Planned

**Deliverables**:
- npm package publication
- GitHub repository public release
- Blog post and announcement
- Community feedback collection

**Success Criteria**:
- 100+ installs in first week
- <5 bug reports
- Positive community feedback

---

## 6. User Workflows

### 6.1 First-Time Setup

**Steps**:
1. User runs `npx mcp-standards install`
2. Tool adds server to `claude_desktop_config.json`
3. User restarts Claude Desktop
4. Server appears in MCP tools list (verifiable via wrench icon)

**Time**: <5 minutes
**Success Rate**: >95%

### 6.2 Storing a Preference

**User Action**: "Remember: use uv instead of pip for Python packages"

**Expected Behavior**:
1. Claude auto-triggers `remember` tool (85%+ rate)
2. Tool stores preference with category=python
3. Claude confirms: "I've stored your preference to use uv for Python packages"

**Fallback**: If auto-trigger fails, Claude prompts: "Would you like me to remember this?"

### 6.3 Recalling Preferences (Implicit)

**User Action**: "Help me install a Python package"

**Expected Behavior**:
1. Claude auto-triggers `recall` tool with query="python package manager" (70%+ rate)
2. Tool returns preference: "use uv instead of pip"
3. Claude suggests: "I'll use uv to install the package: `uv pip install <package>`"

**Fallback**: If no preference found, Claude asks: "Do you have a preferred Python package manager?"

### 6.4 Recalling Preferences (Explicit)

**User Action**: "What's my preferred Git commit style?"

**Expected Behavior**:
1. Claude auto-triggers `recall` tool with query="git commit style"
2. Tool returns preference: "conventional commits"
3. Claude responds: "You prefer conventional commits with the format `<type>: <summary>`"

---

## 7. Non-Functional Requirements

### 7.1 Performance

- **Query Latency**: <100ms p99 for semantic search
- **Memory Usage**: <100MB for 1000+ stored preferences
- **Startup Time**: <2 seconds for server initialization
- **Throughput**: 100+ requests/second

### 7.2 Reliability

- **Uptime**: 99.9% availability during Claude sessions
- **Data Persistence**: Zero data loss on graceful shutdown
- **Error Recovery**: Graceful degradation on database errors
- **Crash Rate**: <0.01% of operations

### 7.3 Security

- **Data Privacy**: All data stored locally (no cloud)
- **Encryption**: Optional encryption at rest (future)
- **Access Control**: Single-user model (no multi-user in v1.0)
- **Audit Trail**: Timestamps for all memory operations

### 7.4 Usability

- **Setup Time**: <5 minutes from install to first use
- **Documentation**: Complete setup guide with screenshots
- **Error Messages**: Clear, actionable error messages
- **Compatibility**: Works on macOS, Linux, Windows (WSL)

### 7.5 Maintainability

- **Code Coverage**: >80% test coverage
- **Type Safety**: 100% type hints with mypy validation
- **Linting**: Zero ruff errors
- **Documentation**: Inline docstrings for all public APIs

---

## 8. Testing Strategy

### 8.1 Unit Tests

**Coverage**: 80%+

**Test Cases**:
- Memory storage and retrieval
- Semantic search accuracy
- Tool parameter validation
- Error handling edge cases
- Duplicate detection

### 8.2 Integration Tests

**Coverage**: Core workflows

**Test Cases**:
- End-to-end remember/recall flow
- AgentDB persistence across restarts
- MCP protocol compliance
- Claude Desktop integration

### 8.3 Performance Tests

**Benchmarks**:
- Query latency under load
- Memory usage with 1000+ memories
- Concurrent request handling
- Embedding generation speed

### 8.4 User Acceptance Tests

**Validation**:
- First-time setup on fresh system
- Auto-discovery rate measurement
- Real-world preference workflows
- Documentation clarity

---

## 9. Success Criteria

### Phase 2 Completion (Current)

- ✅ PRD document complete
- ⏳ Auto-trigger rate >70% for recall
- ⏳ Auto-trigger rate >85% for remember
- ⏳ Setup guide complete with validation checklist
- ⏳ Performance benchmarks documented

### v1.0 Production Release

- Query latency <100ms p99
- Memory usage <100MB
- Test coverage >80%
- Zero critical bugs
- Documentation complete
- 100+ community installs

---

## 10. Future Enhancements (Post-v1.0)

### 10.1 Team Collaboration
- Shared preference stores across team members
- Import/export capabilities
- Preference versioning and history

### 10.2 Advanced Memory Management
- Preference conflict resolution
- Memory importance auto-learning
- Time-based preference decay
- Context-aware preference selection

### 10.3 Enterprise Features
- Multi-user support with RBAC
- Audit logs and compliance
- Encryption at rest
- Cloud sync (optional)

### 10.4 Developer Tools
- CLI for memory management
- Web UI for preference browsing
- Analytics and insights
- Memory debugging tools

---

## 11. Risks & Mitigations

### 11.1 Auto-Discovery Rate Below Target

**Risk**: Tool descriptions don't trigger automatically
**Probability**: Medium
**Impact**: High (defeats primary value proposition)
**Mitigation**:
- A/B test tool description variants
- Monitor actual trigger rates in logs
- Iterate based on real-world usage patterns
- Provide fallback manual invocation patterns

### 11.2 AgentDB Performance Issues

**Risk**: Semantic search too slow for real-time use
**Probability**: Low
**Impact**: High
**Mitigation**:
- Benchmark early and often
- Implement caching layer if needed
- Consider quantization for embedding size
- Fallback to keyword search if semantic fails

### 11.3 Installation Complexity

**Risk**: Users unable to complete setup
**Probability**: Medium
**Impact**: High (blocks adoption)
**Mitigation**:
- Comprehensive setup guide with screenshots
- Automated validation checklist
- Common error troubleshooting section
- Video walkthrough (future)

### 11.4 Data Persistence Bugs

**Risk**: Memories lost on crashes or restarts
**Probability**: Medium
**Impact**: High (trust erosion)
**Mitigation**:
- Thorough integration tests
- Write-ahead logging (WAL) in AgentDB
- Automatic backup on shutdown
- Recovery mode for corrupted databases

---

## 12. Dependencies

### 12.1 External Dependencies

- **MCP SDK** (`mcp`): Official protocol implementation
- **AgentDB**: Vector database (150x faster than alternatives)
- **uv**: Python package manager (required for execution)
- **Claude Desktop**: MCP server runtime

### 12.2 Development Dependencies

- **pytest**: Testing framework
- **mypy**: Type checking
- **ruff**: Linting and formatting
- **pytest-asyncio**: Async test support

### 12.3 Critical Path Dependencies

1. AgentDB stability and performance
2. MCP SDK compatibility with Claude Desktop
3. uv availability on target platforms

---

## 13. Metrics & Monitoring

### 13.1 Key Performance Indicators (KPIs)

- **Auto-trigger Rate**: 70-95% (measured via logs)
- **Query Latency**: p50, p95, p99 response times
- **Memory Usage**: Peak and average RAM consumption
- **Crash Rate**: Errors per 1000 operations
- **User Adoption**: Install count, active users

### 13.2 Monitoring Strategy

**Development**:
- Unit test execution time
- Code coverage reports
- Type checking violations
- Linting errors

**Production**:
- MCP logs in `~/Library/Logs/Claude/mcp*.log`
- AgentDB performance metrics
- Error rate tracking
- User feedback collection

---

## 14. References

- [MCP Specification](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)
- [AgentDB Documentation](https://github.com/ruvnet/agentdb)
- [Project Memory](../docs/.project_memory.md)
- [Validation Checklist](../docs/VALIDATION_CHECKLIST.md)

---

## 15. Approval & Sign-off

**Product Owner**: Matt Strautmann
**Status**: Draft for Review
**Version**: 1.0.0
**Date**: 2025-10-30

**Approval Status**:
- [ ] Product requirements reviewed
- [ ] Technical architecture validated
- [ ] Success criteria agreed upon
- [ ] Ready for Phase 2 completion

---

*This PRD is a living document and will be updated as the project evolves.*

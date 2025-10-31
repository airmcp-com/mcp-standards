# Claude Code Configuration - SPARC Development Environment

## 🚨 CRITICAL: CONCURRENT EXECUTION & FILE MANAGEMENT

**ABSOLUTE RULES**:
1. ALL operations MUST be concurrent/parallel in a single message
2. **NEVER save working files, text/mds and tests to the root folder**
3. ALWAYS organize files in appropriate subdirectories
4. **USE CLAUDE CODE'S TASK TOOL** for spawning agents concurrently, not just MCP

### ⚡ GOLDEN RULE: "1 MESSAGE = ALL RELATED OPERATIONS"

**MANDATORY PATTERNS:**
- **TodoWrite**: ALWAYS batch ALL todos in ONE call (5-10+ todos minimum)
- **Task tool (Claude Code)**: ALWAYS spawn ALL agents in ONE message with full instructions
- **File operations**: ALWAYS batch ALL reads/writes/edits in ONE message
- **Bash commands**: ALWAYS batch ALL terminal operations in ONE message
- **Memory operations**: ALWAYS batch ALL memory store/retrieve in ONE message

### 🎯 CRITICAL: Claude Code Task Tool for Agent Execution

**Claude Code's Task tool is the PRIMARY way to spawn agents:**
```javascript
// ✅ CORRECT: Use Claude Code's Task tool for parallel agent execution
[Single Message]:
  Task("Research agent", "Analyze requirements and patterns...", "researcher")
  Task("Coder agent", "Implement core features...", "coder")
  Task("Tester agent", "Create comprehensive tests...", "tester")
  Task("Reviewer agent", "Review code quality...", "reviewer")
  Task("Architect agent", "Design system architecture...", "system-architect")
```

**MCP tools are ONLY for coordination setup:**
- `mcp__claude-flow__swarm_init` - Initialize coordination topology
- `mcp__claude-flow__agent_spawn` - Define agent types for coordination
- `mcp__claude-flow__task_orchestrate` - Orchestrate high-level workflows

### 📁 File Organization Rules

**NEVER save to root folder. Use these directories:**
- `/src` - Source code files
- `/tests` - Test files
- `/docs` - Documentation and markdown files
- `/config` - Configuration files
- `/scripts` - Utility scripts
- `/examples` - Example code

## Project Overview

**PROJECT: Simple Personal Memory MCP Server**

**Mission**: Build a lightweight, production-ready MCP server that provides Claude with persistent semantic memory for user preferences, corrections, and workflow rules. Demonstrates MCP best practices with 70-95% auto-discovery rates.

**Status**: Phase 2 - Enhancement & Documentation
**Version**: 1.0.0 MVP
**Branch**: fresh-start-simple-memory-mcp

### Core Purpose
Enables Claude to remember user preferences (package managers, commit styles, workflows) across sessions using semantic vector search. Serves as reference implementation for MCP community.

### Key Requirements
- **Auto-trigger Rate**: 70-95% for implicit preference checks
- **Query Latency**: <100ms for semantic search (p99)
- **Memory Footprint**: <100MB for 1000+ preferences
- **Setup Time**: <5 minutes from install to first use
- **Test Coverage**: >80% with mypy strict mode

### Technology Stack

**🚨 DECISION REQUIRED: Choose TypeScript OR Rust**

#### Option A: TypeScript/Node.js (Recommended)
- **Language**: TypeScript + Node.js
- **Package Manager**: npm/pnpm
- **MCP SDK**: Official `@modelcontextprotocol/sdk` (v1.20.2+)
- **Vector DB**: AgentDB (as per PRD - 150x faster, native Node.js)
- **Embeddings**: sentence-transformers via transformers.js (384-dim)
- **Testing**: vitest, typescript-eslint
- **Pros**: Mature ecosystem, AgentDB native support, faster development
- **Cons**: Slightly higher memory footprint than Rust

#### Option B: Rust (High Performance)
- **Language**: Rust
- **Package Manager**: cargo
- **MCP SDK**: Official `rmcp` SDK or Prism MCP (production-grade)
- **Vector DB**: AgentDB via FFI or alternative (qdrant-client)
- **Embeddings**: Rust embeddings crate or Python bridge
- **Testing**: cargo test
- **Pros**: 4,700+ QPS performance, minimal memory footprint
- **Cons**: Steeper learning curve, AgentDB integration more complex

### Critical Context
This project does NOT use SPARC workflow or claude-flow orchestration. It's a simple MCP server following standard TDD practices with **TypeScript or Rust** (Python rejected).

---

## 🎯 Project-Specific Development Guide

### File Structure

**TypeScript Structure** (Recommended):
```
mcp-standards/
├── src/
│   ├── index.ts                  # Main MCP server entry point
│   ├── server.ts                 # MCP server implementation
│   ├── memory-store.ts           # AgentDB wrapper
│   ├── embeddings.ts             # Embedding generation (transformers.js)
│   ├── types.ts                  # TypeScript interfaces
│   └── utils.ts                  # Validation helpers
├── tests/
│   ├── server.test.ts            # MCP integration tests
│   ├── memory-store.test.ts      # AgentDB unit tests
│   ├── embeddings.test.ts        # Embedding tests
│   └── integration.test.ts       # End-to-end workflows
├── docs/
│   ├── .project_memory.md        # Comprehensive project context
│   ├── PRD.md                    # Product requirements
│   ├── SETUP_GUIDE.md            # Installation guide
│   └── VALIDATION_CHECKLIST.md   # Testing procedures
├── package.json                  # npm config + distribution
├── tsconfig.json                 # TypeScript config
└── README.md                     # User documentation
```

**Rust Structure** (High Performance Alternative):
```
mcp-standards/
├── src/
│   ├── main.rs                   # Main MCP server entry point
│   ├── server.rs                 # MCP server implementation
│   ├── memory_store.rs           # AgentDB/vector DB wrapper
│   ├── embeddings.rs             # Embedding generation
│   └── lib.rs                    # Library exports
├── tests/
│   ├── server_test.rs
│   ├── memory_store_test.rs
│   └── integration_test.rs
├── docs/
│   ├── .project_memory.md
│   ├── PRD.md
│   ├── SETUP_GUIDE.md
│   └── VALIDATION_CHECKLIST.md
├── Cargo.toml                    # Rust config
├── package.json                  # npm wrapper for distribution
└── README.md
```

### Development Commands

#### TypeScript Commands (Recommended)

**Setup & Installation**:
```bash
# Install dependencies
npm install
# or
pnpm install

# Build TypeScript
npm run build

# Run server locally
npm start
# or
node dist/index.js
```

**Testing**:
```bash
# Run all tests with coverage
npm test

# Run specific test file
npm test -- tests/memory-store.test.ts

# Type checking (must pass with zero errors)
npm run typecheck
# or
tsc --noEmit

# Linting (must pass with zero errors)
npm run lint
```

**Development Mode**:
```bash
# Watch mode with hot reload
npm run dev

# Verify server starts
npm start -- --validate
```

#### Rust Commands (High Performance Alternative)

**Setup & Installation**:
```bash
# Build project
cargo build

# Build for production (optimized)
cargo build --release

# Run server locally
cargo run
# or
./target/release/mcp-standards
```

**Testing**:
```bash
# Run all tests
cargo test

# Run specific test
cargo test memory_store

# Run with output
cargo test -- --nocapture

# Linting (must pass with zero errors)
cargo clippy -- -D warnings

# Format code
cargo fmt --check
```

**Development Mode**:
```bash
# Watch mode with auto-rebuild
cargo watch -x run

# Check compilation without building
cargo check
```

### Core MCP Tools to Implement

#### TypeScript Implementation

**1. remember** - Store user preferences
```typescript
server.tool({
  name: 'remember',
  description: `Store user preferences, corrections, and workflow rules in semantic memory.

    **Trigger phrases**: 'remember', 'I prefer', 'always use', 'never use'
    **Examples**: 'Remember: use uv not pip', 'I prefer conventional commits'
    **Categories**: python, git, docker, general`,
  inputSchema: {
    type: 'object',
    properties: {
      content: { type: 'string', description: 'The preference to remember' },
      category: { type: 'string', enum: ['python', 'git', 'docker', 'general'], default: 'general' },
      importance: { type: 'number', minimum: 1, maximum: 10, default: 5 }
    },
    required: ['content']
  }
}, async ({ content, category, importance }) => {
  // Implementation: Generate embedding, store in AgentDB, return confirmation
});
```

**2. recall** - Retrieve preferences via semantic search
```typescript
server.tool({
  name: 'recall',
  description: `Search stored preferences using semantic search.

    **IMPORTANT: Use this BEFORE making tool/command recommendations.**
    **Always use when**: suggesting commands, before running npm/pip/git
    **Examples**: 'python package manager', 'git commit style'`,
  inputSchema: {
    type: 'object',
    properties: {
      query: { type: 'string', description: 'Search query' },
      category: { type: 'string', enum: ['python', 'git', 'docker', 'general'] },
      limit: { type: 'number', default: 5 }
    },
    required: ['query']
  }
}, async ({ query, category, limit }) => {
  // Implementation: Generate query embedding, search AgentDB, return ranked results
});
```

#### Rust Implementation (Alternative)

```rust
#[tool]
async fn remember(
    #[description("The preference to remember")] content: String,
    #[description("Category")] category: Option<String>,
    #[description("Importance 1-10")] importance: Option<u8>
) -> Result<ToolResponse, Error> {
    // Implementation
}

#[tool]
async fn recall(
    #[description("Search query")] query: String,
    category: Option<String>,
    limit: Option<usize>
) -> Result<Vec<MemoryRecord>, Error> {
    // Implementation
}
```

### Auto-Discovery Optimization

**Critical Pattern**: Tool descriptions MUST include:
1. **What it does** (specific, not generic)
2. **Explicit trigger phrases** in quotes
3. **Concrete examples** in user language
4. **Domain specificity** (e.g., "pip/uv/poetry/conda")
5. **Directive language** ("IMPORTANT: Use this BEFORE...")

See [docs/.project_memory.md](docs/.project_memory.md) for complete auto-discovery formula.

### Data Model

```python
@dataclass
class MemoryRecord:
    id: str                           # UUID4
    content: str                      # User preference text
    category: str                     # python|git|docker|general
    importance: int                   # 1-10 priority
    timestamp: datetime               # UTC
    embedding: List[float]            # 384-dim (all-MiniLM-L6-v2)
    metadata: Dict[str, str]          # Additional context
```

### Critical Implementation Rules

#### TypeScript Rules

1. **Async/Await**: All MCP tool handlers must be async
   - Use `async/await` for all I/O operations
   - Handle promises properly, no dangling promises

2. **Type Safety**: Use TypeScript strict mode
   - ❌ WRONG: `any` types everywhere
   - ✅ CORRECT: Proper interfaces and type definitions
   - Enable `strict: true` in tsconfig.json

3. **Error Handling**: Graceful degradation, no crashes
   - Return empty arrays for no results, not errors
   - Log errors but don't expose internal details to Claude
   - Use try/catch blocks around all I/O

4. **AgentDB Integration**: Use official AgentDB npm package
   - Initialize once at server startup
   - Reuse connection throughout server lifecycle
   - Handle connection errors gracefully

5. **Dependency Management**: Lock versions in package.json
   - Use exact versions for production dependencies
   - Use `npm ci` in CI/CD, not `npm install`

#### Rust Rules

1. **Error Handling**: Use Result<T, E> pattern
   - Never use `.unwrap()` in production code
   - Use `?` operator for error propagation
   - Return proper error types from tools

2. **Async Runtime**: Use tokio runtime
   - Mark tool functions with `async fn`
   - Use tokio for concurrent operations
   - Configure runtime properly in main.rs

3. **Memory Safety**: Leverage Rust ownership
   - No unsafe code unless absolutely necessary
   - Use Arc<Mutex<T>> for shared state
   - Avoid clones where references work

4. **Dependencies**: Minimize crate count
   - Use cargo-audit to check for vulnerabilities
   - Lock versions in Cargo.lock
   - Prefer well-maintained crates

### Performance Targets

- **Query Latency**: <100ms p99 (measure with pytest-benchmark)
- **Memory Usage**: <100MB for 1000 memories (measure with memory_profiler)
- **Startup Time**: <2 seconds (measure with time command)
- **Test Coverage**: >80% (measure with pytest-cov)

### Testing Strategy

**Unit Tests** (>80% coverage):
- Memory storage and retrieval logic
- Semantic search accuracy (>0.7 similarity for exact matches)
- Tool parameter validation
- Edge cases (empty content, no results, duplicates)

**Integration Tests** (all workflows):
- End-to-end remember → recall flow
- MCP protocol compliance
- Persistence across server restarts
- Claude Desktop integration

**Performance Tests** (benchmarks):
- Query latency under load (100+ memories)
- Memory usage scaling
- Embedding generation speed

### Current Phase: Phase 2 Tasks

- [x] Create PRD document
- [x] Research AgentDB alternatives
- [x] Create comprehensive project memory
- [x] Update CLAUDE.md with project context
- [ ] Decide on vector database (ChromaDB vs custom)
- [ ] Update PRD with corrected specs (384-dim embeddings)
- [ ] Implement core tools (remember, recall, list)
- [ ] Write comprehensive test suite
- [ ] Measure auto-discovery rates
- [ ] Complete setup guide and validation checklist

### Key Documentation

- **[docs/.project_memory.md](docs/.project_memory.md)**: Comprehensive research, decisions, architecture
- **[PRD.md](PRD.md)**: Product requirements (needs updates for 384-dim correction)
- **[CLAUDE.md](CLAUDE.md)**: This file - project configuration

---

## ⚠️ SPARC Commands (Not Used in This Project)

The following SPARC commands are NOT applicable to this project. This is a standard Python MCP server project, not using SPARC methodology.

## SPARC Commands

### Core Commands
- `npx claude-flow sparc modes` - List available modes
- `npx claude-flow sparc run <mode> "<task>"` - Execute specific mode
- `npx claude-flow sparc tdd "<feature>"` - Run complete TDD workflow
- `npx claude-flow sparc info <mode>` - Get mode details

### Batchtools Commands
- `npx claude-flow sparc batch <modes> "<task>"` - Parallel execution
- `npx claude-flow sparc pipeline "<task>"` - Full pipeline processing
- `npx claude-flow sparc concurrent <mode> "<tasks-file>"` - Multi-task processing

### Build Commands
- `npm run build` - Build project
- `npm run test` - Run tests
- `npm run lint` - Linting
- `npm run typecheck` - Type checking

## SPARC Workflow Phases

1. **Specification** - Requirements analysis (`sparc run spec-pseudocode`)
2. **Pseudocode** - Algorithm design (`sparc run spec-pseudocode`)
3. **Architecture** - System design (`sparc run architect`)
4. **Refinement** - TDD implementation (`sparc tdd`)
5. **Completion** - Integration (`sparc run integration`)

## Code Style & Best Practices

- **Modular Design**: Files under 500 lines
- **Environment Safety**: Never hardcode secrets
- **Test-First**: Write tests before implementation
- **Clean Architecture**: Separate concerns
- **Documentation**: Keep updated

## 🚀 Available Agents (54 Total)

### Core Development
`coder`, `reviewer`, `tester`, `planner`, `researcher`

### Swarm Coordination
`hierarchical-coordinator`, `mesh-coordinator`, `adaptive-coordinator`, `collective-intelligence-coordinator`, `swarm-memory-manager`

### Consensus & Distributed
`byzantine-coordinator`, `raft-manager`, `gossip-coordinator`, `consensus-builder`, `crdt-synchronizer`, `quorum-manager`, `security-manager`

### Performance & Optimization
`perf-analyzer`, `performance-benchmarker`, `task-orchestrator`, `memory-coordinator`, `smart-agent`

### GitHub & Repository
`github-modes`, `pr-manager`, `code-review-swarm`, `issue-tracker`, `release-manager`, `workflow-automation`, `project-board-sync`, `repo-architect`, `multi-repo-swarm`

### SPARC Methodology
`sparc-coord`, `sparc-coder`, `specification`, `pseudocode`, `architecture`, `refinement`

### Specialized Development
`backend-dev`, `mobile-dev`, `ml-developer`, `cicd-engineer`, `api-docs`, `system-architect`, `code-analyzer`, `base-template-generator`

### Testing & Validation
`tdd-london-swarm`, `production-validator`

### Migration & Planning
`migration-planner`, `swarm-init`

## 🎯 Claude Code vs MCP Tools

### Claude Code Handles ALL EXECUTION:
- **Task tool**: Spawn and run agents concurrently for actual work
- File operations (Read, Write, Edit, MultiEdit, Glob, Grep)
- Code generation and programming
- Bash commands and system operations
- Implementation work
- Project navigation and analysis
- TodoWrite and task management
- Git operations
- Package management
- Testing and debugging

### MCP Tools ONLY COORDINATE:
- Swarm initialization (topology setup)
- Agent type definitions (coordination patterns)
- Task orchestration (high-level planning)
- Memory management
- Neural features
- Performance tracking
- GitHub integration

**KEY**: MCP coordinates the strategy, Claude Code's Task tool executes with real agents.

## 🚀 Quick Setup

```bash
# Add MCP servers (Claude Flow required, others optional)
claude mcp add claude-flow npx claude-flow@alpha mcp start
claude mcp add ruv-swarm npx ruv-swarm mcp start  # Optional: Enhanced coordination
claude mcp add flow-nexus npx flow-nexus@latest mcp start  # Optional: Cloud features
```

## MCP Tool Categories

### Coordination
`swarm_init`, `agent_spawn`, `task_orchestrate`

### Monitoring
`swarm_status`, `agent_list`, `agent_metrics`, `task_status`, `task_results`

### Memory & Neural
`memory_usage`, `neural_status`, `neural_train`, `neural_patterns`

### GitHub Integration
`github_swarm`, `repo_analyze`, `pr_enhance`, `issue_triage`, `code_review`

### System
`benchmark_run`, `features_detect`, `swarm_monitor`

### Flow-Nexus MCP Tools (Optional Advanced Features)
Flow-Nexus extends MCP capabilities with 70+ cloud-based orchestration tools:

**Key MCP Tool Categories:**
- **Swarm & Agents**: `swarm_init`, `swarm_scale`, `agent_spawn`, `task_orchestrate`
- **Sandboxes**: `sandbox_create`, `sandbox_execute`, `sandbox_upload` (cloud execution)
- **Templates**: `template_list`, `template_deploy` (pre-built project templates)
- **Neural AI**: `neural_train`, `neural_patterns`, `seraphina_chat` (AI assistant)
- **GitHub**: `github_repo_analyze`, `github_pr_manage` (repository management)
- **Real-time**: `execution_stream_subscribe`, `realtime_subscribe` (live monitoring)
- **Storage**: `storage_upload`, `storage_list` (cloud file management)

**Authentication Required:**
- Register: `mcp__flow-nexus__user_register` or `npx flow-nexus@latest register`
- Login: `mcp__flow-nexus__user_login` or `npx flow-nexus@latest login`
- Access 70+ specialized MCP tools for advanced orchestration

## 🚀 Agent Execution Flow with Claude Code

### The Correct Pattern:

1. **Optional**: Use MCP tools to set up coordination topology
2. **REQUIRED**: Use Claude Code's Task tool to spawn agents that do actual work
3. **REQUIRED**: Each agent runs hooks for coordination
4. **REQUIRED**: Batch all operations in single messages

### Example Full-Stack Development:

```javascript
// Single message with all agent spawning via Claude Code's Task tool
[Parallel Agent Execution]:
  Task("Backend Developer", "Build REST API with Express. Use hooks for coordination.", "backend-dev")
  Task("Frontend Developer", "Create React UI. Coordinate with backend via memory.", "coder")
  Task("Database Architect", "Design PostgreSQL schema. Store schema in memory.", "code-analyzer")
  Task("Test Engineer", "Write Jest tests. Check memory for API contracts.", "tester")
  Task("DevOps Engineer", "Setup Docker and CI/CD. Document in memory.", "cicd-engineer")
  Task("Security Auditor", "Review authentication. Report findings via hooks.", "reviewer")
  
  // All todos batched together
  TodoWrite { todos: [...8-10 todos...] }
  
  // All file operations together
  Write "backend/server.js"
  Write "frontend/App.jsx"
  Write "database/schema.sql"
```

## 📋 Agent Coordination Protocol

### Every Agent Spawned via Task Tool MUST:

**1️⃣ BEFORE Work:**
```bash
npx claude-flow@alpha hooks pre-task --description "[task]"
npx claude-flow@alpha hooks session-restore --session-id "swarm-[id]"
```

**2️⃣ DURING Work:**
```bash
npx claude-flow@alpha hooks post-edit --file "[file]" --memory-key "swarm/[agent]/[step]"
npx claude-flow@alpha hooks notify --message "[what was done]"
```

**3️⃣ AFTER Work:**
```bash
npx claude-flow@alpha hooks post-task --task-id "[task]"
npx claude-flow@alpha hooks session-end --export-metrics true
```

## 🎯 Concurrent Execution Examples

### ✅ CORRECT WORKFLOW: MCP Coordinates, Claude Code Executes

```javascript
// Step 1: MCP tools set up coordination (optional, for complex tasks)
[Single Message - Coordination Setup]:
  mcp__claude-flow__swarm_init { topology: "mesh", maxAgents: 6 }
  mcp__claude-flow__agent_spawn { type: "researcher" }
  mcp__claude-flow__agent_spawn { type: "coder" }
  mcp__claude-flow__agent_spawn { type: "tester" }

// Step 2: Claude Code Task tool spawns ACTUAL agents that do the work
[Single Message - Parallel Agent Execution]:
  // Claude Code's Task tool spawns real agents concurrently
  Task("Research agent", "Analyze API requirements and best practices. Check memory for prior decisions.", "researcher")
  Task("Coder agent", "Implement REST endpoints with authentication. Coordinate via hooks.", "coder")
  Task("Database agent", "Design and implement database schema. Store decisions in memory.", "code-analyzer")
  Task("Tester agent", "Create comprehensive test suite with 90% coverage.", "tester")
  Task("Reviewer agent", "Review code quality and security. Document findings.", "reviewer")
  
  // Batch ALL todos in ONE call
  TodoWrite { todos: [
    {id: "1", content: "Research API patterns", status: "in_progress", priority: "high"},
    {id: "2", content: "Design database schema", status: "in_progress", priority: "high"},
    {id: "3", content: "Implement authentication", status: "pending", priority: "high"},
    {id: "4", content: "Build REST endpoints", status: "pending", priority: "high"},
    {id: "5", content: "Write unit tests", status: "pending", priority: "medium"},
    {id: "6", content: "Integration tests", status: "pending", priority: "medium"},
    {id: "7", content: "API documentation", status: "pending", priority: "low"},
    {id: "8", content: "Performance optimization", status: "pending", priority: "low"}
  ]}
  
  // Parallel file operations
  Bash "mkdir -p app/{src,tests,docs,config}"
  Write "app/package.json"
  Write "app/src/server.js"
  Write "app/tests/server.test.js"
  Write "app/docs/API.md"
```

### ❌ WRONG (Multiple Messages):
```javascript
Message 1: mcp__claude-flow__swarm_init
Message 2: Task("agent 1")
Message 3: TodoWrite { todos: [single todo] }
Message 4: Write "file.js"
// This breaks parallel coordination!
```

## Performance Benefits

- **84.8% SWE-Bench solve rate**
- **32.3% token reduction**
- **2.8-4.4x speed improvement**
- **27+ neural models**

## Hooks Integration

### Pre-Operation
- Auto-assign agents by file type
- Validate commands for safety
- Prepare resources automatically
- Optimize topology by complexity
- Cache searches

### Post-Operation
- Auto-format code
- Train neural patterns
- Update memory
- Analyze performance
- Track token usage

### Session Management
- Generate summaries
- Persist state
- Track metrics
- Restore context
- Export workflows

## Advanced Features (v2.0.0)

- 🚀 Automatic Topology Selection
- ⚡ Parallel Execution (2.8-4.4x speed)
- 🧠 Neural Training
- 📊 Bottleneck Analysis
- 🤖 Smart Auto-Spawning
- 🛡️ Self-Healing Workflows
- 💾 Cross-Session Memory
- 🔗 GitHub Integration

## Integration Tips

1. Start with basic swarm init
2. Scale agents gradually
3. Use memory for context
4. Monitor progress regularly
5. Train patterns from success
6. Enable hooks automation
7. Use GitHub tools first

## Support

- Documentation: https://github.com/ruvnet/claude-flow
- Issues: https://github.com/ruvnet/claude-flow/issues
- Flow-Nexus Platform: https://flow-nexus.ruv.io (registration required for cloud features)

---

## 🧠 MCP Tool Auto-Discovery Best Practices

### Critical: Tool Descriptions Control Auto-Discovery

**THE KEY INSIGHT**: In MCP protocol, tool descriptions are the ONLY mechanism for automatic tool discovery. Quality determines whether Claude automatically uses tools (70-85% rate) or requires explicit invocation (manual).

### Formula for Auto-Discovery

```python
Tool(
    name="action_verb",
    description=(
        "<What it does> <domain specificity>. "
        "Use when <trigger conditions>. "
        "**Trigger phrases**: '<phrase1>', '<phrase2>', '<pattern>'. "
        "**Examples**: '<concrete example 1>', '<example 2>'. "
        "**Always use when**: <scenario 1>, <scenario 2>. "
        "**Categories/Domains**: <specific areas it covers>."
    ),
    inputSchema={
        "properties": {
            "param": {
                "description": "<what param is> (e.g., '<concrete example>')"
            }
        }
    }
)
```

### Essential Patterns for High Auto-Trigger Rates

**1. Explicit Trigger Phrases**
- List exact user phrases: "remember", "I prefer", "always use", "never use"
- Include patterns: "instead of", "not X, use Y", "actually use X"
- Show corrections: "no, use X", "switch to Y"

**2. Directive Language for Proactive Tools**
- "**IMPORTANT: Use this BEFORE**" - Strong priority signal
- "**MUST USE BEFORE**" - Maximum strength for prerequisite checks
- "**Always use when**" - Define auto-trigger scenarios explicitly

**3. Domain-Specific Context**
- ✅ "Python package managers (pip/uv/poetry/conda)"
- ❌ "package managers" (too generic)
- ✅ "Git workflows (commit styles, branch naming, merge vs rebase)"
- ❌ "version control" (too vague)

**4. Concrete Examples in Descriptions**
- Show real user phrases: "Remember: use uv not pip"
- Demonstrate queries: "python package manager", "git commit style"
- Include parameter examples: "category: python, git, docker, general"

### What Doesn't Work

- ❌ Generic descriptions: "Store a preference" (Claude won't know when to use)
- ❌ MCP Prompts for routing (must be manually invoked, not auto)
- ❌ MCP Resources for triggers (must be manually added via @)
- ❌ Assuming tool names alone convey purpose
- ❌ Implicit behavior without trigger phrases

### Example: Personal Memory MCP Tools

**remember tool (85-95% auto-trigger)**:
```python
"Store user preferences, corrections, and workflow rules in semantic memory. "
"Use when user explicitly shares preferences or corrects your suggestions. "
"**Trigger phrases**: 'remember', 'I prefer', 'always use', 'never use', "
"'my workflow', 'instead of', 'not X, use Y'. "
"**Examples**: 'Remember: use uv not pip', 'I prefer conventional commits'..."
```

**recall tool (70-85% auto-trigger)**:
```python
"Search user's stored preferences using semantic search. "
"**IMPORTANT: Use this BEFORE making any tool/command recommendations.** "
"Check if user has preferences for: Python package managers (pip/uv/poetry/conda), "
"Git workflows (commit styles, branch naming, merge vs rebase)..."
```

### Testing Auto-Discovery

**Test Patterns**:
- Explicit: "Remember: use uv not pip" → Should auto-trigger remember
- Implicit: "What Python package manager should I use?" → Should auto-trigger recall
- Correction: "Actually, use poetry instead" → Should detect pattern

**Verification**:
```bash
# Monitor MCP tool invocations in real-time
tail -f ~/Library/Logs/Claude/mcp*.log | grep "tools/call"
```

### References

- MCP Specification: https://modelcontextprotocol.io/specification/2025-06-18/server/tools
- GitHub MCP Server: Engineering patterns for tool descriptions
- Project Memory: `docs/.project_memory.md` - Detailed learnings and examples

**Key Quote from GitHub Team**:
> "How we name a tool, explain what it does, and spell out its parameters directly affects whether the model picks the right tool, in the right order, with the right arguments."

---

## 🔧 Python Module Execution (Critical for MCP Servers)

### Problem: Import Errors with Direct File Execution

**Error**: `ImportError: attempted relative import with no known parent package`

**Cause**: Running Python files directly breaks relative imports

```bash
# ❌ WRONG (causes ImportError)
python src/mcp_standards/server_simple.py

# ✅ CORRECT (resolves imports properly)
python -m mcp_standards.server_simple
```

### Solution: Always Use Module Syntax

**Claude Desktop Config**:
```json
{
  "mcpServers": {
    "server-name": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/project",
        "python",
        "-m",
        "package.module"
      ]
    }
  }
}
```

**package.json Scripts**:
```json
{
  "scripts": {
    "start": "uv run python -m package.module"
  }
}
```

**All Documentation**: Update README, setup guides, validation checklists to show `-m` syntax

### Why This Matters

- Python packages with `__init__.py` depend on module context
- MCP servers often use relative imports between modules
- Direct file execution loses package hierarchy
- `python -m` preserves proper import resolution

---

## 📋 User Preferences (Project-Specific)

### Package Management
- **Always use `uv` instead of `pip`** for Python packages
- Syntax: `uv pip install package` or `uv run python -m module`

### Documentation Style
- Concrete examples over abstract explanations
- Include trigger phrases and patterns explicitly
- Show both correct (✅) and incorrect (❌) approaches
- Reference actual file paths with line numbers

### Commit Style
- Conventional commits: `<type>: <summary>`
- Detailed body with bullet points
- Include rationale and references
- Add co-authorship: `Co-Authored-By: Claude <noreply@anthropic.com>`

---

## 🚨 Critical Decisions Required Before MVP Implementation

### Decision 1: Language Choice - TypeScript vs Rust (BLOCKING)

**Context**: User rejected Python, wants TypeScript or Rust. This RESOLVES AgentDB compatibility!

**Recommendation: TypeScript** (85% confidence)

#### TypeScript Advantages:
✅ **AgentDB Native Support** - No FFI or workarounds needed
✅ **Official MCP SDK** - `@modelcontextprotocol/sdk` v1.20.2+ (mature, well-documented)
✅ **Faster MVP Development** - Established ecosystem, more examples
✅ **NPM Distribution** - Natural fit for `npx mcp-standards`
✅ **Easier Debugging** - Better tooling, source maps, REPL
✅ **Lower Barrier** - More developers can contribute (reference implementation goal)

Cons:
⚠️ Slightly higher memory (~50-70MB vs Rust's 20-30MB)
⚠️ GC pauses (minimal impact at this scale)

#### Rust Advantages:
✅ **Extreme Performance** - 4,700+ QPS documented
✅ **Minimal Memory** - <30MB typical footprint
✅ **Zero-Cost Abstractions** - Compile-time guarantees
✅ **Official MCP SDK** - `rmcp` or Prism MCP available

Cons:
⚠️ **AgentDB Integration Complex** - Need FFI or rewrite vector store
⚠️ **Steeper Learning Curve** - Fewer developers can contribute
⚠️ **Longer MVP Timeline** - More boilerplate, borrow checker friction
⚠️ **NPM Distribution** - Need binary compilation per platform

**Decision Needed**: Choose TypeScript (recommended) or Rust
**Impact**: Determines entire tech stack, development timeline, community accessibility

### Decision 2: AgentDB Integration (RESOLVED for TypeScript)

**If TypeScript**: Use AgentDB directly as PRD intended ✅
- Native Node.js package
- 150x performance claims validated
- Zero integration friction

**If Rust**: Need alternative or FFI bridge
- Option A: qdrant-client (pure Rust, battle-tested)
- Option B: Custom vector store (educational but more work)
- Option C: AgentDB via FFI (complex, not recommended)

### Decision 3: PRD Updates (COMPLETED ✅)

**Corrections Applied**:
- ✅ Embedding dimensions: 768 → 384 (all-MiniLM-L6-v2)
- ✅ Technology stack: Added TypeScript/Rust options
- ✅ File structure: Updated for both languages
- ✅ AgentDB clarification: Resolved for TypeScript path

---

## 📋 Immediate Next Steps

### For Continuing Development:

1. **Choose language: TypeScript or Rust** (TypeScript recommended)
2. **Create package.json/Cargo.toml** with dependencies
3. **Implement src/embeddings.ts** (transformers.js wrapper) OR **src/embeddings.rs** (Rust embedding)
4. **Implement src/memory-store.ts** (AgentDB wrapper) OR **src/memory_store.rs** (vector DB)
5. **Implement src/server.ts** (MCP server with 3 tools) OR **src/server.rs** (Rust MCP server)
6. **Write tests/** (unit + integration)
7. **Validate auto-discovery rates** (measure with real usage)
8. **Package for npm distribution** (`npx mcp-standards`)

### Reference Documentation:
- **[docs/.project_memory.md](docs/.project_memory.md)**: Complete research and architecture details
- **[PRD.md](PRD.md)**: Product requirements and success criteria
- This file: Project-specific development guide

---

Remember: **This is a simple Python MCP server, not using SPARC or claude-flow orchestration.**

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
Never save working files, text/mds and tests to the root folder.

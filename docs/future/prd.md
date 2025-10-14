# Research MCP - Unified AI Knowledge Copilot PRD

**Last Updated**: 2025-01-11

---

## Executive Summary

**Research MCP** is the only MCP stack you'll ever need: **MindsDB + Strata + Local Memory**

A unified AI knowledge copilot that solves the three biggest problems in AI workflows:
1. **Data Federation**: Access 200+ sources through one MCP server (MindsDB)
2. **Tool Discovery**: Progressive discovery without context overload (Strata) 
3. **Knowledge Persistence**: Remembers everything with local SQLite storage

**The Problem**: Managing dozens of MCP servers, repeating context, scattered knowledge
**The Solution**: One unified system that federates data, discovers tools intelligently, and remembers everything

## Vision Statement

**Transform AI from scattered tools and lost context to a unified system that learns, remembers, and orchestrates intelligently.**

Not another all-in-one platform. Not rigid automation. **Intelligent orchestration** that makes your existing tools work together seamlessly through persistent knowledge and progressive discovery.

---

## Core Philosophy

### What We Believe

1. **Best-in-class tools > All-in-one platforms**
   - Linear for project management
   - GitHub for code
   - Notion for documentation
   - Each tool does what it's best at
   - Intelligence layer connects them

2. **Reasoning > Rigid automation**
   - Not Zapier's if-this-then-that logic
   - Context-aware orchestration
   - Adaptive execution based on past decisions

3. **Memory > Ephemeral conversations**
   - Every interaction builds the knowledge graph
   - Cross-session context persistence
   - Temporal awareness (what changed when)
   - Semantic retrieval, not keyword search

4. **Transparency > Black boxes**
   - See what's being stored
   - Query your knowledge graph
   - Understand agent reasoning
   - Always in control

---

## The Problem

### Current Pain Points

**Personal Knowledge Management:**
- Conversations with Claude are ephemeral - no memory between sessions
- Repeating context in every new chat
- Lost decisions, forgotten research, duplicate work
- No way to query "what did we decide about X last week?"

**Tool Integration:**
- Each tool is a silo (Linear, GitHub, Notion, Gmail)
- Manual context switching wastes cognitive load
- Information duplication across platforms
- No single source of truth

**AI Assistants Today:**
- Start fresh every conversation
- No project memory
- Can't learn from patterns
- No temporal context

### What We Learned

> "We spent years chasing the perfect all-in-one tool. Notion. ClickUp. Monday. Each promised to do everything and ended up doing nothing well."
>
> "The shift: From seeking perfect all-in-one platforms → combining the best products for each use case with intelligent orchestration."
>
> — Stefan Wirth

**Key Insight**: Every all-in-one tool faces impossible trade-offs. You can't be best-in-class at project management AND docs AND CRM AND automation.

---

## The Solution

### Research MCP: Unified Three-Layer Architecture

A **unified orchestration system** that combines three complementary technologies:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    MindsDB      │    │     Strata      │    │ Local Memory    │
│  (Data Layer)   │    │ (Tool Layer)    │    │(Knowledge Layer)│
│                 │    │                 │    │                 │
│ 200+ Sources    │ +  │ Progressive     │ +  │ SQLite +FTS5    │
│ Federated Query │    │ Discovery       │    │ Automatic Log   │
│ Real-time       │    │ Smart Routing   │    │ Cross-Session   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▼                       ▼                       ▼
    One MCP Server         Intelligent Tools        Persistent Memory
```

### Key Components

#### 1. **MindsDB: Data Federation Layer**
- **Single MCP Server**: Access 200+ data sources (databases, SaaS, APIs)
- **Federated Queries**: Cross-source joins as if one database
- **AI-Native Operations**: Vector search, embeddings, ML models
- **Enterprise Security**: Audit trails, governance, performance optimization

#### 2. **Strata: Progressive Tool Discovery Layer**
- **Hierarchical Discovery**: Intent → Integration → Category → Action
- **Scalable**: Handles thousands of tools without token explosion
- **Context-Aware**: Intelligent routing based on task context
- **Multi-App Workflows**: Seamless orchestration across platforms

#### 3. **Local Memory: Knowledge Persistence Layer**
- **SQLite Database**: Single-file storage with FTS5 full-text search
- **Automatic Capture**: Significant tool executions → knowledge episodes
- **Cross-Session Memory**: Persistent context across interactions
- **Local-First**: No cloud dependencies, you own your data

---

## Use Cases

### Phase 1: Unified Data & Memory (MVP)

**Enterprise Data Analysis**
```sql
-- Single federated query across all enterprise sources
SELECT 
  sf.account_name,
  gh.deployment_frequency, 
  slack.team_communication_score
FROM salesforce.accounts sf
JOIN github.repos gh ON sf.tech_stack = gh.primary_language  
JOIN slack.channels slack ON sf.team_id = slack.team_id
WHERE sf.deal_stage = 'Implementation'
```

**Progressive Tool Discovery**
```
User: "Automate customer onboarding"
  ↓
Strata: Intent → Integration Options [Salesforce, HubSpot, Stripe]
  ↓  
Categories: [Lead Management, Payment, Communication]
  ↓
Actions: [Create Contact, Process Payment, Send Welcome Email]
```

**Persistent Knowledge**
```python
# Automatically captured and searchable
add_episode(
  name="Database Decision", 
  content="Chose PostgreSQL for scalability, supports 10M+ records",
  source="architecture-review"
)

# Later retrieval
search_episodes("database scaling decisions")
```

### Phase 2: Intelligent Orchestration

**Cross-Platform Automation**
```python
# Unified workflow across platforms
workflow = await mcp.orchestrate([
  "Query Salesforce for new leads",
  "Create GitHub repository for each project", 
  "Setup Notion project tracker",
  "Initialize Slack channel",
  "Configure CI/CD pipeline"
])
```

**Research Workflows**
```
User: "Research competitor pricing strategies"
  ↓
Strata: Discovers [Web Scraping, CRM Analysis, Document Search] 
  ↓
MindsDB: Executes federated search across sources
  ↓  
Memory: Stores findings for future reference and analysis
```

### Phase 3: Enterprise Intelligence

**Advanced Agent Coordination**
```python
# Multi-agent research and action
research = await mcp.research(
  "Latest trends in AI agent architecture",
  sources=["web", "arxiv", "github", "internal-docs"]
)

actions = await mcp.orchestrate(
  research.recommendations,
  tools=["notion", "slack", "github"]
)
```

**Knowledge Graph Analytics**
```python
# Semantic search with temporal context
episodes = await mcp.search(
  "database architecture decisions",
  semantic=True,
  time_range="last_quarter",
  related_tools=True
)
```

---

## Design Principles

### 1. **Vibe Coding First**
- Conversational input is primary interface
- Chat to add knowledge, query context, trigger workflows
- Slash commands for common patterns (`/research`, `/standup`, `/sync`)
- File-based workflows as secondary (markdown triggers agents)

### 2. **Progressive Enhancement**
- **Week 1**: Basic memory (add/search episodes)
- **Week 2**: Automatic tool logging (GitHub, Notion, files)
- **Week 3**: Conversation compression
- **Week 4**: Claude Flow integration
- **Month 2**: Agent templates for recurring workflows

Each layer adds value independently, no big-bang deployment.

### 3. **Local-First, Cloud-Optional**
- Core system runs locally (Neo4j, Graphiti, MCP servers)
- No cloud dependencies for MVP
- Data stays on your machine
- Optional: Cloud sync, team sharing (future)

### 4. **Claude Code Native**
- Built specifically for Claude Code/Desktop workflows
- OAuth authentication (no API key complexity)
- Works with existing tools via MCP protocol
- Extends Claude's capabilities, doesn't replace them

---

## Technical Architecture

### Three-Layer Stack

**Data Federation Layer (MindsDB):**
- **Docker Container**: `mindsdb/mindsdb` with MCP server enabled
- **200+ Integrations**: Databases, SaaS apps, APIs, file systems  
- **Federated Query Engine**: Cross-source SQL operations
- **AI-Native**: Vector search, embeddings, ML model deployment

**Tool Discovery Layer (Strata):**
- **NPM Package**: `strata-mcp` for progressive discovery
- **Hierarchical Routing**: Intent → Integration → Category → Action
- **Context Management**: Intelligent tool selection without overload
- **Multi-App Orchestration**: Seamless cross-platform workflows

**Knowledge Layer (Local Memory):**
- **SQLite Database**: Single-file storage with FTS5 search
- **Python MCP Server**: `uv`-based local server
- **Automatic Capture**: Tool execution → knowledge episodes
- **Semantic Extraction**: Convert actions to searchable knowledge

### Data Flow

```
User Intent → Strata Discovery → Tool Selection → MindsDB Execution → Memory Storage
     ↓              ↓                ↓              ↓                ↓
"Research X" → Find Categories → Pick Tools → Query Data → Save Episode
```

### Configuration Architecture

**Unified MCP Setup:**
```json
{
  "mcpServers": {
    "mindsdb": {
      "command": "docker",
      "args": ["exec", "mindsdb", "python", "-m", "mindsdb.interfaces.mcp.server"]
    },
    "strata": {
      "command": "npx",
      "args": ["-y", "strata-mcp"]
    },
    "local-memory": {
      "command": "uv",
      "args": ["--directory", "./mcp-servers/local-memory", "run", "server.py"]
    }
  }
}
```

### Performance Characteristics

| Component | Scale | Response Time | Memory Usage |
|-----------|-------|---------------|--------------|
| MindsDB | 200+ sources | <2s federated queries | ~500MB |
| Strata | 1000+ tools | <100ms discovery | ~50MB |
| SQLite Memory | 1M+ episodes | <50ms FTS search | ~100MB |

---

## Success Metrics

### MVP (30 days)

- [ ] **Setup time**: Under 30 minutes from clone → working system
- [ ] **First magic moment**: Auto-log a file edit, retrieve it later
- [ ] **Knowledge accumulation**: 100+ entities in graph after 1 week of use
- [ ] **Query accuracy**: Natural language queries return relevant results 80%+ of time

### Phase 2 (60 days)

- [ ] **Context retrieval saves time**: 5+ hours/week not re-explaining context
- [ ] **Agent templates working**: Research, standup, project-setup agents functional
- [ ] **Cross-tool value**: GitHub + Notion + Linear working together seamlessly
- [ ] **Temporal queries**: "What changed this week?" returns accurate timeline

### Long-term

- [ ] **Team adoption**: Multiple users sharing knowledge graphs
- [ ] **Pattern learning**: System suggests workflows based on past behavior
- [ ] **Zero context switching**: Tools feel like one integrated system
- [ ] **Trusted memory**: Users rely on the graph as source of truth

---

## What We're NOT Building

1. **Not another all-in-one platform** - We orchestrate best-in-class tools
2. **Not rigid automation** - We provide intelligent reasoning, not if-then rules
3. **Not a replacement for Notion/Linear/GitHub** - We make them work better together
4. **Not a cloud service** - Local-first, you own your data
5. **Not black-box AI** - Transparent, queryable, always in control

---

## Inspiration & Prior Art

### Stefan Wirth - Intelligence Layer
> "AI agents don't just pass data between tools, they reason across them. Claude Code orchestrates our entire stack: Linear for projects, GitHub for code, Notion for docs. Each tool does what it's best at. The intelligence layer makes them work together seamlessly."

### Jan Hesters - Personal AI Assistant
> "Windsurf is doing exactly what I need: An agentic system that can write, read and save files, searches for context, makes edits, and lets me iterate. Why not define project rules to become my personal assistant?"

**Key patterns from Jan's system:**
- Extract key information from every conversation
- Store in structured markdown files
- Organize in logical folder hierarchies
- Maintain persistent memory across sessions
- Natural conversational responses based on saved knowledge

### Graphiti (Zep AI)
> "Build and query dynamic, temporally-aware Knowledge Graphs. Unlike traditional RAG, Graphiti continuously integrates user interactions, structured and unstructured data, and external information into a coherent, queryable graph."

### What We're Adding

- **Automatic capture** - No manual knowledge entry required
- **Cross-session memory** - Persistent context across all interactions
- **Temporal reasoning** - Track how knowledge evolves over time
- **Tool orchestration** - Intelligence layer across your entire stack
- **Claude Code native** - Built for the platform from day one

---

## Current Status

### ✅ Phase 1: Foundation (Completed)

- [x] **Unified Architecture**: MindsDB + Strata + SQLite design
- [x] **Research & Analysis**: Comprehensive evaluation of technologies
- [x] **Documentation**: Architecture, README, Quick Start, PRD
- [x] **Configuration Strategy**: Unified Claude Desktop + Claude Code setup
- [x] **Local Memory Server**: SQLite-based knowledge engine design
- [x] **Integration Analysis**: MindsDB vs traditional approaches

### 🔄 Phase 2: Implementation (Current)

- [ ] **MindsDB MCP Integration**: Docker setup and MCP server configuration
- [ ] **Strata Progressive Discovery**: NPM package integration and testing
- [ ] **Local Memory Implementation**: Complete SQLite MCP server
- [ ] **Unified Configuration Files**: Working configs for both Claude platforms
- [ ] **End-to-End Testing**: Full workflow validation
- [ ] **Setup Automation**: Scripts for 10-minute deployment

### 📋 Phase 3: Intelligence (Next)

- [ ] **Advanced Agent Orchestration**: Multi-agent coordination patterns
- [ ] **Semantic Knowledge Search**: Vector embeddings for episodes
- [ ] **Cross-Tool Workflow Automation**: Template-based automation
- [ ] **Real-time Collaboration**: Team knowledge sharing
- [ ] **Performance Optimization**: Caching and indexing improvements
- [ ] **Enterprise Security**: Advanced permission and audit systems

---

## Getting Started

See **[QUICK-START.md](QUICK-START.md)** for 30-minute setup.

**The simplest flow:**
1. Install Neo4j locally (10 min)
2. Install Research MCP (10 min)
3. Configure Claude Code (5 min)
4. Test: add episode, search it (5 min)
5. Watch as your knowledge graph grows automatically

---

## Contributing

**Core areas for contribution:**

1. **Semantic Extractors** - Add extractors for more tools (Gmail, Slack, Figma)
2. **Agent Templates** - Build reusable workflow patterns
3. **Conversation Compression** - Improve LLM-based extraction
4. **Graph Queries** - Better natural language → Cypher translation
5. **Documentation** - Use cases, tutorials, examples

**Philosophy:**
- Evidence > Assumptions
- Code > Documentation (but write good docs)
- Efficiency > Verbosity
- Ship fast, iterate based on real usage

---

## Vision for the Future

**6 months from now:**
- Claude Code feels like it has perfect memory
- Tools orchestrate seamlessly without manual integration
- Knowledge graphs become collaborative team assets
- Patterns emerge from usage, suggesting better workflows

**1 year from now:**
- Standard practice: AI orchestration > all-in-one platforms
- Research MCP powers knowledge work for thousands of users
- Graph-native AI assistants are the norm
- We've proven: best tools + intelligence > jack-of-all-trades platforms

---

## Questions We're Exploring

1. **How do we balance automatic capture with privacy?** (What should/shouldn't be logged?)
2. **What's the right granularity for knowledge nodes?** (File-level? Function-level? Decision-level?)
3. **How do we make temporal queries intuitive?** (Natural language for time-based context)
4. **Can we learn workflow patterns from the graph?** (Auto-suggest agents based on past behavior)
5. **How do teams share knowledge without losing privacy?** (Federated graphs? Permission layers?)

---

## Contact & Community

- **GitHub**: github.com/mattstrautmann/research-mcp
- **Discussions**: GitHub Discussions for questions, ideas, showcases
- **Issues**: Bug reports, feature requests
- **Philosophy**: Ship fast, learn from users, iterate relentlessly

---

*"The ones who figure out orchestration + intelligence first will win."* - Stefan Wirth

Let's build the future of knowledge work.

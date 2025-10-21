# V2 Architecture Diagrams

Visual representations of the mcp-standards v2.0 architecture with AgentDB integration.

---

## 1. System Architecture Overview

```
┌───────────────────────────────────────────────────────────────────────────┐
│                         Claude Desktop / Claude Code                      │
│                                                                           │
│  User Interactions:                                                       │
│  • Corrections: "use uv not pip"                                         │
│  • Tool executions: Bash, Edit, Write, etc.                              │
│  • MCP tool calls: semantic_search_patterns, update_claudemd             │
└──────────────────────────────┬────────────────────────────────────────────┘
                               │ MCP Protocol
                               ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                       MCP-Standards v2 Server                             │
│                      (ClaudeMemoryMCP + Enhancements)                     │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                        Memory Router Layer                          │ │
│  │                      (Query Type Dispatcher)                        │ │
│  │                                                                     │ │
│  │  Semantic Query  → AgentDB (HNSW vector search)                    │ │
│  │  Exact Query     → SQLite (key-value lookup)                       │ │
│  │  Audit Query     → SQLite (compliance logs)                        │ │
│  │  Temporal Query  → SQLite (knowledge graph)                        │ │
│  │  Hybrid Query    → Both (merge results)                            │ │
│  └─────────────────────────┬─────────────┬─────────────────────────────┘ │
│                            │             │                               │
│         ┌──────────────────▼──────┐   ┌──▼──────────────────┐          │
│         │   AgentDB Layer         │   │   SQLite Layer      │          │
│         │   (Hot Path)            │   │   (Cold Path)       │          │
│         │                         │   │                     │          │
│         │ • 100K vectors          │   │ • Pattern metadata  │          │
│         │ • HNSW graph (M=16)     │   │ • Audit trail       │          │
│         │ • 384-dim embeddings    │   │ • Full history      │          │
│         │ • Disk mode: <10ms      │   │ • Temporal graph    │          │
│         │ • Search: <1ms          │   │ • Compliance data   │          │
│         │                         │   │                     │          │
│         │ Data:                   │   │ Data:               │          │
│         │ - Pattern vectors       │   │ - pattern_frequency │          │
│         │ - Similarity scores     │   │ - tool_preferences  │          │
│         │ - Embeddings            │   │ - reasoning_episodes│          │
│         └─────────────────────────┘   │ - audit_log         │          │
│                                       │ - sync_metadata     │          │
│                                       └─────────────────────┘          │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                    Intelligence Layer (Enhanced)                    │ │
│  │                                                                     │ │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐ │ │
│  │  │ Pattern          │  │ ReasoningBank    │  │ CLAUDE.md       │ │ │
│  │  │ Extractor        │  │                  │  │ Manager         │ │ │
│  │  │                  │  │ • Track outcomes │  │                 │ │ │
│  │  │ v1: Regex        │  │ • Success/fail   │  │ v1: Manual      │ │ │
│  │  │ v2: Semantic     │  │ • Confidence adj │  │ v2: Auto-update │ │ │
│  │  │     clustering   │  │ • Bayesian learn │  │     Event-driven│ │ │
│  │  └──────────────────┘  └──────────────────┘  └─────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                Event-Driven Automation (New in v2)                  │ │
│  │                                                                     │ │
│  │  ┌──────────────┐   ┌───────────────┐   ┌────────────────────┐   │ │
│  │  │ Event Bus    │◄──│ Config Watcher│   │ Proactive          │   │ │
│  │  │              │   │               │   │ Suggester          │   │ │
│  │  │ • Subscribe  │   │ • inotify     │   │                    │   │ │
│  │  │ • Emit       │   │ • FSEvents    │   │ • Background job   │   │ │
│  │  │ • Async proc │   │ • Auto-detect │   │ • Pattern check    │   │ │
│  │  └──────┬───────┘   └───────────────┘   │ • MCP notify       │   │ │
│  │         │                                └────────────────────┘   │ │
│  │         │ Events:                                                 │ │
│  │         ├─► pattern_promoted → Auto-update CLAUDE.md              │ │
│  │         ├─► config_changed → Parse & update preferences           │ │
│  │         ├─► reasoning_outcome → Adjust confidence                 │ │
│  │         └─► claudemd_updated → Notify user                        │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Flow: Pattern Learning Workflow

### v1 (Current) - Keyword Matching
```
┌─────────────┐
│ User        │
│ Correction  │
│ "use uv     │
│  not pip"   │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Pattern Extractor   │
│ (Regex matching)    │
│                     │
│ 1. Detect keyword   │
│    "use X not Y"    │
│ 2. Exact text match │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ SQLite FTS5         │
│ (Text search)       │
│                     │
│ Store: "use uv      │
│         not pip"    │
└──────┬──────────────┘
       │
       ▼ Occurrence #1
┌─────────────────────┐
│ pattern_frequency   │
│ occurrence_count: 1 │
│ confidence: 0.1     │
└──────┬──────────────┘
       │
       ▼ User corrects AGAIN

┌─────────────┐
│ "Use uv!"   │ ◄─── Different wording
└──────┬──────┘       NOT detected as same pattern!
       │
       ▼ Occurrence #2 (NEW pattern!)
┌─────────────────────┐
│ pattern_frequency   │
│ occurrence_count: 1 │ ◄─── Starts at 1 again!
└─────────────────────┘

After 3+ exact matches → Promote to preference
Takes: 3-5 corrections
```

### v2 (New) - Semantic Matching
```
┌─────────────┐
│ User        │
│ Correction  │
│ "use uv     │
│  not pip"   │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────┐
│ Pattern Extractor (Enhanced) │
│                              │
│ 1. Detect pattern (regex)    │
│ 2. Generate embedding        │
│    via EmbeddingManager      │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ Memory Router                │
│ (Dual storage)               │
│                              │
│ ├─► AgentDB: Store vector    │
│ │   [0.23, -0.45, ..., 0.67] │
│ │                            │
│ └─► SQLite: Store metadata   │
│     {type, description, ...} │
└──────┬───────────────────────┘
       │
       ▼ Occurrence #1
┌──────────────────────────────┐
│ AgentDB: Vector stored       │
│ SQLite: confidence=0.1       │
└──────┬───────────────────────┘
       │
       ▼ User corrects with SIMILAR phrase

┌─────────────┐
│ "prefer uv  │ ◄─── Different wording
│  package    │      but SAME meaning!
│  manager"   │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────┐
│ Semantic Clustering          │
│                              │
│ 1. Generate embedding        │
│ 2. Search AgentDB            │
│ 3. Find similar:             │
│    "use uv not pip"          │
│    similarity: 0.87          │
│                              │
│ 4. Cluster size: 2           │
│    ✅ Threshold reached!     │
└──────┬───────────────────────┘
       │
       ▼ Automatic promotion after 2 similar patterns!

┌──────────────────────────────┐
│ tool_preferences             │
│                              │
│ category: python-package     │
│ preference: "use uv not pip" │
│ confidence: 0.85             │
│ learned_from: semantic_cluster│
└──────────────────────────────┘

Promotes after: 1-2 semantically similar corrections
60-70% fewer corrections needed!
```

---

## 3. Query Routing Decision Tree

```
                    User Query
                        │
                        ▼
            ┌───────────────────────┐
            │  Memory Router        │
            │  (Analyze query type) │
            └───────────┬───────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ SEMANTIC?    │ │ EXACT?       │ │ AUDIT?       │
│              │ │              │ │              │
│ "patterns    │ │ pattern_key  │ │ history,     │
│  similar to  │ │ lookup       │ │ compliance   │
│  X"          │ │              │ │              │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       │                │                │
       ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ AgentDB      │ │ SQLite       │ │ SQLite       │
│              │ │              │ │              │
│ • HNSW       │ │ • SELECT by  │ │ • audit_log  │
│   search     │ │   key        │ │   table      │
│ • Vector     │ │ • O(log n)   │ │ • Timestamp  │
│   similarity │ │   lookup     │ │   range      │
│ • <1ms       │ │ • <10ms      │ │ • <50ms      │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       │                │                │
       └────────────────┼────────────────┘
                        │
                        ▼
                ┌──────────────┐
                │ HYBRID?      │
                │              │
                │ Semantic +   │
                │ Metadata     │
                └──────┬───────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
┌──────────────┐             ┌──────────────┐
│ AgentDB      │             │ SQLite       │
│ (parallel)   │             │ (parallel)   │
└──────┬───────┘             └──────┬───────┘
       │                             │
       └──────────────┬──────────────┘
                      ▼
              ┌──────────────┐
              │ Merge Results│
              │              │
              │ • Join by key│
              │ • Sort by    │
              │   similarity │
              │ • Enrich     │
              │   metadata   │
              └──────┬───────┘
                     │
                     ▼
                 Response
```

---

## 4. Event-Driven Architecture Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                       Event Sources                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │ Pattern      │    │ Config File  │    │ User Manual  │    │
│  │ Promotion    │    │ Changes      │    │ CLAUDE.md    │    │
│  │              │    │              │    │ Edits        │    │
│  │ Threshold:2  │    │ .editorconfig│    │              │    │
│  │ similar      │    │ pyproject.toml│   │ Diff detect  │    │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘    │
│         │                   │                   │             │
└─────────┼───────────────────┼───────────────────┼─────────────┘
          │                   │                   │
          │ emit              │ emit              │ emit
          ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                          Event Bus                              │
│                      (Async Processing)                         │
│                                                                 │
│  Events Queue:                                                  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ 1. {type: "pattern_promoted", data: {...}}             │  │
│  │ 2. {type: "config_changed", data: {...}}               │  │
│  │ 3. {type: "reasoning_outcome", data: {...}}            │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Subscribers:                                                   │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ pattern_promoted → [claudemd_manager, notifier]        │  │
│  │ config_changed → [config_parser, claudemd_manager]     │  │
│  │ reasoning_outcome → [reasoning_bank, pattern_adjuster] │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────┬───────────────────┬───────────────────┬───────────────┘
          │                   │                   │
          │ async call        │ async call        │ async call
          ▼                   ▼                   ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ CLAUDE.md        │  │ Config Parser    │  │ ReasoningBank    │
│ Manager          │  │                  │  │                  │
│                  │  │ • Parse new      │  │ • Record outcome │
│ • Load current   │  │   config         │  │ • Update conf.   │
│ • Search AgentDB │  │ • Extract rules  │  │ • Adjust scores  │
│   for patterns   │  │ • Update prefs   │  │                  │
│ • Cluster semantic│ │                  │  │                  │
│ • Generate new   │  │                  │  │                  │
│   CLAUDE.md      │  │                  │  │                  │
│ • Create backup  │  │                  │  │                  │
│ • Atomic write   │  │                  │  │                  │
└────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘
         │                     │                     │
         │ emit                │ emit                │ emit
         ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Event Results                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │ claudemd_    │    │ preferences_ │    │ confidence_  │    │
│  │ updated      │    │ updated      │    │ adjusted     │    │
│  │              │    │              │    │              │    │
│  │ → MCP notify │    │ → Store      │    │ → Update DB  │    │
│  │   user       │    │   SQLite     │    │              │    │
│  └──────────────┘    └──────────────┘    └──────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. HNSW Graph Structure (AgentDB)

```
HNSW Multi-Level Graph (Hierarchical Navigable Small World)

Level 2 (Sparse, Long Range)
    ●─────────●─────────●
   /│         │        /│
  / │         │       / │
 /  │         │      /  │
●───┼─────────┼─────●   │
    │         │         │

Level 1 (Medium Density)
    ●───●───●───●───●───●
   /│\ /│\ /│\ /│\ /│\ /│\
  / │X│ │X│ │X│ │X│ │X│ │ \
 /  │/│\│/│\│/│\│/│\│/│\│  \
●───●─●─●─●─●─●─●─●─●─●─●───●

Level 0 (Dense, Short Range - All Vectors)
●─●─●─●─●─●─●─●─●─●─●─●─●─●─●─●
│\│/│\│/│\│/│\│/│\│/│\│/│\│/│
│ ● │ ● │ ● │ ● │ ● │ ● │ ● │
│/│\│/│\│/│\│/│\│/│\│/│\│/│\│
●─●─●─●─●─●─●─●─●─●─●─●─●─●─●─●

Search Algorithm:
1. Start at top level (Level 2)
2. Navigate to nearest neighbor
3. Drop to Level 1, continue search
4. Drop to Level 0, find exact K nearest
5. Return sorted by similarity

Performance:
- Build time: O(log n) per insert
- Search time: O(log n)
- Space: O(n * M) where M=16 connections

Parameters (Optimized for <1ms search):
- M: 16 (connections per element)
- ef_construction: 200 (build quality)
- ef_search: 50 (search accuracy)

Example Pattern Vectors (384-dim):
vector_1 = [0.234, -0.567, 0.123, ..., 0.891]  # "use uv not pip"
vector_2 = [0.245, -0.543, 0.134, ..., 0.878]  # "prefer uv manager"
                                                 # similarity: 0.87

Distance Metric: Cosine Similarity (Inner Product on normalized vectors)
```

---

## 6. Database Schema Evolution

### v1 Schema (SQLite Only)
```sql
┌────────────────────────────────┐
│      pattern_frequency         │
├────────────────────────────────┤
│ id                 INTEGER PK  │
│ pattern_key        TEXT UNIQUE │
│ tool_name          TEXT        │
│ pattern_type       TEXT        │
│ pattern_description TEXT       │
│ occurrence_count   INTEGER     │
│ first_seen         TIMESTAMP   │
│ last_seen          TIMESTAMP   │
│ promoted_to_pref   BOOLEAN     │
│ confidence         REAL        │
│ examples           TEXT (JSON) │
└────────────────────────────────┘
         │
         │ FTS5 Index
         ▼
┌────────────────────────────────┐
│    episodes_search (FTS5)      │
├────────────────────────────────┤
│ name                           │
│ content                        │
│ source                         │
└────────────────────────────────┘
  Text search only (no semantics)
```

### v2 Schema (Hybrid: AgentDB + SQLite)
```sql
┌──────────────────────────────────────────────────────────────┐
│                      AgentDB (Vector Store)                   │
├──────────────────────────────────────────────────────────────┤
│ HNSW Graph Index:                                            │
│                                                              │
│ vector_id: "patterns:correction:pip→uv"                     │
│ vector: [0.234, -0.567, ..., 0.891] (384-dim)              │
│ metadata: {                                                  │
│   key: "correction:pip→uv",                                 │
│   namespace: "patterns",                                    │
│   confidence: 0.8,                                          │
│   description: "use uv not pip"                             │
│ }                                                            │
└──────────────────────────────────────────────────────────────┘
                              │
                              │ Sync
                              ▼
┌────────────────────────────────┐  ┌────────────────────────────────┐
│   pattern_frequency (v2)       │  │   reasoning_episodes (NEW)     │
├────────────────────────────────┤  ├────────────────────────────────┤
│ id                 INTEGER PK  │  │ id                 INTEGER PK  │
│ pattern_key        TEXT UNIQUE │  │ pattern_id         TEXT FK     │
│ tool_name          TEXT        │  │ context            TEXT        │
│ pattern_type       TEXT        │  │ action_taken       TEXT        │
│ pattern_description TEXT       │  │ outcome            TEXT        │
│ occurrence_count   INTEGER     │  │   ('success'/'failure')        │
│ first_seen         TIMESTAMP   │  │ confidence_before  REAL        │
│ last_seen          TIMESTAMP   │  │ confidence_after   REAL        │
│ promoted_to_pref   BOOLEAN     │  │ timestamp          TIMESTAMP   │
│ confidence         REAL        │  │ metadata           TEXT (JSON) │
│ examples           TEXT (JSON) │  └────────────────────────────────┘
│ agentdb_synced     BOOLEAN ◄───┐
└────────────────────────────────┘ │
                                   │
┌────────────────────────────────┐ │
│      sync_metadata (NEW)       │ │
├────────────────────────────────┤ │
│ id                 INTEGER PK  │ │
│ table_name         TEXT        │ │
│ record_key         TEXT        │ │
│ last_synced        TIMESTAMP   ├─┘
│ sync_status        TEXT        │
│   ('pending'/'synced'/'failed')│
│ error_message      TEXT        │
└────────────────────────────────┘
```

---

## 7. Performance Comparison Chart

```
Startup Time:
v1: ████████████████████████████████████████████████ 500ms
v2: █ <10ms
     ↑ 50x faster

Pattern Search (10K patterns):
v1 (FTS5): ███████████████████████ 50ms
v2 (HNSW): █ <1ms
            ↑ 50x faster

Corrections to Learn:
v1 (Exact match):  ███ 3-5 corrections
v2 (Semantic):     █ 1-2 corrections
                    ↑ 60-70% reduction

Context Window Usage:
v1 (Static): ████████████████████████ 23,000 tokens
v2 (Dynamic): ████ 5,000 tokens
               ↑ 78% reduction

Memory Footprint:
v1: ███ 10 MB (SQLite only)
v2: ██████████ 50 MB (SQLite + AgentDB vectors)
     ↑ 5x increase (acceptable for performance gain)

Semantic Match Accuracy:
v1 (Text): ████████ 40% (keyword only)
v2 (Vector): ████████████████████ 85%+ (semantic)
              ↑ 2x improvement
```

---

## 8. Migration Process Flow

```
┌─────────────────────────────────────────────────────────────┐
│                  Migration Start                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │ Backup v1 Database   │
            │                      │
            │ knowledge.db →       │
            │ knowledge.backup.db  │
            └──────────┬───────────┘
                       │ Success
                       ▼
            ┌──────────────────────┐
            │ Create v2 Schema     │
            │                      │
            │ • Copy v1 tables     │
            │ • Add new columns    │
            │ • Create new tables  │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │ Initialize AgentDB   │
            │                      │
            │ • Create HNSW graph  │
            │ • Configure params   │
            └──────────┬───────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│            Migrate Patterns (Batched)                        │
│                                                              │
│  For each pattern in pattern_frequency:                     │
│                                                              │
│  1. Read pattern metadata from SQLite                       │
│     ┌──────────────────────────────────────┐               │
│     │ pattern_key: "correction:pip→uv"     │               │
│     │ description: "use uv not pip"        │               │
│     │ confidence: 0.8                      │               │
│     └──────────────────────────────────────┘               │
│                     │                                       │
│                     ▼                                       │
│  2. Generate embedding                                      │
│     ┌──────────────────────────────────────┐               │
│     │ EmbeddingManager.encode(...)         │               │
│     │ → [0.234, -0.567, ..., 0.891]       │               │
│     └──────────────────────────────────────┘               │
│                     │                                       │
│                     ▼                                       │
│  3. Store in AgentDB                                        │
│     ┌──────────────────────────────────────┐               │
│     │ agentdb.add(                         │               │
│     │   id=pattern_key,                    │               │
│     │   vector=embedding,                  │               │
│     │   metadata={...}                     │               │
│     │ )                                    │               │
│     └──────────────────────────────────────┘               │
│                     │                                       │
│                     ▼                                       │
│  4. Update SQLite sync flag                                 │
│     ┌──────────────────────────────────────┐               │
│     │ UPDATE pattern_frequency             │               │
│     │ SET agentdb_synced = TRUE            │               │
│     │ WHERE pattern_key = ?                │               │
│     └──────────────────────────────────────┘               │
│                                                              │
│  Batch size: 100 patterns                                   │
│  Progress: 0% ████████████████████ 100%                    │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │ Verify Migration     │
            │                      │
            │ • Count patterns     │
            │   v1: 10,345         │
            │   v2: 10,345 ✓       │
            │                      │
            │ • Test search        │
            │   Query: "use uv"    │
            │   Results: 5 ✓       │
            │                      │
            │ • Benchmark          │
            │   Startup: 8ms ✓     │
            │   Search: 0.7ms ✓    │
            └──────────┬───────────┘
                       │
                       ▼ Success
            ┌──────────────────────┐
            │ Migration Complete   │
            │                      │
            │ v1 backup preserved  │
            │ v2 ready for use     │
            └──────────────────────┘

If error at any step → Rollback to backup
```

---

## 9. Context Token Optimization

### Before (v1): Static 23K Token CLAUDE.md
```
CLAUDE.md (always loaded):
├─ SPARC Methodology: 5,000 tokens ────────── (Rarely used)
├─ 54 Agent Definitions: 8,000 tokens ──────── (Use 2-3)
├─ MCP Tool Descriptions: 6,000 tokens ──────── (Use 5-10)
└─ Workflow Examples: 4,000 tokens ──────────── (Static)

Total: 23,000 tokens (12% of context window)
Relevant: ~3,000 tokens (only 13% relevant!)
Wasted: 20,000 tokens (87% waste!)
```

### After (v2): Dynamic 5K Token Loading
```
CLAUDE.md (minimal):
└─ Universal Essentials: 500 tokens ─────────── (Always loaded)

Dynamic Loading (on-demand via AgentDB):
├─ /prime-bug → Bug Investigation Context ──── (2,000 tokens)
│   • Search AgentDB: "debugging workflow"
│   • Load: Error handling patterns
│   • Load: Test debugging preferences
│
├─ /prime-feature → Feature Development ────── (2,000 tokens)
│   • Search AgentDB: "feature development"
│   • Load: Architecture patterns
│   • Load: Testing workflows
│
└─ /prime-refactor → Refactoring Context ───── (2,000 tokens)
    • Search AgentDB: "refactoring patterns"
    • Load: Code quality standards
    • Load: Naming conventions

Total loaded: 500 (base) + 2,000 (dynamic) = 2,500-5,000 tokens
Relevant: ~2,500 tokens (95% relevant!)
Wasted: ~500 tokens (10% waste)

Token savings: 18,000 tokens per conversation (78% reduction)
```

---

## 10. Development Timeline Gantt Chart

```
Week 1: AgentDB Foundation
├─ Day 1-2: Setup ████
├─ Day 3-4: AgentDB Adapter ████████
├─ Day 5: SQLite Enhancement ████
└─ Day 6-7: Memory Router ████████

Week 2: Integration
├─ Day 8-9: Pattern Extractor ████████
├─ Day 10-11: Benchmarking ████████
├─ Day 12-13: MCP Tools ████████
└─ Day 14: Testing ████

Week 3: Event-Driven
├─ Day 15-16: Event Bus ████████
├─ Day 17-18: File Watcher ████████
├─ Day 19-20: CLAUDE.md Manager ████████
└─ Day 21: Proactive Suggester ████

Week 4: Polish
├─ Day 22-23: ReasoningBank ████████
├─ Day 24-25: Migration Tool ████████
├─ Day 26-27: Testing ████████
└─ Day 28: Documentation ████

Critical Path: ████ (Must complete on schedule)
High Priority: ████ (Important but flexible)
Medium Priority: ████ (Nice to have)
```

---

**End of Architecture Diagrams**

For implementation details, see:
- [V2 AgentDB Integration Specification](./v2-agentdb-integration-spec.md)
- [V2 Implementation Roadmap](./v2-implementation-roadmap.md)

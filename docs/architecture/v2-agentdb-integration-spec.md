# MCP-Standards v2.0: AgentDB Integration Architecture Specification

**Version**: 2.0.0
**Date**: 2025-10-20
**Status**: Technical Design - Ready for Implementation
**Author**: System Architecture Designer

---

## Executive Summary

This document provides the complete technical architecture for integrating AgentDB ultra-fast vector memory into mcp-standards v2.0. The integration transforms the system from a reactive SQLite-based pattern logger into an intelligent, semantic-aware context management system with <10ms startup and <1ms search performance.

**Key Objectives**:
- 50-100x performance improvement via HNSW vector search
- Semantic pattern matching (reduce corrections from 3-5 to 1-2)
- Event-driven CLAUDE.md auto-updates (zero manual triggers)
- Hybrid architecture (AgentDB hot path + SQLite cold path)
- Backward compatibility with v1 data

**Performance Targets**:
| Metric | v1 Current | v2 Target | Improvement |
|--------|-----------|-----------|-------------|
| Startup Time | 500ms | <10ms | 50x faster |
| Pattern Search | 50ms+ | <1ms | 50x+ faster |
| Corrections to Learn | 3-5 | 1-2 | 60-70% reduction |
| Context Tokens | 23,000 | 5,000 | 78% reduction |

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Hybrid Memory Architecture](#2-hybrid-memory-architecture)
3. [Component Integration](#3-component-integration)
4. [Data Migration Strategy](#4-data-migration-strategy)
5. [API Design](#5-api-design)
6. [Performance Optimization](#6-performance-optimization)
7. [Implementation Phases](#7-implementation-phases)
8. [Testing Strategy](#8-testing-strategy)

---

## 1. System Architecture

### 1.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Claude Desktop/Code                          │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              MCP-Standards v2 Server                       │  │
│  │                                                            │  │
│  │  ┌──────────────────────────────────────────────────┐     │  │
│  │  │           Memory Router (Query Dispatcher)       │     │  │
│  │  │                                                  │     │  │
│  │  │  • Semantic queries → AgentDB                   │     │  │
│  │  │  • Audit queries → SQLite                       │     │  │
│  │  │  • Hybrid queries → Both (merge results)        │     │  │
│  │  └─────────────┬────────────────┬───────────────────┘     │  │
│  │                │                │                          │  │
│  │     ┌──────────▼─────────┐  ┌──▼────────────────┐        │  │
│  │     │   AgentDB Layer    │  │   SQLite Layer    │        │  │
│  │     │   (Hot Path)       │  │   (Cold Path)     │        │  │
│  │     │                    │  │                   │        │  │
│  │     │ • HNSW Graph       │  │ • Audit Logs      │        │  │
│  │     │ • Vector Store     │  │ • Metadata        │        │  │
│  │     │ • Pattern Clusters │  │ • Full History    │        │  │
│  │     │ • <10ms startup    │  │ • Compliance      │        │  │
│  │     │ • <1ms search      │  │ • Temporal Graph  │        │  │
│  │     └────────────────────┘  └───────────────────┘        │  │
│  │                                                            │  │
│  │  ┌──────────────────────────────────────────────────┐     │  │
│  │  │         Intelligence Layer (Enhanced)            │     │  │
│  │  │                                                  │     │  │
│  │  │  ┌─────────────────┐  ┌──────────────────────┐ │     │  │
│  │  │  │ Pattern         │  │ ReasoningBank        │ │     │  │
│  │  │  │ Extractor       │  │ (Outcome Tracker)    │ │     │  │
│  │  │  │ (Semantic)      │  │                      │ │     │  │
│  │  │  └─────────────────┘  └──────────────────────┘ │     │  │
│  │  │                                                  │     │  │
│  │  │  ┌─────────────────┐  ┌──────────────────────┐ │     │  │
│  │  │  │ CLAUDE.md       │  │ Event Bus            │ │     │  │
│  │  │  │ Manager         │  │ (Event-Driven)       │ │     │  │
│  │  │  │ (Auto-Update)   │  │                      │ │     │  │
│  │  │  └─────────────────┘  └──────────────────────┘ │     │  │
│  │  └──────────────────────────────────────────────────┘     │  │
│  │                                                            │  │
│  │  ┌──────────────────────────────────────────────────┐     │  │
│  │  │          Event-Driven Automation                 │     │  │
│  │  │                                                  │     │  │
│  │  │  • Config File Watcher (inotify/FSEvents)       │     │  │
│  │  │  • Pattern Promotion Monitor (background job)   │     │  │
│  │  │  • Proactive Suggester (MCP notifications)      │     │  │
│  │  │  • Diff-Based Learner (CLAUDE.md edits)         │     │  │
│  │  └──────────────────────────────────────────────────┘     │  │
│  └────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Component Responsibilities

| Component | Responsibility | Performance Target |
|-----------|---------------|-------------------|
| **Memory Router** | Query dispatch, result merging | <100μs routing overhead |
| **AgentDB Layer** | Vector search, semantic matching, pattern clustering | <1ms search, <10ms startup |
| **SQLite Layer** | Audit logs, metadata, compliance, full history | 50ms acceptable (cold path) |
| **Pattern Extractor** | Extract patterns with semantic embeddings | <5ms per pattern |
| **ReasoningBank** | Track outcomes, adjust confidence | Async background |
| **CLAUDE.md Manager** | Auto-generate/update config files | Event-driven (on-demand) |
| **Event Bus** | Event routing, notification dispatch | <10ms event delivery |
| **File Watcher** | Monitor config file changes | Real-time (inotify) |

---

## 2. Hybrid Memory Architecture

### 2.1 Memory Router Design

The Memory Router is the core abstraction that intelligently routes queries to either AgentDB (hot path) or SQLite (cold path) based on query type.

```python
# src/mcp_standards/memory/router.py

from typing import Any, Dict, List, Optional, Union
from enum import Enum
import asyncio
from pathlib import Path

class QueryType(Enum):
    """Query type classification"""
    SEMANTIC = "semantic"        # Vector similarity search
    EXACT = "exact"             # Key-value lookup
    AUDIT = "audit"             # Audit trail query
    TEMPORAL = "temporal"       # Temporal knowledge graph
    HYBRID = "hybrid"           # Requires both stores

class MemoryRouter:
    """
    Intelligent query router for hybrid AgentDB + SQLite architecture.

    Routes queries to optimal storage backend:
    - Semantic queries → AgentDB (HNSW vector search)
    - Audit/compliance → SQLite (full history)
    - Hybrid queries → Both (merge results)
    """

    def __init__(
        self,
        agentdb_path: Path,
        sqlite_path: Path,
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        from .agentdb_adapter import AgentDBAdapter
        from .sqlite_adapter import SQLiteAdapter

        # Initialize storage backends
        self.agentdb = AgentDBAdapter(
            db_path=agentdb_path,
            embedding_model=embedding_model,
            dimension=384
        )

        self.sqlite = SQLiteAdapter(db_path=sqlite_path)

        # Sync layer keeps both stores updated
        self._sync_enabled = True

    async def store_pattern(
        self,
        pattern_key: str,
        pattern_data: Dict[str, Any],
        metadata: Optional[Dict] = None,
        confidence: float = 0.1,
        namespace: str = "patterns"
    ) -> bool:
        """
        Store pattern in both AgentDB (vector) and SQLite (metadata).

        AgentDB: Embedding for semantic search
        SQLite: Full metadata, audit trail, temporal tracking
        """
        # Store in AgentDB with vector embedding
        agentdb_success = await self.agentdb.store(
            key=pattern_key,
            value=pattern_data,
            namespace=namespace,
            metadata={
                **metadata,
                "confidence": confidence,
                "stored_at": "agentdb"
            }
        )

        # Store metadata in SQLite
        sqlite_success = await self.sqlite.store_metadata(
            pattern_key=pattern_key,
            pattern_data=pattern_data,
            metadata=metadata,
            confidence=confidence
        )

        return agentdb_success and sqlite_success

    async def search_patterns(
        self,
        query: str,
        query_type: QueryType = QueryType.SEMANTIC,
        top_k: int = 5,
        namespace: Optional[str] = None,
        filters: Optional[Dict] = None,
        min_confidence: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search patterns using query type-specific routing.

        SEMANTIC: AgentDB vector search
        EXACT: SQLite key-value lookup
        AUDIT: SQLite audit trail
        HYBRID: Merge results from both
        """
        if query_type == QueryType.SEMANTIC:
            # Route to AgentDB for vector similarity search
            return await self.agentdb.search(
                query=query,
                top_k=top_k,
                namespace=namespace,
                threshold=min_confidence
            )

        elif query_type == QueryType.EXACT:
            # Route to SQLite for exact key lookup
            return await self.sqlite.retrieve(
                key=query,
                namespace=namespace,
                filters=filters
            )

        elif query_type == QueryType.AUDIT:
            # Route to SQLite audit log
            return await self.sqlite.query_audit_log(
                filters=filters,
                limit=top_k
            )

        elif query_type == QueryType.TEMPORAL:
            # Route to SQLite temporal graph
            return await self.sqlite.query_temporal_graph(
                pattern_key=query,
                filters=filters
            )

        elif query_type == QueryType.HYBRID:
            # Query both stores in parallel and merge
            semantic_results, metadata_results = await asyncio.gather(
                self.agentdb.search(query, top_k, namespace, min_confidence),
                self.sqlite.retrieve(query, namespace, filters)
            )

            return self._merge_results(semantic_results, metadata_results)

        else:
            raise ValueError(f"Unknown query type: {query_type}")

    def _merge_results(
        self,
        semantic_results: List[Dict],
        metadata_results: List[Dict]
    ) -> List[Dict]:
        """
        Merge results from AgentDB and SQLite.

        Strategy:
        1. Use semantic results as base (sorted by similarity)
        2. Enrich with metadata from SQLite
        3. Handle missing entries gracefully
        """
        merged = []

        # Create lookup map for metadata
        metadata_map = {
            result['key']: result
            for result in metadata_results
        }

        for sem_result in semantic_results:
            key = sem_result['key']

            # Enrich with metadata if available
            if key in metadata_map:
                merged_entry = {
                    **sem_result,  # Vector search results (similarity, value)
                    **metadata_map[key],  # SQLite metadata (full history, audit)
                    'sources': ['agentdb', 'sqlite']
                }
            else:
                merged_entry = {
                    **sem_result,
                    'sources': ['agentdb']
                }

            merged.append(merged_entry)

        return merged

    async def get_stats(self) -> Dict[str, Any]:
        """Get statistics from both storage layers."""
        agentdb_stats, sqlite_stats = await asyncio.gather(
            self.agentdb.get_stats(),
            self.sqlite.get_stats()
        )

        return {
            'agentdb': agentdb_stats,
            'sqlite': sqlite_stats,
            'router': {
                'sync_enabled': self._sync_enabled,
                'query_types': [qt.value for qt in QueryType]
            }
        }
```

### 2.2 AgentDB Adapter

```python
# src/mcp_standards/memory/agentdb_adapter.py

import asyncio
import numpy as np
from typing import Any, Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class AgentDBAdapter:
    """
    Adapter for AgentDB ultra-fast vector memory.

    Features:
    - HNSW graph for 116x faster similarity search
    - <10ms startup time (disk mode)
    - <1ms search queries
    - Automatic embedding generation
    """

    def __init__(
        self,
        db_path: Path,
        embedding_model: str = "all-MiniLM-L6-v2",
        dimension: int = 384,
        max_elements: int = 100_000
    ):
        self.db_path = db_path
        self.dimension = dimension

        # Use existing EmbeddingManager from v1
        from ...intelligence.memory.embeddings import EmbeddingManager
        self.embedder = EmbeddingManager(model_name=embedding_model)

        # Initialize AgentDB (note: this is pseudocode, actual API may differ)
        # AgentDB is a separate package installed via npm/npx
        # We'll interact with it via subprocess or native Python bindings
        self._init_agentdb(max_elements)

        logger.info(f"AgentDB initialized at {db_path} (dim={dimension})")

    def _init_agentdb(self, max_elements: int):
        """
        Initialize AgentDB instance.

        AgentDB Setup Options:
        1. Use npx agentdb (zero-install mode)
        2. Use native Python bindings (if available)
        3. Use HTTP API (for remote AgentDB)

        For v2, we'll use approach #2 with fallback to #1
        """
        try:
            # Option 1: Try to import native Python bindings
            # (This is aspirational - may need to implement via subprocess)
            import agentdb

            self.db = agentdb.VectorStore(
                path=str(self.db_path),
                dimension=self.dimension,
                max_elements=max_elements,
                ef_construction=200,  # HNSW build-time parameter
                M=16,  # HNSW connections per element
                mode='disk'  # or 'memory' for <10ms startup
            )

            logger.info("Using native AgentDB bindings")

        except ImportError:
            # Option 2: Fallback to subprocess wrapper
            logger.warning("Native AgentDB bindings not available, using subprocess")
            self.db = AgentDBSubprocessWrapper(
                db_path=self.db_path,
                dimension=self.dimension,
                max_elements=max_elements
            )

    async def store(
        self,
        key: str,
        value: Any,
        namespace: str = "global",
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Store value with automatic embedding generation.

        Returns:
            Success status
        """
        try:
            # Generate embedding
            embedding = await self._generate_embedding(value)

            # Store in AgentDB with metadata
            await self.db.add(
                id=f"{namespace}:{key}",
                vector=embedding.tolist(),
                metadata={
                    'key': key,
                    'namespace': namespace,
                    'value': self._serialize_value(value),
                    **(metadata or {})
                }
            )

            return True

        except Exception as e:
            logger.error(f"AgentDB store failed: {e}")
            return False

    async def search(
        self,
        query: str,
        top_k: int = 5,
        namespace: Optional[str] = None,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Semantic search using HNSW vector similarity.

        Performance target: <1ms
        """
        try:
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)

            # Search AgentDB HNSW graph
            results = await self.db.search(
                query_vector=query_embedding.tolist(),
                k=top_k,
                filter={"namespace": namespace} if namespace else None
            )

            # Transform results
            transformed = []
            for result in results:
                if result['score'] >= threshold:
                    transformed.append({
                        'key': result['metadata']['key'],
                        'namespace': result['metadata']['namespace'],
                        'value': self._deserialize_value(
                            result['metadata']['value']
                        ),
                        'similarity': float(result['score']),
                        'metadata': result['metadata']
                    })

            return transformed

        except Exception as e:
            logger.error(f"AgentDB search failed: {e}")
            return []

    async def _generate_embedding(self, value: Any) -> np.ndarray:
        """Generate embedding for a value."""
        # Convert value to text
        if isinstance(value, dict):
            text = self._extract_text_from_dict(value)
        else:
            text = str(value)

        # Use existing embedder from v1
        embedding = self.embedder.encode(text, normalize=True)

        return embedding[0] if embedding.ndim > 1 else embedding

    def _extract_text_from_dict(self, data: Dict) -> str:
        """Extract meaningful text from dict for embedding."""
        # Priority fields for embedding
        fields = ['description', 'preference', 'pattern_description',
                 'content', 'message']

        parts = []
        for field in fields:
            if field in data and data[field]:
                parts.append(str(data[field]))

        return " | ".join(parts) if parts else str(data)

    def _serialize_value(self, value: Any) -> str:
        """Serialize value for storage."""
        import json
        return json.dumps(value, default=str)

    def _deserialize_value(self, value_str: str) -> Any:
        """Deserialize value from storage."""
        import json
        try:
            return json.loads(value_str)
        except:
            return value_str

    async def get_stats(self) -> Dict[str, Any]:
        """Get AgentDB statistics."""
        return {
            'total_vectors': await self.db.count(),
            'dimension': self.dimension,
            'mode': 'disk',
            'hnsw_enabled': True
        }


class AgentDBSubprocessWrapper:
    """
    Wrapper for AgentDB when native bindings unavailable.

    Uses subprocess to call npx agentdb CLI commands.
    This is a fallback - native bindings preferred for performance.
    """

    def __init__(self, db_path: Path, dimension: int, max_elements: int):
        self.db_path = db_path
        self.dimension = dimension
        # Implementation details for subprocess wrapper...
        pass

    # Implement same interface as native AgentDB...
```

### 2.3 SQLite Adapter (Enhanced)

```python
# src/mcp_standards/memory/sqlite_adapter.py

import sqlite3
import json
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime

class SQLiteAdapter:
    """
    Enhanced SQLite adapter for audit logs, metadata, and temporal tracking.

    Responsibilities:
    - Audit trail (compliance, security)
    - Full pattern history (metadata)
    - Temporal knowledge graph
    - Pattern frequency tracking
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._ensure_schema()

    def _ensure_schema(self):
        """Ensure all tables exist (v1 + v2 tables)."""
        with sqlite3.connect(self.db_path) as conn:
            # Existing v1 tables (keep for backward compatibility)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pattern_frequency (
                    id INTEGER PRIMARY KEY,
                    pattern_key TEXT NOT NULL UNIQUE,
                    tool_name TEXT NOT NULL,
                    pattern_type TEXT,
                    pattern_description TEXT,
                    occurrence_count INTEGER DEFAULT 1,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    promoted_to_preference BOOLEAN DEFAULT FALSE,
                    confidence REAL DEFAULT 0.0,
                    examples TEXT,
                    agentdb_synced BOOLEAN DEFAULT FALSE  -- v2: sync flag
                )
            """)

            # v2: Reasoning bank for outcome tracking
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reasoning_episodes (
                    id INTEGER PRIMARY KEY,
                    pattern_id TEXT NOT NULL,
                    context TEXT,
                    action_taken TEXT,
                    outcome TEXT,  -- 'success', 'failure', 'partial'
                    confidence_before REAL,
                    confidence_after REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY (pattern_id) REFERENCES pattern_frequency(pattern_key)
                )
            """)

            # v2: Sync metadata (track AgentDB sync status)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sync_metadata (
                    id INTEGER PRIMARY KEY,
                    table_name TEXT NOT NULL,
                    record_key TEXT NOT NULL,
                    last_synced TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    sync_status TEXT,  -- 'pending', 'synced', 'failed'
                    error_message TEXT,
                    UNIQUE(table_name, record_key)
                )
            """)

            conn.commit()

    async def store_metadata(
        self,
        pattern_key: str,
        pattern_data: Dict[str, Any],
        metadata: Optional[Dict] = None,
        confidence: float = 0.1
    ) -> bool:
        """Store pattern metadata (complements AgentDB vector)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO pattern_frequency (
                        pattern_key,
                        tool_name,
                        pattern_type,
                        pattern_description,
                        confidence,
                        examples,
                        agentdb_synced
                    ) VALUES (?, ?, ?, ?, ?, ?, TRUE)
                """, (
                    pattern_key,
                    pattern_data.get('tool_name', ''),
                    pattern_data.get('type', ''),
                    pattern_data.get('description', ''),
                    confidence,
                    json.dumps(metadata or {}),
                    True  # Mark as synced to AgentDB
                ))

                conn.commit()
                return True

        except Exception as e:
            logger.error(f"SQLite metadata store failed: {e}")
            return False

    async def retrieve(
        self,
        key: str,
        namespace: Optional[str] = None,
        filters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve patterns by exact key match."""
        # Implementation similar to existing pattern_extractor...
        pass

    async def query_audit_log(
        self,
        filters: Optional[Dict] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Query audit log for compliance/security."""
        # Implementation using existing audit_log table...
        pass

    async def query_temporal_graph(
        self,
        pattern_key: str,
        filters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Query temporal knowledge graph (existing v1 feature)."""
        # Delegate to existing temporal_graph.py...
        pass

    async def get_stats(self) -> Dict[str, Any]:
        """Get SQLite statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) as total_patterns,
                       SUM(CASE WHEN agentdb_synced THEN 1 ELSE 0 END) as synced,
                       AVG(confidence) as avg_confidence
                FROM pattern_frequency
            """)

            row = cursor.fetchone()

            return {
                'total_patterns': row[0],
                'agentdb_synced': row[1],
                'avg_confidence': row[2]
            }
```

---

## 3. Component Integration

### 3.1 Pattern Extractor Integration (Modified)

The existing `pattern_extractor.py` will be modified to store embeddings in AgentDB while maintaining SQLite for metadata.

```python
# src/mcp_standards/hooks/pattern_extractor.py (modified)

class PatternExtractor:
    """
    Enhanced pattern extractor with semantic embeddings.

    v1: Stored patterns only in SQLite
    v2: Stores vectors in AgentDB + metadata in SQLite
    """

    def __init__(self, db_path: Path, memory_router: Optional['MemoryRouter'] = None):
        self.db_path = db_path

        # v2: Use memory router instead of direct SQLite
        if memory_router:
            self.memory = memory_router
        else:
            # Fallback: Initialize router automatically
            from ..memory.router import MemoryRouter
            self.memory = MemoryRouter(
                agentdb_path=db_path.parent / "agentdb",
                sqlite_path=db_path
            )

        # Keep existing rate limiting
        self._pattern_timestamps = []

    def extract_patterns(
        self,
        tool_name: str,
        args: Dict[str, Any],
        result: Any,
        project_path: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Extract patterns with semantic embeddings (v2 enhancement).

        Changes from v1:
        - Now stores in both AgentDB (vectors) and SQLite (metadata)
        - Semantic clustering reduces promotion threshold from 3 → 2
        """
        # Rate limiting check (unchanged from v1)
        if not self._check_rate_limit():
            return []

        patterns = []

        # 1. Detect patterns (unchanged logic from v1)
        correction_patterns = self._detect_corrections(tool_name, args, result)
        patterns.extend(correction_patterns)

        workflow_patterns = self._detect_workflow_patterns(tool_name, args, project_path)
        patterns.extend(workflow_patterns)

        tool_prefs = self._detect_tool_preferences(tool_name, args, result)
        patterns.extend(tool_prefs)

        # 2. Store patterns in hybrid memory (v2 change)
        for pattern in patterns:
            asyncio.create_task(
                self._store_pattern_hybrid(pattern, project_path)
            )

        # 3. Check semantic clustering for early promotion (v2 change)
        asyncio.create_task(
            self._check_semantic_promotion(patterns)
        )

        return patterns

    async def _store_pattern_hybrid(
        self,
        pattern: Dict[str, Any],
        project_path: str
    ) -> None:
        """
        Store pattern in both AgentDB and SQLite.

        v2 enhancement: Hybrid storage for semantic + metadata
        """
        pattern_key = pattern["pattern_key"]

        await self.memory.store_pattern(
            pattern_key=pattern_key,
            pattern_data=pattern,
            metadata={
                "project_path": project_path,
                "detected_at": datetime.now().isoformat()
            },
            confidence=pattern.get("confidence", 0.1)
        )

    async def _check_semantic_promotion(
        self,
        new_patterns: List[Dict[str, Any]]
    ) -> None:
        """
        v2 enhancement: Semantic clustering for early promotion.

        Instead of requiring 3 exact matches, we now:
        1. Find semantically similar patterns (>0.85 similarity)
        2. Promote if total cluster size >= 2 (reduced from 3)
        """
        SIMILARITY_THRESHOLD = 0.85
        PROMOTION_CLUSTER_SIZE = 2  # Reduced from 3

        for pattern in new_patterns:
            # Find semantically similar patterns
            similar = await self.memory.search_patterns(
                query=pattern['description'],
                query_type=QueryType.SEMANTIC,
                top_k=10,
                min_confidence=SIMILARITY_THRESHOLD
            )

            # Check cluster size
            if len(similar) >= PROMOTION_CLUSTER_SIZE:
                await self._promote_pattern_cluster(pattern, similar)

    async def _promote_pattern_cluster(
        self,
        pattern: Dict[str, Any],
        similar_patterns: List[Dict]
    ) -> None:
        """
        Promote a cluster of semantically similar patterns.

        v2: Combines similar patterns into a single preference
        """
        # Calculate cluster confidence (average of similar patterns)
        cluster_confidence = sum(p['similarity'] for p in similar_patterns) / len(similar_patterns)

        # Create preference entry (existing v1 logic)
        category = pattern.get('category', 'general')

        # Store in SQLite tool_preferences
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO tool_preferences (
                    category,
                    context,
                    preference,
                    confidence,
                    examples,
                    learned_from,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                category,
                f"Learned from {len(similar_patterns)} similar patterns (semantic)",
                pattern['description'],
                cluster_confidence,
                json.dumps([p['key'] for p in similar_patterns]),
                f"semantic_cluster:{pattern['pattern_key']}",
                datetime.now().isoformat()
            ))

            conn.commit()
```

### 3.2 CLAUDE.md Manager Integration (Event-Driven)

```python
# src/mcp_standards/intelligence/claudemd_manager.py (enhanced)

import asyncio
from pathlib import Path
from typing import Optional
from ..events.event_bus import EventBus, Event
from ..memory.router import MemoryRouter, QueryType

class ClaudeMdManager:
    """
    Enhanced CLAUDE.md manager with event-driven updates.

    v1: Manual trigger via update_claudemd() MCP tool
    v2: Automatic updates on pattern promotion events
    """

    def __init__(
        self,
        db_path: Path,
        memory_router: MemoryRouter,
        event_bus: EventBus
    ):
        self.db_path = db_path
        self.memory = memory_router
        self.events = event_bus

        # Subscribe to pattern promotion events
        self.events.subscribe("pattern_promoted", self._on_pattern_promoted)
        self.events.subscribe("config_changed", self._on_config_changed)

    async def _on_pattern_promoted(self, event: Event):
        """
        Handle pattern promotion event (v2 enhancement).

        Automatically updates CLAUDE.md when patterns are promoted.
        """
        pattern_data = event.data

        # Determine which CLAUDE.md to update
        project_path = pattern_data.get('project_path')

        if project_path:
            # Update project-specific CLAUDE.md
            claudemd_path = Path(project_path) / "CLAUDE.md"
        else:
            # Update global CLAUDE.md
            claudemd_path = Path.home() / ".claude" / "CLAUDE.md"

        # Generate updated content using semantic search
        updated_content = await self._generate_content_semantic(
            project_path=project_path,
            min_confidence=0.7
        )

        # Update file with smart merge (existing v1 logic)
        success, message = await self.update_claudemd_file(
            file_path=claudemd_path,
            content=updated_content
        )

        # Emit notification event
        if success:
            await self.events.emit(Event(
                type="claudemd_updated",
                data={
                    "file_path": str(claudemd_path),
                    "auto_updated": True,
                    "trigger": "pattern_promotion"
                }
            ))

    async def _generate_content_semantic(
        self,
        project_path: Optional[str] = None,
        min_confidence: float = 0.7
    ) -> str:
        """
        Generate CLAUDE.md content using semantic search (v2 enhancement).

        v1: Queried SQLite directly
        v2: Uses AgentDB semantic search for better grouping
        """
        # Search for high-confidence patterns semantically
        patterns = await self.memory.search_patterns(
            query="learned preferences and workflow patterns",
            query_type=QueryType.HYBRID,  # Use both AgentDB + SQLite
            top_k=50,
            min_confidence=min_confidence
        )

        # Group patterns by semantic similarity
        pattern_clusters = self._cluster_patterns_semantically(patterns)

        # Generate markdown sections
        sections = self._format_pattern_clusters(pattern_clusters)

        return self._build_markdown_template(sections, project_path)

    def _cluster_patterns_semantically(
        self,
        patterns: List[Dict]
    ) -> Dict[str, List[Dict]]:
        """
        v2 enhancement: Cluster patterns by semantic similarity.

        Groups related patterns together for better CLAUDE.md organization.
        """
        # Use simple similarity-based clustering
        clusters = {}

        for pattern in patterns:
            # Find best matching cluster
            best_cluster = None
            best_similarity = 0.0

            for cluster_name, cluster_patterns in clusters.items():
                # Calculate similarity to cluster centroid
                similarity = self._calculate_cluster_similarity(
                    pattern,
                    cluster_patterns
                )

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_cluster = cluster_name

            # Assign to cluster or create new one
            if best_cluster and best_similarity > 0.75:
                clusters[best_cluster].append(pattern)
            else:
                # Create new cluster
                cluster_name = pattern.get('category', 'general')
                if cluster_name not in clusters:
                    clusters[cluster_name] = []
                clusters[cluster_name].append(pattern)

        return clusters
```

### 3.3 Event Bus Implementation

```python
# src/mcp_standards/events/event_bus.py

import asyncio
from typing import Callable, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class Event:
    """Event data structure."""
    type: str
    data: Dict
    timestamp: datetime = None
    source: str = "mcp-standards"

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class EventBus:
    """
    Event bus for decoupled component communication.

    Events:
    - pattern_promoted: When pattern reaches promotion threshold
    - config_changed: When config files (.editorconfig, etc) change
    - claudemd_updated: When CLAUDE.md is auto-updated
    - reasoning_outcome: When ReasoningBank records outcome
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_queue = asyncio.Queue()
        self._running = False

    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []

        self._subscribers[event_type].append(callback)
        logger.info(f"Subscribed to event: {event_type}")

    async def emit(self, event: Event):
        """Emit event to subscribers."""
        await self._event_queue.put(event)

    async def start(self):
        """Start event processing loop."""
        self._running = True

        while self._running:
            try:
                event = await asyncio.wait_for(
                    self._event_queue.get(),
                    timeout=1.0
                )

                await self._process_event(event)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Event processing error: {e}")

    async def _process_event(self, event: Event):
        """Process event by calling subscribers."""
        if event.type in self._subscribers:
            # Call all subscribers in parallel
            tasks = [
                asyncio.create_task(callback(event))
                for callback in self._subscribers[event.type]
            ]

            await asyncio.gather(*tasks, return_exceptions=True)

    def stop(self):
        """Stop event processing."""
        self._running = False
```

---

## 4. Data Migration Strategy

### 4.1 Migration Plan: v1 SQLite → v2 Hybrid

```python
# src/mcp_standards/migration/v2_migrator.py

from pathlib import Path
import sqlite3
import asyncio
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class V2Migrator:
    """
    Migrate v1 SQLite-only data to v2 hybrid AgentDB + SQLite.

    Migration Steps:
    1. Backup v1 database
    2. Create v2 schema (add new tables)
    3. Migrate patterns to AgentDB (generate embeddings)
    4. Update SQLite with sync metadata
    5. Verify data integrity
    """

    def __init__(self, v1_db_path: Path):
        self.v1_db_path = v1_db_path
        self.v2_db_path = v1_db_path.parent / "knowledge_v2.db"
        self.agentdb_path = v1_db_path.parent / "agentdb"

    async def migrate(self) -> bool:
        """
        Execute migration from v1 to v2.

        Returns:
            Success status
        """
        try:
            # Step 1: Backup v1 database
            await self._backup_v1_database()

            # Step 2: Create v2 schema
            await self._create_v2_schema()

            # Step 3: Migrate pattern data
            await self._migrate_patterns()

            # Step 4: Migrate tool preferences
            await self._migrate_preferences()

            # Step 5: Verify migration
            await self._verify_migration()

            logger.info("Migration completed successfully")
            return True

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            await self._rollback()
            return False

    async def _backup_v1_database(self):
        """Create backup of v1 database."""
        import shutil
        from datetime import datetime

        backup_path = self.v1_db_path.with_suffix(
            f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        )

        shutil.copy2(self.v1_db_path, backup_path)
        logger.info(f"Backup created: {backup_path}")

    async def _create_v2_schema(self):
        """Create v2 schema additions."""
        with sqlite3.connect(self.v2_db_path) as conn:
            # Copy v1 schema
            v1_conn = sqlite3.connect(self.v1_db_path)

            for line in v1_conn.iterdump():
                if line not in ('BEGIN;', 'COMMIT;'):
                    conn.execute(line)

            v1_conn.close()

            # Add v2 tables
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reasoning_episodes (
                    id INTEGER PRIMARY KEY,
                    pattern_id TEXT NOT NULL,
                    context TEXT,
                    action_taken TEXT,
                    outcome TEXT,
                    confidence_before REAL,
                    confidence_after REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)

            # Add sync metadata column to existing table
            conn.execute("""
                ALTER TABLE pattern_frequency
                ADD COLUMN agentdb_synced BOOLEAN DEFAULT FALSE
            """)

            conn.commit()

    async def _migrate_patterns(self):
        """
        Migrate patterns to AgentDB with embeddings.

        This is the core migration step - generates embeddings for all
        existing patterns and stores in AgentDB.
        """
        from ..memory.router import MemoryRouter

        # Initialize memory router
        router = MemoryRouter(
            agentdb_path=self.agentdb_path,
            sqlite_path=self.v2_db_path
        )

        # Read patterns from v1 database
        with sqlite3.connect(self.v1_db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM pattern_frequency
            """)

            patterns = [dict(row) for row in cursor.fetchall()]

        logger.info(f"Migrating {len(patterns)} patterns to AgentDB...")

        # Migrate patterns in batches
        BATCH_SIZE = 100
        migrated_count = 0

        for i in range(0, len(patterns), BATCH_SIZE):
            batch = patterns[i:i + BATCH_SIZE]

            # Store batch in parallel
            tasks = [
                router.store_pattern(
                    pattern_key=p['pattern_key'],
                    pattern_data={
                        'type': p['pattern_type'],
                        'description': p['pattern_description'],
                        'tool_name': p['tool_name']
                    },
                    metadata={
                        'occurrence_count': p['occurrence_count'],
                        'first_seen': p['first_seen'],
                        'last_seen': p['last_seen']
                    },
                    confidence=p['confidence']
                )
                for p in batch
            ]

            results = await asyncio.gather(*tasks)
            migrated_count += sum(results)

            # Update progress
            logger.info(f"Migrated {migrated_count}/{len(patterns)} patterns")

        logger.info(f"Pattern migration complete: {migrated_count} patterns")

    async def _verify_migration(self):
        """Verify migration data integrity."""
        # Count patterns in v1 vs v2
        v1_count = self._count_patterns(self.v1_db_path)
        v2_count = self._count_patterns(self.v2_db_path)

        if v1_count != v2_count:
            raise Exception(
                f"Migration verification failed: "
                f"v1={v1_count}, v2={v2_count}"
            )

        logger.info(f"Verification passed: {v2_count} patterns migrated")

    def _count_patterns(self, db_path: Path) -> int:
        """Count patterns in database."""
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM pattern_frequency"
            )
            return cursor.fetchone()[0]
```

### 4.2 Migration CLI

```python
# src/mcp_standards/cli/migrate.py

import asyncio
import sys
from pathlib import Path
import click

@click.command()
@click.option('--db-path', type=click.Path(exists=True),
              help='Path to v1 database (default: ~/.mcp-standards/knowledge.db)')
@click.option('--dry-run', is_flag=True,
              help='Simulate migration without applying changes')
def migrate_v2(db_path: str, dry_run: bool):
    """Migrate mcp-standards v1 database to v2 hybrid architecture."""

    if not db_path:
        db_path = Path.home() / ".mcp-standards" / "knowledge.db"
    else:
        db_path = Path(db_path)

    if not db_path.exists():
        click.echo(f"Error: Database not found: {db_path}", err=True)
        sys.exit(1)

    click.echo(f"Migrating database: {db_path}")
    click.echo(f"Dry run: {dry_run}")

    from ..migration.v2_migrator import V2Migrator

    migrator = V2Migrator(v1_db_path=db_path)

    if dry_run:
        click.echo("Dry run - no changes will be made")
        # TODO: Implement dry run analysis
    else:
        # Run migration
        success = asyncio.run(migrator.migrate())

        if success:
            click.echo("✅ Migration completed successfully!")
        else:
            click.echo("❌ Migration failed. Check logs for details.", err=True)
            sys.exit(1)

if __name__ == '__main__':
    migrate_v2()
```

---

## 5. API Design

### 5.1 New MCP Tools (v2 Additions)

```python
# src/mcp_standards/server.py (additions)

# Add to list_tools():

Tool(
    name="semantic_search_patterns",
    description="Search patterns using semantic similarity (AgentDB vector search)",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Natural language search query"
            },
            "top_k": {
                "type": "integer",
                "description": "Number of results",
                "default": 5
            },
            "min_confidence": {
                "type": "number",
                "description": "Minimum confidence threshold",
                "default": 0.7
            },
            "namespace": {
                "type": "string",
                "description": "Filter by namespace (optional)"
            }
        },
        "required": ["query"]
    }
),

Tool(
    name="cluster_related_patterns",
    description="Find semantically related patterns and cluster them",
    inputSchema={
        "type": "object",
        "properties": {
            "pattern_key": {
                "type": "string",
                "description": "Pattern to find related items for"
            },
            "similarity_threshold": {
                "type": "number",
                "description": "Minimum similarity score",
                "default": 0.75
            }
        },
        "required": ["pattern_key"]
    }
),

Tool(
    name="record_reasoning_outcome",
    description="Record outcome of applying a pattern (for ReasoningBank learning)",
    inputSchema={
        "type": "object",
        "properties": {
            "pattern_id": {
                "type": "string",
                "description": "Pattern that was applied"
            },
            "outcome": {
                "type": "string",
                "enum": ["success", "failure", "partial"],
                "description": "Outcome of applying pattern"
            },
            "context": {
                "type": "object",
                "description": "Context in which pattern was applied"
            }
        },
        "required": ["pattern_id", "outcome"]
    }
),

Tool(
    name="get_pattern_success_rate",
    description="Get success rate statistics for a pattern (from ReasoningBank)",
    inputSchema={
        "type": "object",
        "properties": {
            "pattern_id": {
                "type": "string",
                "description": "Pattern to get stats for"
            }
        },
        "required": ["pattern_id"]
    }
),

Tool(
    name="predict_next_correction",
    description="Predict likely next correction based on current context (experimental)",
    inputSchema={
        "type": "object",
        "properties": {
            "context": {
                "type": "string",
                "description": "Current context or action"
            },
            "top_k": {
                "type": "integer",
                "description": "Number of predictions",
                "default": 3
            }
        },
        "required": ["context"]
    }
)
```

### 5.2 MCP Tool Handlers

```python
# src/mcp_standards/server.py (handler implementations)

async def _semantic_search_patterns(
    self,
    query: str,
    top_k: int = 5,
    min_confidence: float = 0.7,
    namespace: Optional[str] = None
) -> Dict[str, Any]:
    """
    Semantic search using AgentDB vector similarity.

    Example:
        query: "prefer uv package manager"
        Returns: ["use uv not pip", "always use uv", ...]
    """
    results = await self.memory_router.search_patterns(
        query=query,
        query_type=QueryType.SEMANTIC,
        top_k=top_k,
        namespace=namespace,
        min_confidence=min_confidence
    )

    return {
        "success": True,
        "query": query,
        "results": results,
        "count": len(results)
    }

async def _cluster_related_patterns(
    self,
    pattern_key: str,
    similarity_threshold: float = 0.75
) -> Dict[str, Any]:
    """
    Find and cluster semantically related patterns.

    Uses AgentDB to find similar patterns and groups them.
    """
    # Get pattern description
    pattern = await self.memory_router.search_patterns(
        query=pattern_key,
        query_type=QueryType.EXACT,
        top_k=1
    )

    if not pattern:
        return {"success": False, "error": "Pattern not found"}

    # Find similar patterns
    similar = await self.memory_router.search_patterns(
        query=pattern[0]['value']['description'],
        query_type=QueryType.SEMANTIC,
        top_k=20,
        min_confidence=similarity_threshold
    )

    return {
        "success": True,
        "pattern_key": pattern_key,
        "cluster_size": len(similar),
        "related_patterns": similar
    }

async def _record_reasoning_outcome(
    self,
    pattern_id: str,
    outcome: str,
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Record outcome for ReasoningBank learning.

    Tracks whether applying a pattern succeeded or failed.
    """
    # Store outcome in SQLite reasoning_episodes table
    with sqlite3.connect(self.db_path) as conn:
        # Get current confidence
        cursor = conn.execute("""
            SELECT confidence FROM pattern_frequency
            WHERE pattern_key = ?
        """, (pattern_id,))

        row = cursor.fetchone()
        confidence_before = row[0] if row else 0.0

        # Calculate new confidence based on outcome
        confidence_after = self._adjust_confidence(
            confidence_before,
            outcome
        )

        # Record episode
        conn.execute("""
            INSERT INTO reasoning_episodes (
                pattern_id,
                context,
                action_taken,
                outcome,
                confidence_before,
                confidence_after
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            pattern_id,
            json.dumps(context),
            "pattern_applied",
            outcome,
            confidence_before,
            confidence_after
        ))

        # Update pattern confidence
        conn.execute("""
            UPDATE pattern_frequency
            SET confidence = ?
            WHERE pattern_key = ?
        """, (confidence_after, pattern_id))

        conn.commit()

    # Emit event
    await self.event_bus.emit(Event(
        type="reasoning_outcome",
        data={
            "pattern_id": pattern_id,
            "outcome": outcome,
            "confidence_change": confidence_after - confidence_before
        }
    ))

    return {
        "success": True,
        "pattern_id": pattern_id,
        "outcome": outcome,
        "confidence_before": confidence_before,
        "confidence_after": confidence_after
    }

def _adjust_confidence(
    self,
    current_confidence: float,
    outcome: str
) -> float:
    """
    Bayesian confidence adjustment based on outcome.

    success: +0.1 (up to max 1.0)
    failure: -0.15 (down to min 0.0)
    partial: +0.05
    """
    if outcome == "success":
        return min(1.0, current_confidence + 0.1)
    elif outcome == "failure":
        return max(0.0, current_confidence - 0.15)
    elif outcome == "partial":
        return min(1.0, current_confidence + 0.05)
    else:
        return current_confidence
```

---

## 6. Performance Optimization

### 6.1 AgentDB Configuration for <10ms Startup

```python
# src/mcp_standards/config/performance.py

class AgentDBPerformanceConfig:
    """
    Optimized AgentDB configuration for <10ms startup.

    Based on AgentDB benchmarks:
    - Memory mode: ~100ms startup (browser)
    - Disk mode: <10ms startup (Node.js/native)
    - HNSW graph: 116x faster than naive search
    """

    # HNSW Graph Parameters
    HNSW_M = 16  # Connections per element (trade-off: speed vs accuracy)
    HNSW_EF_CONSTRUCTION = 200  # Build-time parameter (higher = better quality)
    HNSW_EF_SEARCH = 50  # Search-time parameter (higher = better recall)

    # Memory Configuration
    MODE = "disk"  # 'disk' for <10ms startup, 'memory' for pure speed
    MAX_ELEMENTS = 100_000  # Maximum vectors to store

    # Embedding Configuration
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 384 dimensions, fast inference
    EMBEDDING_DIMENSION = 384
    EMBEDDING_BATCH_SIZE = 32  # Batch size for encoding

    # Search Configuration
    DEFAULT_TOP_K = 5  # Default number of results
    MIN_SIMILARITY = 0.7  # Minimum similarity threshold

    @classmethod
    def for_startup_speed(cls):
        """Optimize for <10ms startup (disk mode, small graph)."""
        return {
            'mode': 'disk',
            'max_elements': 50_000,
            'hnsw_m': 12,  # Smaller graph = faster load
            'hnsw_ef_construction': 150
        }

    @classmethod
    def for_search_speed(cls):
        """Optimize for <1ms search (memory mode, optimized graph)."""
        return {
            'mode': 'memory',
            'max_elements': 100_000,
            'hnsw_m': 16,
            'hnsw_ef_construction': 200,
            'hnsw_ef_search': 50
        }

    @classmethod
    def for_accuracy(cls):
        """Optimize for search accuracy (larger graph, higher ef)."""
        return {
            'mode': 'memory',
            'max_elements': 100_000,
            'hnsw_m': 32,  # More connections = better accuracy
            'hnsw_ef_construction': 400,
            'hnsw_ef_search': 100
        }
```

### 6.2 Benchmarking Suite

```python
# src/mcp_standards/benchmarks/performance.py

import asyncio
import time
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class PerformanceBenchmark:
    """
    Benchmark suite for v2 performance targets.

    Targets:
    - Startup: <10ms
    - Search: <1ms
    - Pattern extraction: <5ms
    - CLAUDE.md generation: <100ms
    """

    def __init__(self, memory_router):
        self.memory = memory_router

    async def benchmark_startup(self) -> Dict[str, float]:
        """
        Benchmark startup time.

        Target: <10ms for AgentDB
        """
        start = time.perf_counter()

        # Initialize fresh AgentDB instance
        from ..memory.agentdb_adapter import AgentDBAdapter

        adapter = AgentDBAdapter(
            db_path=Path("/tmp/test_agentdb"),
            embedding_model="all-MiniLM-L6-v2"
        )

        end = time.perf_counter()
        startup_time_ms = (end - start) * 1000

        logger.info(f"Startup time: {startup_time_ms:.2f}ms")

        return {
            'startup_time_ms': startup_time_ms,
            'target_ms': 10,
            'passed': startup_time_ms < 10
        }

    async def benchmark_search(self, num_queries: int = 100) -> Dict[str, Any]:
        """
        Benchmark search performance.

        Target: <1ms average search time
        """
        # Load test data
        await self._load_test_patterns(count=10_000)

        # Test queries
        queries = [
            "use uv not pip",
            "run tests after code changes",
            "update docs when adding features",
            # ... more test queries
        ]

        times = []

        for _ in range(num_queries):
            query = queries[_ % len(queries)]

            start = time.perf_counter()

            results = await self.memory.search_patterns(
                query=query,
                query_type=QueryType.SEMANTIC,
                top_k=5
            )

            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to ms

        avg_time = sum(times) / len(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        p99_time = sorted(times)[int(len(times) * 0.99)]

        logger.info(f"Search - Avg: {avg_time:.2f}ms, P95: {p95_time:.2f}ms, P99: {p99_time:.2f}ms")

        return {
            'avg_search_time_ms': avg_time,
            'p95_search_time_ms': p95_time,
            'p99_search_time_ms': p99_time,
            'target_ms': 1,
            'passed': avg_time < 1
        }

    async def benchmark_pattern_extraction(self) -> Dict[str, Any]:
        """
        Benchmark pattern extraction with embedding generation.

        Target: <5ms per pattern
        """
        from ..hooks.pattern_extractor import PatternExtractor

        extractor = PatternExtractor(
            db_path=Path("/tmp/test.db"),
            memory_router=self.memory
        )

        # Test pattern extraction
        test_cases = [
            {
                'tool_name': 'Bash',
                'args': {'command': 'uv pip install pytest'},
                'result': 'success'
            },
            # ... more test cases
        ]

        times = []

        for case in test_cases:
            start = time.perf_counter()

            patterns = extractor.extract_patterns(
                tool_name=case['tool_name'],
                args=case['args'],
                result=case['result']
            )

            end = time.perf_counter()
            times.append((end - start) * 1000)

        avg_time = sum(times) / len(times)

        logger.info(f"Pattern extraction: {avg_time:.2f}ms")

        return {
            'avg_extraction_time_ms': avg_time,
            'target_ms': 5,
            'passed': avg_time < 5
        }

    async def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run complete benchmark suite."""
        results = {
            'startup': await self.benchmark_startup(),
            'search': await self.benchmark_search(),
            'pattern_extraction': await self.benchmark_pattern_extraction()
        }

        # Overall pass/fail
        all_passed = all(
            result['passed'] for result in results.values()
        )

        results['overall_passed'] = all_passed

        return results
```

---

## 7. Implementation Phases

### Phase 1: AgentDB Core Integration (Weeks 1-2)

**Goal**: Replace SQLite FTS5 with AgentDB HNSW for semantic search.

**Tasks**:
1. ✅ Install AgentDB dependency
   ```bash
   npm install agentdb
   # or for Python native bindings (if available)
   pip install agentdb-python
   ```

2. ✅ Create `agentdb_adapter.py`
   - HNSW configuration
   - Embedding generation
   - Vector search interface

3. ✅ Create `memory_router.py`
   - Query routing logic
   - Hybrid query support
   - Result merging

4. ✅ Create `sqlite_adapter.py`
   - Metadata storage
   - Audit logging
   - Temporal queries

5. ✅ Update `pattern_extractor.py`
   - Use memory router
   - Store vectors in AgentDB
   - Semantic clustering logic

6. ✅ Testing & Benchmarking
   - Load 10K test patterns
   - Measure search latency (<1ms target)
   - Test semantic matching accuracy

**Deliverables**:
- Working AgentDB integration
- <10ms startup time
- <1ms search performance
- Semantic pattern matching

**Success Criteria**:
- [ ] AgentDB adapter passes unit tests
- [ ] Search latency <1ms (P95)
- [ ] Startup time <10ms
- [ ] Semantic matching: "use uv" matches "prefer uv package manager"

---

### Phase 2: Event-Driven CLAUDE.md (Week 3)

**Goal**: Automatic CLAUDE.md updates with zero manual triggers.

**Tasks**:
1. ✅ Create `event_bus.py`
   - Event subscription/emission
   - Async event processing
   - Event types definition

2. ✅ Create `config_watcher.py`
   - File system monitoring (inotify/FSEvents)
   - Config file change detection
   - Event emission on changes

3. ✅ Create `proactive_suggester.py`
   - Background monitoring job
   - Pattern promotion detection
   - MCP notification integration

4. ✅ Update `claudemd_manager.py`
   - Event subscription
   - Auto-update on pattern promotion
   - Semantic content generation

5. ✅ Create `diff_learner.py`
   - CLAUDE.md backup analysis
   - Extract user-added preferences
   - Learn from manual edits

**Deliverables**:
- Event-driven architecture
- Automatic CLAUDE.md updates
- Proactive suggestion notifications
- Learning from manual edits

**Success Criteria**:
- [ ] CLAUDE.md auto-updates on pattern promotion
- [ ] File watcher detects config changes
- [ ] MCP notifications sent for suggestions
- [ ] Diff learner extracts manual preferences

---

### Phase 3: ReasoningBank Outcomes (Week 4)

**Goal**: Track pattern outcomes and adjust confidence automatically.

**Tasks**:
1. ✅ Create `reasoning_bank.py`
   - Outcome recording
   - Success rate calculation
   - Confidence adjustment (Bayesian)

2. ✅ Add `reasoning_episodes` table
   - Schema definition
   - Indexes for performance

3. ✅ Integrate with pattern application flow
   - Auto-detect outcomes
   - Record successes/failures
   - Adjust confidence scores

4. ✅ Create MCP tools
   - `record_reasoning_outcome`
   - `get_pattern_success_rate`

**Deliverables**:
- ReasoningBank implementation
- Automatic confidence adjustment
- Outcome tracking API

**Success Criteria**:
- [ ] Outcomes recorded correctly
- [ ] Confidence adjusts based on success rate
- [ ] Failed patterns demoted automatically
- [ ] Successful patterns boosted

---

### Phase 4: Testing & Documentation (Week 5)

**Goal**: Production-ready release with comprehensive tests and docs.

**Tasks**:
1. ✅ Re-enable test suite
   - Migrate tests from `tests/_disabled/`
   - Update for v2 architecture
   - Add AgentDB integration tests

2. ✅ Create migration tool
   - CLI for v1 → v2 migration
   - Data verification
   - Rollback support

3. ✅ Update documentation
   - ARCHITECTURE.md
   - API documentation
   - Migration guide
   - Performance tuning guide

4. ✅ Performance testing
   - Benchmark suite execution
   - Optimization tuning
   - Load testing

**Deliverables**:
- >80% test coverage
- Migration tool
- Complete documentation
- Performance benchmarks

**Success Criteria**:
- [ ] All tests passing
- [ ] Migration tool verified
- [ ] Documentation complete
- [ ] Performance targets met

---

## 8. Testing Strategy

### 8.1 Unit Tests

```python
# tests/unit/test_memory_router.py

import pytest
from pathlib import Path
from mcp_standards.memory.router import MemoryRouter, QueryType

@pytest.mark.asyncio
async def test_semantic_search():
    """Test semantic search routing to AgentDB."""
    router = MemoryRouter(
        agentdb_path=Path("/tmp/test_agentdb"),
        sqlite_path=Path("/tmp/test.db")
    )

    # Store test pattern
    await router.store_pattern(
        pattern_key="test_uv_preference",
        pattern_data={
            'description': "use uv instead of pip for Python packages",
            'category': 'python-package'
        },
        confidence=0.8
    )

    # Search with semantic query
    results = await router.search_patterns(
        query="prefer uv package manager",  # Different wording
        query_type=QueryType.SEMANTIC,
        top_k=5
    )

    # Should find the pattern despite different wording
    assert len(results) > 0
    assert results[0]['key'] == "test_uv_preference"
    assert results[0]['similarity'] > 0.7

@pytest.mark.asyncio
async def test_hybrid_search():
    """Test hybrid search merging AgentDB + SQLite."""
    # Test implementation...
    pass
```

### 8.2 Integration Tests

```python
# tests/integration/test_pattern_learning.py

import pytest
from pathlib import Path
from mcp_standards.hooks.pattern_extractor import PatternExtractor

@pytest.mark.asyncio
async def test_semantic_clustering_promotion():
    """
    Test that semantically similar patterns trigger early promotion.

    v2: Should promote after 2 similar patterns (not 3)
    """
    extractor = PatternExtractor(
        db_path=Path("/tmp/test.db"),
        memory_router=router
    )

    # Pattern 1: "use uv not pip"
    patterns1 = extractor.extract_patterns(
        tool_name="Bash",
        args={'command': 'uv pip install pytest'},
        result='success'
    )

    # Pattern 2: "prefer uv package manager" (semantically similar)
    patterns2 = extractor.extract_patterns(
        tool_name="Bash",
        args={'command': 'prefer uv package manager for python'},
        result='success'
    )

    # Check if promoted after just 2 similar patterns
    preferences = await extractor.get_learned_preferences(
        category="python-package",
        min_confidence=0.7
    )

    # v2: Should be promoted after 2 (not 3)
    assert len(preferences) > 0
    assert "uv" in preferences[0]['preference'].lower()
```

### 8.3 Performance Tests

```python
# tests/performance/test_benchmarks.py

import pytest
from mcp_standards.benchmarks.performance import PerformanceBenchmark

@pytest.mark.asyncio
async def test_startup_performance():
    """Test that startup meets <10ms target."""
    benchmark = PerformanceBenchmark(router)

    result = await benchmark.benchmark_startup()

    assert result['passed'], \
        f"Startup time {result['startup_time_ms']:.2f}ms exceeds target {result['target_ms']}ms"

@pytest.mark.asyncio
async def test_search_performance():
    """Test that search meets <1ms target."""
    benchmark = PerformanceBenchmark(router)

    result = await benchmark.benchmark_search(num_queries=1000)

    assert result['passed'], \
        f"Avg search time {result['avg_search_time_ms']:.2f}ms exceeds target {result['target_ms']}ms"
```

---

## 9. Appendix

### 9.1 Class Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        MCP Server                           │
│                    (ClaudeMemoryMCP)                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
           ┌────────────┴────────────┐
           │                         │
    ┌──────▼──────┐          ┌──────▼──────┐
    │ Memory      │          │ Event Bus   │
    │ Router      │          │             │
    └──┬──────┬───┘          └──────┬──────┘
       │      │                     │
       │      │              ┌──────┴──────┐
       │      │              │             │
   ┌───▼──┐ ┌▼────┐    ┌────▼────┐  ┌────▼────┐
   │Agent │ │SQLite│    │CLAUDE.md│  │Config   │
   │ DB   │ │     │    │Manager  │  │Watcher  │
   │Adapter│ │Adapter│   └─────────┘  └─────────┘
   └──────┘ └──────┘
       │        │
   ┌───▼───┐ ┌─▼────┐
   │HNSW   │ │Audit │
   │Graph  │ │Log   │
   └───────┘ └──────┘
```

### 9.2 Dependencies Update

```toml
# pyproject.toml (v2 additions)

[project]
name = "mcp-standards"
version = "2.0.0"
dependencies = [
    "mcp>=1.0.0",
    "sentence-transformers>=2.2.0",  # Existing
    "faiss-cpu>=1.7.4",  # Existing
    "numpy>=1.24.0",  # Existing
    "networkx>=3.1",  # Existing
    # v2 additions:
    "watchdog>=3.0.0",  # File system monitoring
    "agentdb-python>=0.1.0",  # AgentDB bindings (if available)
]
```

### 9.3 Configuration File

```yaml
# .mcp-standards/config.yaml (v2 config)

version: "2.0"

memory:
  agentdb:
    enabled: true
    path: "${HOME}/.mcp-standards/agentdb"
    mode: "disk"  # 'disk' for <10ms startup, 'memory' for speed
    max_elements: 100000
    hnsw:
      m: 16
      ef_construction: 200
      ef_search: 50

  sqlite:
    path: "${HOME}/.mcp-standards/knowledge.db"
    wal_mode: true

  embedding:
    model: "all-MiniLM-L6-v2"
    dimension: 384
    batch_size: 32

intelligence:
  pattern_extractor:
    semantic_clustering: true
    promotion_threshold: 2  # Reduced from 3
    similarity_threshold: 0.85

  reasoning_bank:
    enabled: true
    confidence_adjustment:
      success: 0.1
      failure: -0.15
      partial: 0.05

events:
  file_watcher:
    enabled: true
    watch_patterns:
      - ".editorconfig"
      - ".prettierrc*"
      - "pyproject.toml"
      - "package.json"

  proactive_suggestions:
    enabled: true
    check_interval_seconds: 300  # 5 minutes
    notification_threshold: 3  # patterns ready

performance:
  startup_target_ms: 10
  search_target_ms: 1
  benchmarks:
    enabled: true
    report_path: "${HOME}/.mcp-standards/benchmarks"
```

---

## 10. Conclusion

This specification provides a complete technical architecture for integrating AgentDB into mcp-standards v2.0. The hybrid architecture (AgentDB hot path + SQLite cold path) delivers:

- **50-100x performance improvement** via HNSW vector search
- **Semantic pattern matching** reducing corrections from 3-5 to 1-2
- **Event-driven automation** eliminating manual CLAUDE.md updates
- **ReasoningBank outcomes** enabling self-adjusting confidence
- **Backward compatibility** with v1 data via migration tool

**Development can begin immediately** using this specification as the blueprint. All components, APIs, and integration points are defined with concrete code examples and performance targets.

**Next Steps**:
1. Create git feature branch: `feature/v2-agentdb-integration`
2. Begin Phase 1 implementation (AgentDB core)
3. Set up CI/CD for performance benchmarking
4. Create project tracking board with tasks from Phase 1-4

---

**Document Control**:
- Version: 1.0
- Last Updated: 2025-10-20
- Review Status: Ready for Implementation
- Approvals: Architecture Team


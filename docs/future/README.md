# Future Enhancements

This directory contains documentation for planned features that are **not part of the MVP**.

The MVP focuses on: **Simple, persistent memory for Claude using SQLite**.

## Archived Documents

- **ARCHITECTURE.md**: Complex multi-layer architecture with MindsDB + Strata
- **QUICK-START.md**: 10-minute setup guide for the complex system
- **prd.md**: Full product vision and roadmap

## Why These Are "Future"

The current MVP deliberately excludes:

1. **MindsDB** - Requires Docker, adds complexity, not needed for memory
2. **Strata** - Progressive tool discovery is interesting but orthogonal to memory
3. **Enterprise Features** - Multi-tenant, federation, advanced orchestration
4. **Complex Integrations** - Can be added later once core memory works

## Roadmap

Once the core memory system is stable and users are finding value:

### Phase 2: Enhanced Memory
- Semantic search with embeddings
- Automatic conversation summarization
- Better relevance ranking

### Phase 3: Intelligence Layer
- Pattern detection in stored knowledge
- Suggested workflows based on history
- Cross-tool correlation

### Phase 4: Optional Extensions
- MindsDB integration for federated data access
- Strata integration for tool discovery
- Team collaboration features

## Philosophy

**Do one thing well first.**

The MVP is intentionally minimal:
- SQLite storage
- Full-text search
- add/search episodes
- Zero external dependencies

Everything else is optional and should be proven necessary by user demand, not speculation.

---

**Want to discuss these features?** Open a GitHub Discussion or Issue.

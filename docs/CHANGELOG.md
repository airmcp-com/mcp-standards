# Changelog

All notable changes to MCP Standards will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## 📦 ARCHIVED - [0.2.0-alpha.1] - 2024-11-30

### Archive Notice
**This project has been archived and is provided for reference only.**

See [ARCHIVE.md](ARCHIVE.md) for complete details on:
- Final project status and achievements
- Security audit results (no secrets found)
- Complete documentation index
- Lessons learned and technical insights

### Added (v0.2.0-alpha.1 - Final Release)
- **AgentDB Integration**: Ultra-fast vector memory (<1ms search, 150x faster than SQLite)
- **Simple MCP Server**: Reduced from 6,000+ LOC to ~950 LOC (84% reduction)
- **Auto-Detection**: Automatic pattern recognition for "use X not Y" preferences
- **Zero-Config Design**: 5-minute setup with automatic configuration
- **4 Core MCP Tools**: `remember`, `recall`, `list_categories`, `memory_stats`
- **Comprehensive Testing**: 5/5 validation tests passing
- **Semantic Search**: Context-aware preference matching with vector embeddings
- **25+ Claude Skills**: Integration with Claude Code ecosystem

### Changed
- **Architecture**: Simplified to focus on core auto-learning functionality
- **Storage**: Migrated from SQLite to AgentDB vector memory
- **Performance**: <1ms search latency (vs 50ms+ in v1)
- **UX**: Zero manual steps (vs 4-5 manual MCP calls in v1)
- **Code Size**: 84% reduction in codebase complexity

### Security
- ✅ **Security Audit Complete**: No secrets, tokens, or credentials in codebase
- ✅ **Privacy Verified**: 100% local storage, no cloud dependencies
- ✅ **Git History Clean**: No leaked secrets in commit history
- ✅ **Configuration Safe**: `.env.example` is template only

---

## [0.1.0-alpha.1] - 2025-10-15

### Added
- **Self-Learning System**: Automatically learns from corrections and updates CLAUDE.md
- **Episode Storage**: Manual knowledge storage with full-text search
- **Learned Preferences**: Automatic pattern detection from repeated corrections
- **AI Standards Generation**: Auto-generate CLAUDE.md from project config files
- **Cost Optimization Integration**: Optional agentic-flow integration for 99.5% cost savings
- **Security Features**: Path validation, audit logging, CLAUDE.md-only updates
- **Pattern Learning**: Confidence scoring system (0.3, 0.7, 0.9 thresholds)
- **9 MCP Tools**: add_episode, search_episodes, list_recent, generate_ai_standards, get_learned_preferences, suggest_claudemd_update, update_claudemd, log_tool_execution, export_to_markdown
- **Comprehensive Documentation**: Quick Start Guide, Security Guide, Architecture docs

### Changed
- Rebranded from `research-mcp/claude-memory` to `mcp-standards`
- Database path: `.claude-memory` → `.mcp-standards`
- Server name: `claude-memory` → `mcp-standards`
- Repository: `research-mcp` → `airmcp-com/mcp-standards`

### Fixed
- MCP server startup with `--directory` flag for proper module resolution
- Agentic-flow configuration with correct repository and tracking variables
- Claude Desktop config path documentation (macOS)
- Installation instructions with proper `uv` commands

### Documentation
- Added comprehensive Quick Start Guide with two-system explanation
- Added 60-second quickstart tutorial
- Clear distinction between Episodes (manual) vs Learned Preferences (automatic)
- Practical example: Teaching Claude to use `uv` instead of `pip`
- Installation instructions for packaged versions

### Technical
- Python 3.10+ with uv package manager
- SQLite with FTS5 full-text search
- MCP 1.0 protocol compliant
- 12/12 smoke tests passing
- Local-first architecture (100% privacy)

## [Unreleased]

### Planned
- Additional test coverage (integration and unit tests)
- Performance benchmarking
- Multi-language support for standards generation
- Plugin system for custom extractors
- Web UI for knowledge base management

[0.1.0-alpha.1]: https://github.com/airmcp-com/mcp-standards/releases/tag/v0.1.0-alpha.1

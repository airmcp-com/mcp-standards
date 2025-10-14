# Comprehensive Testing Strategy for Claude Memory MCP Server

**Project**: Claude Memory - AI Coding Standards Made Easy
**Version**: 1.0.0
**Date**: 2025-10-13
**Prepared by**: Tester Agent (Hive Mind Swarm)

---

## Executive Summary

This document outlines a comprehensive testing strategy for the Claude Memory MCP server before production launch. The strategy covers unit, integration, end-to-end, auto-learning, performance, and security testing with clear quality gates and framework recommendations.

**Target Coverage**: 80%+ across all test types
**Recommended Framework**: pytest for Python testing
**CI/CD Integration**: GitHub Actions with automated test execution
**Quality Gates**: All tests must pass before deployment

---

## 1. Unit Testing Strategy

### 1.1 Scope

Test individual functions and methods in isolation from external dependencies.

**Components to Test**:
- `ClaudeMemoryMCP` class methods
- `EnhancedClaudeMemoryMCP` class methods
- Database operations (episodes, tool_logs, audit_log)
- Pattern extraction logic
- CLAUDE.md generation
- Model routing decisions
- Significance scoring
- Validation engine
- Agent performance tracking
- Temporal knowledge graph operations

### 1.2 Testing Approach

**Framework**: pytest with fixtures for database setup/teardown

**Sample Test Structure**:
```python
# tests/unit/test_server.py
import pytest
import sqlite3
from pathlib import Path
from claude_memory.server import ClaudeMemoryMCP

@pytest.fixture
def temp_db(tmp_path):
    """Create temporary database for testing"""
    db_path = tmp_path / "test_knowledge.db"
    return db_path

@pytest.fixture
def memory_server(temp_db):
    """Create ClaudeMemoryMCP instance with test database"""
    return ClaudeMemoryMCP(db_path=str(temp_db))

class TestEpisodeOperations:
    """Test episode CRUD operations"""

    async def test_add_episode_success(self, memory_server):
        """Test adding episode with valid data"""
        result = await memory_server._add_episode(
            name="Test Episode",
            content="Test content",
            source="test"
        )

        assert result["success"] == True
        assert "id" in result
        assert result["message"].startswith("Episode")

    async def test_add_episode_empty_name(self, memory_server):
        """Test adding episode with empty name fails"""
        result = await memory_server._add_episode(
            name="",
            content="Test content",
            source="test"
        )

        assert result["success"] == False
        assert "error" in result

    async def test_search_episodes_fts(self, memory_server):
        """Test full-text search functionality"""
        # Add test episodes
        await memory_server._add_episode(
            "Python Best Practices",
            "Use type hints and docstrings",
            "coding-standards"
        )

        # Search
        results = await memory_server._search_episodes("python", limit=10)

        assert results["success"] == True
        assert results["count"] > 0
        assert any("Python" in r["name"] for r in results["results"])

    async def test_list_recent_with_limit(self, memory_server):
        """Test listing recent episodes respects limit"""
        # Add multiple episodes
        for i in range(15):
            await memory_server._add_episode(
                f"Episode {i}",
                f"Content {i}",
                "test"
            )

        results = await memory_server._list_recent(limit=5)

        assert results["success"] == True
        assert results["count"] == 5
        assert len(results["results"]) == 5
```

### 1.3 Test Categories

**Database Operations (20 tests)**:
- CRUD operations for episodes
- Search functionality (FTS5)
- Index management
- Audit logging
- Schema migrations

**Pattern Extraction (15 tests)**:
- Pattern detection from corrections
- Confidence scoring
- Category classification
- Project-specific vs global patterns
- Pattern promotion logic

**CLAUDE.md Generation (10 tests)**:
- Content generation from learned preferences
- File update with backup
- Security validation (path whitelist)
- Confidence threshold filtering
- Project-specific content merging

**Model Routing (8 tests)**:
- Task complexity assessment
- Model selection logic
- Cost optimization
- Fallback handling
- Routing statistics

**Validation Engine (12 tests)**:
- Spec capture and validation
- Quality gate checking
- Deliverable verification
- Error reporting

**Agent Performance Tracking (10 tests)**:
- Execution logging
- Performance statistics
- Agent recommendations
- Success rate calculation

### 1.4 Coverage Target

**Minimum**: 85% line coverage
**Target**: 90%+ line coverage
**Critical paths**: 100% coverage (database operations, security validation)

---

## 2. Integration Testing Strategy

### 2.1 Scope

Test interactions between components and external systems (SQLite, file system, MCP protocol).

**Integration Points**:
- MCP server ↔ SQLite database
- Pattern extractor ↔ CLAUDE.md manager
- Validation engine ↔ temporal graph
- Agent tracker ↔ performance metrics
- File system operations
- Environment variable handling

### 2.2 Testing Approach

**Framework**: pytest with real database and file operations

**Sample Test Structure**:
```python
# tests/integration/test_mcp_server.py
import pytest
import json
from mcp.types import TextContent
from claude_memory.server import ClaudeMemoryMCP

@pytest.fixture
async def running_server(tmp_path):
    """Start MCP server with temporary database"""
    db_path = tmp_path / "integration_test.db"
    server = ClaudeMemoryMCP(db_path=str(db_path))
    return server

class TestMCPServerIntegration:
    """Test MCP server end-to-end workflows"""

    async def test_add_and_search_workflow(self, running_server):
        """Test complete add -> search workflow"""
        # Add episode via MCP tool
        add_result = await running_server.server.call_tool(
            "add_episode",
            {
                "name": "Integration Test",
                "content": "Testing MCP protocol integration",
                "source": "test"
            }
        )

        result_data = json.loads(add_result[0].text)
        assert result_data["success"] == True

        # Search for the episode
        search_result = await running_server.server.call_tool(
            "search_episodes",
            {"query": "integration", "limit": 10}
        )

        search_data = json.loads(search_result[0].text)
        assert search_data["success"] == True
        assert search_data["count"] > 0

    async def test_pattern_learning_workflow(self, running_server):
        """Test pattern learning from corrections"""
        # Simulate multiple corrections to same pattern
        for i in range(3):
            await running_server._log_tool_execution(
                "edit_file",
                {
                    "file_path": "src/app.py",
                    "old_string": f"print('debug {i}')",
                    "new_string": f"logger.debug('debug {i}')"
                },
                {"success": True}
            )

        # Check learned preferences
        prefs = await running_server._get_learned_preferences(
            category="python-logging",
            min_confidence=0.7
        )

        assert prefs["success"] == True
        assert len(prefs["preferences"]) > 0

    async def test_claudemd_generation_workflow(self, running_server, tmp_path):
        """Test CLAUDE.md file generation with security"""
        # Add learned preferences
        await running_server._learn_preference(
            category="python-package",
            context="dependency management",
            preference="Use uv for package management",
            project_specific=False,
            project_path=""
        )

        # Generate CLAUDE.md
        output_file = tmp_path / "CLAUDE.md"
        result = await running_server._update_claudemd(
            str(output_file),
            project_path=None,
            min_confidence=0.7
        )

        assert result["success"] == True
        assert output_file.exists()

        # Verify backup was created
        backup_files = list(tmp_path.glob("CLAUDE.md.backup.*"))
        assert len(backup_files) > 0
```

### 2.3 Test Scenarios

**End-to-End Workflows (15 tests)**:
- Add → Search → List workflow
- Pattern detection → Learning → CLAUDE.md update
- Tool execution → Logging → Performance tracking
- Validation → Quality gates → Approval
- Agent execution → Tracking → Recommendations

**File System Operations (8 tests)**:
- Database creation and migration
- CLAUDE.md file updates with backup
- Export to markdown functionality
- Path security validation
- Concurrent access handling

**Environment Configuration (5 tests)**:
- Database path override via env var
- Gemini API key detection
- Cost optimization activation
- Model routing configuration
- Fallback model selection

### 2.4 Coverage Target

**Minimum**: 75% integration coverage
**Focus**: Critical user workflows and data persistence

---

## 3. End-to-End Testing Strategy

### 3.1 Scope

Test complete user journeys from Claude Desktop/Code client through MCP server to database.

**User Journeys**:
1. First-time setup and installation
2. Add knowledge episodes and recall later
3. Automatic learning from corrections
4. Generate AI standards from project configs
5. Update CLAUDE.md with learned preferences
6. Export knowledge base to markdown
7. Performance tracking and agent recommendations

### 3.2 Testing Approach

**Framework**: pytest with subprocess spawning for MCP server simulation

**Sample Test Structure**:
```python
# tests/e2e/test_user_journeys.py
import pytest
import subprocess
import json
from pathlib import Path

@pytest.fixture
def mcp_server_process(tmp_path):
    """Start actual MCP server process"""
    db_path = tmp_path / "e2e_test.db"
    env = {"CLAUDE_MEMORY_DB": str(db_path)}

    process = subprocess.Popen(
        ["uv", "run", "run_server.py"],
        cwd="mcp-servers/claude-memory",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )

    yield process

    process.terminate()
    process.wait()

class TestUserJourneys:
    """Test complete user workflows"""

    def test_first_time_setup_journey(self, tmp_path):
        """Test: User installs and sets up for first time"""
        # 1. Run installation script
        result = subprocess.run(
            ["./install.sh"],
            cwd="/path/to/research-mcp",
            capture_output=True,
            text=True,
            env={"HOME": str(tmp_path)}
        )

        assert result.returncode == 0
        assert "Installation complete" in result.stdout

        # 2. Verify config file created
        config_file = tmp_path / ".claude" / "config.json"
        assert config_file.exists()

        config = json.loads(config_file.read_text())
        assert "claude-memory" in config["mcpServers"]

        # 3. Verify database initialized
        db_file = tmp_path / ".claude-memory" / "knowledge.db"
        assert db_file.exists()

    def test_knowledge_management_journey(self, mcp_server_process):
        """Test: User adds and retrieves knowledge"""
        # Simulate MCP protocol messages

        # 1. Add episode
        add_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "add_episode",
                "arguments": {
                    "name": "API Design",
                    "content": "Use REST for public API, GraphQL internal",
                    "source": "architecture-review"
                }
            },
            "id": 1
        }

        mcp_server_process.stdin.write(
            json.dumps(add_request).encode() + b"\n"
        )
        mcp_server_process.stdin.flush()

        response = mcp_server_process.stdout.readline()
        result = json.loads(response)

        assert result["result"]["success"] == True

        # 2. Search for episode
        search_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "search_episodes",
                "arguments": {"query": "API", "limit": 10}
            },
            "id": 2
        }

        mcp_server_process.stdin.write(
            json.dumps(search_request).encode() + b"\n"
        )
        mcp_server_process.stdin.flush()

        response = mcp_server_process.stdout.readline()
        result = json.loads(response)

        assert result["result"]["count"] > 0
        assert any("API" in r["name"] for r in result["result"]["results"])

    def test_automatic_learning_journey(self, mcp_server_process):
        """Test: System learns from repeated corrections"""
        # Simulate 3 identical corrections
        for i in range(3):
            log_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "log_tool_execution",
                    "arguments": {
                        "tool_name": "edit_file",
                        "args": {
                            "file_path": "src/utils.py",
                            "old_string": f"print('log {i}')",
                            "new_string": f"logger.info('log {i}')"
                        },
                        "result": {"success": True}
                    }
                },
                "id": 10 + i
            }

            mcp_server_process.stdin.write(
                json.dumps(log_request).encode() + b"\n"
            )
            mcp_server_process.stdin.flush()

            response = mcp_server_process.stdout.readline()
            result = json.loads(response)

            if i == 2:
                # After 3rd occurrence, should detect pattern
                assert "patterns_detected" in result["result"]
                assert result["result"]["patterns_detected"] > 0
```

### 3.3 Test Scenarios

**Installation & Setup (5 tests)**:
- Fresh installation on macOS
- Fresh installation on Linux
- Installation with .env file (cost optimization)
- Config file generation
- Database initialization

**Knowledge Management (10 tests)**:
- Add single episode
- Add bulk episodes
- Search with FTS5
- List recent episodes
- Update existing episodes
- Delete episodes (if implemented)
- Export to markdown
- Import from markdown (if implemented)

**Automatic Learning (12 tests)**:
- Learn from 3 identical corrections
- Learn project-specific preferences
- Learn global preferences
- Generate CLAUDE.md from patterns
- Update existing CLAUDE.md safely
- Verify backup creation
- Test confidence scoring
- Test pattern promotion

**AI Standards Generation (8 tests)**:
- Generate from .editorconfig
- Generate from .prettierrc
- Generate from pyproject.toml
- Generate from package.json
- Multi-file standards extraction
- Project type detection
- Package manager detection
- Test framework detection

### 3.4 Coverage Target

**Minimum**: 70% E2E coverage
**Focus**: Critical user paths that must work in production

---

## 4. Auto-Learning System Tests

### 4.1 Scope

Validate the AI standards generation and self-learning capabilities.

**Components**:
- Standards extraction from config files
- Pattern detection from corrections
- CLAUDE.md content generation
- Confidence scoring
- Project vs global preference distinction
- Security validation (path whitelisting)

### 4.2 Testing Approach

**Framework**: pytest with mock project structures

**Sample Test Structure**:
```python
# tests/auto_learning/test_standards_extraction.py
import pytest
from pathlib import Path
from claude_memory.standards import ConfigParser, StandardsExtractor

@pytest.fixture
def mock_project(tmp_path):
    """Create mock project with config files"""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    # Create .editorconfig
    editorconfig = project_dir / ".editorconfig"
    editorconfig.write_text("""
root = true

[*]
indent_style = space
indent_size = 2
end_of_line = lf
charset = utf-8
    """)

    # Create pyproject.toml
    pyproject = project_dir / "pyproject.toml"
    pyproject.write_text("""
[project]
name = "test-project"
version = "1.0.0"

[tool.black]
line-length = 88

[tool.pytest.ini_options]
testpaths = ["tests"]
    """)

    return project_dir

class TestStandardsExtraction:
    """Test standards extraction from config files"""

    def test_editorconfig_parsing(self, mock_project):
        """Test parsing .editorconfig file"""
        parser = ConfigParser(str(mock_project))
        standards = parser.parse_all()

        assert "formatting" in standards
        assert standards["formatting"]["indent_style"]["value"] == "space"
        assert standards["formatting"]["indent_size"]["value"] == 2
        assert standards["formatting"]["charset"]["value"] == "utf-8"

    def test_pyproject_parsing(self, mock_project):
        """Test parsing pyproject.toml file"""
        parser = ConfigParser(str(mock_project))
        standards = parser.parse_all()

        assert "formatting" in standards
        assert standards["formatting"]["line_length"]["value"] == 88
        assert standards["formatting"]["line_length"]["source"] == "black"

    def test_project_type_detection(self, mock_project):
        """Test automatic project type detection"""
        extractor = StandardsExtractor(str(mock_project))
        conventions = extractor.extract_all()

        assert conventions["project_type"] == "Python project"
        assert "test_framework" in conventions

    def test_claudemd_generation(self, mock_project):
        """Test CLAUDE.md content generation"""
        from claude_memory.standards import InstructionGenerator

        parser = ConfigParser(str(mock_project))
        standards = parser.parse_all()

        extractor = StandardsExtractor(str(mock_project))
        conventions = extractor.extract_all()

        generator = InstructionGenerator(standards, conventions)
        content = generator.generate_claude_md()

        assert "## Code Style" in content
        assert "indent_style: space" in content
        assert "line_length: 88" in content
        assert "## Project Information" in content
```

### 4.3 Test Scenarios

**Config Parsing (20 tests)**:
- .editorconfig parsing
- .prettierrc / .prettierrc.json parsing
- .eslintrc parsing
- pyproject.toml parsing
- package.json parsing
- Cargo.toml parsing
- tsconfig.json parsing
- Multiple config file merging
- Conflicting config resolution
- Invalid config handling

**Pattern Detection (15 tests)**:
- Single correction detection
- Pattern promotion after 3 occurrences
- Category classification
- Context extraction
- Confidence scoring
- Project-specific pattern detection
- Global pattern detection
- Pattern similarity matching
- False positive prevention

**CLAUDE.md Generation (12 tests)**:
- Content generation from standards
- Markdown formatting validation
- Section organization
- Enhancement hints inclusion
- Project-specific content
- Global content merging
- Backup creation
- File update atomicity
- Security validation
- Path whitelisting

### 4.4 Coverage Target

**Minimum**: 85% coverage for auto-learning components
**Critical**: 100% coverage for security validation

---

## 5. Performance Testing Strategy

### 5.1 Scope

Ensure the MCP server meets production performance requirements.

**Metrics**:
- Response time for MCP tool calls
- Database query performance
- Memory usage over time
- Concurrent request handling
- Large dataset scalability

### 5.2 Testing Approach

**Framework**: pytest-benchmark + locust for load testing

**Sample Test Structure**:
```python
# tests/performance/test_benchmarks.py
import pytest
from claude_memory.server import ClaudeMemoryMCP

@pytest.fixture
def large_dataset_server(tmp_path):
    """Server with large dataset"""
    db_path = tmp_path / "large_test.db"
    server = ClaudeMemoryMCP(db_path=str(db_path))

    # Add 10,000 episodes
    import asyncio
    for i in range(10000):
        asyncio.run(server._add_episode(
            f"Episode {i}",
            f"Content for episode {i} with searchable text",
            "perf-test"
        ))

    return server

class TestPerformance:
    """Performance benchmarks"""

    def test_add_episode_performance(self, benchmark, memory_server):
        """Benchmark episode addition"""
        async def add_episode():
            return await memory_server._add_episode(
                "Perf Test",
                "Performance testing content",
                "benchmark"
            )

        result = benchmark.pedantic(
            lambda: asyncio.run(add_episode()),
            iterations=100,
            rounds=5
        )

        # Should complete under 50ms
        assert benchmark.stats.mean < 0.05

    def test_search_performance_large_dataset(
        self,
        benchmark,
        large_dataset_server
    ):
        """Benchmark search on 10K episodes"""
        async def search():
            return await large_dataset_server._search_episodes(
                "searchable",
                limit=10
            )

        result = benchmark(lambda: asyncio.run(search()))

        # Should complete under 50ms even with 10K episodes
        assert benchmark.stats.mean < 0.05

    def test_concurrent_operations(self, memory_server):
        """Test concurrent MCP tool calls"""
        import asyncio
        import time

        async def concurrent_adds():
            tasks = [
                memory_server._add_episode(
                    f"Concurrent {i}",
                    f"Content {i}",
                    "concurrency-test"
                )
                for i in range(100)
            ]
            return await asyncio.gather(*tasks)

        start = time.time()
        results = asyncio.run(concurrent_adds())
        duration = time.time() - start

        # Should handle 100 concurrent operations under 5s
        assert duration < 5.0
        assert all(r["success"] for r in results)

    def test_memory_usage_over_time(self, memory_server):
        """Test memory doesn't leak over long sessions"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Simulate 1000 operations
        for i in range(1000):
            asyncio.run(memory_server._add_episode(
                f"Memory Test {i}",
                f"Content {i}",
                "memory-test"
            ))

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be under 50MB
        assert memory_increase < 50
```

### 5.3 Performance Requirements

**Response Time Targets**:
- add_episode: < 50ms (p95)
- search_episodes: < 50ms (p95)
- list_recent: < 20ms (p95)
- generate_ai_standards: < 500ms (p95)
- update_claudemd: < 200ms (p95)

**Throughput Targets**:
- 100+ concurrent requests without degradation
- 10K+ episodes in database without slowdown
- 1M+ episodes searchable under 50ms (with FTS5)

**Resource Limits**:
- Memory usage: < 100MB for normal operations
- Memory growth: < 50MB over 1000 operations
- Database size: < 10MB per 10K episodes

**Load Testing Scenarios**:
- 10 concurrent users, 100 operations each
- 100 concurrent users, 10 operations each
- 1000 episodes added in bulk
- 10K episode search performance

### 5.4 Monitoring

**Metrics to Track**:
- Response time percentiles (p50, p95, p99)
- Error rate
- Memory usage (RSS, heap)
- Database size growth
- Query execution time
- Connection pool utilization

**Tools**:
- pytest-benchmark for microbenchmarks
- locust for load testing
- psutil for memory monitoring
- SQLite query analyzer for database performance

---

## 6. Security Testing Strategy

### 6.1 Scope

Validate security measures and identify vulnerabilities before production deployment.

**Security Areas**:
- Path traversal prevention
- SQL injection prevention
- File system access control
- Environment variable handling
- Audit logging
- Input validation
- Privilege escalation prevention

### 6.2 Testing Approach

**Framework**: pytest with security-focused test cases

**Sample Test Structure**:
```python
# tests/security/test_security.py
import pytest
from pathlib import Path
from claude_memory.server import ClaudeMemoryMCP

class TestPathSecurity:
    """Test path traversal and file access security"""

    async def test_claudemd_path_whitelist(self, memory_server, tmp_path):
        """Test CLAUDE.md update only allows whitelisted paths"""
        # Attempt to update file outside whitelist
        malicious_path = "/etc/passwd"

        result = await memory_server._update_claudemd(
            malicious_path,
            project_path=None,
            min_confidence=0.7
        )

        assert result["success"] == False
        assert "not in allowed directories" in result["error"]

    async def test_claudemd_filename_restriction(self, memory_server, tmp_path):
        """Test only CLAUDE.md files can be updated"""
        # Attempt to update arbitrary file
        malicious_file = tmp_path / "malicious.py"

        result = await memory_server._update_claudemd(
            str(malicious_file),
            project_path=None,
            min_confidence=0.7
        )

        assert result["success"] == False
        assert "Only CLAUDE.md" in result["error"]

    async def test_path_traversal_prevention(self, memory_server, tmp_path):
        """Test path traversal attacks are blocked"""
        # Attempt path traversal
        traversal_path = tmp_path / ".." / ".." / "etc" / "CLAUDE.md"

        result = await memory_server._update_claudemd(
            str(traversal_path),
            project_path=None,
            min_confidence=0.7
        )

        assert result["success"] == False

class TestSQLInjection:
    """Test SQL injection prevention"""

    async def test_search_sql_injection(self, memory_server):
        """Test search query with SQL injection attempt"""
        # Attempt SQL injection
        malicious_query = "'; DROP TABLE episodes; --"

        result = await memory_server._search_episodes(
            malicious_query,
            limit=10
        )

        # Should not crash and should return safe results
        assert "success" in result

        # Verify table still exists
        with sqlite3.connect(memory_server.db_path) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='episodes'"
            )
            assert cursor.fetchone() is not None

    async def test_add_episode_sql_injection(self, memory_server):
        """Test episode addition with SQL injection attempt"""
        malicious_content = "'; DROP TABLE episodes; --"

        result = await memory_server._add_episode(
            "SQL Injection Test",
            malicious_content,
            "security-test"
        )

        assert result["success"] == True

        # Verify table still exists and data is safely stored
        with sqlite3.connect(memory_server.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM episodes")
            count = cursor.fetchone()[0]
            assert count > 0

class TestAuditLogging:
    """Test audit trail for sensitive operations"""

    async def test_claudemd_update_logged(self, memory_server, tmp_path):
        """Test CLAUDE.md updates are logged"""
        file_path = tmp_path / "CLAUDE.md"

        result = await memory_server._update_claudemd(
            str(file_path),
            project_path=None,
            min_confidence=0.7
        )

        # Check audit log
        with sqlite3.connect(memory_server.db_path) as conn:
            cursor = conn.execute("""
                SELECT action, target_type, target_path, success
                FROM audit_log
                WHERE action = 'update_claudemd'
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            log_entry = cursor.fetchone()

            assert log_entry is not None
            assert log_entry[0] == "update_claudemd"
            assert log_entry[1] == "file"
            assert str(file_path) in log_entry[2]

    async def test_failed_operations_logged(self, memory_server):
        """Test failed security attempts are logged"""
        # Attempt malicious operation
        malicious_path = "/etc/passwd"

        await memory_server._update_claudemd(
            malicious_path,
            project_path=None,
            min_confidence=0.7
        )

        # Verify logged as failed
        with sqlite3.connect(memory_server.db_path) as conn:
            cursor = conn.execute("""
                SELECT success
                FROM audit_log
                WHERE target_path = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (malicious_path,))
            log_entry = cursor.fetchone()

            assert log_entry is not None
            assert log_entry[0] == 0  # False/failed

class TestInputValidation:
    """Test input validation and sanitization"""

    async def test_episode_name_length_limit(self, memory_server):
        """Test extremely long episode names are handled"""
        long_name = "A" * 10000

        result = await memory_server._add_episode(
            long_name,
            "Content",
            "test"
        )

        # Should either truncate or reject gracefully
        assert "success" in result or "error" in result

    async def test_special_characters_handling(self, memory_server):
        """Test special characters in input are handled safely"""
        special_chars = "!@#$%^&*(){}[]|\\:;\"'<>,.?/~`"

        result = await memory_server._add_episode(
            f"Special {special_chars}",
            f"Content with {special_chars}",
            "test"
        )

        assert result["success"] == True

    async def test_unicode_handling(self, memory_server):
        """Test unicode characters are handled correctly"""
        unicode_text = "测试 テスト тест 🚀 😀"

        result = await memory_server._add_episode(
            f"Unicode {unicode_text}",
            unicode_text,
            "test"
        )

        assert result["success"] == True

        # Verify can retrieve
        search_result = await memory_server._search_episodes(unicode_text[:4], 10)
        assert search_result["success"] == True
```

### 6.3 Security Test Categories

**Path Security (10 tests)**:
- Path traversal prevention
- Symlink attack prevention
- Whitelist enforcement
- Filename validation
- Directory creation security

**SQL Injection (8 tests)**:
- Search query injection
- Episode content injection
- Pattern preference injection
- Parameterized query verification

**Access Control (6 tests)**:
- File system permissions
- Database access control
- Environment variable protection
- API key handling

**Audit & Logging (5 tests)**:
- Sensitive operation logging
- Failed attempt logging
- Log tampering prevention
- Audit trail completeness

**Input Validation (8 tests)**:
- Length limits
- Special characters
- Unicode handling
- Null/empty input
- Type validation

**Authentication & Authorization (if applicable)**:
- API key validation
- Token expiration
- Privilege escalation prevention

### 6.4 Security Checklist

**Pre-Deployment Security Review**:
- [ ] All SQL queries use parameterized statements
- [ ] File path operations use whitelist validation
- [ ] No hardcoded secrets in code
- [ ] Environment variables properly validated
- [ ] Audit logging enabled for sensitive operations
- [ ] Input validation on all user-facing functions
- [ ] Error messages don't leak sensitive info
- [ ] Dependencies scanned for vulnerabilities
- [ ] Database file permissions correctly set (600)
- [ ] No world-writable files created

**Security Scanning Tools**:
- bandit (Python security linter)
- safety (dependency vulnerability scanner)
- semgrep (static analysis)
- OWASP dependency-check

---

## 7. Test Coverage Requirements

### 7.1 Coverage Targets

**Overall Project Coverage**:
- **Minimum**: 80% line coverage
- **Target**: 85%+ line coverage
- **Critical paths**: 100% coverage

**Coverage by Component**:
| Component | Minimum | Target |
|-----------|---------|--------|
| Core server (server.py) | 85% | 90% |
| Enhanced server | 85% | 90% |
| Pattern extraction | 90% | 95% |
| CLAUDE.md manager | 90% | 95% |
| Standards extraction | 85% | 90% |
| Validation engine | 85% | 90% |
| Agent tracker | 80% | 85% |
| Model router | 80% | 85% |
| Database operations | 95% | 100% |
| Security validation | 100% | 100% |

### 7.2 Coverage Measurement

**Tool**: pytest-cov

**Configuration** (`pyproject.toml`):
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "--cov=claude_memory",
    "--cov=hooks",
    "--cov=intelligence",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--cov-report=xml",
    "--cov-fail-under=80"
]

[tool.coverage.run]
source = ["claude_memory", "hooks", "intelligence"]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__pycache__/*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod"
]
```

**Running Coverage**:
```bash
# Run tests with coverage
pytest --cov=claude_memory --cov-report=html

# View HTML report
open htmlcov/index.html

# Check if coverage meets minimum
pytest --cov=claude_memory --cov-fail-under=80
```

### 7.3 Coverage Exceptions

**Acceptable Low Coverage Areas**:
- CLI entry points (if applicable)
- Debug logging code
- Deprecated/legacy code marked for removal
- Abstract base classes

**100% Coverage Required**:
- Security validation functions
- Database operations
- File system operations
- SQL query construction

---

## 8. Testing Framework Recommendations

### 8.1 Primary Framework: pytest

**Why pytest**:
- Native async/await support
- Excellent fixture system
- Parametrized testing
- Rich plugin ecosystem
- Clear assertion introspection
- Industry standard for Python

**Key Plugins**:
```bash
# Install testing dependencies
uv add --dev pytest pytest-asyncio pytest-cov pytest-mock pytest-benchmark
```

**pytest.ini Configuration**:
```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    performance: Performance tests
    security: Security tests
    slow: Slow running tests
```

### 8.2 Supporting Tools

**Code Coverage**: pytest-cov
**Mocking**: pytest-mock
**Performance**: pytest-benchmark
**Load Testing**: locust
**Security Scanning**: bandit, safety
**Static Analysis**: mypy, ruff

### 8.3 Test Organization

**Directory Structure**:
```
research-mcp/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_server.py
│   │   ├── test_pattern_extractor.py
│   │   ├── test_claudemd_manager.py
│   │   └── test_model_router.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_mcp_server.py
│   │   ├── test_database_integration.py
│   │   └── test_file_operations.py
│   ├── e2e/
│   │   ├── __init__.py
│   │   ├── test_user_journeys.py
│   │   └── test_installation.py
│   ├── auto_learning/
│   │   ├── __init__.py
│   │   ├── test_standards_extraction.py
│   │   └── test_pattern_learning.py
│   ├── performance/
│   │   ├── __init__.py
│   │   ├── test_benchmarks.py
│   │   └── test_load.py
│   └── security/
│       ├── __init__.py
│       ├── test_security.py
│       └── test_audit_logging.py
├── mcp-servers/
│   └── claude-memory/
│       ├── claude_memory/
│       │   ├── server.py
│       │   ├── enhanced_server.py
│       │   └── ...
│       └── hooks/
│           └── ...
└── pyproject.toml
```

### 8.4 Fixture Strategy

**Shared Fixtures** (`tests/conftest.py`):
```python
import pytest
from pathlib import Path
from claude_memory.server import ClaudeMemoryMCP

@pytest.fixture(scope="session")
def test_data_dir():
    """Directory for test data files"""
    return Path(__file__).parent / "test_data"

@pytest.fixture
def temp_db(tmp_path):
    """Temporary database for tests"""
    db_path = tmp_path / "test_knowledge.db"
    return db_path

@pytest.fixture
async def memory_server(temp_db):
    """ClaudeMemoryMCP instance with test database"""
    server = ClaudeMemoryMCP(db_path=str(temp_db))
    yield server
    # Cleanup if needed

@pytest.fixture
def mock_project(tmp_path):
    """Mock project structure with config files"""
    project = tmp_path / "test_project"
    project.mkdir()
    # Create config files
    return project
```

---

## 9. CI/CD Integration Strategy

### 9.1 GitHub Actions Workflow

**File**: `.github/workflows/test.yml`

```yaml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ['3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v3

    - name: Install uv
      run: curl -LsSf https://astral.sh/uv/install.sh | sh

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        cd mcp-servers/claude-memory
        uv sync

    - name: Run unit tests
      run: |
        cd mcp-servers/claude-memory
        uv run pytest tests/unit -v --cov=claude_memory --cov-report=xml

    - name: Run integration tests
      run: |
        cd mcp-servers/claude-memory
        uv run pytest tests/integration -v

    - name: Run security tests
      run: |
        cd mcp-servers/claude-memory
        uv run pytest tests/security -v

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./mcp-servers/claude-memory/coverage.xml
        fail_ci_if_error: true

    - name: Check coverage threshold
      run: |
        cd mcp-servers/claude-memory
        uv run pytest --cov=claude_memory --cov-fail-under=80

  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Run Bandit security scan
      run: |
        cd mcp-servers/claude-memory
        uv run bandit -r claude_memory/ -f json -o bandit-report.json

    - name: Run Safety dependency check
      run: |
        cd mcp-servers/claude-memory
        uv run safety check --json > safety-report.json

    - name: Upload security reports
      uses: actions/upload-artifact@v3
      with:
        name: security-reports
        path: |
          mcp-servers/claude-memory/bandit-report.json
          mcp-servers/claude-memory/safety-report.json

  performance:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Install dependencies
      run: |
        cd mcp-servers/claude-memory
        uv sync

    - name: Run performance benchmarks
      run: |
        cd mcp-servers/claude-memory
        uv run pytest tests/performance --benchmark-only --benchmark-json=benchmark.json

    - name: Upload benchmark results
      uses: actions/upload-artifact@v3
      with:
        name: benchmark-results
        path: mcp-servers/claude-memory/benchmark.json
```

### 9.2 Pre-commit Hooks

**File**: `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: local
    hooks:
      - id: pytest-unit
        name: pytest-unit
        entry: bash -c 'cd mcp-servers/claude-memory && uv run pytest tests/unit -v'
        language: system
        pass_filenames: false
        always_run: true

      - id: pytest-coverage
        name: pytest-coverage
        entry: bash -c 'cd mcp-servers/claude-memory && uv run pytest --cov=claude_memory --cov-fail-under=80'
        language: system
        pass_filenames: false
        always_run: true
```

### 9.3 Quality Gates

**Deployment Blockers**:
- [ ] All tests passing (unit, integration, E2E)
- [ ] Code coverage ≥ 80%
- [ ] No high/critical security vulnerabilities
- [ ] Performance benchmarks within acceptable range
- [ ] No failing security tests
- [ ] All audit logging tests passing

**Warning Thresholds**:
- Coverage drops below 85%
- Performance regression > 20%
- New medium-severity security issues
- Test execution time > 5 minutes

### 9.4 Test Execution Strategy

**On Every Commit**:
- Unit tests (fast, < 30 seconds)
- Linting and formatting
- Type checking

**On Pull Request**:
- All unit tests
- Integration tests
- Security tests
- Coverage check

**Before Merge to Main**:
- Full test suite
- E2E tests
- Performance tests
- Security scans

**Nightly Build**:
- Extended E2E tests
- Load testing
- Memory leak detection
- Dependency vulnerability scan

---

## 10. Quality Gates Before Deployment

### 10.1 Mandatory Requirements

**Code Quality**:
- [ ] All tests passing (unit, integration, E2E)
- [ ] Code coverage ≥ 80%
- [ ] No linting errors (ruff)
- [ ] No type checking errors (mypy)
- [ ] No security issues (bandit, safety)

**Functional Requirements**:
- [ ] All MCP tools working correctly
- [ ] Database operations reliable
- [ ] Pattern learning functioning
- [ ] CLAUDE.md generation working
- [ ] Security validation passing
- [ ] Audit logging complete

**Performance Requirements**:
- [ ] Response times within targets
- [ ] Memory usage within limits
- [ ] No memory leaks detected
- [ ] Concurrent operations stable
- [ ] Large dataset performance acceptable

**Security Requirements**:
- [ ] Path traversal prevention verified
- [ ] SQL injection prevention verified
- [ ] Audit trail complete
- [ ] No high/critical vulnerabilities
- [ ] Input validation comprehensive

**Documentation**:
- [ ] README.md up to date
- [ ] Installation guide accurate
- [ ] API documentation complete
- [ ] Troubleshooting guide helpful
- [ ] Example usage provided

### 10.2 Release Checklist

**Pre-Release**:
1. Run full test suite
2. Execute security scans
3. Verify documentation
4. Test installation process
5. Check dependencies for vulnerabilities
6. Review audit logs
7. Verify backup/restore procedures
8. Test on fresh systems (macOS, Linux)

**Release Validation**:
1. Tag release version
2. Generate release notes
3. Update CHANGELOG.md
4. Deploy to staging environment
5. Execute smoke tests
6. Monitor for 24 hours
7. Promote to production

**Post-Release**:
1. Monitor error rates
2. Track performance metrics
3. Review user feedback
4. Document issues
5. Plan hotfixes if needed

---

## 11. Test Execution Schedule

### 11.1 Development Phase

**Daily**:
- Unit tests on developer machines
- Pre-commit hooks
- Local coverage checks

**Per Pull Request**:
- Full unit test suite
- Integration tests
- Security tests
- Coverage verification

**Weekly**:
- Full E2E test suite
- Performance benchmarks
- Security vulnerability scans

### 11.2 Pre-Launch Phase

**Week 1-2: Implementation**:
- Write unit tests (85% coverage target)
- Write integration tests
- Set up CI/CD pipeline

**Week 3: Security & Performance**:
- Write security tests
- Write performance tests
- Execute load testing
- Security audit

**Week 4: E2E & Validation**:
- Write E2E tests
- Execute full test suite
- Fix any critical issues
- Final security review

**Week 5: Pre-Launch**:
- Staging deployment
- Smoke testing
- Documentation review
- Release preparation

### 11.3 Post-Launch

**Daily**:
- Automated test suite (CI/CD)
- Performance monitoring
- Error tracking

**Weekly**:
- Security scans
- Dependency updates
- Coverage review

**Monthly**:
- Full regression testing
- Performance benchmarking
- Security audit
- Test suite maintenance

---

## 12. Monitoring & Metrics

### 12.1 Test Metrics to Track

**Coverage Metrics**:
- Line coverage (target: 80%+)
- Branch coverage (target: 75%+)
- Function coverage (target: 85%+)
- Coverage trend over time

**Test Execution Metrics**:
- Total test count
- Pass rate (target: 100%)
- Test execution time
- Flaky test rate (target: <1%)

**Performance Metrics**:
- Response time (p95)
- Memory usage
- Database query time
- Throughput

**Security Metrics**:
- Vulnerability count (target: 0 high/critical)
- Security test pass rate
- Audit log completeness

### 12.2 Reporting

**Daily Reports** (CI/CD):
- Test pass/fail status
- Coverage percentage
- New failures

**Weekly Reports**:
- Test trends
- Performance benchmarks
- Security scan results
- Coverage changes

**Monthly Reports**:
- Test suite health
- Coverage analysis
- Performance trends
- Security posture

---

## 13. Risk Assessment

### 13.1 Testing Risks

**High Risk Areas**:
- Database migrations (data loss potential)
- File system operations (security)
- Concurrent operations (race conditions)
- Pattern learning (accuracy)
- Security validation (bypass potential)

**Mitigation Strategies**:
- 100% coverage for high-risk areas
- Extensive security testing
- Backup validation before file updates
- Transaction rollback testing
- Race condition testing

### 13.2 Known Limitations

**Current Gaps**:
- Limited load testing with > 100 concurrent users
- Mobile/tablet client testing not included
- Network failure simulation needed
- Backup/restore testing needed
- Disaster recovery scenarios

**Future Improvements**:
- Chaos engineering tests
- Property-based testing
- Mutation testing
- Fuzz testing
- Contract testing for MCP protocol

---

## 14. Success Criteria

### 14.1 Launch Readiness Criteria

**Must Have** (Blockers):
- [ ] 80%+ test coverage achieved
- [ ] Zero high/critical security vulnerabilities
- [ ] All core functionality tests passing
- [ ] Performance within acceptable limits
- [ ] Security tests 100% passing
- [ ] Installation tested on macOS and Linux
- [ ] Documentation complete and accurate

**Should Have** (Important):
- [ ] 85%+ test coverage
- [ ] E2E tests covering main user journeys
- [ ] Load testing completed
- [ ] Memory leak testing passed
- [ ] CI/CD pipeline operational

**Nice to Have** (Enhancements):
- [ ] 90%+ test coverage
- [ ] Comprehensive E2E suite
- [ ] Performance benchmarking dashboard
- [ ] Automated security scanning

### 14.2 Definition of Done

A feature is considered "done" when:
1. Code written and reviewed
2. Unit tests written (85%+ coverage)
3. Integration tests written (if applicable)
4. E2E test written (if user-facing)
5. Security review completed
6. Performance validated
7. Documentation updated
8. All tests passing
9. Code merged to main

---

## 15. Next Steps

### 15.1 Immediate Actions (Week 1)

1. **Set up test infrastructure**:
   - Create test directory structure
   - Configure pytest and pytest-cov
   - Set up CI/CD pipeline (GitHub Actions)
   - Configure pre-commit hooks

2. **Write unit tests**:
   - Start with core server operations
   - Add database operation tests
   - Cover pattern extraction logic
   - Test CLAUDE.md generation

3. **Establish baseline coverage**:
   - Run initial coverage report
   - Identify low-coverage areas
   - Set coverage targets

### 15.2 Short-term Goals (Weeks 2-3)

1. **Integration testing**:
   - MCP server integration tests
   - File system operation tests
   - Database integration tests

2. **Security testing**:
   - Path security tests
   - SQL injection tests
   - Audit logging verification

3. **Performance baseline**:
   - Initial benchmarks
   - Memory usage profiling
   - Identify bottlenecks

### 15.3 Pre-Launch Goals (Week 4-5)

1. **E2E testing**:
   - User journey tests
   - Installation tests
   - Cross-platform validation

2. **Final validation**:
   - Full test suite execution
   - Security audit
   - Performance validation
   - Documentation review

3. **Launch preparation**:
   - Staging deployment
   - Smoke tests
   - Release notes
   - Deployment plan

---

## 16. Conclusion

This comprehensive testing strategy provides a roadmap for ensuring the Claude Memory MCP server is production-ready. By following this strategy and meeting the defined quality gates, we can confidently deploy a robust, secure, and performant system.

**Key Takeaways**:
- **80%+ test coverage** is mandatory before launch
- **pytest** is the recommended framework for Python testing
- **Security testing** is critical given file system access
- **Performance testing** ensures scalability
- **CI/CD integration** automates quality assurance
- **Quality gates** prevent regressions

**Estimated Timeline**:
- Test infrastructure setup: 1 week
- Test implementation: 2-3 weeks
- Security & performance validation: 1 week
- Pre-launch testing & fixes: 1 week
- **Total: 5-6 weeks** to full test coverage

**Success Metrics**:
- 80%+ code coverage achieved
- Zero high/critical security vulnerabilities
- All performance targets met
- All quality gates passing
- CI/CD pipeline operational
- Ready for production deployment

---

## Appendix A: Test File Templates

### A.1 Unit Test Template

```python
# tests/unit/test_feature.py
import pytest
from claude_memory.server import ClaudeMemoryMCP

@pytest.fixture
def memory_server(temp_db):
    """Create server instance for testing"""
    return ClaudeMemoryMCP(db_path=str(temp_db))

class TestFeature:
    """Test suite for Feature X"""

    async def test_feature_success_case(self, memory_server):
        """Test feature works with valid input"""
        # Arrange
        input_data = {...}

        # Act
        result = await memory_server.feature_method(input_data)

        # Assert
        assert result["success"] == True
        assert "expected_key" in result

    async def test_feature_error_case(self, memory_server):
        """Test feature handles errors gracefully"""
        # Arrange
        invalid_input = {...}

        # Act
        result = await memory_server.feature_method(invalid_input)

        # Assert
        assert result["success"] == False
        assert "error" in result
```

### A.2 Integration Test Template

```python
# tests/integration/test_integration.py
import pytest
from claude_memory.server import ClaudeMemoryMCP

class TestIntegration:
    """Test component integration"""

    async def test_end_to_end_workflow(self, memory_server):
        """Test complete workflow from A to Z"""
        # Step 1: Initial operation
        result1 = await memory_server.operation_a()
        assert result1["success"] == True

        # Step 2: Dependent operation
        result2 = await memory_server.operation_b(result1["data"])
        assert result2["success"] == True

        # Step 3: Verify final state
        final_state = await memory_server.get_state()
        assert final_state["expected_value"] == "expected"
```

### A.3 Security Test Template

```python
# tests/security/test_security_feature.py
import pytest

class TestSecurityFeature:
    """Test security measures for Feature X"""

    async def test_malicious_input_rejected(self, memory_server):
        """Test malicious input is rejected"""
        # Arrange
        malicious_input = "'; DROP TABLE users; --"

        # Act
        result = await memory_server.secure_method(malicious_input)

        # Assert
        assert result["success"] == False or result["success"] == True
        # Verify no damage was done
        # ... verification code ...

    async def test_audit_log_created(self, memory_server):
        """Test security event is logged"""
        # Arrange & Act
        await memory_server.sensitive_operation()

        # Assert - check audit log
        # ... audit verification code ...
```

---

## Appendix B: Resources

**pytest Documentation**: https://docs.pytest.org/
**pytest-cov**: https://pytest-cov.readthedocs.io/
**MCP Protocol Spec**: https://modelcontextprotocol.io/
**SQLite Testing**: https://www.sqlite.org/testing.html
**OWASP Testing Guide**: https://owasp.org/www-project-web-security-testing-guide/

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-13
**Author**: Tester Agent (Hive Mind Swarm)
**Review Status**: Ready for Coordinator Review

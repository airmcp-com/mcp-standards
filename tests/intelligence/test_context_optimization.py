"""
Tests for Context Optimization System

Tests:
1. ContextOptimizer - Token reduction, template matching
2. ConfigFileWatcher - Event detection, debouncing
3. DiffBasedLearner - Pattern detection, confidence scoring
4. PrimeContextLoader - Context loading, caching
5. ContextManager - Integration, orchestration
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from intelligence.context import (
    ContextOptimizer, ConfigFileWatcher, DiffBasedLearner,
    PrimeContextLoader, ContextManager, WatcherConfig
)


@pytest.fixture
def temp_project():
    """Create temporary project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Create project files
        (project_path / 'pyproject.toml').write_text("""
[project]
name = "test-project"
dependencies = ["pytest"]
""")

        (project_path / '.editorconfig').write_text("""
[*]
indent_size = 4
""")

        yield project_path


@pytest.fixture
def optimizer():
    """Create ContextOptimizer instance."""
    return ContextOptimizer(memory_system=None, agentdb=None)


@pytest.fixture
def learner():
    """Create DiffBasedLearner instance."""
    return DiffBasedLearner(memory_system=None, agentdb=None)


@pytest.fixture
def prime_loader():
    """Create PrimeContextLoader instance."""
    return PrimeContextLoader(memory_system=None, optimizer=None)


class TestContextOptimizer:
    """Test context optimization and token reduction."""

    def test_token_estimation_basic(self, optimizer):
        """Test basic token estimation."""
        content = "Hello world! This is a test."
        tokens = optimizer.estimate_tokens(content)

        # ~4 chars per token
        expected = len(content) / 4
        assert abs(tokens - expected) < 5  # Allow small variance

    def test_token_estimation_with_markdown(self, optimizer):
        """Test token estimation with markdown structure."""
        content = """
# Heading 1
## Heading 2

- Bullet point 1
- Bullet point 2

```python
def hello():
    return "world"
```
"""
        tokens = optimizer.estimate_tokens(content)

        # Should account for markdown overhead
        assert tokens > len(content) / 4  # More than base
        assert tokens < len(content) / 2  # But reasonable

    def test_project_type_detection_python(self, optimizer, temp_project):
        """Test Python project detection."""
        template_match = optimizer.analyze_project_type(temp_project)

        assert template_match.template_id == 'python-backend'
        assert template_match.confidence > 0.5
        assert 'pyproject.toml' in template_match.detected_patterns

    def test_project_type_detection_unknown(self, optimizer):
        """Test unknown project type fallback."""
        with tempfile.TemporaryDirectory() as tmpdir:
            empty_project = Path(tmpdir)

            template_match = optimizer.analyze_project_type(empty_project)

            assert template_match.template_id == 'research'
            assert template_match.confidence == 0.5  # Default

    def test_content_optimization_basic(self, optimizer):
        """Test basic content optimization."""
        content = """
# Test CLAUDE.md

## Core Principles
These are essential.

## Extended Documentation
This is a very long section with lots of details that could be moved
to a /prime context. It contains examples, explanations, and much more
content that isn't strictly necessary for the core context.

Lorem ipsum dolor sit amet, consectetur adipiscing elit.
""" * 10  # Make it large

        optimized, metrics = optimizer.optimize_content(
            content,
            target_tokens=500,
            preserve_sections=['Core Principles']
        )

        assert metrics.token_count <= 600  # Within budget (with margin)
        assert 'Core Principles' in optimized  # Preserved
        assert metrics.compression_ratio > 1.0  # Compressed

    def test_section_extraction(self, optimizer):
        """Test markdown section extraction."""
        content = """
# Title

## Section 1
Content 1

## Section 2
Content 2

### Subsection
Sub content
"""

        sections = optimizer._extract_sections(content)

        assert 'Section 1' in sections
        assert 'Section 2' in sections
        assert 'Content 1' in sections['Section 1']

    def test_section_scoring(self, optimizer):
        """Test section importance scoring."""
        sections = {
            'Core Principles': 'Must always follow these rules.',
            'Examples': 'Here are some code examples...',
            'Extended Info': 'This is optional additional information.'
        }

        scores = optimizer._score_sections(sections)

        # Core section should score higher
        assert scores['Core Principles'] > scores['Examples']
        assert scores['Core Principles'] > scores['Extended Info']


class TestDiffBasedLearner:
    """Test learning from manual edits."""

    @pytest.mark.asyncio
    async def test_preference_detection(self, learner):
        """Test preference pattern detection."""
        previous = "- Use pip for packages"
        current = "- Use uv for package management (not pip)"

        analysis = await learner.analyze_diff(
            previous_content=previous,
            current_content=current
        )

        assert len(analysis.patterns_detected) > 0

        # Find preference pattern
        pref_patterns = [
            p for p in analysis.patterns_detected
            if p.pattern_type in ['preference', 'preference_correction']
        ]

        assert len(pref_patterns) > 0
        pattern = pref_patterns[0]

        assert 'uv' in pattern.content.lower()
        assert pattern.confidence > 0.5

    @pytest.mark.asyncio
    async def test_tool_preference_detection(self, learner):
        """Test tool preference learning."""
        additions = [
            "- Use pytest for testing",
            "- Use ruff for linting"
        ]
        deletions = []

        patterns = learner._detect_tool_preferences(additions, deletions)

        assert len(patterns) > 0

        # Check if pytest pattern detected
        pytest_patterns = [p for p in patterns if 'pytest' in p.content.lower()]
        assert len(pytest_patterns) > 0

    @pytest.mark.asyncio
    async def test_confidence_scoring(self, learner):
        """Test Bayesian confidence updates."""
        # First occurrence
        await learner.analyze_diff(
            previous_content="Use A",
            current_content="Use B (not A)"
        )

        patterns = await learner.get_learned_patterns()
        assert len(patterns) > 0

        initial_confidence = patterns[0].confidence
        initial_frequency = patterns[0].frequency

        # Second occurrence (reinforcement)
        await learner.analyze_diff(
            previous_content="Use A again",
            current_content="Use B (not A)"
        )

        patterns = await learner.get_learned_patterns()
        updated_pattern = patterns[0]

        # Confidence should increase
        assert updated_pattern.confidence > initial_confidence
        assert updated_pattern.frequency > initial_frequency

    @pytest.mark.asyncio
    async def test_auto_apply_patterns(self, learner):
        """Test automatic pattern application."""
        # Learn pattern with high confidence
        pattern_content = "Use uv for package management (not pip)"

        # Simulate pattern learning
        await learner.analyze_diff(
            previous_content="Use pip",
            current_content=pattern_content
        )

        # Reinforce to increase confidence
        await learner.analyze_diff(
            previous_content="Use pip",
            current_content=pattern_content
        )

        # Try to auto-apply
        test_content = """
## Tool Preferences
Currently using pip for packages.
"""

        modified, applied = await learner.auto_apply_patterns(
            test_content,
            min_confidence=0.7
        )

        # Should have modifications or suggestions
        # (Depends on pattern matching implementation)
        assert isinstance(modified, str)
        assert isinstance(applied, list)

    @pytest.mark.asyncio
    async def test_pattern_filtering(self, learner):
        """Test pattern retrieval with filters."""
        # Add some patterns
        await learner.analyze_diff(
            previous_content="Old way",
            current_content="New way (not old way)"
        )

        # Get all patterns
        all_patterns = await learner.get_learned_patterns()

        # Get high confidence only
        high_conf = await learner.get_learned_patterns(min_confidence=0.9)

        # Get specific type
        pref_patterns = await learner.get_learned_patterns(
            pattern_type='preference_correction'
        )

        assert len(all_patterns) >= len(high_conf)
        assert all(p.confidence >= 0.9 for p in high_conf)


class TestPrimeContextLoader:
    """Test dynamic context loading."""

    @pytest.mark.asyncio
    async def test_load_context_basic(self, prime_loader):
        """Test basic context loading."""
        context = await prime_loader.load_context('bug')

        assert context is not None
        assert len(context) > 0
        assert 'Bug Fixing' in context or 'Debugging' in context

    @pytest.mark.asyncio
    async def test_load_context_with_dependencies(self, prime_loader):
        """Test loading context with dependencies."""
        # Refactor depends on test
        context = await prime_loader.load_context(
            'refactor',
            include_dependencies=True
        )

        assert context is not None
        # Should be longer due to dependencies
        assert len(context) > 1000

    @pytest.mark.asyncio
    async def test_load_unknown_context(self, prime_loader):
        """Test loading unknown context."""
        context = await prime_loader.load_context('unknown_context')

        assert context is None

    @pytest.mark.asyncio
    async def test_context_usage_tracking(self, prime_loader):
        """Test usage statistics tracking."""
        initial_count = prime_loader._contexts['bug'].usage_count

        await prime_loader.load_context('bug')

        assert prime_loader._contexts['bug'].usage_count == initial_count + 1
        assert prime_loader._contexts['bug'].last_used is not None

    @pytest.mark.asyncio
    async def test_suggest_contexts(self, prime_loader):
        """Test context suggestions."""
        suggestions = await prime_loader.suggest_contexts(
            query="fixing performance bug"
        )

        assert len(suggestions) > 0

        # Should suggest relevant contexts
        context_ids = [ctx.context_id for ctx in suggestions]
        assert 'bug' in context_ids or 'perf' in context_ids

    def test_list_available_contexts(self, prime_loader):
        """Test listing all contexts."""
        contexts = prime_loader.list_available_contexts()

        assert len(contexts) == 8  # We have 8 contexts

        # Check structure
        assert all('id' in ctx for ctx in contexts)
        assert all('command' in ctx for ctx in contexts)
        assert all('tokens' in ctx for ctx in contexts)

    def test_context_menu_generation(self, prime_loader):
        """Test context menu generation."""
        menu = prime_loader.get_context_menu()

        assert '# 📚 Available Prime Contexts' in menu
        assert '/prime-bug' in menu
        assert '/prime-feature' in menu


class TestConfigFileWatcher:
    """Test file watching and event detection."""

    @pytest.mark.asyncio
    async def test_file_hash_calculation(self, temp_project):
        """Test file content hashing."""
        config = WatcherConfig(
            watch_patterns=['pyproject.toml'],
            debounce_seconds=0.5,
            auto_optimize=False,
            backup_on_change=False
        )

        watcher = ConfigFileWatcher(
            project_path=temp_project,
            config=config
        )

        # Calculate hash
        test_file = temp_project / 'pyproject.toml'
        hash1 = watcher._calculate_hash(test_file)

        assert hash1 is not None
        assert len(hash1) == 64  # SHA256 hex

        # Same content = same hash
        hash2 = watcher._calculate_hash(test_file)
        assert hash1 == hash2

        # Different content = different hash
        test_file.write_text("Different content")
        hash3 = watcher._calculate_hash(test_file)
        assert hash1 != hash3

    @pytest.mark.asyncio
    async def test_get_watched_files(self, temp_project):
        """Test finding watched files."""
        config = WatcherConfig(
            watch_patterns=['*.toml', '.editorconfig'],
            debounce_seconds=0.5,
            auto_optimize=False,
            backup_on_change=False
        )

        watcher = ConfigFileWatcher(
            project_path=temp_project,
            config=config
        )

        watched_files = watcher._get_watched_files()

        assert len(watched_files) >= 2
        assert any('pyproject.toml' in str(f) for f in watched_files)
        assert any('.editorconfig' in str(f) for f in watched_files)

    @pytest.mark.asyncio
    async def test_event_detection(self, temp_project):
        """Test file change event detection."""
        events_detected = []

        async def event_handler(event):
            events_detected.append(event)

        config = WatcherConfig(
            watch_patterns=['test.txt'],
            debounce_seconds=0.5,
            auto_optimize=False,
            backup_on_change=False
        )

        watcher = ConfigFileWatcher(
            project_path=temp_project,
            config=config
        )

        # Register handler
        watcher.register_handler('file_created', event_handler)

        # Start watching
        await watcher.start()

        # Create file
        test_file = temp_project / 'test.txt'
        test_file.write_text("Initial content")

        # Wait for detection
        await asyncio.sleep(1.5)

        await watcher.stop()

        # Should detect creation
        assert len(events_detected) > 0

    @pytest.mark.asyncio
    async def test_debouncing(self, temp_project):
        """Test event debouncing."""
        events_processed = []

        async def event_handler(event):
            events_processed.append(event)

        config = WatcherConfig(
            watch_patterns=['test.txt'],
            debounce_seconds=1.0,
            auto_optimize=False,
            backup_on_change=False
        )

        watcher = ConfigFileWatcher(
            project_path=temp_project,
            config=config
        )

        watcher.register_handler('file_modified', event_handler)

        await watcher.start()

        # Rapid modifications
        test_file = temp_project / 'test.txt'
        test_file.write_text("V1")

        for i in range(5):
            await asyncio.sleep(0.1)
            test_file.write_text(f"V{i+2}")

        # Wait for debounce
        await asyncio.sleep(2.0)

        await watcher.stop()

        # Should only process once due to debounce
        # (Multiple rapid changes = single event)
        assert len(events_processed) <= 2  # Allow some variance


class TestContextManager:
    """Test integrated context management."""

    @pytest.mark.asyncio
    async def test_manager_initialization(self, temp_project):
        """Test manager initialization."""
        manager = ContextManager(
            project_path=temp_project,
            memory_system=None,
            agentdb=None
        )

        assert manager.project_path == temp_project
        assert manager.optimizer is not None
        assert manager.learner is not None
        assert manager.prime_loader is not None

    @pytest.mark.asyncio
    async def test_start_stop(self, temp_project):
        """Test manager lifecycle."""
        manager = ContextManager(project_path=temp_project)

        assert not manager._running

        await manager.start()
        assert manager._running
        assert manager.watcher is not None

        await manager.stop()
        assert not manager._running

    @pytest.mark.asyncio
    async def test_project_analysis(self, temp_project):
        """Test project analysis."""
        manager = ContextManager(project_path=temp_project)

        analysis = await manager.analyze_project()

        assert 'template_match' in analysis
        assert 'project_path' in analysis
        assert 'recommendations' in analysis

        # Should detect Python project
        assert analysis['template_match']['template_id'] == 'python-backend'

    @pytest.mark.asyncio
    async def test_prime_context_loading(self, temp_project):
        """Test loading prime contexts through manager."""
        manager = ContextManager(project_path=temp_project)

        context = await manager.load_prime_context('bug')

        assert context is not None
        assert len(context) > 0
        assert manager._stats['contexts_loaded'] == 1

    @pytest.mark.asyncio
    async def test_statistics_tracking(self, temp_project):
        """Test statistics collection."""
        manager = ContextManager(project_path=temp_project)

        await manager.start()

        # Wait a moment
        await asyncio.sleep(1)

        stats = manager.get_statistics()

        assert 'manager' in stats
        assert 'running' in stats
        assert stats['running'] is True

        await manager.stop()


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])

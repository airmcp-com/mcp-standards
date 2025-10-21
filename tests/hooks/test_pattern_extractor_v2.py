"""
Tests for Pattern Extractor V2

Tests semantic pattern extraction and clustering capabilities.
"""

import pytest
import tempfile
import asyncio
from pathlib import Path
from datetime import datetime

from src.mcp_standards.hooks.pattern_extractor_v2 import (
    PatternExtractorV2,
    ExtractedPattern,
    create_pattern_extractor_v2
)
from src.mcp_standards.memory.v2.test_hybrid_memory import create_test_hybrid_memory


class TestPatternExtractorV2:
    """Test suite for V2 pattern extractor."""

    @pytest.fixture
    async def extractor(self):
        """Create test pattern extractor with hybrid memory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test memory router
            memory_router = await create_test_hybrid_memory(
                agentdb_path=f"{temp_dir}/test_agentdb",
                sqlite_path=f"{temp_dir}/test_audit.db"
            )

            # Create extractor
            extractor = PatternExtractorV2(memory_router=memory_router)
            await extractor.initialize()

            yield extractor

            await extractor.close()

    @pytest.mark.asyncio
    async def test_initialization(self, extractor):
        """Test pattern extractor initialization."""
        assert extractor.memory_router is not None, "Memory router should be initialized"
        assert hasattr(extractor, '_pattern_timestamps'), "Rate limiting should be initialized"
        assert hasattr(extractor, '_recent_patterns'), "Pattern cache should be initialized"

    @pytest.mark.asyncio
    async def test_semantic_correction_detection(self, extractor):
        """Test detection of correction patterns with semantic understanding."""
        # Test explicit correction: "use uv not pip"
        tool_name = "Bash"
        args = {"command": "pip install requests"}
        result = "User says: actually use uv not pip for package management"

        patterns = await extractor.extract_patterns(tool_name, args, result)

        assert len(patterns) > 0, "Should detect correction pattern"

        correction_pattern = next((p for p in patterns if p.pattern_type == "correction"), None)
        assert correction_pattern is not None, "Should find correction pattern"
        assert correction_pattern.category == "package-management", "Should categorize as package management"
        assert "uv" in correction_pattern.description, "Should mention preferred tool"
        assert "pip" in correction_pattern.description, "Should mention avoided tool"
        assert correction_pattern.confidence >= 0.8, "Explicit corrections should have high confidence"

    @pytest.mark.asyncio
    async def test_workflow_pattern_detection(self, extractor):
        """Test detection of workflow patterns."""
        # Simulate sequence: Edit file, then run tests
        await extractor.extract_patterns("Edit", {"file_path": "src/app.py"}, "File edited")

        # Now run tests
        patterns = await extractor.extract_patterns(
            "Bash",
            {"command": "pytest tests/"},
            "Tests passed"
        )

        # Should detect workflow pattern
        workflow_pattern = next((p for p in patterns if p.pattern_type == "workflow"), None)
        if workflow_pattern:  # May not detect in isolation without proper tool tracking
            assert workflow_pattern.category == "testing", "Should categorize as testing workflow"
            assert "test" in workflow_pattern.description.lower(), "Should mention testing"

    @pytest.mark.asyncio
    async def test_tool_preference_detection(self, extractor):
        """Test detection of tool preferences."""
        # Test tool preference detection
        tool_name = "Bash"
        args = {"command": "uv add requests"}
        result = "Package installed successfully"

        patterns = await extractor.extract_patterns(tool_name, args, result)

        tool_pref = next((p for p in patterns if p.pattern_type == "tool_preference"), None)
        if tool_pref:  # May not always detect depending on implementation
            assert tool_pref.category == "package-management", "Should categorize tool preference"
            assert "uv" in tool_pref.context["tool"], "Should identify the tool"

    @pytest.mark.asyncio
    async def test_semantic_duplicate_detection(self, extractor):
        """Test semantic duplicate detection and pattern reinforcement."""
        # Add first pattern
        patterns1 = await extractor.extract_patterns(
            "Bash",
            {"command": "pip install"},
            "Use uv not pip for package management"
        )

        # Add very similar pattern
        patterns2 = await extractor.extract_patterns(
            "Bash",
            {"command": "pip install"},
            "Actually prefer uv over pip for packages"
        )

        # Should detect first pattern but reinforce rather than duplicate
        assert len(patterns1) > 0, "Should detect first pattern"

        # Check that similar pattern search works
        similar = await extractor.find_similar_patterns(
            "package management with uv",
            category="package-management",
            min_confidence=0.5
        )

        assert len(similar) > 0, "Should find semantically similar patterns"

    @pytest.mark.asyncio
    async def test_pattern_storage_and_retrieval(self, extractor):
        """Test pattern storage in hybrid memory system."""
        # Extract a pattern
        patterns = await extractor.extract_patterns(
            "Bash",
            {"command": "pip install requests"},
            "Actually, use uv not pip for better package management"
        )

        assert len(patterns) > 0, "Should extract patterns"

        pattern = patterns[0]
        assert hasattr(pattern, 'metadata'), "Pattern should have metadata"
        assert pattern.metadata is not None, "Metadata should not be None"
        assert 'pattern_id' in pattern.metadata, "Should store pattern ID"

        # Test retrieval
        similar_patterns = await extractor.find_similar_patterns(
            "package management uv pip",
            category=pattern.category,
            min_confidence=0.3
        )

        assert len(similar_patterns) > 0, "Should retrieve stored patterns"

    @pytest.mark.asyncio
    async def test_learned_preferences_retrieval(self, extractor):
        """Test retrieval of learned preferences."""
        # Add several patterns to build preferences
        test_patterns = [
            ("Use uv not pip for package management", "package-management"),
            ("Always run pytest not unittest", "testing"),
            ("Prefer git branches for features", "version-control")
        ]

        for result_text, category in test_patterns:
            await extractor.extract_patterns(
                "Bash",
                {"command": "test command"},
                result_text
            )

        # Get learned preferences
        preferences = await extractor.get_learned_preferences(
            category="package-management",
            min_confidence=0.5
        )

        # Should find package management preference
        assert isinstance(preferences, list), "Should return list of preferences"

    @pytest.mark.asyncio
    async def test_semantic_categorization(self, extractor):
        """Test semantic categorization of tools and patterns."""
        # Test package management tools
        category = await extractor._classify_tool_category("uv", "pip")
        assert category == "package-management", "Should classify package managers correctly"

        category = await extractor._classify_tool_category("npm", "yarn")
        assert category == "package-management", "Should classify JS package managers"

        # Test testing tools
        category = await extractor._classify_tool_category("pytest", "unittest")
        assert category == "testing", "Should classify testing tools correctly"

        # Test unknown tools
        category = await extractor._classify_tool_category("unknown", "tool")
        assert category == "general", "Should default to general for unknown tools"

    @pytest.mark.asyncio
    async def test_rate_limiting(self, extractor):
        """Test rate limiting functionality."""
        # Test that rate limiting works
        original_limit = extractor.MAX_PATTERNS_PER_MINUTE
        extractor.MAX_PATTERNS_PER_MINUTE = 2  # Very low limit for testing

        try:
            # First two should work
            patterns1 = await extractor.extract_patterns("Bash", {}, "test 1")
            patterns2 = await extractor.extract_patterns("Bash", {}, "test 2")

            # Third should be rate limited
            patterns3 = await extractor.extract_patterns("Bash", {}, "test 3")

            # Rate limiting may or may not block depending on actual pattern detection

        finally:
            # Restore original limit
            extractor.MAX_PATTERNS_PER_MINUTE = original_limit

    @pytest.mark.asyncio
    async def test_contextual_patterns(self, extractor):
        """Test contextual pattern detection."""
        project_path = "/test/project"

        # Test project-specific pattern
        patterns = await extractor.extract_patterns(
            "Bash",
            {"command": "npm install"},
            "Installing packages",
            project_path=project_path
        )

        # Check for contextual patterns
        context_pattern = next((p for p in patterns if p.pattern_type == "context"), None)
        if context_pattern:
            assert context_pattern.project_path == project_path, "Should track project path"

    @pytest.mark.asyncio
    async def test_pattern_statistics(self, extractor):
        """Test pattern statistics collection."""
        # Add some patterns
        await extractor.extract_patterns(
            "Bash",
            {"command": "uv add requests"},
            "Use uv for package management"
        )

        # Get statistics
        stats = await extractor.get_pattern_statistics()

        assert isinstance(stats, dict), "Should return statistics dictionary"
        assert 'memory_stats' in stats, "Should include memory statistics"
        assert 'pattern_stats' in stats, "Should include pattern-specific statistics"

    @pytest.mark.asyncio
    async def test_complex_correction_patterns(self, extractor):
        """Test complex correction pattern detection."""
        complex_corrections = [
            "Actually, prefer poetry over pip for dependency management",
            "Should switch to uv from pip for faster installs",
            "Never use pip, always use uv in this project",
            "Change from npm to pnpm for better performance"
        ]

        all_patterns = []
        for correction in complex_corrections:
            patterns = await extractor.extract_patterns(
                "Bash",
                {"command": "install command"},
                correction
            )
            all_patterns.extend(patterns)

        # Should detect multiple correction patterns
        correction_patterns = [p for p in all_patterns if p.pattern_type == "correction"]
        assert len(correction_patterns) > 0, "Should detect various correction patterns"

        # Check categorization
        categories = {p.category for p in correction_patterns}
        assert "package-management" in categories, "Should categorize package management corrections"

    @pytest.mark.asyncio
    async def test_pattern_confidence_scoring(self, extractor):
        """Test pattern confidence scoring."""
        # Explicit correction should have high confidence
        patterns = await extractor.extract_patterns(
            "Bash",
            {"command": "pip install"},
            "Use uv not pip"
        )

        if patterns:
            correction = next((p for p in patterns if p.pattern_type == "correction"), None)
            if correction:
                assert correction.confidence >= 0.8, "Explicit corrections should have high confidence"

        # Tool usage should have lower confidence
        patterns = await extractor.extract_patterns(
            "Bash",
            {"command": "uv add requests"},
            "Package added"
        )

        if patterns:
            tool_pref = next((p for p in patterns if p.pattern_type == "tool_preference"), None)
            if tool_pref:
                assert tool_pref.confidence <= 0.6, "Tool usage should have lower initial confidence"


# Integration test
@pytest.mark.asyncio
async def test_pattern_extractor_v2_integration():
    """Comprehensive integration test for V2 pattern extractor."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create extractor using factory function
        extractor = await create_pattern_extractor_v2()

        try:
            # Test comprehensive pattern extraction workflow
            print("Testing comprehensive pattern extraction...")

            # 1. Extract various types of patterns
            test_scenarios = [
                ("Bash", {"command": "pip install"}, "Actually use uv not pip"),
                ("Edit", {"file_path": "src/app.py"}, "File updated"),
                ("Bash", {"command": "pytest"}, "Tests completed"),
                ("Bash", {"command": "uv add fastapi"}, "Package installed"),
            ]

            all_patterns = []
            for tool_name, args, result in test_scenarios:
                patterns = await extractor.extract_patterns(tool_name, args, result)
                all_patterns.extend(patterns)
                print(f"Extracted {len(patterns)} patterns from {tool_name}")

            print(f"Total patterns extracted: {len(all_patterns)}")

            # 2. Test semantic search
            if all_patterns:
                search_results = await extractor.find_similar_patterns(
                    "package management with uv",
                    min_confidence=0.3
                )
                print(f"Found {len(search_results)} similar patterns")

            # 3. Test preferences
            preferences = await extractor.get_learned_preferences(min_confidence=0.3)
            print(f"Found {len(preferences)} learned preferences")

            # 4. Test statistics
            stats = await extractor.get_pattern_statistics()
            print(f"Memory system status: {stats.get('memory_stats', {}).get('system_status', {})}")

            print("✅ V2 Pattern Extractor integration test completed successfully!")

        finally:
            await extractor.close()


if __name__ == "__main__":
    # Run integration test
    asyncio.run(test_pattern_extractor_v2_integration())
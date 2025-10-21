"""Claude Code Hooks Integration for Automatic Learning

This module provides intelligent hooks that capture tool executions
and automatically extract learning patterns to improve Claude Code over time.

V2 System Features:
- Semantic pattern detection with AgentDB vector search
- Hybrid memory system (AgentDB + SQLite)
- Enhanced pattern deduplication and confidence scoring
- Automatic fallback to V1 if AgentDB unavailable
"""

# V2 System (default)
from .capture_hook_v2 import capture_tool_execution_sync as capture_tool_execution_v2
from .capture_hook_v2 import HookCaptureSystemV2
from .pattern_extractor_v2 import PatternExtractorV2, ExtractedPattern

# V1 System (fallback)
from .capture_hook import capture_tool_execution as capture_tool_execution_v1
from .capture_hook import HookCaptureSystem
from .pattern_extractor import PatternExtractor

# Common components
from .significance_scorer import SignificanceScorer

# Default to V2 system
capture_tool_execution = capture_tool_execution_v2

__all__ = [
    # V2 (default)
    'capture_tool_execution',
    'capture_tool_execution_v2',
    'HookCaptureSystemV2',
    'PatternExtractorV2',
    'ExtractedPattern',

    # V1 (fallback)
    'capture_tool_execution_v1',
    'HookCaptureSystem',
    'PatternExtractor',

    # Common
    'SignificanceScorer',
]

# Version info
__version__ = "2.0.0"
__system_default__ = "v2"

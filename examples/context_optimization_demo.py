"""
Context Optimization System - Practical Examples

Demonstrates the intelligent CLAUDE.md optimization system with:
1. Automatic event-driven updates
2. Token reduction (23K → 5K)
3. Learning from manual edits
4. Dynamic context loading
"""

import asyncio
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from intelligence.context import ContextManager, setup_context_manager
from intelligence.memory import PersistentMemory


async def demo_basic_setup():
    """Demo 1: Basic setup and automatic optimization."""
    print("=" * 60)
    print("Demo 1: Basic Setup and Automatic Optimization")
    print("=" * 60)

    # Initialize memory system
    memory = PersistentMemory(
        db_path=".claude/demo_memory.db",
        embedding_model="all-MiniLM-L6-v2"
    )

    # Create context manager
    manager = ContextManager(
        project_path=Path.cwd(),
        memory_system=memory
    )

    # Start watching (don't await - runs in background)
    await manager.start()

    print("\n✅ Context manager started")
    print(f"📁 Watching: {manager.project_path}")
    print(f"👀 Watching {len(manager.watcher._file_hashes)} files")

    # Get project analysis
    print("\n" + "-" * 60)
    print("Project Analysis:")
    print("-" * 60)

    analysis = await manager.analyze_project()

    print(f"Project Type: {analysis['template_match']['project_type']}")
    print(f"Template Confidence: {analysis['template_match']['confidence']:.0%}")
    print(f"Detected Markers: {', '.join(analysis['template_match']['detected_patterns'])}")

    if analysis['current_metrics']:
        print(f"\nCurrent CLAUDE.md:")
        print(f"  Token Count: {analysis['current_metrics']['token_count']}")
        print(f"  Section Count: {analysis['current_metrics']['section_count']}")
        print(f"  Optimization Potential: {analysis['current_metrics']['optimization_potential']} tokens")

    print(f"\nLearned Patterns: {analysis['learned_patterns']}")
    print(f"High-Confidence Patterns: {analysis['high_confidence_patterns']}")
    print(f"Available Contexts: {analysis['available_contexts']}")

    if analysis['recommendations']:
        print("\n📋 Recommendations:")
        for rec in analysis['recommendations']:
            print(f"  [{rec['priority'].upper()}] {rec['message']}")
            print(f"    → {rec['action']}")

    # Clean up
    await manager.stop()
    print("\n✅ Manager stopped")


async def demo_manual_optimization():
    """Demo 2: Manual optimization with metrics."""
    print("\n" + "=" * 60)
    print("Demo 2: Manual Optimization")
    print("=" * 60)

    # Quick setup
    manager = await setup_context_manager(
        project_path=str(Path.cwd()),
        auto_start=False  # Don't start watcher
    )

    # Check if CLAUDE.md exists
    claudemd_path = Path.cwd() / 'CLAUDE.md'
    if not claudemd_path.exists():
        print("\n❌ No CLAUDE.md found")
        print("Creating example CLAUDE.md...")

        # Create example file
        example_content = """# Claude Code Configuration

## Core Principles
- Evidence > Assumptions
- Code > Documentation
- Efficiency > Verbosity

## Tool Preferences
- Use pytest for testing
- Use ruff for linting
- Use mypy for type checking

## Workflow Patterns
### Test-Driven Development
1. Write test first
2. Implement feature
3. Refactor

### Code Review
- Review before merge
- Check tests pass
- Verify documentation

## Quality Standards
- Code coverage >80%
- All tests must pass
- No linting errors
- Type hints required

## Example Code Patterns

```python
# Example: Proper error handling
def process_data(data: Dict[str, Any]) -> Result:
    try:
        validated = validate(data)
        return Result.success(validated)
    except ValidationError as e:
        return Result.error(str(e))
```

## Extended Documentation

This is a long section that could be moved to /prime contexts...
[Many more paragraphs of detailed documentation]
"""
        claudemd_path.write_text(example_content * 3)  # Make it large
        print(f"✅ Created example CLAUDE.md ({len(example_content * 3)} chars)")

    # Get initial metrics
    initial_content = claudemd_path.read_text()
    initial_tokens = manager.optimizer.estimate_tokens(initial_content)

    print(f"\n📊 Initial Metrics:")
    print(f"  Token Count: {initial_tokens}")
    print(f"  Target: {manager.optimizer.TOKEN_BUDGET['project']}")
    print(f"  Reduction Needed: {max(0, initial_tokens - manager.optimizer.TOKEN_BUDGET['project'])}")

    # Optimize
    print("\n⚙️  Optimizing...")
    metrics = await manager.optimize_claudemd()

    print(f"\n✅ Optimization Complete!")
    print(f"  Final Token Count: {metrics.token_count}")
    print(f"  Compression Ratio: {metrics.compression_ratio:.2f}x")
    print(f"  Sections: {metrics.section_count}")
    print(f"  Semantic Density: {metrics.semantic_density:.2f}")

    # Calculate savings
    savings = initial_tokens - metrics.token_count
    savings_percent = (savings / initial_tokens * 100) if initial_tokens > 0 else 0

    print(f"\n💰 Token Savings:")
    print(f"  Absolute: {savings} tokens")
    print(f"  Percentage: {savings_percent:.1f}%")


async def demo_prime_contexts():
    """Demo 3: Dynamic context loading."""
    print("\n" + "=" * 60)
    print("Demo 3: Dynamic Context Loading (/prime commands)")
    print("=" * 60)

    manager = await setup_context_manager(
        project_path=str(Path.cwd()),
        auto_start=False
    )

    # Show available contexts
    print("\n📚 Available Prime Contexts:")
    contexts = manager.list_available_contexts()

    for ctx in contexts:
        print(f"\n  {ctx['command']}")
        print(f"    Name: {ctx['name']}")
        print(f"    Description: {ctx['description']}")
        print(f"    Tokens: {ctx['tokens']}")
        if ctx['dependencies']:
            print(f"    Dependencies: {', '.join(ctx['dependencies'])}")

    # Load a context
    print("\n" + "-" * 60)
    print("Loading /prime-bug context...")
    print("-" * 60)

    bug_context = await manager.load_prime_context('bug')

    if bug_context:
        print(f"\n✅ Loaded bug context ({len(bug_context)} chars)")
        print("\n--- Context Preview ---")
        print(bug_context[:500] + "...")

    # Suggest contexts based on query
    print("\n" + "-" * 60)
    print("Context Suggestions for 'performance problem':")
    print("-" * 60)

    suggestions = await manager.suggest_contexts("performance problem")

    for ctx in suggestions:
        print(f"\n  📌 {ctx.display_name}")
        print(f"     Command: /prime-{ctx.context_id}")
        print(f"     {ctx.description}")
        print(f"     {ctx.token_estimate} tokens")


async def demo_learning_system():
    """Demo 4: Learning from manual edits."""
    print("\n" + "=" * 60)
    print("Demo 4: Learning from Manual Edits")
    print("=" * 60)

    manager = await setup_context_manager(
        project_path=str(Path.cwd()),
        auto_start=False
    )

    # Simulate manual edits
    print("\n📝 Simulating manual edit to CLAUDE.md...")

    previous_content = """# Claude Code Configuration

## Tool Preferences
- Use pip for package management
- Use unittest for testing
"""

    current_content = """# Claude Code Configuration

## Tool Preferences
- **Use uv for package management** (not pip)
- **Use pytest for testing** (not unittest)
- Always use ruff for linting
"""

    print("\nPrevious content:")
    print(previous_content)
    print("\nNew content:")
    print(current_content)

    # Analyze the diff
    print("\n⚙️  Analyzing diff...")
    analysis = await manager.learner.analyze_diff(
        previous_content=previous_content,
        current_content=current_content,
        project_path=str(Path.cwd())
    )

    print(f"\n✅ Analysis Complete!")
    print(f"  Additions: {analysis.additions_count}")
    print(f"  Deletions: {analysis.deletions_count}")
    print(f"  Patterns Detected: {len(analysis.patterns_detected)}")
    print(f"  Token Impact: {analysis.token_impact:+d}")

    if analysis.patterns_detected:
        print("\n📋 Learned Patterns:")
        for pattern in analysis.patterns_detected:
            print(f"\n  Type: {pattern.pattern_type}")
            print(f"  Content: {pattern.content[:100]}")
            print(f"  Confidence: {pattern.confidence:.0%}")
            print(f"  Contexts: {', '.join(pattern.contexts)}")

    if analysis.preferences_changed:
        print("\n🔧 Preference Changes:")
        for pref in analysis.preferences_changed:
            print(f"  - {pref['content']}")
            if 'preferred' in pref:
                print(f"    Preferred: {pref['preferred']}")
            if 'avoided' in pref:
                print(f"    Avoided: {pref['avoided']}")

    # Show how patterns would be auto-applied
    print("\n" + "-" * 60)
    print("Auto-Application Demo (after 2+ occurrences):")
    print("-" * 60)

    # Simulate second occurrence
    await manager.learner.analyze_diff(
        previous_content=current_content,
        current_content=current_content,  # Reinforcement
        project_path=str(Path.cwd())
    )

    # Get learned patterns
    patterns = await manager.learner.get_learned_patterns(
        min_confidence=0.7
    )

    print(f"\nLearned Patterns Database: {len(patterns)} patterns")

    for pattern in patterns[:5]:  # Show first 5
        print(f"\n  Pattern: {pattern.content[:80]}")
        print(f"  Type: {pattern.pattern_type}")
        print(f"  Frequency: {pattern.frequency}")
        print(f"  Confidence: {pattern.confidence:.0%}")
        print(f"  Auto-Apply: {'✅' if pattern.confidence >= 0.8 and pattern.frequency >= 2 else '❌'}")


async def demo_suggestions():
    """Demo 5: Getting improvement suggestions."""
    print("\n" + "=" * 60)
    print("Demo 5: Improvement Suggestions")
    print("=" * 60)

    manager = await setup_context_manager(
        project_path=str(Path.cwd()),
        auto_start=False
    )

    # Get suggestions
    suggestions = await manager.suggest_improvements()

    if not suggestions:
        print("\n✅ No suggestions - CLAUDE.md is optimized!")
    else:
        print(f"\n📋 Found {len(suggestions)} suggestions:")

        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n{i}. [{suggestion['priority'].upper()}] {suggestion['type']}")
            print(f"   {suggestion['suggestion']}")
            print(f"   Confidence: {suggestion['confidence']:.0%}")


async def demo_statistics():
    """Demo 6: System statistics and monitoring."""
    print("\n" + "=" * 60)
    print("Demo 6: System Statistics")
    print("=" * 60)

    manager = await setup_context_manager(
        project_path=str(Path.cwd()),
        auto_start=True
    )

    # Let it run for a moment
    await asyncio.sleep(3)

    # Get statistics
    stats = manager.get_statistics()

    print("\n📊 Context Manager Statistics:")
    print(f"  Running: {stats['running']}")
    print(f"  Optimizations: {stats['manager']['optimizations']}")
    print(f"  Patterns Learned: {stats['manager']['patterns_learned']}")
    print(f"  Contexts Loaded: {stats['manager']['contexts_loaded']}")
    print(f"  Auto Applications: {stats['manager']['auto_applications']}")

    if 'uptime_seconds' in stats:
        print(f"  Uptime: {stats['uptime_seconds']:.1f}s")

    if 'watcher' in stats:
        print("\n📁 File Watcher:")
        print(f"  Events Detected: {stats['watcher']['events_detected']}")
        print(f"  Events Processed: {stats['watcher']['events_processed']}")
        print(f"  Files Tracked: {stats['watcher']['files_tracked']}")
        print(f"  Pending Events: {stats['watcher']['pending_events']}")
        print(f"  Errors: {stats['watcher']['errors']}")

    print("\n🧠 Learning System:")
    print(f"  Diffs Analyzed: {stats['learner']['diffs_analyzed']}")
    print(f"  Patterns in Database: {stats['learner']['patterns_in_database']}")
    print(f"  High-Confidence Patterns: {stats['learner']['high_confidence_patterns']}")

    print("\n📚 Prime Context Loader:")
    print(f"  Contexts Loaded: {stats['prime_loader']['contexts_loaded']}")
    print(f"  Cache Hits: {stats['prime_loader']['cache_hits']}")
    print(f"  Cache Misses: {stats['prime_loader']['cache_misses']}")

    await manager.stop()


async def main():
    """Run all demos."""
    print("\n" + "🚀 " * 30)
    print("Context Optimization System - Demo Suite")
    print("🚀 " * 30)

    try:
        # Run demos
        await demo_basic_setup()
        await demo_manual_optimization()
        await demo_prime_contexts()
        await demo_learning_system()
        await demo_suggestions()
        await demo_statistics()

        print("\n" + "=" * 60)
        print("✅ All demos completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

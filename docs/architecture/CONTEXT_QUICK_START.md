# Context Optimization System - Quick Start Guide

**Get started in 5 minutes with intelligent CLAUDE.md optimization**

---

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or with uv
uv pip install -r requirements.txt
```

**Dependencies**:
- `sentence-transformers>=2.2.0` (for embeddings)
- `faiss-cpu>=1.7.4` (for vector search)
- `numpy>=1.24.0`
- `networkx>=3.1`

---

## Quick Start (3 Commands)

### 1. Basic Setup

```python
from intelligence.context import setup_context_manager
from intelligence.memory import PersistentMemory

# Initialize memory
memory = PersistentMemory(db_path=".claude/memory.db")

# Setup and start
manager = await setup_context_manager(
    project_path="./",
    memory_system=memory,
    auto_start=True  # Start watching immediately
)

# That's it! System is now monitoring config files
```

### 2. Optimize CLAUDE.md

```python
# Manual optimization
metrics = await manager.optimize_claudemd()

print(f"Optimized: {metrics.token_count} tokens")
print(f"Compression: {metrics.compression_ratio:.2f}x")
```

### 3. Load Prime Context

```python
# Load debugging context
bug_context = await manager.load_prime_context('bug')

# Use in your prompt
prompt = f"""
{bug_context}

Debug this error: {error}
"""
```

---

## Common Use Cases

### Automatic Optimization on Config Changes

```python
# Start manager
manager = await setup_context_manager("./myproject", auto_start=True)

# Now edit any config file:
# - .editorconfig
# - pyproject.toml
# - package.json
# etc.

# CLAUDE.md will be automatically optimized within 2 seconds!
```

### Learn from Manual Edits

```python
# Just edit CLAUDE.md manually:
# Add: "- Use uv for package management (not pip)"

# System automatically:
# 1. Detects the edit
# 2. Learns the preference
# 3. Stores pattern with confidence score
# 4. Auto-applies to future optimizations (after 2+ occurrences)
```

### Token Reduction

```python
# Before optimization
current = Path("CLAUDE.md").read_text()
tokens_before = manager.optimizer.estimate_tokens(current)
# → 23,000 tokens

# Optimize
await manager.optimize_claudemd(target_tokens=5000)

# After optimization
optimized = Path("CLAUDE.md").read_text()
tokens_after = manager.optimizer.estimate_tokens(optimized)
# → 5,000 tokens (78% reduction!)
```

### Dynamic Context Loading

```python
# List available contexts
contexts = manager.list_available_contexts()
# → [bug, feature, refactor, test, docs, api, perf, security]

# Load specific context
bug_ctx = await manager.load_prime_context('bug')    # 1.8K tokens
feature_ctx = await manager.load_prime_context('feature')  # 2K tokens
perf_ctx = await manager.load_prime_context('perf')   # 1.8K tokens

# Total: Only load what you need!
```

---

## Configuration Options

### Watcher Configuration

```python
from intelligence.context import ConfigFileWatcher, WatcherConfig

config = WatcherConfig(
    watch_patterns=[
        '.editorconfig',
        'pyproject.toml',
        'package.json',
        # ... add more
    ],
    debounce_seconds=2.0,     # Wait 2s before processing
    auto_optimize=True,        # Auto-optimize on changes
    backup_on_change=True      # Create backups
)

watcher = ConfigFileWatcher(
    project_path=Path("./"),
    config=config
)
```

### Optimization Configuration

```python
# Custom token budgets
manager.optimizer.TOKEN_BUDGET = {
    'global': 3000,      # Global CLAUDE.md
    'project': 4000,     # Project CLAUDE.md (more space)
    'prime_context': 1500,  # Smaller contexts
    'total_budget': 8000    # Lower total
}

# Optimize with custom settings
metrics = await manager.optimize_claudemd(
    target_tokens=4000,
    preserve_sections=['Core Principles', 'Essential Rules']
)
```

### Learning Configuration

```python
# Auto-apply threshold
learner.auto_apply_confidence = 0.75  # Default: 0.8
learner.auto_apply_frequency = 3     # Default: 2

# Get patterns with custom filters
patterns = await manager.learner.get_learned_patterns(
    pattern_type='preference_correction',
    min_confidence=0.7,
    min_frequency=2
)
```

---

## Available Prime Contexts

| Command | Description | Tokens | Best For |
|---------|-------------|--------|----------|
| `/prime-bug` | Debugging workflows, error patterns | 1,800 | Bug fixing |
| `/prime-feature` | Design patterns, implementation | 2,000 | New features |
| `/prime-refactor` | Code quality, refactoring | 1,700 | Code cleanup |
| `/prime-test` | Testing strategies, TDD | 1,600 | Writing tests |
| `/prime-docs` | Documentation standards | 1,500 | Writing docs |
| `/prime-api` | REST/GraphQL API design | 1,900 | API development |
| `/prime-perf` | Performance optimization | 1,800 | Speed issues |
| `/prime-security` | Security best practices | 2,100 | Security review |

**Total**: 8 contexts, ~15K tokens (load only what you need)

---

## Monitoring & Statistics

### Get System Status

```python
stats = manager.get_statistics()

print(f"Running: {stats['running']}")
print(f"Optimizations: {stats['manager']['optimizations']}")
print(f"Patterns Learned: {stats['manager']['patterns_learned']}")
print(f"Uptime: {stats['uptime_seconds']:.1f}s")
```

### Get Suggestions

```python
suggestions = await manager.suggest_improvements()

for suggestion in suggestions:
    print(f"[{suggestion['priority']}] {suggestion['suggestion']}")
    # Example output:
    # [high] CLAUDE.md can be reduced by ~15000 tokens
    # [high] 3 high-confidence patterns ready to apply
```

### Analyze Project

```python
analysis = await manager.analyze_project()

print(f"Project Type: {analysis['template_match']['project_type']}")
print(f"Confidence: {analysis['template_match']['confidence']:.0%}")
print(f"Current Tokens: {analysis['current_metrics']['token_count']}")
print(f"Learned Patterns: {analysis['learned_patterns']}")

for rec in analysis['recommendations']:
    print(f"[{rec['priority']}] {rec['message']}")
```

---

## Advanced Features

### Export/Import Learned Patterns

```python
# Export patterns
await manager.export_learned_patterns(Path("patterns.json"))

# Share with team or import to another project
await manager.import_learned_patterns(Path("patterns.json"))
```

### Custom Event Handlers

```python
async def my_handler(event):
    print(f"File changed: {event.file_path}")
    # Custom logic here

# Register handler
manager.watcher.register_handler('file_modified', my_handler)
```

### Force Optimization

```python
# Bypass debounce, optimize immediately
await manager.force_optimization()
```

### Context Suggestions

```python
# Get context suggestions based on task
suggestions = await manager.suggest_contexts("fixing performance bug")
# → Suggests: [perf, bug]

for ctx in suggestions:
    print(f"/prime-{ctx.context_id}: {ctx.description}")
```

---

## Best Practices

### 1. Start with Auto Mode

```python
# Let the system learn from your workflow
manager = await setup_context_manager(
    project_path="./",
    auto_start=True  # Watch and learn
)

# Edit config files normally
# System learns your preferences automatically
```

### 2. Manual Edits for Learning

**Do this:**
```markdown
## Tool Preferences
- Use uv for package management (not pip)
- Use pytest for testing (not unittest)
```

The system learns:
- Preference: `uv` over `pip`
- Preference: `pytest` over `unittest`
- Pattern type: `tool_preference`
- Confidence: 80% (first correction)

After 2nd occurrence → Auto-applies to all optimizations!

### 3. Progressive Disclosure

**Instead of:**
```markdown
# Large CLAUDE.md with everything (23K tokens)
## Debugging (5K tokens of detailed workflows)
## Feature Development (4K tokens of patterns)
## Testing (3K tokens of strategies)
...
```

**Do this:**
```markdown
# Minimal CLAUDE.md (5K tokens)
## Core Principles
## Essential Rules

## Extended Context Available
- /prime-bug: Debugging workflows
- /prime-feature: Feature development
- /prime-test: Testing strategies

# Load on-demand when needed!
```

### 4. Regular Analysis

```python
# Weekly analysis
analysis = await manager.analyze_project()

if analysis['current_metrics']['optimization_potential'] > 5000:
    await manager.optimize_claudemd()

if analysis['high_confidence_patterns'] > 3:
    # Apply learned patterns
    await manager.optimize_claudemd()
```

---

## Troubleshooting

### Issue: Optimization not triggering

**Solution**: Check watcher is running
```python
stats = manager.get_statistics()
print(stats['running'])  # Should be True
print(stats['watcher']['files_tracked'])  # Should be >0
```

### Issue: Patterns not learning

**Solution**: Ensure edits are significant
```python
# System learns from these:
"Use X (not Y)"  ✅
"Always use X"   ✅
"Never use Y"    ✅

# But not from:
"Maybe consider X"  ❌ (too vague)
```

### Issue: Token count still high

**Solution**: Check section preservation
```python
# Don't preserve too many sections
await manager.optimize_claudemd(
    preserve_sections=['Core Principles']  # Minimal
)

# Instead of:
preserve_sections=[
    'Core Principles',
    'Tool Preferences',
    'Workflow Patterns',
    'Quality Standards',
    # ... too many!
]
```

### Issue: Context not loading

**Solution**: Check context ID
```python
# Valid IDs
contexts = manager.list_available_contexts()
print([c['id'] for c in contexts])
# → ['bug', 'feature', 'refactor', 'test', 'docs', 'api', 'perf', 'security']

# Use exact ID
await manager.load_prime_context('bug')  # ✅
await manager.load_prime_context('debugging')  # ❌ Wrong ID
```

---

## Performance Tips

### 1. Memory System

```python
# Use memory for caching
memory = PersistentMemory(
    db_path=".claude/memory.db",
    enable_faiss=True  # Fast vector search
)

# Contexts cached for 1 hour
# Patterns persisted indefinitely
```

### 2. Debounce Configuration

```python
# Rapid edits → longer debounce
config = WatcherConfig(
    debounce_seconds=5.0  # Wait 5s for quiet period
)

# Single edits → shorter debounce
config = WatcherConfig(
    debounce_seconds=1.0  # Quick response
)
```

### 3. Batch Operations

```python
# Optimize multiple files
for project in projects:
    manager = await setup_context_manager(project)
    await manager.optimize_claudemd()
    await manager.stop()
```

---

## Integration Examples

### With Existing ClaudeMdManager

```python
from mcp_standards.intelligence import ClaudeMdManager
from intelligence.context import ContextManager

# Extend existing manager
class EnhancedManager(ClaudeMdManager):
    def __init__(self, db_path):
        super().__init__(db_path)
        self.context_mgr = ContextManager(Path.cwd())

    async def update_file(self, path):
        # New optimization first
        await self.context_mgr.optimize_claudemd()

        # Then old logic
        return super().update_claudemd_file(path)
```

### With MCP Server

```python
# In your MCP server
from intelligence.context import ContextManager

class MyMCPServer:
    def __init__(self):
        self.context_mgr = ContextManager(Path.cwd())

    async def handle_optimize_request(self):
        metrics = await self.context_mgr.optimize_claudemd()
        return {"tokens": metrics.token_count}

    async def handle_prime_request(self, context_id):
        context = await self.context_mgr.load_prime_context(context_id)
        return {"content": context}
```

---

## Next Steps

1. **Run the demo**: `python examples/context_optimization_demo.py`
2. **Optimize your CLAUDE.md**: See immediate 70-80% token reduction
3. **Enable auto-watch**: Let system learn from your edits
4. **Use /prime contexts**: Load task-specific context on-demand
5. **Monitor statistics**: Track optimization impact

**Full Documentation**: See [CONTEXT_OPTIMIZATION_SYSTEM.md](./CONTEXT_OPTIMIZATION_SYSTEM.md)

---

## Support

- **Issues**: [GitHub Issues](https://github.com/mattstrautmann/research-mcp/issues)
- **Documentation**: `docs/architecture/`
- **Examples**: `examples/context_optimization_demo.py`

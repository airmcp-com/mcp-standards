# Hooks Implementation Plan

**Version**: 2.0.0
**Status**: Design Phase
**Last Updated**: 2025-10-20

---

## Executive Summary

A comprehensive hooks system leveraging Claude Code's native PostToolUse/PreToolUse hooks to enable automatic memory management, pattern learning, and intelligent configuration updates. Designed for zero-impact performance (<5ms overhead) with intelligent significance filtering.

### Key Capabilities

- **5-Layer Pattern Detection**: Explicit, Implicit, Violations, Behavioral, Semantic
- **Automatic Learning**: Confidence-based preference promotion (3+ occurrences)
- **Skills Auto-Generation**: Dynamic skills file creation from learned patterns
- **CLAUDE.md Management**: Intelligent config updates with smart merging
- **Performance Optimized**: Async processing, significance filtering, <5ms impact
- **Error Resilient**: Always exit 0, fallback mode, automatic disable on failures

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                     Claude Code/Desktop                       │
│                    (Execution Layer)                          │
└─────────────────────┬────────────────────────────────────────┘
                      │
                      │ Native Hook Events
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │PreToolUse│  │PostToolUse│ │SessionEnd│
  │  Hook    │  │   Hook    │ │   Hook   │
  └────┬─────┘  └────┬──────┘ └────┬─────┘
       │             │              │
       │             │              │
       └─────────────┼──────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   Hook Manager        │
         │   capture_hook.py     │
         │   • Event routing     │
         │   • Error handling    │
         │   • Timeout (5s)      │
         └──────────┬────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│Significance  │ │Pattern       │ │Context       │
│Scorer        │ │Extractor     │ │Builder       │
│              │ │              │ │              │
│Multi-factor  │ │5-layer       │ │Session       │
│scoring       │ │detection     │ │tracking      │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       │                │                │
       └────────────────┼────────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │ Intelligence    │
              │ Layer           │
              │                 │
              │ • Learning      │
              │ • Validation    │
              │ • Agent Track   │
              │ • Temporal      │
              └────────┬────────┘
                       │
                       ▼
         ┌─────────────────────────┐
         │  Storage Layer          │
         │  • SQLite (structured)  │
         │  • AgentDB (vectors)    │
         └─────────────────────────┘
                       │
                       ▼
         ┌─────────────────────────┐
         │  Auto-Update Layer      │
         │  • Skills files         │
         │  • CLAUDE.md            │
         │  • Config sync          │
         └─────────────────────────┘
```

---

## Hook Event Specifications

### 1. PreToolUse Hook

**Trigger**: Before tool execution
**Purpose**: Preparation, validation, resource allocation

```json
{
  "event": "PreToolUse",
  "timestamp": 1729485234567,
  "tool": {
    "name": "Read",
    "arguments": {
      "file_path": "/path/to/file.py"
    }
  },
  "context": {
    "session_id": "sess-1729485234567",
    "project_path": "/Users/user/project",
    "user_message": "Review this file for bugs",
    "conversation_history": []
  }
}
```

**Hook Actions**:

```python
async def pre_tool_use_hook(event: dict) -> dict:
    """
    PreToolUse hook implementation

    Returns:
        dict: Modifications or metadata to inject
    """
    # 1. Validate tool arguments
    if not validate_tool_args(event['tool']):
        return {'error': 'Invalid arguments', 'skip': True}

    # 2. Check if learned preferences apply
    preferences = await load_preferences(event['tool']['name'])
    if preferences:
        event['tool']['arguments'] = apply_preferences(
            event['tool']['arguments'],
            preferences
        )

    # 3. Prepare context
    context = await build_context(event)

    # 4. Log preparation
    await log_event('pre_tool_use', event, context)

    return {'modified_args': event['tool']['arguments'], 'context': context}
```

**Use Cases**:
- Auto-apply learned preferences (e.g., "use uv not pip")
- Validate command safety
- Prepare resources (e.g., create temp directories)
- Load relevant context from memory

---

### 2. PostToolUse Hook

**Trigger**: After tool execution
**Purpose**: Capture, learn, update

```json
{
  "event": "PostToolUse",
  "timestamp": 1729485235789,
  "tool": {
    "name": "Bash",
    "arguments": {
      "command": "uv pip install requests",
      "description": "Install Python package"
    }
  },
  "result": {
    "success": true,
    "output": "Successfully installed requests-2.31.0",
    "execution_time_ms": 1234
  },
  "context": {
    "session_id": "sess-1729485234567",
    "project_path": "/Users/user/project",
    "user_feedback": null,
    "correction_detected": false
  }
}
```

**Hook Actions**:

```python
async def post_tool_use_hook(event: dict) -> None:
    """
    PostToolUse hook implementation

    Main entry point for automatic learning
    """
    try:
        # 1. Significance scoring (0.0-1.0)
        significance = await score_significance(event)

        if significance < 0.3:
            return  # Skip insignificant events

        # 2. Extract patterns (5-layer detection)
        patterns = await extract_patterns(event, significance)

        # 3. Store in database
        await store_execution(event, significance, patterns)

        # 4. Update learning models
        if significance >= 0.6:
            await update_learning(patterns)

        # 5. Auto-update configs if high confidence
        if patterns and patterns.confidence >= 0.9:
            await auto_update_configs(patterns)

        # 6. Notify MCP server (optional)
        if significance >= 0.7:
            await notify_mcp_server(event, patterns)

    except Exception as e:
        # Never fail - always exit 0
        log_error(f"Hook error: {e}")
        return
```

**Use Cases**:
- Capture significant tool executions
- Detect user corrections
- Learn workflow patterns
- Update CLAUDE.md automatically
- Track agent performance

---

### 3. SessionEnd Hook

**Trigger**: End of session
**Purpose**: Consolidation, summary, cleanup

```json
{
  "event": "SessionEnd",
  "timestamp": 1729489999999,
  "session": {
    "session_id": "sess-1729485234567",
    "duration_ms": 4765432,
    "tools_executed": 127,
    "corrections_detected": 3,
    "patterns_learned": 1,
    "project_path": "/Users/user/project"
  }
}
```

**Hook Actions**:

```python
async def session_end_hook(event: dict) -> None:
    """
    SessionEnd hook implementation

    Consolidate learning and update configs
    """
    # 1. Generate session summary
    summary = await generate_session_summary(event['session'])

    # 2. Consolidate learned patterns
    patterns = await consolidate_patterns(event['session']['session_id'])

    # 3. Promote high-confidence patterns
    for pattern in patterns:
        if pattern.confidence >= 0.9 and pattern.occurrence_count >= 3:
            await promote_to_preference(pattern)
            await update_claudemd(pattern)

    # 4. Generate skills files if new patterns
    if len(patterns) > 0:
        await generate_skills_files(patterns)

    # 5. Cleanup temporary data
    await cleanup_session(event['session']['session_id'])

    # 6. Export metrics
    await export_session_metrics(event['session'])
```

---

## Pattern Detection Layers

### Layer 1: Explicit Corrections (Highest Confidence)

**Detection**: User explicitly corrects Claude's output

```python
def detect_explicit_correction(event: dict) -> Optional[Pattern]:
    """
    Detect explicit user corrections

    Examples:
    - "Use • bullets not -"
    - "Use uv instead of pip"
    - "Always run tests after code changes"
    """
    user_message = event['context'].get('user_message', '')

    # Patterns indicating corrections
    correction_indicators = [
        r'use\s+(\w+)\s+(?:not|instead of)\s+(\w+)',
        r'(?:always|never)\s+(.+)',
        r'prefer\s+(\w+)\s+over\s+(\w+)',
        r'don\'?t\s+(.+)',
        r'(?:should|must|need to)\s+(.+)',
    ]

    for pattern in correction_indicators:
        match = re.search(pattern, user_message, re.IGNORECASE)
        if match:
            return Pattern(
                type='explicit_correction',
                confidence=0.95,
                content=user_message,
                extracted_rule=match.group(0),
                timestamp=event['timestamp']
            )

    return None
```

**Confidence**: 0.9-1.0

---

### Layer 2: Implicit Rejections (High Confidence)

**Detection**: User edits Claude's output within 2 minutes

```python
def detect_implicit_rejection(event: dict, history: list) -> Optional[Pattern]:
    """
    Detect implicit rejections via user edits

    Example:
    - Claude writes code with "pip install"
    - User edits to "uv pip install" within 2 minutes
    """
    if event['tool']['name'] != 'Edit':
        return None

    # Find recent tool execution on same file
    recent = find_recent_execution(
        file_path=event['tool']['arguments']['file_path'],
        window_ms=120000,  # 2 minutes
        history=history
    )

    if not recent:
        return None

    # Compare original vs edited
    original = recent['result']['content']
    edited = event['tool']['arguments']['new_string']

    # Extract differences
    diff = compute_diff(original, edited)

    if len(diff) > 0:
        return Pattern(
            type='implicit_rejection',
            confidence=0.85,
            content=f"Changed '{diff.old}' to '{diff.new}'",
            extracted_rule=f"Prefer '{diff.new}' over '{diff.old}'",
            timestamp=event['timestamp']
        )

    return None
```

**Confidence**: 0.8-0.9

---

### Layer 3: Rule Violations (Medium Confidence)

**Detection**: Compare execution vs existing CLAUDE.md rules

```python
async def detect_rule_violation(event: dict) -> Optional[Pattern]:
    """
    Detect violations of existing rules

    Example:
    - CLAUDE.md says "use uv for Python packages"
    - Claude executes "pip install requests"
    """
    # Load CLAUDE.md rules
    rules = await load_claudemd_rules(event['context']['project_path'])

    # Check if execution violates any rule
    for rule in rules:
        if rule.applies_to(event['tool']):
            if not rule.satisfied_by(event['tool']['arguments']):
                return Pattern(
                    type='rule_violation',
                    confidence=0.7,
                    content=f"Violated rule: {rule.description}",
                    extracted_rule=rule.description,
                    timestamp=event['timestamp'],
                    metadata={'rule_id': rule.id}
                )

    return None
```

**Confidence**: 0.6-0.8

---

### Layer 4: Behavioral Patterns (Medium Confidence)

**Detection**: Repeated sequences across sessions

```python
async def detect_behavioral_pattern(event: dict, history: list) -> Optional[Pattern]:
    """
    Detect behavioral patterns via repetition

    Example:
    - User always runs "npm run test" after editing code
    - Detected after 5+ occurrences
    """
    # Build sequence fingerprint
    sequence = build_sequence_fingerprint(event, history, window=5)

    # Check pattern frequency
    frequency = await query_pattern_frequency(sequence)

    if frequency.occurrence_count >= 5:
        return Pattern(
            type='behavioral_pattern',
            confidence=min(0.5 + (frequency.occurrence_count * 0.05), 0.8),
            content=f"Repeated sequence: {sequence.description}",
            extracted_rule=f"Auto-suggest: {sequence.next_action}",
            timestamp=event['timestamp'],
            metadata={'frequency': frequency.occurrence_count}
        )

    return None
```

**Confidence**: 0.5-0.8 (increases with repetition)

---

### Layer 5: Semantic Clustering (Lower Confidence)

**Detection**: Group semantically similar corrections via embeddings

```python
async def detect_semantic_cluster(event: dict) -> Optional[Pattern]:
    """
    Detect semantic clusters via vector similarity

    Example:
    - Multiple corrections about bullet formatting
    - Cluster: "formatting preferences for resumes"
    """
    # Compute embedding for event
    embedding = await compute_embedding(event['tool']['arguments'])

    # Search for similar patterns
    similar = await agentDB.retrieveWithReasoning(embedding, {
        domain: 'corrections',
        k: 10,
        minSimilarity: 0.85,
    })

    if len(similar.memories) >= 3:
        # Cluster detected
        cluster = await synthesize_cluster(similar.memories)

        return Pattern(
            type='semantic_cluster',
            confidence=0.6,
            content=f"Cluster: {cluster.theme}",
            extracted_rule=cluster.generalized_rule,
            timestamp=event['timestamp'],
            metadata={'cluster_size': len(similar.memories)}
        )

    return None
```

**Confidence**: 0.5-0.7

---

## Significance Scoring System

### Multi-Factor Scoring

```python
async def score_significance(event: dict) -> float:
    """
    Calculate significance score (0.0-1.0)

    Factors:
    1. Tool type (Write/Edit > Read)
    2. File importance (src/ > tests/ > docs/)
    3. Execution result (error > success)
    4. User feedback presence
    5. Correction indicators
    6. Project context
    """
    score = 0.0

    # 1. Tool type (0.0-0.3)
    tool_scores = {
        'Write': 0.3, 'Edit': 0.25, 'Bash': 0.2,
        'Read': 0.1, 'Grep': 0.05, 'Glob': 0.05
    }
    score += tool_scores.get(event['tool']['name'], 0.1)

    # 2. File importance (0.0-0.2)
    if 'file_path' in event['tool']['arguments']:
        path = event['tool']['arguments']['file_path']
        if '/src/' in path or '/lib/' in path:
            score += 0.2
        elif '/tests/' in path:
            score += 0.15
        elif '/docs/' in path:
            score += 0.1

    # 3. Execution result (0.0-0.2)
    if not event['result'].get('success', True):
        score += 0.2

    # 4. User feedback (0.0-0.2)
    if event['context'].get('user_feedback'):
        score += 0.2

    # 5. Correction indicators (0.0-0.3)
    if event['context'].get('correction_detected'):
        score += 0.3

    # 6. Project context (0.0-0.1)
    if await is_active_project(event['context']['project_path']):
        score += 0.1

    return min(score, 1.0)
```

### Thresholds

- `score < 0.3`: Skip (insignificant)
- `0.3 ≤ score < 0.6`: Store only
- `0.6 ≤ score < 0.8`: Store + Extract patterns
- `score ≥ 0.8`: Store + Extract + Suggest updates

---

## Skills Auto-Generation

### Skills File Structure

```markdown
---
name: "Learned Preference: Use UV Package Manager"
description: "Automatically learned from 3+ corrections. User prefers 'uv' over 'pip' for Python package management."
confidence: 0.95
learned_from: [episode-123, episode-456, episode-789]
category: "python-tooling"
---

# Use UV Package Manager

## What This Skill Does

Ensures Python package operations use `uv` instead of `pip` based on learned user preferences.

## When to Apply

- Installing Python packages
- Managing virtual environments
- Updating dependencies

## Correct Usage

```bash
# ✅ Preferred
uv pip install requests
uv pip install -r requirements.txt
uv venv .venv

# ❌ Avoid
pip install requests
pip install -r requirements.txt
python -m venv .venv
```

## Context

Learned from user corrections:
1. 2025-10-15: "Use uv instead of pip" (Episode #123)
2. 2025-10-17: "Always use uv for package management" (Episode #456)
3. 2025-10-18: Changed `pip install` to `uv pip install` (Episode #789)

## Confidence: 95%

Based on 3 explicit corrections with consistent pattern.

---

**Auto-generated by**: MCP Standards Learning System
**Last updated**: 2025-10-20
```

### Auto-Generation Logic

```python
async def generate_skills_file(pattern: Pattern) -> None:
    """
    Auto-generate skills file from learned pattern

    Triggers:
    - Confidence >= 0.9
    - Occurrence count >= 3
    - Pattern type: explicit_correction or implicit_rejection
    """
    if pattern.confidence < 0.9 or pattern.occurrence_count < 3:
        return

    # Load template
    template = load_template('skill_template.md')

    # Fill in details
    content = template.render(
        name=pattern.generate_skill_name(),
        description=pattern.description,
        confidence=pattern.confidence,
        learned_from=pattern.episode_ids,
        category=pattern.category,
        correct_usage=pattern.extract_correct_usage(),
        incorrect_usage=pattern.extract_incorrect_usage(),
        context=pattern.get_context_summary(),
        last_updated=datetime.now().isoformat()
    )

    # Write to .claude/skills/
    skill_path = f".claude/skills/learned-{pattern.id}/SKILL.md"
    await write_file(skill_path, content)

    # Notify user
    await notify(f"✨ Generated new skill: {pattern.generate_skill_name()}")
```

---

## CLAUDE.md Auto-Update

### Smart Merge Strategy

```python
async def update_claudemd(pattern: Pattern) -> None:
    """
    Intelligently update CLAUDE.md without conflicts

    Strategy:
    1. Detect CLAUDE.md hierarchy (global → parent → project)
    2. Choose appropriate file (project-specific vs global)
    3. Parse existing content (preserve structure)
    4. Insert new rule in correct section
    5. Create backup before writing
    6. Validate after update
    """
    # 1. Detect hierarchy
    claudemd_files = await find_claudemd_hierarchy(pattern.project_path)
    # Returns: [global, parent, project, nested]

    # 2. Choose file
    target_file = choose_claudemd_file(pattern, claudemd_files)

    # 3. Parse existing
    existing = await parse_claudemd(target_file)

    # 4. Determine section
    section = determine_section(pattern)
    # e.g., "Tool Preferences", "Workflow Rules", "Code Style"

    # 5. Insert rule
    new_rule = format_rule(pattern)
    updated = existing.insert_rule(section, new_rule)

    # 6. Backup
    await create_backup(target_file)

    # 7. Write
    await write_file(target_file, updated.to_markdown())

    # 8. Validate
    if not await validate_claudemd(target_file):
        await rollback_from_backup(target_file)
        raise ValidationError("CLAUDE.md validation failed")

    # 9. Notify
    await notify(f"✅ Updated {target_file} with new rule: {pattern.description}")
```

### Rule Formatting

```python
def format_rule(pattern: Pattern) -> str:
    """
    Format pattern as CLAUDE.md rule

    Example output:

    ### Python Package Management

    **Preference**: Use `uv` instead of `pip`

    **Reason**: User preference learned from 3 corrections

    **Examples**:
    ```bash
    # ✅ Correct
    uv pip install requests

    # ❌ Incorrect
    pip install requests
    ```

    **Confidence**: 95% (learned 2025-10-20)

    ---
    """
    return f"""
### {pattern.category.title()}

**Preference**: {pattern.extracted_rule}

**Reason**: {pattern.description}

**Examples**:
```{pattern.language or 'bash'}
# ✅ Correct
{pattern.correct_example}

# ❌ Incorrect
{pattern.incorrect_example}
```

**Confidence**: {int(pattern.confidence * 100)}% (learned {pattern.timestamp.date()})

---
"""
```

### File Selection Logic

```python
def choose_claudemd_file(pattern: Pattern, hierarchy: list) -> str:
    """
    Choose appropriate CLAUDE.md file

    Logic:
    - Project-specific pattern → project CLAUDE.md
    - Repeated across projects → parent/global CLAUDE.md
    - Unclear → ask user once
    """
    if pattern.project_specific:
        return hierarchy['project']

    # Check if pattern appears in other projects
    other_projects = await find_pattern_in_other_projects(pattern)

    if len(other_projects) >= 2:
        # Pattern is universal
        return hierarchy['global']
    elif len(other_projects) == 1:
        # Pattern in 2 projects → parent
        return hierarchy['parent'] or hierarchy['global']
    else:
        # Single project
        return hierarchy['project']
```

---

## Error Handling & Resilience

### Critical Requirements

1. **Always Exit 0**: Never fail Claude Code
2. **Async Processing**: Don't block execution
3. **Timeout**: 5 seconds max
4. **Fallback Mode**: Disable on repeated failures
5. **Logging**: All errors logged, never shown to user

### Implementation

```python
async def safe_hook_execution(hook_func, event: dict) -> dict:
    """
    Safe wrapper for all hook functions

    Guarantees:
    - Never raises exceptions to caller
    - Respects 5s timeout
    - Auto-disables on repeated failures
    - Always returns valid result
    """
    try:
        # 1. Check if hooks are enabled
        if not await is_hooks_enabled():
            return {'skipped': True, 'reason': 'hooks_disabled'}

        # 2. Execute with timeout
        result = await asyncio.wait_for(
            hook_func(event),
            timeout=5.0
        )

        # 3. Reset failure counter on success
        await reset_failure_count()

        return result

    except asyncio.TimeoutError:
        log_error("Hook timeout exceeded 5s")
        await increment_failure_count()
        return {'skipped': True, 'reason': 'timeout'}

    except Exception as e:
        log_error(f"Hook error: {e}")
        await increment_failure_count()

        # Auto-disable after 3 consecutive failures
        if await get_failure_count() >= 3:
            await disable_hooks()
            log_error("Hooks auto-disabled due to repeated failures")

        return {'skipped': True, 'reason': 'error'}
```

---

## Configuration

### Hooks Configuration File

**Location**: `~/.claude/hooks.json`

```json
{
  "version": "1.0.0",
  "enabled": true,
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "uv run --directory /path/to/mcp-standards python -m mcp_standards.hooks.capture_hook pre",
            "timeout": 5000,
            "async": true
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "uv run --directory /path/to/mcp-standards python -m mcp_standards.hooks.capture_hook post",
            "timeout": 5000,
            "async": true
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "uv run --directory /path/to/mcp-standards python -m mcp_standards.hooks.capture_hook session-end",
            "timeout": 10000,
            "async": true
          }
        ]
      }
    ]
  },
  "settings": {
    "min_significance": 0.3,
    "auto_update_claudemd": true,
    "auto_generate_skills": true,
    "notification_level": "important",
    "max_failures": 3
  }
}
```

### Environment Variables

```bash
# Enable/disable features
HOOKS_ENABLED=true
AUTO_LEARN=true
AUTO_UPDATE_CLAUDEMD=true
AUTO_GENERATE_SKILLS=true

# Performance tuning
SIGNIFICANCE_THRESHOLD=0.3
PATTERN_CONFIDENCE_THRESHOLD=0.9
BATCH_SIZE=100

# Paths
DB_PATH=.swarm/memory.db
AGENTDB_PATH=.agentdb/reasoningbank.db
SKILLS_DIR=.claude/skills
CLAUDEMD_PATH=CLAUDE.md
```

---

## Testing Strategy

### Unit Tests

```python
# test_hooks.py

async def test_significance_scoring():
    """Test significance scoring accuracy"""
    event = create_test_event(tool='Write', file_path='/src/main.py')
    score = await score_significance(event)
    assert 0.5 <= score <= 0.6  # Write to src/ should score high

async def test_explicit_correction_detection():
    """Test explicit correction detection"""
    event = create_test_event(
        user_message="Use uv instead of pip",
        tool='Bash',
        command='pip install requests'
    )
    pattern = await detect_explicit_correction(event)
    assert pattern is not None
    assert pattern.confidence >= 0.9
    assert 'uv' in pattern.extracted_rule

async def test_hooks_resilience():
    """Test hooks never fail Claude"""
    event = create_malformed_event()
    result = await safe_hook_execution(post_tool_use_hook, event)
    assert result['skipped'] == True
    # Should never raise exception
```

### Integration Tests

```python
# test_integration.py

async def test_full_learning_workflow():
    """Test end-to-end learning workflow"""
    # 1. Execute tool
    event1 = simulate_tool_execution('pip install requests')
    await post_tool_use_hook(event1)

    # 2. User corrects
    event2 = simulate_user_correction("Use uv instead of pip")
    await post_tool_use_hook(event2)

    # 3. Repeat correction
    event3 = simulate_tool_execution('pip install numpy')
    event4 = simulate_user_correction("Use uv instead of pip")
    await post_tool_use_hook(event3)
    await post_tool_use_hook(event4)

    # 4. Third correction triggers learning
    event5 = simulate_tool_execution('pip install pandas')
    event6 = simulate_user_correction("Always use uv")
    await post_tool_use_hook(event5)
    await post_tool_use_hook(event6)

    # 5. Verify pattern learned
    patterns = await get_learned_patterns()
    assert len(patterns) == 1
    assert patterns[0].confidence >= 0.9

    # 6. Verify CLAUDE.md updated
    claudemd = await read_file('CLAUDE.md')
    assert 'uv' in claudemd

    # 7. Verify skills file generated
    assert await file_exists('.claude/skills/learned-uv-preference/SKILL.md')
```

---

## Performance Benchmarks

### Expected Overhead

| Operation | Overhead | Target |
|-----------|----------|--------|
| PreToolUse hook | <2ms | <5ms |
| PostToolUse hook | <3ms | <5ms |
| SessionEnd hook | <100ms | <1s |
| Pattern extraction | <50ms | <100ms |
| CLAUDE.md update | <200ms | <500ms |

### Optimization Strategies

1. **Async Processing**: All heavy work in background
2. **Batching**: Group database operations
3. **Caching**: Cache CLAUDE.md parsing
4. **Lazy Loading**: Load AgentDB only when needed
5. **Incremental Updates**: Don't recompute everything

---

## Migration Plan

### Phase 1: Basic Hooks (Week 1)
- [ ] Implement capture_hook.py entry point
- [ ] Setup significance_scorer.py
- [ ] Create pattern_extractor.py
- [ ] Configure hooks.json
- [ ] Test with Claude Code

### Phase 2: Intelligence (Week 2)
- [ ] Implement 5-layer detection
- [ ] Add pattern learning logic
- [ ] Setup confidence scoring
- [ ] Create pattern database tables

### Phase 3: Auto-Update (Week 3)
- [ ] Implement CLAUDE.md manager
- [ ] Create skills auto-generation
- [ ] Add smart merge logic
- [ ] Setup backup system

### Phase 4: Polish (Week 4)
- [ ] Add comprehensive tests
- [ ] Performance optimization
- [ ] Error handling hardening
- [ ] Documentation and examples

---

## Next Steps

1. Review hooks implementation plan with hive mind
2. Implement proof-of-concept hook
3. Test with real Claude Code executions
4. Iterate based on performance data
5. Create detailed API specifications

---

**Designed by**: Memory Architecture Agent
**Coordinated via**: Hive Mind Collective
**Implementation**: `.mcp_standards/hooks/`

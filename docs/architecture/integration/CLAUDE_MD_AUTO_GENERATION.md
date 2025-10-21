# CLAUDE.md Auto-Generation & Maintenance System

**Version**: 2.0.0
**Status**: Design Phase
**Last Updated**: 2025-10-20

---

## Executive Summary

An intelligent system for automatically generating, maintaining, and optimizing CLAUDE.md configuration files across the hierarchy (global → parent → project → nested), ensuring AI coding assistants have optimal context without manual maintenance.

### Key Capabilities

- **Auto-Generation**: Create CLAUDE.md from scratch with intelligent defaults
- **Smart Merging**: Update existing files without conflicts
- **Hierarchy Management**: Global, parent, project, and nested file coordination
- **Context Optimization**: Token-efficient configuration based on actual usage
- **Cross-Tool Sync**: Optional updates to Cursor, Copilot, Windsurf configs
- **Version Control**: Track changes, backup before updates, rollback support

---

## Architecture Overview

```
┌────────────────────────────────────────────────────────────┐
│              Pattern Learning System                        │
│  • Learned preferences (confidence ≥ 0.9)                  │
│  • Workflow patterns (repetition ≥ 5)                      │
│  • Agent performance insights                              │
│  • Validation gate requirements                            │
└─────────────────────┬──────────────────────────────────────┘
                      │
                      │ High-confidence patterns
                      │
                      ▼
┌────────────────────────────────────────────────────────────┐
│          CLAUDE.md Generation Pipeline                      │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  1. Hierarchy Detection                              │ │
│  │     • Find all CLAUDE.md files                       │ │
│  │     • Build hierarchy tree                           │ │
│  │     • Detect inheritance                             │ │
│  └──────────────────┬───────────────────────────────────┘ │
│                     │                                       │
│  ┌──────────────────▼───────────────────────────────────┐ │
│  │  2. File Selection                                   │ │
│  │     • Project-specific → project CLAUDE.md           │ │
│  │     • Cross-project → parent/global CLAUDE.md        │ │
│  │     • User preference if ambiguous                   │ │
│  └──────────────────┬───────────────────────────────────┘ │
│                     │                                       │
│  ┌──────────────────▼───────────────────────────────────┐ │
│  │  3. Content Parser                                   │ │
│  │     • Parse existing CLAUDE.md                       │ │
│  │     • Extract sections and rules                     │ │
│  │     • Identify insertion points                      │ │
│  └──────────────────┬───────────────────────────────────┘ │
│                     │                                       │
│  ┌──────────────────▼───────────────────────────────────┐ │
│  │  4. Smart Merger                                     │ │
│  │     • Detect conflicts                               │ │
│  │     • Merge new rules into sections                  │ │
│  │     • Preserve user comments                         │ │
│  │     • Optimize token usage                           │ │
│  └──────────────────┬───────────────────────────────────┘ │
│                     │                                       │
│  ┌──────────────────▼───────────────────────────────────┐ │
│  │  5. Validation & Backup                              │ │
│  │     • Validate markdown syntax                       │ │
│  │     • Check token count                              │ │
│  │     • Create timestamped backup                      │ │
│  │     • Atomic write operation                         │ │
│  └──────────────────┬───────────────────────────────────┘ │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│              CLAUDE.md Hierarchy                            │
│                                                             │
│  ~/.claude/CLAUDE.md (Global)                              │
│       ↓ inherits                                           │
│  ~/Documents/CLAUDE.md (Parent)                            │
│       ↓ inherits                                           │
│  ~/Documents/project/CLAUDE.md (Project)                   │
│       ↓ inherits                                           │
│  ~/Documents/project/subdir/CLAUDE.md (Nested)             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Optional cross-tool sync
                     ▼
┌────────────────────────────────────────────────────────────┐
│              Cross-Tool Configuration Sync                  │
│  • .cursorrules                                            │
│  • .cursor/rules/*.mdc                                     │
│  • .github/copilot-instructions.md                         │
│  • .windsurfrules                                          │
│  • .clinerules                                             │
└────────────────────────────────────────────────────────────┘
```

---

## CLAUDE.md Structure

### Standard Template

```markdown
# Claude Code Configuration - [Project Name]

**Last Updated**: [ISO timestamp]
**Auto-managed by**: MCP Standards v2.0.0
**Token Budget**: [current]/[max] (target: <10k)

---

## 🎯 Project Overview

[Brief project description - auto-generated from README or user input]

**Project Type**: [python | javascript | typescript | go | rust | etc]
**Primary Technologies**: [list of detected technologies]
**Development Stage**: [active | maintenance | legacy]

---

## 🚀 Quick Reference

### Most Common Operations

[Auto-generated list of top 5 most frequent operations from usage data]

1. **[Operation]**: `[command]`
2. **[Operation]**: `[command]`
3. **[Operation]**: `[command]`

### Project Commands

[Auto-detected from package.json, Makefile, pyproject.toml, etc.]

```bash
# Build
[detected build command]

# Test
[detected test command]

# Lint
[detected lint command]
```

---

## 📋 Tool Preferences

[Auto-generated from learned patterns with confidence ≥ 90%]

### Package Management

**Preference**: Use `[tool]` instead of `[alternative]`

**Reason**: Learned from [N] consistent corrections

**Examples**:
```bash
# ✅ Correct
[correct example]

# ❌ Incorrect
[incorrect example]
```

**Confidence**: [X]% | **Last Verified**: [date]

---

[Additional preference sections...]

---

## 🔄 Workflow Automation

[Auto-detected behavioral patterns with repetition ≥ 5]

### Code Change Workflow

1. **Edit Code**: Modify source files
2. **Run Tests**: `[detected test command]` *(auto-suggested)*
3. **Check Lint**: `[detected lint command]` *(auto-suggested)*
4. **Commit**: Only after tests pass

**Pattern Detected**: [date] | **Frequency**: [N] occurrences | **Success Rate**: [X]%

---

[Additional workflow sections...]

---

## ✅ Quality Gates

[Auto-configured based on project requirements]

### Pre-Commit Requirements

- [ ] Tests pass (`[test command]`)
- [ ] Linting clean (`[lint command]`)
- [ ] Type check passes (`[typecheck command]`)
- [ ] Documentation updated (if public API changed)

**Enforcement**: Auto-check enabled | **Failures**: [N]

---

## 🎨 Code Style

[Learned style preferences with high confidence]

### Formatting Rules

[Auto-detected from .editorconfig, .prettierrc, pyproject.toml, etc.]

**Indentation**: [spaces | tabs] ([N] spaces)
**Line Length**: [N] characters
**Quotes**: [single | double]
**Trailing Commas**: [always | never | es5]

### Project-Specific Conventions

[Learned from repeated corrections]

---

## 🤖 Agent Performance

[Auto-tracked agent effectiveness]

### Recommended Agents

1. **[Agent Type]** for **[Task Category]**
   - Success Rate: [X]%
   - Avg Execution Time: [N]s
   - Last Used: [date]

2. **[Agent Type]** for **[Task Category]**
   - Success Rate: [X]%
   - Avg Execution Time: [N]s
   - Last Used: [date]

### Agents to Avoid

- **[Agent Type]** for **[Task Category]**: High correction rate ([X]%)

---

## 📊 Context Optimization

### Token Usage Analysis

- **Current Size**: [N] tokens
- **Usage Patterns**: [most accessed sections]
- **Recommended Optimizations**: [suggestions]

### Dynamic Context Loading

[Instructions for /prime commands if implemented]

```
/prime-debug → Load debugging context
/prime-feature → Load feature development context
/prime-refactor → Load refactoring context
```

---

## 🔧 Advanced Configuration

### MCP Servers (Load on Demand)

[Project-specific MCP servers only]

```json
{
  "mcpServers": {
    "[server-name]": {
      "command": "[command]",
      "args": [...]
    }
  }
}
```

**Note**: Load MCP servers explicitly per task to minimize token overhead.

---

## 📝 Learning History

### Recently Learned

[Last 5 learned patterns with timestamps]

1. **[Date]**: [Pattern description] (Confidence: [X]%)
2. **[Date]**: [Pattern description] (Confidence: [X]%)

### Pattern Evolution

- **Total Patterns Learned**: [N]
- **High Confidence (≥90%)**: [N]
- **Medium Confidence (70-89%)**: [N]
- **Under Review (<70%)**: [N]

---

## 🎓 Skills Integration

### Auto-Generated Skills

Skills are auto-generated in `.claude/skills/` from learned patterns:

```
.claude/skills/
  ├── learned-[pattern-name]/SKILL.md
  └── INDEX.json
```

**Total Skills**: [N] | **Last Updated**: [date]

---

## 🔍 Validation Rules

### Spec Validation

When completing tasks, automatically validate:

- [ ] Original specification met
- [ ] All requirements implemented
- [ ] Edge cases handled
- [ ] Tests cover new code
- [ ] Documentation updated

**Validation Failures**: [N] prevented | **Quality Improvement**: [X]%

---

## 💡 Usage Tips

### Best Practices

- Start commands with project context (detected automatically)
- Reference this file for project-specific conventions
- Update via corrections (system learns automatically)
- Review learning history monthly for accuracy

### Token Optimization

- This file: [N] tokens ([X]% of budget)
- Optimized for frequent operations
- Rare operations excluded (use /prime commands)

---

## 📚 Related Files

- **Skills**: `.claude/skills/INDEX.json` (auto-generated)
- **Workflows**: `.github/workflows/` (auto-detected)
- **Config**: `.editorconfig`, `.prettierrc` (parsed automatically)

---

**🤖 This file is auto-managed by MCP Standards Learning System v2.0.0**

**Last Auto-Update**: [ISO timestamp]
**Manual Edits**: Preserved during auto-updates (comments retained)
**Backup**: `.claude/backups/CLAUDE.md.[timestamp]`

---

## ⚙️ System Configuration

```yaml
auto_learning: enabled
auto_update: enabled
confidence_threshold: 0.9
occurrence_threshold: 3
token_budget: 10000
notification_level: important
```

**To disable auto-updates**: Set `auto_update: disabled` in this section.
```

---

## File Selection Algorithm

```python
async def choose_claudemd_file(
    pattern: Pattern,
    hierarchy: dict[str, Path]
) -> Path:
    """
    Intelligently choose which CLAUDE.md file to update

    Decision tree:
    1. Project-specific pattern → project CLAUDE.md
    2. Appears in 2+ projects → parent CLAUDE.md
    3. Appears in 3+ projects → global CLAUDE.md
    4. Ambiguous → ask user once, remember preference

    Returns:
        Path to CLAUDE.md file to update
    """
    # Check if pattern is project-specific
    if pattern.project_specific:
        return hierarchy['project']

    # Check how many projects have this pattern
    project_count = await count_projects_with_pattern(pattern)

    if project_count >= 3:
        # Universal pattern → global
        return hierarchy['global']
    elif project_count == 2:
        # Two projects → parent (if exists)
        if hierarchy.get('parent'):
            return hierarchy['parent']
        else:
            return hierarchy['global']
    else:
        # Single project
        if await should_promote_to_global(pattern):
            # User indicated this is universal
            return hierarchy['global']
        else:
            return hierarchy['project']


async def should_promote_to_global(pattern: Pattern) -> bool:
    """
    Ask user once if pattern should be global

    Remembers preference for similar patterns
    """
    # Check if we've asked about similar patterns
    similar_decision = await find_similar_pattern_decision(pattern)
    if similar_decision:
        return similar_decision.is_global

    # Ask user
    response = await ask_user(
        f"Apply '{pattern.description}' globally across all projects?",
        options=['Yes, make global', 'No, project-specific only'],
        remember=True
    )

    return response == 'Yes, make global'
```

---

## Smart Merging Algorithm

```python
async def smart_merge_claudemd(
    file_path: Path,
    new_rules: list[Rule]
) -> str:
    """
    Merge new rules into existing CLAUDE.md without conflicts

    Algorithm:
    1. Parse existing file into sections
    2. Identify section for each new rule
    3. Check for conflicts (duplicate/contradictory rules)
    4. Resolve conflicts intelligently
    5. Insert rules in appropriate sections
    6. Preserve user comments and manual edits
    7. Optimize token usage
    8. Validate result

    Returns:
        str: Updated CLAUDE.md content
    """
    # 1. Parse existing file
    existing = await parse_claudemd(file_path)
    sections = existing.sections

    # 2. Group new rules by section
    rules_by_section = group_rules_by_section(new_rules)

    # 3. Process each section
    for section_name, rules in rules_by_section.items():
        section = sections.get(section_name) or Section(name=section_name)

        for rule in rules:
            # 4. Check for conflicts
            conflict = section.find_conflicting_rule(rule)

            if conflict:
                # 5. Resolve conflict
                resolved = await resolve_conflict(conflict, rule)
                section.replace_rule(conflict, resolved)
            else:
                # No conflict, add rule
                section.add_rule(rule)

    # 6. Preserve user comments
    for comment in existing.user_comments:
        sections[comment.section].preserve_comment(comment)

    # 7. Optimize token usage
    if existing.token_count + sum(r.token_count for r in new_rules) > 10000:
        sections = await optimize_sections(sections, target_tokens=10000)

    # 8. Render to markdown
    rendered = render_claudemd(sections, existing.metadata)

    # 9. Validate
    if not validate_claudemd(rendered):
        raise ValidationError("Generated CLAUDE.md is invalid")

    return rendered


async def resolve_conflict(old_rule: Rule, new_rule: Rule) -> Rule:
    """
    Resolve conflicting rules intelligently

    Resolution strategies:
    - Higher confidence wins
    - More recent wins if confidence equal
    - Combine if complementary
    - Ask user if critical conflict
    """
    # Compare confidence
    if new_rule.confidence > old_rule.confidence + 0.1:
        # New rule significantly more confident
        return new_rule
    elif old_rule.confidence > new_rule.confidence + 0.1:
        # Old rule significantly more confident
        return old_rule

    # Compare recency (if confidence similar)
    if new_rule.timestamp > old_rule.timestamp:
        # New rule is more recent
        return new_rule

    # Check if rules are complementary
    if old_rule.is_complementary_to(new_rule):
        # Combine rules
        return old_rule.merge_with(new_rule)

    # Critical conflict → ask user
    choice = await ask_user(
        f"Conflicting rules detected:\n"
        f"1. {old_rule.description} (confidence: {old_rule.confidence})\n"
        f"2. {new_rule.description} (confidence: {new_rule.confidence})\n"
        f"Which should we keep?",
        options=['Keep old', 'Use new', 'Combine both']
    )

    if choice == 'Keep old':
        return old_rule
    elif choice == 'Use new':
        return new_rule
    else:
        return old_rule.merge_with(new_rule)
```

---

## Section Management

### Standard Sections

```python
STANDARD_SECTIONS = {
    'project_overview': {
        'title': '🎯 Project Overview',
        'order': 1,
        'auto_generate': True,
        'sources': ['README.md', 'package.json', 'pyproject.toml'],
    },
    'quick_reference': {
        'title': '🚀 Quick Reference',
        'order': 2,
        'auto_generate': True,
        'sources': ['usage_data', 'command_history'],
    },
    'tool_preferences': {
        'title': '📋 Tool Preferences',
        'order': 3,
        'auto_generate': True,
        'sources': ['learned_patterns'],
    },
    'workflow_automation': {
        'title': '🔄 Workflow Automation',
        'order': 4,
        'auto_generate': True,
        'sources': ['behavioral_patterns'],
    },
    'quality_gates': {
        'title': '✅ Quality Gates',
        'order': 5,
        'auto_generate': True,
        'sources': ['validation_gates'],
    },
    'code_style': {
        'title': '🎨 Code Style',
        'order': 6,
        'auto_generate': True,
        'sources': ['.editorconfig', '.prettierrc', 'learned_patterns'],
    },
    'agent_performance': {
        'title': '🤖 Agent Performance',
        'order': 7,
        'auto_generate': True,
        'sources': ['agent_performance_db'],
    },
    'context_optimization': {
        'title': '📊 Context Optimization',
        'order': 8,
        'auto_generate': True,
        'sources': ['token_usage_data'],
    },
    'advanced_configuration': {
        'title': '🔧 Advanced Configuration',
        'order': 9,
        'auto_generate': False,
        'sources': ['user_manual'],
    },
    'learning_history': {
        'title': '📝 Learning History',
        'order': 10,
        'auto_generate': True,
        'sources': ['pattern_database'],
    },
}
```

### Dynamic Section Generation

```python
async def generate_section(section_config: dict, context: dict) -> Section:
    """
    Generate section content from sources

    Each section has multiple data sources that are
    automatically aggregated and formatted
    """
    section = Section(name=section_config['title'])

    if not section_config['auto_generate']:
        # User-managed section, preserve existing content
        return await load_existing_section(section_config['title'])

    # Generate from sources
    for source in section_config['sources']:
        if source == 'learned_patterns':
            patterns = await load_learned_patterns(
                confidence_threshold=0.9
            )
            for pattern in patterns:
                section.add_rule(format_pattern_as_rule(pattern))

        elif source == 'behavioral_patterns':
            patterns = await load_behavioral_patterns(
                repetition_threshold=5
            )
            for pattern in patterns:
                section.add_workflow(format_behavioral_pattern(pattern))

        elif source == 'usage_data':
            top_commands = await get_top_commands(limit=5)
            section.add_subsection('Most Common Operations', top_commands)

        elif source == 'agent_performance_db':
            agents = await get_agent_recommendations()
            section.add_subsection('Recommended Agents', agents)

        elif source.endswith('.md') or source.endswith('.json'):
            # File source
            content = await parse_config_file(source)
            section.merge_content(content)

    return section
```

---

## Token Optimization

### Token Budget Management

```python
class TokenBudget:
    """
    Manage CLAUDE.md token budget

    Target: <10,000 tokens (5% of 200k context window)
    Critical threshold: 15,000 tokens
    """

    MAX_TOKENS = 10000
    CRITICAL_THRESHOLD = 15000

    async def optimize_sections(
        self,
        sections: dict[str, Section],
        target_tokens: int = MAX_TOKENS
    ) -> dict[str, Section]:
        """
        Optimize sections to fit token budget

        Strategies:
        1. Remove low-confidence rules (<0.7)
        2. Collapse verbose sections
        3. Move infrequent rules to /prime commands
        4. Summarize learning history
        5. Remove redundant examples
        """
        current_tokens = sum(s.token_count for s in sections.values())

        if current_tokens <= target_tokens:
            return sections  # Already under budget

        # 1. Remove low-confidence rules
        for section in sections.values():
            section.remove_rules_below_confidence(0.7)

        current_tokens = sum(s.token_count for s in sections.values())
        if current_tokens <= target_tokens:
            return sections

        # 2. Collapse verbose sections
        verbose_sections = ['learning_history', 'agent_performance']
        for section_name in verbose_sections:
            if section_name in sections:
                sections[section_name].collapse_to_summary()

        current_tokens = sum(s.token_count for s in sections.values())
        if current_tokens <= target_tokens:
            return sections

        # 3. Move infrequent rules to /prime commands
        all_rules = []
        for section in sections.values():
            all_rules.extend(section.rules)

        # Sort by usage frequency
        all_rules.sort(key=lambda r: r.usage_count)

        # Bottom 20% → move to /prime
        infrequent_count = len(all_rules) // 5
        infrequent_rules = all_rules[:infrequent_count]

        await create_prime_command(
            name='prime-infrequent',
            rules=infrequent_rules
        )

        # Remove from main sections
        for rule in infrequent_rules:
            for section in sections.values():
                section.remove_rule(rule)

        current_tokens = sum(s.token_count for s in sections.values())
        if current_tokens <= target_tokens:
            return sections

        # 4. Last resort: warn user
        await notify(
            f"⚠️ CLAUDE.md token count ({current_tokens}) exceeds budget ({target_tokens}). "
            f"Consider moving some rules to /prime commands or increasing token budget."
        )

        return sections
```

### Usage-Based Prioritization

```python
async def prioritize_rules_by_usage(rules: list[Rule]) -> list[Rule]:
    """
    Prioritize rules based on actual usage frequency

    Rules used frequently → keep in CLAUDE.md
    Rules rarely used → move to /prime commands
    """
    # Get usage stats
    for rule in rules:
        rule.usage_count = await get_rule_usage_count(rule.id)
        rule.last_used = await get_rule_last_used(rule.id)

    # Calculate priority score
    for rule in rules:
        rule.priority = calculate_priority(
            confidence=rule.confidence,
            usage_count=rule.usage_count,
            recency=rule.last_used,
            category=rule.category
        )

    # Sort by priority
    return sorted(rules, key=lambda r: r.priority, reverse=True)


def calculate_priority(
    confidence: float,
    usage_count: int,
    recency: datetime,
    category: str
) -> float:
    """
    Calculate rule priority score

    Formula:
    priority = (confidence * 0.4) +
               (usage_frequency * 0.3) +
               (recency_score * 0.2) +
               (category_weight * 0.1)
    """
    # Normalize usage count (log scale)
    usage_score = min(math.log10(usage_count + 1) / 3, 1.0)

    # Recency score (exponential decay)
    days_since_use = (datetime.now() - recency).days
    recency_score = math.exp(-days_since_use / 30)

    # Category weights
    category_weights = {
        'tool-preference': 1.0,     # Highest priority
        'workflow-automation': 0.9,
        'quality-gates': 0.8,
        'code-style': 0.7,
        'agent-performance': 0.6,
    }
    category_weight = category_weights.get(category, 0.5)

    # Calculate final priority
    priority = (
        confidence * 0.4 +
        usage_score * 0.3 +
        recency_score * 0.2 +
        category_weight * 0.1
    )

    return priority
```

---

## Cross-Tool Synchronization

### Universal Config Formats

```python
async def sync_cross_tool_configs(
    claude_md: Path,
    enable_cursor: bool = False,
    enable_copilot: bool = False,
    enable_windsurf: bool = False,
    enable_cline: bool = False
) -> None:
    """
    Synchronize learned rules to other AI assistant configs

    Optional feature - disabled by default
    """
    # Parse CLAUDE.md
    config = await parse_claudemd(claude_md)
    rules = config.extract_universal_rules()

    # Cursor (.cursorrules)
    if enable_cursor:
        cursor_rules = convert_to_cursor_format(rules)
        await write_file('.cursorrules', cursor_rules)
        await notify("✅ Updated .cursorrules")

    # GitHub Copilot
    if enable_copilot:
        copilot_instructions = convert_to_copilot_format(rules)
        await write_file('.github/copilot-instructions.md', copilot_instructions)
        await notify("✅ Updated GitHub Copilot instructions")

    # Windsurf
    if enable_windsurf:
        windsurf_rules = convert_to_windsurf_format(rules)
        await write_file('.windsurfrules', windsurf_rules)
        await notify("✅ Updated .windsurfrules")

    # Cline
    if enable_cline:
        cline_rules = convert_to_cline_format(rules)
        await write_file('.clinerules', cline_rules)
        await notify("✅ Updated .clinerules")
```

### Format Converters

```python
def convert_to_cursor_format(rules: list[Rule]) -> str:
    """
    Convert to Cursor .cursorrules format

    Cursor uses markdown-based rules
    """
    output = []
    output.append("# Cursor Rules\n")
    output.append("# Auto-synced from CLAUDE.md\n\n")

    for rule in rules:
        output.append(f"## {rule.title}\n\n")
        output.append(f"{rule.description}\n\n")

        if rule.correct_examples:
            output.append("**Correct:**\n```\n")
            output.append('\n'.join(rule.correct_examples))
            output.append("\n```\n\n")

        if rule.incorrect_examples:
            output.append("**Incorrect:**\n```\n")
            output.append('\n'.join(rule.incorrect_examples))
            output.append("\n```\n\n")

    return ''.join(output)


def convert_to_copilot_format(rules: list[Rule]) -> str:
    """
    Convert to GitHub Copilot instructions format

    Copilot prefers concise, directive language
    """
    output = []
    output.append("# GitHub Copilot Instructions\n\n")
    output.append("Auto-synced from CLAUDE.md learning system.\n\n")

    for rule in rules:
        output.append(f"- {rule.as_directive()}\n")

    return ''.join(output)
```

---

## Backup & Version Control

### Backup Strategy

```python
async def create_backup(file_path: Path) -> Path:
    """
    Create timestamped backup before modifying CLAUDE.md

    Backups stored in .claude/backups/
    Retention: Last 10 backups per file
    """
    backup_dir = file_path.parent / '.claude' / 'backups'
    await ensure_directory(backup_dir)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = backup_dir / f"{file_path.name}.{timestamp}"

    # Copy file
    await copy_file(file_path, backup_path)

    # Cleanup old backups (keep last 10)
    await cleanup_old_backups(backup_dir, max_backups=10)

    return backup_path


async def rollback_from_backup(file_path: Path, backup_path: Path = None) -> None:
    """
    Rollback to previous version

    If backup_path not specified, use most recent backup
    """
    if not backup_path:
        backup_path = await find_latest_backup(file_path)

    if not backup_path:
        raise FileNotFoundError("No backups found")

    # Restore from backup
    await copy_file(backup_path, file_path)

    await notify(f"✅ Rolled back to backup: {backup_path.name}")
```

### Git Integration

```python
async def commit_claudemd_update(
    file_path: Path,
    rules: list[Rule]
) -> None:
    """
    Create git commit for CLAUDE.md updates

    Optional feature - only if project uses git
    """
    if not await is_git_repo():
        return

    # Create commit message
    rule_descriptions = [r.short_description for r in rules]
    message = f"""chore: Update CLAUDE.md with learned patterns

Auto-learned patterns:
{chr(10).join(f"- {desc}" for desc in rule_descriptions)}

Generated by: MCP Standards Learning System v2.0.0
"""

    # Stage and commit
    await run_command(f"git add {file_path}")
    await run_command(f"git commit -m '{message}'")

    await notify(f"✅ Committed CLAUDE.md updates to git")
```

---

## Testing Strategy

### Unit Tests

```python
# test_claudemd_generation.py

async def test_file_selection():
    """Test intelligent file selection logic"""
    pattern = create_test_pattern(project_specific=False)
    hierarchy = create_test_hierarchy()

    # Pattern appears in 3 projects → should choose global
    file = await choose_claudemd_file(pattern, hierarchy)
    assert file == hierarchy['global']

async def test_smart_merging():
    """Test conflict-free merging"""
    existing_content = """
# CLAUDE.md

## Tool Preferences

### Python Packages

Use pip for package management.
"""

    new_rule = create_rule(
        category='tool-preference',
        content='Use uv instead of pip',
        confidence=0.95
    )

    merged = await smart_merge_claudemd(
        content=existing_content,
        new_rules=[new_rule]
    )

    # Should replace old rule with higher-confidence new rule
    assert 'uv' in merged
    assert merged.count('Python Packages') == 1  # No duplicates

async def test_token_optimization():
    """Test token budget enforcement"""
    sections = create_large_sections(token_count=15000)

    optimized = await optimize_sections(sections, target_tokens=10000)

    total_tokens = sum(s.token_count for s in optimized.values())
    assert total_tokens <= 10000
```

---

## Configuration

### Environment Variables

```bash
# Auto-generation settings
AUTO_UPDATE_CLAUDEMD=true
CLAUDEMD_TOKEN_BUDGET=10000
BACKUP_RETENTION=10

# Cross-tool sync (opt-in)
SYNC_TO_CURSOR=false
SYNC_TO_COPILOT=false
SYNC_TO_WINDSURF=false
SYNC_TO_CLINE=false

# Conflict resolution
CONFLICT_RESOLUTION=auto  # auto | ask | keep-old | use-new

# Git integration
AUTO_COMMIT_UPDATES=false
```

---

## Migration Plan

### Phase 1: Core Generation (Week 1)
- [ ] Implement hierarchy detection
- [ ] Create file selection logic
- [ ] Build content parser
- [ ] Setup backup system

### Phase 2: Smart Merging (Week 2)
- [ ] Implement conflict detection
- [ ] Create resolution strategies
- [ ] Add token optimization
- [ ] Build validation system

### Phase 3: Cross-Tool Sync (Week 3)
- [ ] Create format converters
- [ ] Implement sync logic
- [ ] Add configuration options
- [ ] Test with real configs

### Phase 4: Polish (Week 4)
- [ ] Comprehensive testing
- [ ] Performance optimization
- [ ] Documentation
- [ ] Real-world validation

---

## Next Steps

1. Review CLAUDE.md architecture
2. Implement file selection algorithm
3. Test smart merging with real files
4. Validate token optimization
5. Create format converters for cross-tool sync

---

**Designed by**: Memory Architecture Agent
**Coordinated via**: Hive Mind Collective
**Implementation**: `src/mcp_standards/intelligence/claudemd_manager.py`

# Skills Auto-Generation System

**Version**: 2.0.0
**Status**: Design Phase
**Last Updated**: 2025-10-20

---

## Executive Summary

An intelligent system for automatically generating Claude Code skills files from learned patterns, enabling dynamic skill discovery and contextual knowledge application without manual maintenance.

### Key Features

- **Automatic Generation**: Create skills from 3+ consistent patterns
- **Template-Based**: Structured format for consistency
- **Confidence-Scored**: Only high-confidence patterns (≥90%)
- **Context-Aware**: Apply skills based on project context
- **Self-Updating**: Skills evolve as patterns strengthen
- **Discovery-Enabled**: Claude Code's native skill discovery integration

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                Pattern Learning System                    │
│  • 5-layer detection                                     │
│  • Confidence scoring                                    │
│  • Frequency tracking                                    │
└─────────────────────┬────────────────────────────────────┘
                      │
                      │ Patterns with confidence ≥ 0.9
                      │ and occurrence ≥ 3
                      ▼
┌──────────────────────────────────────────────────────────┐
│              Skill Generation Pipeline                    │
│  ┌──────────────────────────────────────────────────┐   │
│  │  1. Pattern Analyzer                             │   │
│  │     • Extract actionable rules                   │   │
│  │     • Identify correct/incorrect usage           │   │
│  │     • Build context requirements                 │   │
│  └──────────────────┬───────────────────────────────┘   │
│                     │                                     │
│  ┌──────────────────▼───────────────────────────────┐   │
│  │  2. Template Renderer                            │   │
│  │     • Load appropriate template                  │   │
│  │     • Fill in pattern details                    │   │
│  │     • Generate examples                          │   │
│  └──────────────────┬───────────────────────────────┘   │
│                     │                                     │
│  ┌──────────────────▼───────────────────────────────┐   │
│  │  3. Skill File Writer                            │   │
│  │     • Create .claude/skills/[name]/ directory    │   │
│  │     • Write SKILL.md file                        │   │
│  │     • Update skill index                         │   │
│  └──────────────────┬───────────────────────────────┘   │
│                     │                                     │
│  ┌──────────────────▼───────────────────────────────┐   │
│  │  4. Validation & Testing                         │   │
│  │     • Validate YAML frontmatter                  │   │
│  │     • Check markdown structure                   │   │
│  │     • Test skill application                     │   │
│  └──────────────────┬───────────────────────────────┘   │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│           Generated Skills Repository                     │
│  .claude/skills/                                         │
│    ├── learned-uv-preference/                           │
│    │   └── SKILL.md                                     │
│    ├── learned-bullet-formatting/                       │
│    │   └── SKILL.md                                     │
│    ├── learned-test-workflow/                           │
│    │   └── SKILL.md                                     │
│    └── INDEX.json                                       │
└─────────────────────┬────────────────────────────────────┘
                      │
                      │ Claude Code Discovery
                      ▼
┌──────────────────────────────────────────────────────────┐
│              Claude Code/Desktop                          │
│  • Auto-discover skills in .claude/skills/               │
│  • Apply context-aware rules                             │
│  • Suggest skills during execution                       │
└──────────────────────────────────────────────────────────┘
```

---

## Skill File Structure

### Standard Template

```markdown
---
name: "Skill Name (Descriptive)"
description: "Clear description of what this skill does and when to use it"
version: "1.0.0"
confidence: 0.95
learned_from: ["episode-123", "episode-456", "episode-789"]
category: "tool-preference | workflow-automation | code-style | testing"
applies_to:
  tools: ["Bash", "Write", "Edit"]
  file_patterns: ["*.py", "requirements.txt"]
  project_types: ["python", "web"]
contexts:
  - "Installing Python packages"
  - "Managing virtual environments"
created_at: "2025-10-20T10:30:00Z"
updated_at: "2025-10-20T10:30:00Z"
auto_generated: true
---

# [Skill Name]

## What This Skill Does

[Clear explanation of the skill's purpose and value]

## When to Apply

[Specific scenarios where this skill should be used]

- Context 1
- Context 2
- Context 3

## Correct Usage

```[language]
# ✅ Preferred approach
[correct example]

# ✅ Also acceptable
[alternative correct example]
```

## Incorrect Usage

```[language]
# ❌ Avoid this
[incorrect example]

# ❌ Also avoid
[alternative incorrect example]
```

## Context & Learning History

### How This Was Learned

1. **[Date]**: [First occurrence description] (Episode #[id])
2. **[Date]**: [Second occurrence description] (Episode #[id])
3. **[Date]**: [Third occurrence description] (Episode #[id])

### Pattern Analysis

- **Frequency**: [X] occurrences over [Y] days
- **Consistency**: [X]% of similar cases followed this pattern
- **Success Rate**: [X]% when applied correctly

## Related Skills

- [Link to related skill 1]
- [Link to related skill 2]

## Examples from Real Usage

### Example 1: [Description]

```[language]
[Real code example]
```

**Context**: [When this was used]
**Outcome**: [What happened]

### Example 2: [Description]

```[language]
[Another real code example]
```

**Context**: [When this was used]
**Outcome**: [What happened]

## Confidence: [X]%

Based on [N] consistent observations with [description of evidence].

## Troubleshooting

### Common Issues

**Issue**: [Problem that might occur]
**Solution**: [How to resolve it]

**Issue**: [Another problem]
**Solution**: [Another solution]

## Notes

- [Additional notes or caveats]
- [Edge cases to be aware of]

---

**Auto-generated by**: MCP Standards Learning System v2.0.0
**Last updated**: [ISO timestamp]
**Review status**: ✅ Validated | ⚠️ Needs review | ❌ Deprecated
```

---

## Template Types

### 1. Tool Preference Template

**Use Case**: Learned preferences for specific tools

```markdown
---
name: "Use UV for Python Package Management"
category: "tool-preference"
applies_to:
  tools: ["Bash"]
  commands: ["pip", "python -m pip"]
---

# Use UV for Python Package Management

## What This Skill Does

Ensures all Python package operations use the modern `uv` tool instead of legacy `pip`.

## When to Apply

- Installing Python packages
- Creating virtual environments
- Managing project dependencies
- Updating requirements

## Correct Usage

```bash
# ✅ Package installation
uv pip install requests

# ✅ Requirements file
uv pip install -r requirements.txt

# ✅ Virtual environment
uv venv .venv

# ✅ Development dependencies
uv pip install -e ".[dev]"
```

## Incorrect Usage

```bash
# ❌ Don't use pip directly
pip install requests

# ❌ Don't use python -m pip
python -m pip install requests

# ❌ Don't use venv module
python -m venv .venv
```

## Context & Learning History

### How This Was Learned

1. **2025-10-15 14:23**: User corrected "pip install" to "uv pip install" (Episode #123)
2. **2025-10-17 09:45**: Explicit instruction: "Always use uv for packages" (Episode #456)
3. **2025-10-18 16:12**: User edited requirements script to use uv (Episode #789)

### Pattern Analysis

- **Frequency**: 5 occurrences over 4 days
- **Consistency**: 100% of Python package operations
- **Success Rate**: 100% when using uv

## Confidence: 95%

Based on 5 consistent corrections with explicit user instructions.
```

---

### 2. Workflow Automation Template

**Use Case**: Learned behavioral patterns and workflows

```markdown
---
name: "Auto-run Tests After Code Changes"
category: "workflow-automation"
applies_to:
  tools: ["Edit", "Write"]
  file_patterns: ["*.py", "*.ts", "*.js"]
  project_types: ["python", "typescript", "javascript"]
---

# Auto-run Tests After Code Changes

## What This Skill Does

Automatically suggests running tests after modifying source code files to catch regressions early.

## When to Apply

- After editing source files (*.py, *.ts, *.js)
- After creating new modules
- After refactoring code
- Before committing changes

## Correct Usage

```bash
# ✅ Edit code then test
# 1. Edit file
Edit src/api.py

# 2. Run tests immediately
Bash "pytest tests/test_api.py"

# ✅ Or run full test suite
Bash "npm run test"
```

## Workflow Pattern

1. **Code Change**: Edit/Write to source file
2. **Test Execution**: Run relevant tests (auto-suggested)
3. **Fix Issues**: If tests fail, iterate
4. **Commit**: Only after tests pass

## Context & Learning History

### How This Was Learned

1. **2025-10-10**: User ran `pytest` after 5 consecutive edits (Episode #234)
2. **2025-10-12**: User ran `npm test` after each React component edit (Episode #267)
3. **2025-10-14**: Explicit: "Always run tests after code changes" (Episode #301)
4. **2025-10-15**: User aborted commit due to missing tests (Episode #312)
5. **2025-10-17**: Repeated pattern confirmed (Episode #345)

### Pattern Analysis

- **Frequency**: 12 occurrences over 8 days
- **Consistency**: 92% of code edits followed by tests
- **Success Rate**: 87% reduction in bugs when tests run

## Auto-Suggestion Logic

```python
# Trigger conditions
if tool_name in ['Edit', 'Write']:
    if file_path matches ['*.py', '*.ts', '*.js']:
        if file_path in ['src/', 'lib/', 'app/']:
            suggest: "Run tests for {file_path}?"
            command: determine_test_command(file_path)
```

## Confidence: 88%

Based on 12 consistent occurrences with strong correlation to code quality.
```

---

### 3. Code Style Template

**Use Case**: Learned formatting and style preferences

```markdown
---
name: "Use Bullet Points (•) Not Dashes (-) for Resumes"
category: "code-style"
applies_to:
  tools: ["Write", "Edit"]
  file_patterns: ["*resume*.md", "*cv*.md"]
---

# Use Bullet Points (•) Not Dashes (-) for Resumes

## What This Skill Does

Ensures resume and CV documents use proper bullet points (•) instead of markdown dashes (-) for professional formatting.

## When to Apply

- Writing resume content
- Editing CV files
- Creating professional documents
- Formatting job descriptions

## Correct Usage

```markdown
# ✅ Professional bullet points
• Led team of 5 engineers on cloud migration
• Increased system performance by 40%
• Implemented CI/CD pipeline reducing deploy time by 60%

# ✅ Nested bullets
• Senior Software Engineer (2020-2024)
  • Built microservices architecture
  • Mentored junior developers
```

## Incorrect Usage

```markdown
# ❌ Don't use markdown dashes
- Led team of 5 engineers on cloud migration
- Increased system performance by 40%

# ❌ Don't use asterisks
* Senior Software Engineer
* Built microservices
```

## Implementation

```python
# Auto-correction logic
if file_path.contains(['resume', 'cv']):
    content = content.replace('- ', '• ')
    content = content.replace('* ', '• ')
```

## Context & Learning History

### How This Was Learned

1. **2025-10-08**: User changed "- " to "• " in resume.md (Episode #156)
2. **2025-10-09**: Explicit: "Use • bullets not - for resume" (Episode #167)
3. **2025-10-11**: User manually edited all bullets in CV (Episode #189)

### Pattern Analysis

- **Frequency**: 3 corrections within 4 days
- **Consistency**: 100% of resume files
- **Context**: Professional document formatting

## Confidence: 97%

Explicit user instruction with consistent application.
```

---

## Generation Pipeline

### Step 1: Pattern Analysis

```python
async def analyze_pattern_for_skill(pattern: Pattern) -> SkillAnalysis:
    """
    Analyze pattern to extract skill components

    Returns:
        SkillAnalysis with:
        - skill_name: Generated name
        - category: Classification
        - correct_usage: Examples
        - incorrect_usage: Anti-patterns
        - contexts: When to apply
        - confidence: Confidence score
    """
    # Extract actionable rule
    rule = await extract_actionable_rule(pattern)

    # Identify correct vs incorrect usage
    examples = await extract_examples(pattern)
    correct = [ex for ex in examples if ex.is_correct]
    incorrect = [ex for ex in examples if not ex.is_correct]

    # Build context list
    contexts = await build_contexts(pattern)

    # Determine category
    category = classify_pattern(pattern)

    # Generate skill name
    name = generate_skill_name(pattern, category)

    return SkillAnalysis(
        skill_name=name,
        category=category,
        rule=rule,
        correct_usage=correct,
        incorrect_usage=incorrect,
        contexts=contexts,
        confidence=pattern.confidence,
        metadata=pattern.metadata
    )
```

### Step 2: Template Rendering

```python
async def render_skill_template(analysis: SkillAnalysis) -> str:
    """
    Render skill file from analysis

    Uses Jinja2 templates with custom filters
    """
    # Load appropriate template
    template_name = f"skill_{analysis.category}.md.j2"
    template = await load_template(template_name)

    # Prepare context
    context = {
        'name': analysis.skill_name,
        'description': analysis.rule.description,
        'version': '1.0.0',
        'confidence': analysis.confidence,
        'learned_from': analysis.pattern.episode_ids,
        'category': analysis.category,
        'applies_to': analysis.pattern.applies_to,
        'contexts': analysis.contexts,
        'correct_examples': analysis.correct_usage,
        'incorrect_examples': analysis.incorrect_usage,
        'learning_history': analysis.pattern.history,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'auto_generated': True,
    }

    # Render
    rendered = template.render(**context)

    # Validate YAML frontmatter
    if not validate_frontmatter(rendered):
        raise ValidationError("Invalid YAML frontmatter")

    return rendered
```

### Step 3: File Writing

```python
async def write_skill_file(analysis: SkillAnalysis, content: str) -> str:
    """
    Write skill file to .claude/skills/

    Returns:
        str: Path to generated skill file
    """
    # Generate directory name
    skill_dir = f".claude/skills/learned-{slugify(analysis.skill_name)}"

    # Create directory
    await ensure_directory(skill_dir)

    # Write SKILL.md
    skill_path = f"{skill_dir}/SKILL.md"
    await write_file(skill_path, content)

    # Update index
    await update_skill_index(skill_path, analysis)

    # Create examples directory (optional)
    if analysis.correct_usage:
        examples_dir = f"{skill_dir}/examples"
        await create_examples(examples_dir, analysis.correct_usage)

    return skill_path
```

### Step 4: Validation

```python
async def validate_skill_file(skill_path: str) -> ValidationResult:
    """
    Validate generated skill file

    Checks:
    - YAML frontmatter syntax
    - Required fields present
    - Markdown structure
    - Code blocks valid
    - Links working
    """
    content = await read_file(skill_path)

    # Parse frontmatter
    try:
        frontmatter = parse_yaml_frontmatter(content)
    except Exception as e:
        return ValidationResult(valid=False, error=f"Invalid YAML: {e}")

    # Check required fields
    required = ['name', 'description', 'category', 'confidence']
    for field in required:
        if field not in frontmatter:
            return ValidationResult(valid=False, error=f"Missing field: {field}")

    # Validate markdown structure
    if not has_required_sections(content):
        return ValidationResult(valid=False, error="Missing required sections")

    # Validate code blocks
    code_blocks = extract_code_blocks(content)
    for block in code_blocks:
        if not validate_code_block(block):
            return ValidationResult(valid=False, error=f"Invalid code block: {block.language}")

    return ValidationResult(valid=True)
```

---

## Skill Index Management

### INDEX.json Structure

```json
{
  "version": "1.0.0",
  "last_updated": "2025-10-20T10:30:00Z",
  "total_skills": 12,
  "categories": {
    "tool-preference": 5,
    "workflow-automation": 3,
    "code-style": 2,
    "testing": 2
  },
  "skills": [
    {
      "id": "learned-uv-preference",
      "name": "Use UV for Python Package Management",
      "path": ".claude/skills/learned-uv-preference/SKILL.md",
      "category": "tool-preference",
      "confidence": 0.95,
      "applies_to": {
        "tools": ["Bash"],
        "commands": ["pip"],
        "file_patterns": []
      },
      "created_at": "2025-10-15T14:23:00Z",
      "updated_at": "2025-10-20T10:30:00Z",
      "usage_count": 23,
      "success_rate": 1.0
    },
    {
      "id": "learned-bullet-formatting",
      "name": "Use Bullet Points (•) Not Dashes (-) for Resumes",
      "path": ".claude/skills/learned-bullet-formatting/SKILL.md",
      "category": "code-style",
      "confidence": 0.97,
      "applies_to": {
        "tools": ["Write", "Edit"],
        "file_patterns": ["*resume*.md", "*cv*.md"]
      },
      "created_at": "2025-10-08T16:45:00Z",
      "updated_at": "2025-10-11T09:12:00Z",
      "usage_count": 8,
      "success_rate": 1.0
    }
  ]
}
```

### Index Operations

```python
async def update_skill_index(skill_path: str, analysis: SkillAnalysis) -> None:
    """
    Update INDEX.json with new or updated skill
    """
    # Load existing index
    index = await load_skill_index()

    # Create skill entry
    skill_entry = {
        'id': analysis.skill_id,
        'name': analysis.skill_name,
        'path': skill_path,
        'category': analysis.category,
        'confidence': analysis.confidence,
        'applies_to': analysis.pattern.applies_to,
        'created_at': analysis.pattern.created_at,
        'updated_at': datetime.now().isoformat(),
        'usage_count': 0,
        'success_rate': 0.0,
    }

    # Update or add
    existing = index.find_skill(analysis.skill_id)
    if existing:
        # Update existing
        existing.update(skill_entry)
        existing['usage_count'] += 1
    else:
        # Add new
        index['skills'].append(skill_entry)
        index['total_skills'] += 1
        index['categories'][analysis.category] += 1

    index['last_updated'] = datetime.now().isoformat()

    # Write back
    await write_skill_index(index)
```

---

## Claude Code Integration

### Discovery Mechanism

Claude Code automatically discovers skills in `.claude/skills/` directories:

```
.claude/
  └── skills/
      ├── INDEX.json (optional, for optimization)
      ├── learned-uv-preference/
      │   └── SKILL.md
      ├── learned-bullet-formatting/
      │   └── SKILL.md
      └── learned-test-workflow/
          └── SKILL.md
```

### Application Logic

```python
# In Claude Code's skill application system

async def apply_skills(tool_name: str, arguments: dict, context: dict) -> dict:
    """
    Apply relevant skills to tool execution

    1. Load all skills from .claude/skills/
    2. Filter by applies_to criteria
    3. Rank by confidence and relevance
    4. Apply highest-ranked skill modifications
    5. Return modified arguments
    """
    # Load skills
    skills = await discover_skills('.claude/skills/')

    # Filter applicable skills
    applicable = [
        skill for skill in skills
        if skill.applies_to_tool(tool_name, arguments, context)
    ]

    # Rank by confidence and context match
    ranked = sorted(applicable, key=lambda s: (s.confidence, s.context_match(context)), reverse=True)

    # Apply top skill
    if ranked:
        top_skill = ranked[0]
        modified_args = top_skill.apply(arguments)

        # Log application
        await log_skill_application(top_skill, tool_name, modified_args)

        return modified_args

    return arguments
```

---

## Auto-Update Mechanism

### Skill Evolution

```python
async def update_skill_confidence(skill_id: str, success: bool) -> None:
    """
    Update skill confidence based on usage feedback

    Success → increase confidence
    Failure → decrease confidence
    """
    skill = await load_skill(skill_id)

    # Update usage stats
    skill.usage_count += 1
    skill.success_count += 1 if success else 0
    skill.success_rate = skill.success_count / skill.usage_count

    # Adjust confidence
    if success:
        # Gradual increase (max 0.99)
        skill.confidence = min(skill.confidence + 0.01, 0.99)
    else:
        # Steeper decrease
        skill.confidence = max(skill.confidence - 0.05, 0.5)

    # Deprecate if confidence drops below threshold
    if skill.confidence < 0.6:
        skill.status = 'deprecated'
        await notify(f"⚠️ Skill '{skill.name}' deprecated due to low confidence")

    # Rewrite skill file with updated confidence
    await rewrite_skill_file(skill)
```

### Pattern Strengthening

```python
async def strengthen_skill(skill_id: str, new_evidence: Evidence) -> None:
    """
    Strengthen existing skill with new evidence

    1. Add new example to learning history
    2. Update confidence score
    3. Refresh examples with latest patterns
    4. Rewrite skill file
    """
    skill = await load_skill(skill_id)

    # Add evidence
    skill.learning_history.append(new_evidence)
    skill.confidence = calculate_confidence(skill.learning_history)

    # Refresh examples
    all_examples = extract_examples(skill.learning_history)
    skill.correct_examples = [ex for ex in all_examples if ex.is_correct][-5:]  # Top 5
    skill.incorrect_examples = [ex for ex in all_examples if not ex.is_correct][-3:]  # Top 3

    # Update metadata
    skill.updated_at = datetime.now().isoformat()
    skill.version = increment_version(skill.version)

    # Rewrite file
    await rewrite_skill_file(skill)

    await notify(f"✨ Skill '{skill.name}' strengthened (confidence: {skill.confidence:.0%})")
```

---

## Testing Strategy

### Unit Tests

```python
# test_skill_generation.py

async def test_pattern_to_skill_conversion():
    """Test pattern analysis and skill generation"""
    pattern = create_test_pattern(
        type='explicit_correction',
        content="Use uv instead of pip",
        confidence=0.95,
        occurrence_count=3
    )

    analysis = await analyze_pattern_for_skill(pattern)

    assert analysis.skill_name == "Use UV for Python Package Management"
    assert analysis.category == "tool-preference"
    assert len(analysis.correct_usage) > 0
    assert len(analysis.incorrect_usage) > 0

async def test_skill_file_validation():
    """Test skill file structure validation"""
    content = create_test_skill_file()

    result = await validate_skill_file_content(content)

    assert result.valid == True
    assert 'name' in result.frontmatter
    assert 'confidence' in result.frontmatter

async def test_skill_index_management():
    """Test skill index updates"""
    index = await load_skill_index()
    initial_count = index['total_skills']

    await add_skill_to_index(create_test_skill())

    index = await load_skill_index()
    assert index['total_skills'] == initial_count + 1
```

---

## Configuration

### Environment Variables

```bash
# Skill generation settings
AUTO_GENERATE_SKILLS=true
SKILL_CONFIDENCE_THRESHOLD=0.9
SKILL_OCCURRENCE_THRESHOLD=3
SKILLS_DIR=.claude/skills

# Template settings
SKILL_TEMPLATES_DIR=templates/skills
DEFAULT_SKILL_TEMPLATE=skill_base.md.j2

# Update behavior
AUTO_UPDATE_SKILLS=true
SKILL_UPDATE_STRATEGY=strengthen  # strengthen | replace | version
```

---

## Migration Plan

### Phase 1: Basic Generation (Week 1)
- [ ] Implement pattern analysis
- [ ] Create base templates
- [ ] Build rendering engine
- [ ] Setup file writing

### Phase 2: Claude Integration (Week 2)
- [ ] Test with Claude Code discovery
- [ ] Implement application logic
- [ ] Create skill index
- [ ] Add validation

### Phase 3: Evolution (Week 3)
- [ ] Implement auto-update
- [ ] Add confidence tracking
- [ ] Build strengthening logic
- [ ] Create deprecation system

### Phase 4: Polish (Week 4)
- [ ] Comprehensive testing
- [ ] Template refinement
- [ ] Documentation
- [ ] Performance optimization

---

## Next Steps

1. Review skills auto-generation architecture
2. Create template prototypes
3. Test with real learned patterns
4. Validate Claude Code discovery
5. Iterate based on usage data

---

**Designed by**: Memory Architecture Agent
**Coordinated via**: Hive Mind Collective
**Implementation**: `src/mcp_standards/skills/`

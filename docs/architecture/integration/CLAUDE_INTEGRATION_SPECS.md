# Claude Desktop/Code Integration Specifications

**Version**: 2.0.0
**Status**: Design Phase
**Last Updated**: 2025-10-20

---

## Executive Summary

Comprehensive integration specifications for MCP Standards with Claude Desktop and Claude Code, leveraging native hooks, skills discovery, and MCP protocol for seamless automatic learning and configuration management.

### Integration Points

- **Native Hooks**: PostToolUse, PreToolUse, SessionEnd
- **Skills Discovery**: `.claude/skills/` auto-discovery
- **MCP Protocol**: Enhanced tool endpoints for learning
- **Configuration**: `.claude/` directory structure
- **Real-time Sync**: Live updates and notifications

---

## Claude Desktop Integration

### Directory Structure

```
~/.claude/                          # Global configuration
├── CLAUDE.md                       # Global preferences
├── mcp.json                        # MCP servers config
├── hooks.json                      # Hooks configuration
├── skills/                         # Global skills
│   ├── INDEX.json
│   └── [skill-dirs]/
│       └── SKILL.md
└── backups/                        # Auto-backups
    └── CLAUDE.md.20251020_103000

~/Documents/project/                # Project-specific
├── CLAUDE.md                       # Project preferences
├── .claude/
│   ├── skills/                     # Project skills
│   │   ├── INDEX.json
│   │   └── [skill-dirs]/
│   │       └── SKILL.md
│   └── backups/
│       └── CLAUDE.md.20251020_103000
└── .swarm/
    └── memory.db                   # SQLite memory
```

### MCP Configuration

**File**: `~/.claude/mcp.json` or `~/Documents/project/.mcp.json`

```json
{
  "mcpServers": {
    "mcp-standards": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/mcp-standards",
        "python",
        "-m",
        "mcp_standards.server"
      ],
      "env": {
        "DB_PATH": "${PROJECT_ROOT}/.swarm/memory.db",
        "AGENTDB_PATH": "${PROJECT_ROOT}/.agentdb/reasoningbank.db",
        "AUTO_LEARNING": "true",
        "AUTO_UPDATE_CLAUDEMD": "true",
        "AUTO_GENERATE_SKILLS": "true",
        "HOOKS_ENABLED": "true"
      }
    }
  }
}
```

### Hooks Configuration

**File**: `~/.claude/hooks.json`

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
            "command": "uv run --directory /path/to/mcp-standards python -m mcp_standards.hooks.capture_hook pre {tool_name} {tool_args_json}",
            "timeout": 5000,
            "async": true,
            "env": {
              "HOOK_TYPE": "pre",
              "SESSION_ID": "${SESSION_ID}",
              "PROJECT_PATH": "${PROJECT_ROOT}"
            }
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
            "command": "uv run --directory /path/to/mcp-standards python -m mcp_standards.hooks.capture_hook post {tool_name} {tool_args_json} {tool_result_json}",
            "timeout": 5000,
            "async": true,
            "env": {
              "HOOK_TYPE": "post",
              "SESSION_ID": "${SESSION_ID}",
              "PROJECT_PATH": "${PROJECT_ROOT}",
              "USER_MESSAGE": "${USER_MESSAGE}"
            }
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
            "command": "uv run --directory /path/to/mcp-standards python -m mcp_standards.hooks.capture_hook session-end {session_id} {session_summary_json}",
            "timeout": 10000,
            "async": true,
            "env": {
              "HOOK_TYPE": "session-end",
              "SESSION_ID": "${SESSION_ID}",
              "PROJECT_PATH": "${PROJECT_ROOT}"
            }
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
    "max_failures": 3,
    "log_level": "info",
    "log_file": "~/.claude/logs/hooks.log"
  }
}
```

---

## Claude Code Integration

### Skills Discovery

Claude Code automatically discovers skills in `.claude/skills/`:

```python
# Claude Code's skill discovery (built-in)

def discover_skills(base_path: str = ".claude/skills") -> list[Skill]:
    """
    Auto-discover skills from .claude/skills/ directory

    Scans for:
    - .claude/skills/*/SKILL.md files
    - INDEX.json for optimization
    """
    skills = []

    # Check for INDEX.json (optimization)
    index_path = Path(base_path) / "INDEX.json"
    if index_path.exists():
        # Fast path: use index
        index = json.loads(index_path.read_text())
        for skill_entry in index['skills']:
            skill = load_skill_from_path(skill_entry['path'])
            skills.append(skill)
    else:
        # Slow path: scan filesystem
        for skill_dir in Path(base_path).iterdir():
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                skill = load_skill_from_file(skill_file)
                skills.append(skill)

    return skills


def load_skill_from_file(skill_file: Path) -> Skill:
    """
    Parse SKILL.md file

    Extracts:
    - YAML frontmatter (metadata)
    - Markdown content (instructions)
    """
    content = skill_file.read_text()

    # Parse frontmatter
    frontmatter, markdown = split_frontmatter(content)

    return Skill(
        name=frontmatter['name'],
        description=frontmatter['description'],
        category=frontmatter['category'],
        confidence=frontmatter['confidence'],
        applies_to=frontmatter.get('applies_to', {}),
        content=markdown,
        file_path=skill_file
    )
```

### Skill Application

```python
# How Claude Code applies skills during execution

async def before_tool_execution(
    tool_name: str,
    arguments: dict,
    context: dict
) -> dict:
    """
    Apply relevant skills before tool execution

    1. Discover skills
    2. Filter applicable skills
    3. Rank by confidence and context
    4. Apply top skill modifications
    """
    # 1. Discover
    skills = discover_skills()

    # 2. Filter applicable
    applicable = [
        skill for skill in skills
        if skill_applies_to_context(skill, tool_name, arguments, context)
    ]

    # 3. Rank
    ranked = sorted(
        applicable,
        key=lambda s: (s.confidence, s.context_relevance(context)),
        reverse=True
    )

    # 4. Apply top skill
    if ranked:
        top_skill = ranked[0]
        modified_args = apply_skill_transformations(
            top_skill,
            arguments
        )

        # Log application
        log_skill_application(top_skill, tool_name, modified_args)

        return modified_args

    return arguments


def skill_applies_to_context(
    skill: Skill,
    tool_name: str,
    arguments: dict,
    context: dict
) -> bool:
    """
    Check if skill applies to current context

    Criteria:
    - Tool name matches
    - File patterns match (if applicable)
    - Project type matches (if applicable)
    - Context requirements met
    """
    applies_to = skill.applies_to

    # Check tool name
    if 'tools' in applies_to:
        if tool_name not in applies_to['tools']:
            return False

    # Check file patterns
    if 'file_patterns' in applies_to and 'file_path' in arguments:
        file_path = arguments['file_path']
        if not any(fnmatch.fnmatch(file_path, pattern) for pattern in applies_to['file_patterns']):
            return False

    # Check project types
    if 'project_types' in applies_to:
        project_type = detect_project_type(context['project_path'])
        if project_type not in applies_to['project_types']:
            return False

    # Check contexts
    if 'contexts' in skill.metadata:
        if not context_matches_any(context, skill.metadata['contexts']):
            return False

    return True
```

---

## MCP Protocol Enhancements

### New MCP Tools

```python
# Enhanced MCP server with learning tools

server = Server("mcp-standards")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    List available MCP tools including new learning tools
    """
    return [
        # Existing tools
        Tool(name="create_episode", ...),
        Tool(name="semantic_search", ...),
        Tool(name="list_episodes", ...),

        # New learning tools
        Tool(
            name="learn_preference",
            description="Manually add a learned preference",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "context": {"type": "string"},
                    "preference": {"type": "string"},
                    "project_specific": {"type": "boolean", "default": False}
                },
                "required": ["category", "context", "preference"]
            }
        ),
        Tool(
            name="suggest_claudemd_update",
            description="Get suggested CLAUDE.md updates based on learned patterns",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string"},
                    "min_confidence": {"type": "number", "default": 0.7}
                }
            }
        ),
        Tool(
            name="validate_spec",
            description="Validate deliverable against original specification",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_description": {"type": "string"},
                    "deliverable_summary": {"type": "string"}
                },
                "required": ["task_description", "deliverable_summary"]
            }
        ),
        Tool(
            name="check_quality_gates",
            description="Check if quality gates are satisfied",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string"},
                    "gate_types": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["project_path"]
            }
        ),
        Tool(
            name="get_agent_suggestions",
            description="Get agent recommendations based on task and performance",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_category": {"type": "string"},
                    "context": {"type": "string"}
                },
                "required": ["task_category"]
            }
        ),
        Tool(
            name="query_agent_performance",
            description="Query agent performance statistics",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_type": {"type": "string"},
                    "task_category": {"type": "string"},
                    "time_range": {"type": "string"}
                }
            }
        ),
        Tool(
            name="generate_skills_file",
            description="Manually trigger skills file generation",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern_id": {"type": "string"}
                },
                "required": ["pattern_id"]
            }
        ),
        Tool(
            name="update_claudemd",
            description="Manually trigger CLAUDE.md update",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern_ids": {"type": "array", "items": {"type": "string"}},
                    "file_path": {"type": "string"}
                }
            }
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Handle tool calls including new learning tools
    """
    if name == "learn_preference":
        result = await learn_preference(
            category=arguments['category'],
            context=arguments['context'],
            preference=arguments['preference'],
            project_specific=arguments.get('project_specific', False)
        )
        return [TextContent(type="text", text=json.dumps(result))]

    elif name == "suggest_claudemd_update":
        suggestions = await suggest_claudemd_update(
            project_path=arguments.get('project_path'),
            min_confidence=arguments.get('min_confidence', 0.7)
        )
        return [TextContent(type="text", text=json.dumps(suggestions))]

    elif name == "validate_spec":
        validation = await validate_spec(
            task_description=arguments['task_description'],
            deliverable_summary=arguments['deliverable_summary']
        )
        return [TextContent(type="text", text=json.dumps(validation))]

    # ... other tool handlers
```

---

## Real-Time Notifications

### Notification System

```python
# MCP server notifications

from mcp.server.models import Notification

async def notify_user(
    level: str,
    message: str,
    data: dict = None
) -> None:
    """
    Send notification to Claude Desktop/Code

    Levels:
    - info: Informational only
    - important: User should be aware
    - critical: Requires user action
    """
    if level == "info" and notification_level != "all":
        return  # Skip info notifications unless user opted in

    notification = Notification(
        level=level,
        message=message,
        data=data or {}
    )

    await server.send_notification(notification)


# Usage examples

async def on_pattern_learned(pattern: Pattern):
    """Notify when new pattern learned"""
    await notify_user(
        level="important",
        message=f"✨ Learned new pattern: {pattern.description}",
        data={
            "pattern_id": pattern.id,
            "confidence": pattern.confidence,
            "category": pattern.category
        }
    )


async def on_claudemd_updated(file_path: Path, rules: list[Rule]):
    """Notify when CLAUDE.md updated"""
    await notify_user(
        level="important",
        message=f"✅ Updated {file_path.name} with {len(rules)} new rules",
        data={
            "file_path": str(file_path),
            "rules": [r.short_description for r in rules]
        }
    )


async def on_skill_generated(skill_path: Path, skill: Skill):
    """Notify when new skill generated"""
    await notify_user(
        level="important",
        message=f"🎓 Generated new skill: {skill.name}",
        data={
            "skill_path": str(skill_path),
            "confidence": skill.confidence,
            "category": skill.category
        }
    )


async def on_validation_failed(validation: Validation):
    """Notify when spec validation fails"""
    await notify_user(
        level="critical",
        message=f"⚠️ Deliverable doesn't match spec: {len(validation.gaps)} gaps found",
        data={
            "gaps": validation.gaps,
            "task": validation.task_description
        }
    )
```

---

## Environment Variables

```bash
# Core settings
DB_PATH=.swarm/memory.db
AGENTDB_PATH=.agentdb/reasoningbank.db
PROJECT_ROOT=${PWD}

# Feature flags
AUTO_LEARNING=true
AUTO_UPDATE_CLAUDEMD=true
AUTO_GENERATE_SKILLS=true
HOOKS_ENABLED=true
CROSS_TOOL_SYNC=false

# Thresholds
SIGNIFICANCE_THRESHOLD=0.3
PATTERN_CONFIDENCE_THRESHOLD=0.9
PATTERN_OCCURRENCE_THRESHOLD=3

# Performance
CACHE_SIZE=2000
BATCH_SIZE=100
ASYNC_PROCESSING=true

# Notifications
NOTIFICATION_LEVEL=important  # all | important | critical | none

# Logging
LOG_LEVEL=info
LOG_FILE=~/.claude/logs/mcp-standards.log

# Cross-tool sync (opt-in)
SYNC_TO_CURSOR=false
SYNC_TO_COPILOT=false
SYNC_TO_WINDSURF=false

# Token optimization
CLAUDEMD_TOKEN_BUDGET=10000
ENABLE_PRIME_COMMANDS=true

# Backup
BACKUP_RETENTION=10
AUTO_COMMIT_UPDATES=false
```

---

## Installation & Setup

### Step 1: Install MCP Standards

```bash
# Install via uv
uv add mcp-standards

# Or install globally
uv tool install mcp-standards
```

### Step 2: Initialize Project

```bash
# Initialize .claude directory structure
mcp-standards init

# Creates:
# .claude/
# ├── skills/
# │   └── INDEX.json
# └── backups/
# .swarm/
# └── memory.db
# .agentdb/
# └── reasoningbank.db
```

### Step 3: Configure Claude Desktop

```bash
# Add MCP server to Claude Desktop
mcp-standards configure --claude-desktop

# Or manually edit ~/.claude/mcp.json
```

### Step 4: Configure Hooks

```bash
# Setup hooks configuration
mcp-standards configure --hooks

# Or manually edit ~/.claude/hooks.json
```

### Step 5: Verify Installation

```bash
# Test MCP server
mcp-standards test

# Expected output:
# ✅ MCP server responding
# ✅ Database connected
# ✅ AgentDB initialized
# ✅ Hooks configured
# ✅ Skills directory ready
```

---

## Usage Examples

### Example 1: Automatic Learning

```
User: "Install requests library"

Claude executes: Bash "pip install requests"

User corrects: "Use uv instead of pip"

[PostToolUse hook triggers]
↓
[Pattern detected: explicit correction]
↓
[Confidence: 0.95 (first occurrence)]
↓
[Stored in pattern database]

---

User: "Install numpy"

Claude executes: Bash "pip install numpy"

User corrects: "Always use uv for Python packages"

[PostToolUse hook triggers]
↓
[Pattern detected: 2nd occurrence]
↓
[Confidence: 0.97]

---

User: "Install pandas"

Claude suggests: "Should I use uv pip install pandas?"

User: "Yes"

[PostToolUse hook triggers]
↓
[Pattern detected: 3rd occurrence]
↓
[Confidence: 0.98]
↓
[Auto-promotion triggered]
↓
[CLAUDE.md updated]
[Skills file generated]
[User notified]

Notification: "✨ Learned new preference: Use uv for Python packages (98% confidence)"
```

### Example 2: Skills Auto-Application

```
[Claude Code discovers skills on startup]
↓
[Loads .claude/skills/learned-uv-preference/SKILL.md]
↓
[Skill: applies_to.tools = ["Bash"], commands = ["pip"]]

---

User: "Install requests"

[Claude prepares to execute: Bash "pip install requests"]
↓
[PreToolUse hook checks applicable skills]
↓
[Skill "Use UV Preference" matches]
↓
[Arguments modified: "pip" → "uv pip"]
↓
[Claude executes: Bash "uv pip install requests"]

User: "Perfect!"

[No correction needed - skill applied successfully]
```

### Example 3: Spec Validation

```
User: "Build a REST API with authentication, rate limiting, and error handling"

[Claude implements API]

Claude: "Done! Created REST API with endpoints"

[Claude calls check_quality_gates tool]
↓
[Validation engine compares deliverable vs spec]
↓
[Gap detected: Rate limiting not implemented]
↓
[Validation fails]

Claude: "⚠️ Implementation incomplete:
- ✅ Authentication implemented
- ✅ Error handling implemented
- ❌ Rate limiting missing

Should I add rate limiting?"

User: "Yes, please"

[Claude adds rate limiting]
[Validation passes]
[Quality gate satisfied]
```

---

## Performance Considerations

### Expected Overhead

| Operation | Time | Impact |
|-----------|------|--------|
| PreToolUse hook | <2ms | Negligible |
| PostToolUse hook | <3ms | Negligible |
| SessionEnd hook | <100ms | None (async) |
| Skill discovery | <10ms | Once per session |
| Pattern detection | <50ms | Background |
| CLAUDE.md update | <200ms | Async |

### Optimization Strategies

1. **Async Processing**: All heavy work in background threads
2. **Caching**: Skills and rules cached in memory
3. **Batching**: Database operations batched
4. **Lazy Loading**: AgentDB loaded only when needed
5. **Index Optimization**: INDEX.json for fast skill discovery

---

## Troubleshooting

### Issue: Hooks not triggering

```bash
# Check hooks configuration
cat ~/.claude/hooks.json

# Verify hooks are enabled
grep "enabled" ~/.claude/hooks.json

# Check logs
tail -f ~/.claude/logs/hooks.log
```

### Issue: Skills not discovered

```bash
# Check skills directory
ls -la .claude/skills/

# Verify SKILL.md files
find .claude/skills -name "SKILL.md"

# Check INDEX.json
cat .claude/skills/INDEX.json
```

### Issue: MCP server not responding

```bash
# Test MCP server
mcp-standards test

# Check logs
tail -f ~/.claude/logs/mcp-standards.log

# Restart server
claude mcp restart mcp-standards
```

---

## Next Steps

1. Install and configure MCP Standards
2. Test hooks integration with Claude Code
3. Validate skills discovery
4. Create first learned pattern
5. Verify CLAUDE.md auto-update

---

**Designed by**: Memory Architecture Agent
**Coordinated via**: Hive Mind Collective
**Integration**: Claude Desktop + Claude Code

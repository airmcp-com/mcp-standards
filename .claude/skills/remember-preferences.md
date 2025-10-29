---
skill_name: remember-preferences
version: 1.0.0
author: MCP Standards Team
description: Automatically remember and recall user preferences using AgentDB personal memory
tags: [memory, preferences, learning, agentdb]
---

# Remember Preferences Skill

**Purpose**: Make Claude remember YOUR preferences automatically across all conversations.

## How It Works

This skill enables Claude to:
1. **Auto-detect corrections** - When you say "actually, use X not Y", it's automatically stored
2. **Semantic recall** - Before responding, Claude checks personal memory for relevant preferences
3. **Cross-session learning** - Preferences persist across all conversations

## Usage

### Automatic (Zero Config)

Just correct Claude naturally:
```
You: "Run pip install pytest"
Claude: *executes*

You: "Actually, use uv not pip"
Claude: ✓ Remembered: "use uv not pip" (python)

Next session:
You: "Install pytest"
Claude: *uses uv automatically*
```

### Manual (If Needed)

Explicitly tell Claude to remember:
```
Remember: Always run tests before committing code
Remember: Use TypeScript for new JavaScript files
Remember: Prefer functional components in React
```

## What Gets Remembered

✅ **Tool preferences**: "use uv not pip", "prefer yarn over npm"
✅ **Workflow patterns**: "run tests before commit", "update docs when adding features"
✅ **Code style**: "use TypeScript", "prefer functional components"
✅ **Project conventions**: "follow PEP 8", "use 2 spaces for indentation"

## Technical Details

- **Storage**: AgentDB vector memory (semantic search)
- **Speed**: <1ms to recall preferences
- **Persistence**: Stored in ~/.mcp-standards/agentdb
- **Privacy**: 100% local, no cloud

## Commands

### Check what's remembered
```
What preferences have you remembered about me?
```

### Search specific category
```
What do you remember about Python package management?
What preferences do you have about Git?
```

### See statistics
```
Show me memory stats
```

## Integration Points

This skill automatically integrates with:
- Config file parsing (.editorconfig, pyproject.toml)
- Tool execution monitoring (Bash, Read, Write, etc.)
- Natural language corrections in conversations

## Best Practices

1. **Be explicit the first time**: "Use uv not pip" is clearer than "don't use pip"
2. **Provide context**: "For Python projects, use uv" helps categorization
3. **Trust the system**: You don't need to repeat yourself - it's remembered after the first correction
4. **Review occasionally**: Ask "what do you remember?" to verify

## Example Workflow

```
Session 1:
You: "Run the Python tests"
Claude: pytest tests/
You: "Actually, use uv run pytest"
Claude: ✓ Remembered

Session 2:
You: "Run the Python tests"
Claude: uv run pytest tests/  [uses remembered preference]

Session 10:
You: "What Python preferences do you have?"
Claude: "I remember you prefer:
- Use uv for package management (not pip)
- Run tests with uv run pytest
- Use Python 3.11+ features"
```

## Troubleshooting

**Preference not being remembered?**
- Use clear language: "use X not Y"
- Check logs: Look for "🎯 Detected correction" messages

**Wrong preference recalled?**
- More specific context helps: "for Python projects, use X"
- Categories help filtering: python, git, docker, etc.

**Want to forget something?**
- Currently: Preferences persist forever (future: expiration/override)
- Workaround: Correct it again with new preference

## Future Enhancements

- Confidence scores (promote after 2-3 occurrences)
- Preference conflicts detection
- Cross-project learning (global vs project-specific)
- Preference expiration (time-based decay)

---

**Remember**: The best correction is the one you only have to make once.

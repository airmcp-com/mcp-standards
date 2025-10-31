# Usage Examples

## Two Ways to Use mcp-standards

### 1. As an MCP Server (Claude Desktop)

Configure in `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "memory": {
      "command": "node",
      "args": ["/absolute/path/to/mcp-standards/dist/index.js"]
    }
  }
}
```

Then in Claude Desktop:
- "Remember: use uv instead of pip"
- "What's my preferred Python package manager?"

### 2. As a Library (Claude Code / Your Code)

Install:
```bash
npm install mcp-standards
```

Use in your code:

```typescript
import { SimpleMemoryClient } from 'mcp-standards';

const memory = new SimpleMemoryClient();
await memory.init();

// Store preferences
await memory.remember("Use uv instead of pip", "python", 9);

// Recall preferences
const results = await memory.recall("python package manager");
console.log(results[0].memory.content); // "Use uv instead of pip"
```

## Quick Helpers

For one-off operations:

```typescript
import { quickRecall, quickRemember } from 'mcp-standards';

// Store quickly
await quickRemember("Always create feature branches", "git", 8);

// Recall quickly
const results = await quickRecall("git workflow");
```

## Advanced Usage

Access core classes directly:

```typescript
import { EmbeddingService, MemoryStore } from 'mcp-standards';

const embeddings = new EmbeddingService();
const store = new MemoryStore(embeddings);
await store.init();

// Full control over memory operations
const memory = await store.store("My preference", "general", 5);
const results = await store.search("query", { limit: 10 });
```

## Examples

See [direct-usage.ts](./direct-usage.ts) for complete examples including:
- Client class usage
- Helper functions
- Integration with Claude Code workflows

Run the example:
```bash
npm run build
node examples/direct-usage.js
```

## Shared Memory

Both approaches (MCP server and direct library) use the **same memory file**:
- Location: `~/.mcp-memory/memories.json`
- Format: JSON array of memory records with embeddings
- Shared between Claude Desktop and your code

This means:
- ✅ Store preferences in Claude Desktop
- ✅ Access them in Claude Code or your scripts
- ✅ Single source of truth

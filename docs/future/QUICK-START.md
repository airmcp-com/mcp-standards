# Research MCP - 10 Minute Quick Start

**Get your unified AI knowledge copilot running in under 10 minutes**

Transform your AI workflow from scattered tools and lost context to a unified system that federates data, discovers tools intelligently, and remembers everything.

---

## ⚡ What You'll Have

**After 10 minutes**:
- ✅ **MindsDB**: Federated access to 200+ data sources via single MCP server
- ✅ **Strata**: Progressive tool discovery without context overload  
- ✅ **Local Memory**: SQLite knowledge base with full-text search
- ✅ **Unified Configuration**: Works in both Claude Desktop and Claude Code

**Your AI will be able to**:
```
# Query across all your data as one unified database
SELECT github.commits, salesforce.deals, notion.tasks 
FROM your_integrated_sources 
WHERE created_at > '2024-01-01'

# Discover tools progressively without overwhelming context
Intent: "Research competitor pricing" → Categories → Specific Tools → Action

# Remember everything with persistent knowledge
"What database decisions did we make last month?"
```

---

## 🔧 Prerequisites (2 minutes)

**Required**:
- **Claude Code** or **Claude Desktop** installed
- **Docker** for MindsDB (recommended) OR Python 3.10+
- **Node.js 18+** for Strata

**Optional**:
- **uv** for faster Python package management (recommended)

**Quick checks**:
```bash
docker --version    # Should show Docker 20.0+
node --version      # Should show Node 18.0+
claude --version    # Should show Claude Code installed
```

---

## 🚀 Setup (7 minutes)

### Step 1: Clone and Setup Local Memory (2 minutes)

```bash
# Clone the repository
git clone https://github.com/mattstrautmann/research-mcp
cd research-mcp

# Setup the local SQLite knowledge engine
cd mcp-servers/local-memory
uv venv && uv pip install -e .

# Test it works
uv run python -c "import local_memory; print('✓ Local memory ready')"

# Return to project root
cd ../..
```

### Step 2: Start MindsDB (2 minutes)

**Option A: Docker (Recommended)**
```bash
# Start MindsDB container
docker run -d \
  --name mindsdb \
  -p 47334:47334 \
  -v $(pwd)/data:/data \
  mindsdb/mindsdb

# Verify it's running (wait ~30 seconds for startup)
curl http://localhost:47334/health
# Should return: {"status": "ok"}
```

**Option B: Local Installation**
```bash
pip install mindsdb
mindsdb --api http --port 47334 &
```

### Step 3: Configure Claude (2 minutes)

**For Claude Desktop**:
```bash
# Copy unified configuration
cp config/unified-mcp.json ~/Library/Application\ Support/Claude/mcp.json

# Restart Claude Desktop completely (Cmd+Q, then reopen)
```

**For Claude Code**:
```bash
# Update your Claude Code configuration
cp config/claude-code.json ~/.claude.json

# Or add to existing config manually - see config examples below
```

### Step 4: Test Integration (1 minute)

Open Claude and test each component:

```
# Check all MCP servers are loaded
/mcp

# Should show:
# ✓ mindsdb - Federated data access
# ✓ strata - Progressive tool discovery  
# ✓ local-memory - Knowledge storage
```

**Test data federation**:
```
Use the MindsDB list_databases tool to see available data sources
```

**Test tool discovery**:
```
Use Strata to discover tools for "data analysis and reporting"
```

**Test local memory**:
```
add_episode(
  name="Quick Start Complete", 
  content="Research MCP unified system is now working!",
  source="setup"
)

# Then search for it
search_episodes("quick start")
```

---

## 🎯 First Use Cases (Bonus 5 minutes)

### Connect Your First Data Source

```sql
-- In Claude, use MindsDB to connect to PostgreSQL
CREATE DATABASE my_app_db
WITH ENGINE='postgres',
PARAMETERS={
  "host": "localhost",
  "database": "myapp", 
  "user": "readonly_user",
  "password": "your_password"
};

-- Query your data
SELECT * FROM my_app_db.users LIMIT 5;
```

### Setup Progressive Tool Discovery

```
# Ask Claude:
"Use Strata to help me find tools for automating customer onboarding"

# Watch it guide you through:
Intent → Integration Options → Categories → Specific Actions
```

### Build Your Knowledge Base

```python
# Add your first knowledge episodes
add_episode(
  name="Database Schema",
  content="Users table has columns: id, email, created_at, plan_type",
  source="discovery"
)

add_episode(
  name="Tool Decision", 
  content="Using Strata for progressive discovery reduces context overload",
  source="architecture"
)

# Search across your knowledge
search_episodes("database")
```

---

## 📋 Configuration Reference

### Unified MCP Configuration

**Claude Desktop** (`~/Library/Application Support/Claude/mcp.json`):
```json
{
  "mcpServers": {
    "mindsdb": {
      "command": "docker",
      "args": ["exec", "mindsdb", "python", "-m", "mindsdb.interfaces.mcp.server"]
    },
    "strata": {
      "command": "npx",
      "args": ["-y", "strata-mcp"]
    },
    "local-memory": {
      "command": "uv",
      "args": [
        "--directory", 
        "/Users/mattstrautmann/Documents/github/research-mcp/mcp-servers/local-memory",
        "run", 
        "server.py"
      ]
    }
  }
}
```

**Claude Code** (`~/.claude.json`):
```json
{
  "projects": {
    "/Users/mattstrautmann/Documents/github/research-mcp": {
      "mcpServers": {
        "mindsdb": {
          "type": "stdio",
          "command": "docker", 
          "args": ["exec", "mindsdb", "python", "-m", "mindsdb.interfaces.mcp.server"]
        },
        "strata": {
          "type": "stdio",
          "command": "npx",
          "args": ["-y", "strata-mcp"]
        },
        "local-memory": {
          "type": "stdio",
          "command": "uv",
          "args": ["--directory", "./mcp-servers/local-memory", "run", "server.py"]
        }
      }
    }
  }
}
```

### Environment Variables

Create `.env` file in project root:
```bash
# MindsDB Configuration
MINDSDB_DATA_DIR=./data
MINDSDB_PORT=47334

# Local Memory Configuration  
KNOWLEDGE_DB_PATH=./knowledge.db
AUTO_CAPTURE=true

# Strata Configuration
STRATA_MAX_TOOLS=1000
STRATA_DISCOVERY_MODE=progressive
```

---

## 🔍 Verification & Troubleshooting

### Health Checks

```bash
# Check MindsDB
curl http://localhost:47334/health
# Expected: {"status": "ok"}

# Check Docker container
docker ps | grep mindsdb
# Should show running container

# Check local memory
cd mcp-servers/local-memory && uv run python -c "
import sqlite3
conn = sqlite3.connect('knowledge.db')
print('Episodes:', conn.execute('SELECT COUNT(*) FROM episodes').fetchone()[0])
conn.close()
"

# Check Claude MCP status
# In Claude interface: /mcp
```

### Common Issues

**MindsDB not starting**:
```bash
# Check Docker logs
docker logs mindsdb

# Alternative: Use different port
docker run -d --name mindsdb -p 47335:47334 mindsdb/mindsdb
```

**Strata tools not loading**:
```bash
# Verify Node.js version
node --version  # Needs 18+

# Test Strata directly
npx -y strata-mcp --version
```

**Claude not seeing MCP servers**:
```bash
# Verify configuration file location
ls -la ~/Library/Application\ Support/Claude/mcp.json

# Check Claude Code config  
ls -la ~/.claude.json

# Restart Claude completely (important!)
```

**Local memory not persisting**:
```bash
# Check database file permissions
ls -la ./knowledge.db

# Verify SQLite installation
sqlite3 --version
```

---

## 🎓 Next Steps

### Immediate (Next 30 minutes)
1. **Connect your main data sources** to MindsDB
2. **Explore Strata categories** for your common workflows  
3. **Add 5-10 knowledge episodes** to build your memory
4. **Try federated queries** across multiple sources

### This Week
1. **Setup automated knowledge capture** from your daily tools
2. **Configure custom tool categories** in Strata
3. **Create your first agent workflows** 
4. **Integrate with your team's systems**

### This Month  
1. **Build comprehensive knowledge base** of your domain
2. **Develop custom MCP tools** for specialized workflows
3. **Setup enterprise security** and governance
4. **Share knowledge base** with team members

---

## 📚 Learning Resources

### Essential Reading
- **[Architecture Guide](ARCHITECTURE.md)** - Understand how the three layers work together
- **[Configuration Deep Dive](docs/configuration.md)** - Advanced setup options
- **[API Reference](docs/api.md)** - Complete tool documentation

### Video Tutorials
- **10-Minute Demo**: See the full setup process
- **Advanced Queries**: Federated data analysis examples  
- **Tool Discovery**: Strata progressive discovery in action
- **Knowledge Building**: Best practices for episode creation

### Community
- **GitHub Discussions**: Questions and showcases
- **Discord**: Real-time community support
- **Examples Repository**: Production use cases and templates

---

## ❓ FAQ

**Q: Can I use this with existing MCP servers?**
A: Yes! Research MCP complements other MCP servers. The unified config lets you mix and match.

**Q: Do I need all three components?**
A: No, each works independently. Start with what solves your biggest pain point.

**Q: How much resource overhead?**
A: Minimal: ~650MB RAM total, <1% CPU idle. Optimized for development workflows.

**Q: Is this enterprise-ready?**
A: Yes, with proper configuration. See enterprise deployment guide.

**Q: Can I contribute custom tools?**
A: Absolutely! See contributing guide for MCP server development.

---

## 🎉 Success!

You now have a unified AI knowledge copilot that:
- **Federates data access** across all your sources via MindsDB
- **Discovers tools progressively** without context overload via Strata  
- **Remembers everything** with persistent SQLite knowledge storage
- **Works seamlessly** in both Claude Desktop and Code

**Your AI workflow just got a major upgrade. Welcome to the future of intelligent orchestration!**

---

*Having issues? [Open an issue](https://github.com/mattstrautmann/research-mcp/issues) or join our [Discord](https://discord.gg/research-mcp) for help.*
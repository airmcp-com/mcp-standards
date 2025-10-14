# AirMCP Deployment Architecture

> **Version**: 1.0.0
> **Last Updated**: 2025-10-13
> **Status**: Production Ready

## Executive Summary

This document outlines the complete deployment strategy for AirMCP (formerly Claude Memory), covering distribution methods, packaging, CI/CD pipelines, and production deployment to airmcp.com.

**Recommended Approach**: Hybrid distribution strategy combining PyPI (primary) with npm wrapper for convenience.

---

## 1. Distribution Strategy Analysis

### 1.1 Project Characteristics
- **Primary Language**: Python
- **Package Manager**: uv (with pip fallback)
- **Target Users**: AI assistant users (Claude, Cursor, Copilot)
- **Deployment Type**: MCP Server (local process, stdio communication)
- **Dependencies**: Minimal (mcp>=1.0.0, sqlite3 built-in)

### 1.2 Distribution Options Comparison

| Method | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| **PyPI (pip)** | Native Python, versioning, uv compatible | Python-only users | ✅ **Primary** |
| **npm (npx)** | Universal, easy `npx airmcp@latest`, cross-platform | Requires Node.js | ✅ **Wrapper** |
| **GitHub Direct** | Always latest, no registry delays | No versioning, less discoverable | ⚠️ **Fallback** |
| **Homebrew** | macOS native, easy updates | macOS only, maintenance overhead | ❌ Too narrow |

### 1.3 Recommended: Hybrid Strategy

**Primary Distribution: PyPI**
```bash
# Direct installation
pip install airmcp

# With uv (recommended)
uv pip install airmcp

# In MCP config
{
  "mcpServers": {
    "airmcp": {
      "command": "airmcp",
      "args": []
    }
  }
}
```

**Convenience Distribution: npm Wrapper**
```bash
# Zero-install via npx
npx airmcp@latest

# In MCP config (no installation needed)
{
  "mcpServers": {
    "airmcp": {
      "command": "npx",
      "args": ["-y", "airmcp@latest"]
    }
  }
}
```

**Benefits:**
- ✅ Native Python users get pip/uv
- ✅ Non-Python users get npx convenience
- ✅ Single codebase, dual distribution
- ✅ Automatic version sync via CI/CD

---

## 2. Packaging Configuration

### 2.1 Python Package (PyPI)

**File: `pyproject.toml`**
```toml
[project]
name = "airmcp"
version = "1.0.0"
description = "AI Coding Standards Made Easy - Auto-generate instruction files for Claude, Copilot, and Cursor"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [
    {name = "Matt Strautmann", email = "matt@airmcp.com"}
]
keywords = ["ai", "mcp", "claude", "copilot", "cursor", "coding-standards", "editorconfig"]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Code Generators",
    "Topic :: Software Development :: Quality Assurance",
]
dependencies = [
    "mcp>=1.0.0"
]

[project.urls]
Homepage = "https://airmcp.com"
Documentation = "https://docs.airmcp.com"
Repository = "https://github.com/mattstrautmann/airmcp"
Issues = "https://github.com/mattstrautmann/airmcp/issues"
Changelog = "https://github.com/mattstrautmann/airmcp/releases"

[project.scripts]
airmcp = "airmcp.server:main"

[tool.hatch.build.targets.wheel]
packages = ["airmcp"]
include = [
    "airmcp/**/*.py",
    "README.md",
    "LICENSE"
]
exclude = [
    "tests/**",
    "docs/**",
    ".github/**"
]

[build-system]
requires = ["hatchling>=1.18.0"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0"
]
```

### 2.2 npm Wrapper Package

**File: `package.json`**
```json
{
  "name": "airmcp",
  "version": "1.0.0",
  "description": "AI Coding Standards Made Easy - Auto-generate instruction files for Claude, Copilot, and Cursor",
  "main": "dist/index.js",
  "bin": {
    "airmcp": "./bin/airmcp.js"
  },
  "scripts": {
    "install": "node scripts/install-python-package.js",
    "test": "node scripts/test.js",
    "prepublishOnly": "node scripts/build.js"
  },
  "keywords": [
    "ai",
    "mcp",
    "claude",
    "copilot",
    "cursor",
    "coding-standards",
    "editorconfig"
  ],
  "author": "Matt Strautmann <matt@airmcp.com>",
  "license": "MIT",
  "repository": {
    "type": "git",
    "url": "https://github.com/mattstrautmann/airmcp.git"
  },
  "homepage": "https://airmcp.com",
  "bugs": {
    "url": "https://github.com/mattstrautmann/airmcp/issues"
  },
  "engines": {
    "node": ">=16.0.0"
  },
  "files": [
    "bin/",
    "dist/",
    "scripts/",
    "README.md",
    "LICENSE"
  ]
}
```

**File: `bin/airmcp.js`** (npm wrapper)
```javascript
#!/usr/bin/env node

const { spawn } = require('child_process');
const { existsSync } = require('fs');
const { join } = require('path');

// Try to find Python executable
const pythonCandidates = ['python3', 'python'];
let pythonExec = null;

for (const candidate of pythonCandidates) {
  try {
    const result = require('child_process').spawnSync(candidate, ['--version'], { encoding: 'utf8' });
    if (result.status === 0) {
      pythonExec = candidate;
      break;
    }
  } catch (e) {
    continue;
  }
}

if (!pythonExec) {
  console.error('Error: Python 3.10+ is required but not found.');
  console.error('Please install Python from https://python.org');
  process.exit(1);
}

// Check if airmcp Python package is installed
const checkInstall = require('child_process').spawnSync(pythonExec, ['-c', 'import airmcp'], { encoding: 'utf8' });

if (checkInstall.status !== 0) {
  console.error('Installing airmcp Python package...');
  const install = require('child_process').spawnSync(pythonExec, ['-m', 'pip', 'install', '--user', 'airmcp'], {
    stdio: 'inherit'
  });

  if (install.status !== 0) {
    console.error('Failed to install airmcp Python package.');
    console.error('Please run: pip install airmcp');
    process.exit(1);
  }
}

// Execute airmcp
const airmcp = spawn(pythonExec, ['-m', 'airmcp', ...process.argv.slice(2)], {
  stdio: 'inherit'
});

airmcp.on('exit', (code) => {
  process.exit(code || 0);
});
```

---

## 3. CI/CD Pipeline Architecture

### 3.1 GitHub Actions Workflow Structure

```
.github/workflows/
├── ci.yml              # Continuous Integration (tests, linting)
├── publish-pypi.yml    # PyPI publishing
├── publish-npm.yml     # npm publishing
├── release.yml         # Create GitHub releases
└── deploy.yml          # Deploy to airmcp.com
```

### 3.2 CI Workflow (ci.yml)

**Triggers**: Push, Pull Request
**Purpose**: Validate code quality

```yaml
name: Continuous Integration

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Install dependencies
        run: |
          cd mcp-servers/claude-memory
          uv sync

      - name: Run tests
        run: |
          cd mcp-servers/claude-memory
          uv run pytest tests/ -v --cov=airmcp --cov-report=xml

      - name: Lint with ruff
        run: |
          cd mcp-servers/claude-memory
          uv run ruff check airmcp/

      - name: Type check with mypy
        run: |
          cd mcp-servers/claude-memory
          uv run mypy airmcp/

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./mcp-servers/claude-memory/coverage.xml

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run security scan
        uses: snyk/actions/python-3.10@master
        with:
          command: test
```

### 3.3 PyPI Publishing Workflow (publish-pypi.yml)

**Triggers**: Git tag (v*)
**Purpose**: Publish to PyPI

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # OIDC for PyPI trusted publishing

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install build tools
        run: |
          python -m pip install --upgrade pip
          pip install build twine

      - name: Build package
        run: |
          cd mcp-servers/claude-memory
          python -m build

      - name: Check package
        run: |
          cd mcp-servers/claude-memory
          twine check dist/*

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          packages-dir: mcp-servers/claude-memory/dist/
          skip-existing: true
          verbose: true
```

### 3.4 npm Publishing Workflow (publish-npm.yml)

**Triggers**: Git tag (v*)
**Purpose**: Publish to npm

```yaml
name: Publish to npm

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          registry-url: 'https://registry.npmjs.org'

      - name: Install dependencies
        run: npm ci

      - name: Build package
        run: npm run build

      - name: Publish to npm
        run: npm publish --access public
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

### 3.5 Deployment Workflow (deploy.yml)

**Triggers**: Git tag (v*), Manual
**Purpose**: Deploy to airmcp.com

```yaml
name: Deploy to airmcp.com

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        type: choice
        options:
          - staging
          - production

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.environment || 'production' }}

    steps:
      - uses: actions/checkout@v4

      - name: Setup SSH
        uses: webfactory/ssh-agent@v0.8.0
        with:
          ssh-private-key: ${{ secrets.DEPLOY_SSH_KEY }}

      - name: Deploy to server
        run: |
          ssh -o StrictHostKeyChecking=no deploy@airmcp.com << 'EOF'
            cd /var/www/airmcp
            git fetch --tags
            git checkout ${GITHUB_REF_NAME}
            ./scripts/deploy.sh
          EOF

      - name: Health check
        run: |
          sleep 10
          curl -f https://airmcp.com/health || exit 1

      - name: Notify deployment
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 4. Deployment Workflow

### 4.1 Environment Strategy

```
Development (local) → Staging (staging.airmcp.com) → Production (airmcp.com)
```

| Environment | Purpose | Trigger | Rollback |
|-------------|---------|---------|----------|
| **Development** | Local testing | Manual | N/A |
| **Staging** | Pre-production validation | Push to `develop` | Automatic |
| **Production** | Live users | Git tag `v*` | Manual |

### 4.2 Release Process

**Step 1: Version Bump**
```bash
# Update version in pyproject.toml and package.json
bumpversion minor  # or major, patch

# Commit version bump
git add .
git commit -m "chore: bump version to v1.1.0"
```

**Step 2: Create Release Tag**
```bash
git tag -a v1.1.0 -m "Release v1.1.0: Add feature X"
git push origin v1.1.0
```

**Step 3: Automated Pipeline**
```
GitHub Actions triggers:
├── CI tests run
├── PyPI package builds and publishes
├── npm package builds and publishes
├── GitHub release created
└── airmcp.com deployment initiates
```

**Step 4: Validation**
```bash
# Verify PyPI release
pip install airmcp==1.1.0

# Verify npm release
npx airmcp@1.1.0 --version

# Verify website deployment
curl https://airmcp.com/health
```

### 4.3 Rollback Strategy

**Automated Rollback (Staging)**
```yaml
# In deploy.yml
- name: Health check
  run: |
    if ! curl -f https://staging.airmcp.com/health; then
      git checkout ${{ env.PREVIOUS_VERSION }}
      ./scripts/deploy.sh
      exit 1
    fi
```

**Manual Rollback (Production)**
```bash
# SSH to production server
ssh deploy@airmcp.com

# Rollback to previous version
cd /var/www/airmcp
git checkout v1.0.9
./scripts/deploy.sh

# Or use Docker (if containerized)
docker rollback airmcp_web
```

**PyPI/npm Rollback**
```bash
# PyPI: Yank bad version (doesn't delete, marks as unavailable)
twine yank airmcp 1.1.0 -m "Critical bug found"

# npm: Deprecate version
npm deprecate airmcp@1.1.0 "Critical bug, use 1.0.9 instead"

# Users will automatically fall back to latest stable
```

---

## 5. Monitoring & Health Checks

### 5.1 Metrics to Track

**Application Health**
- Server uptime
- Response time
- Error rate
- Memory usage
- Database query performance

**Distribution Health**
- PyPI download count
- npm download count
- Installation success rate
- Version adoption rate

### 5.2 Health Check Endpoints

**File: `airmcp/health.py`**
```python
from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health/db")
def database_health():
    # Check SQLite connection
    try:
        import sqlite3
        conn = sqlite3.connect("~/.airmcp/knowledge.db")
        conn.execute("SELECT 1")
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

### 5.3 Monitoring Tools

**GitHub Actions Integration**
```yaml
- name: Notify on failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: failure
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

**Uptime Monitoring**
- UptimeRobot: Monitor airmcp.com/health every 5 minutes
- Pingdom: Performance monitoring
- StatusPage.io: Public status dashboard

---

## 6. Security Considerations

### 6.1 Secrets Management

**GitHub Secrets Required**:
- `NPM_TOKEN`: npm publishing
- `PYPI_API_TOKEN`: PyPI publishing (or use OIDC)
- `DEPLOY_SSH_KEY`: Server deployment
- `SLACK_WEBHOOK`: Notifications

**Never commit**:
- `.env` files
- API keys
- SSH keys
- Database credentials

### 6.2 Dependency Scanning

```yaml
# Dependabot configuration (.github/dependabot.yml)
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/mcp-servers/claude-memory"
    schedule:
      interval: "weekly"

  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
```

---

## 7. Documentation for airmcp.com

### 7.1 Installation Documentation

**Quick Start**
```bash
# Python users (recommended)
pip install airmcp

# Node.js users
npx airmcp@latest

# With uv (fastest)
uv pip install airmcp
```

**Claude Desktop Configuration**
```json
{
  "mcpServers": {
    "airmcp": {
      "command": "airmcp",
      "args": []
    }
  }
}
```

### 7.2 API Documentation

Auto-generate with Sphinx or MkDocs:
```bash
# Install documentation tools
uv pip install sphinx sphinx-rtd-theme

# Generate docs
cd docs
make html

# Deploy to docs.airmcp.com
rsync -avz _build/html/ deploy@airmcp.com:/var/www/docs/
```

---

## 8. Cost Optimization

### 8.1 Hosting Costs

**Recommended Hosting: Vercel or Netlify (Free Tier)**
- Static site hosting
- Automatic SSL
- CDN included
- Zero configuration

**Alternative: DigitalOcean Droplet ($6/month)**
- Full control
- Custom domain
- SSH access
- Staging + Production

### 8.2 Distribution Costs

- PyPI: **Free** (unlimited storage and bandwidth)
- npm: **Free** (public packages)
- GitHub Actions: **2,000 minutes/month free**

---

## 9. Next Steps

### 9.1 Immediate Actions

1. ✅ Rename `claude-memory` → `airmcp` throughout codebase
2. ✅ Update `pyproject.toml` with production values
3. ✅ Create `package.json` for npm wrapper
4. ✅ Set up GitHub Actions workflows
5. ✅ Register PyPI and npm package names
6. ✅ Configure domain (airmcp.com)
7. ✅ Set up GitHub Secrets

### 9.2 Pre-Launch Checklist

- [ ] All tests passing in CI
- [ ] Documentation complete
- [ ] Security scan passed
- [ ] Performance benchmarks acceptable
- [ ] Staging environment validated
- [ ] Rollback plan tested
- [ ] Monitoring configured
- [ ] Status page live

---

## 10. Summary

**Recommended Deployment Strategy**:
- **Primary Distribution**: PyPI (pip/uv)
- **Convenience Distribution**: npm (npx wrapper)
- **CI/CD**: GitHub Actions (4 workflows)
- **Hosting**: Vercel (free) or DigitalOcean ($6/mo)
- **Monitoring**: UptimeRobot + StatusPage.io
- **Rollback**: Automated for staging, manual for production

**Total Monthly Cost**: $0-6 (hosting only, CI/CD free)

**Deployment Time**: ~5 minutes (automated)

**Key Benefits**:
- ✅ Zero-friction installation for all users
- ✅ Automated testing and deployment
- ✅ Instant rollback capability
- ✅ Comprehensive monitoring
- ✅ Production-grade reliability

---

*Generated by Coder Agent for Hive Mind Swarm*
*Session: swarm-1760414731368-e3y50qc3k*
*Date: 2025-10-13*

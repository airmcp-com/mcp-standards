# Publishing Guide for MCP Standards

This guide documents how to publish MCP Standards to various registries.

## Prerequisites

1. **PyPI Account**: Create account at https://pypi.org/account/register/
2. **API Token**: Generate at https://pypi.org/manage/account/token/
3. **uv installed**: Ensure `uv` is installed and updated

## Publishing to PyPI

### First Time Setup

```bash
# Create PyPI API token at: https://pypi.org/manage/account/token/
# Save token to ~/.pypirc:

cat > ~/.pypirc << 'EOF'
[distutils]
index-servers = pypi

[pypi]
username = __token__
password = pypi-YOUR_API_TOKEN_HERE
EOF

chmod 600 ~/.pypirc
```

### Build and Publish

```bash
# 1. Ensure version is updated in pyproject.toml
# Check: version = "0.1.0-alpha.1"

# 2. Build the package
uv build

# 3. Check the built packages
ls -la dist/
# Should see: mcp_standards-0.1.0a1-py3-none-any.whl and .tar.gz

# 4. Publish to PyPI
uv publish

# Or use twine for more control:
pip install twine
twine upload dist/*
```

### Test Installation

```bash
# Create fresh environment
uv venv test-env
source test-env/bin/activate

# Install from PyPI
pip install mcp-standards

# Verify installation
python -c "import mcp_standards; print(mcp_standards.__version__)"

# Test MCP server
mcp-standards --help
```

## Publishing to mcp.so Registry

The MCP registry at https://mcp.so is for discovery and listing.

### Steps:

1. Visit https://mcp.so/submit
2. Fill in the form:
   - **Name**: MCP Standards
   - **Description**: Self-learning AI standards system that learns from corrections
   - **Repository**: https://github.com/airmcp-com/mcp-standards
   - **Category**: Developer Tools
   - **Tags**: ai-assistant, knowledge-base, self-learning, claude, standards
3. Submit for review

### registry.json Format (if required):

```json
{
  "name": "mcp-standards",
  "version": "0.1.0-alpha.1",
  "description": "Self-learning AI standards system",
  "author": "Matt Strautmann",
  "license": "MIT",
  "repository": "https://github.com/airmcp-com/mcp-standards",
  "homepage": "https://github.com/airmcp-com/mcp-standards",
  "keywords": ["ai", "claude", "mcp", "standards", "self-learning"],
  "install": {
    "pip": "pip install mcp-standards",
    "uv": "uv pip install mcp-standards"
  }
}
```

## Publishing to npm (Optional - for npx support)

While MCP Standards is Python-based, you can create an npm wrapper for `npx` support.

### Create package.json

```json
{
  "name": "@mcp-standards/server",
  "version": "0.1.0-alpha.1",
  "description": "Self-learning AI standards system (Python MCP server)",
  "bin": {
    "mcp-standards": "./bin/mcp-standards.js"
  },
  "scripts": {
    "postinstall": "pip install mcp-standards"
  },
  "repository": {
    "type": "git",
    "url": "https://github.com/airmcp-com/mcp-standards"
  },
  "keywords": ["mcp", "ai", "claude", "standards"],
  "author": "Matt Strautmann",
  "license": "MIT"
}
```

### Create bin/mcp-standards.js

```javascript
#!/usr/bin/env node
const { spawn } = require('child_process');

const python = spawn('python', ['-m', 'mcp_standards.server'], {
  stdio: 'inherit'
});

python.on('exit', (code) => {
  process.exit(code);
});
```

### Publish to npm

```bash
npm login
npm publish --access public
```

## Version Bumping

### For next release:

```bash
# Update version in pyproject.toml
# Example: 0.1.0-alpha.1 → 0.1.0-alpha.2 or 0.1.0

# Update CHANGELOG.md with new version

# Commit changes
git add pyproject.toml CHANGELOG.md
git commit -m "Bump version to X.Y.Z"

# Tag release
git tag -a vX.Y.Z -m "Release vX.Y.Z"

# Push
git push origin main --tags

# Build and publish
uv build
uv publish

# Create GitHub release
gh release create vX.Y.Z --title "vX.Y.Z" --notes-file CHANGELOG.md
```

## Troubleshooting

### PyPI Upload Fails

```bash
# Check package validity
twine check dist/*

# Test on TestPyPI first
twine upload --repository testpypi dist/*
```

### Version Conflicts

```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info

# Rebuild
uv build
```

### MCP Registry Issues

- Ensure README.md is comprehensive (registry scrapes it)
- Add good keywords for discoverability
- Include screenshots if possible

## Post-Publication Checklist

- [ ] Verify PyPI package page: https://pypi.org/project/mcp-standards/
- [ ] Test fresh installation: `pip install mcp-standards`
- [ ] Update README installation instructions
- [ ] Announce on GitHub Discussions
- [ ] Submit to mcp.so registry
- [ ] Update related documentation

## Support

For publishing issues, contact: matt.strautmann@gmail.com

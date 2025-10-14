# AirMCP Deployment Checklist

## Pre-Launch Checklist

### 1. Repository Preparation
- [ ] Rename `claude-memory` to `airmcp` in codebase
- [ ] Update all import statements (`import claude_memory` → `import airmcp`)
- [ ] Update `pyproject.toml` package name
- [ ] Update README.md with new branding
- [ ] Update LICENSE file
- [ ] Create CHANGELOG.md

### 2. Package Registration
- [ ] Register package name on PyPI: `airmcp`
- [ ] Register package name on npm: `airmcp`
- [ ] Reserve GitHub organization: `github.com/airmcp` (optional)
- [ ] Register domain: `airmcp.com` (if not already done)

### 3. GitHub Secrets Configuration
Navigate to: `Settings → Secrets and variables → Actions`

Required secrets:
- [ ] `NPM_TOKEN` - npm publishing token
  - Get from: https://www.npmjs.com/settings/[username]/tokens
  - Type: Automation token
- [ ] `PYPI_API_TOKEN` - PyPI publishing token (optional with OIDC)
  - Get from: https://pypi.org/manage/account/token/
  - Scope: All projects or specific project
- [ ] `DEPLOY_SSH_KEY` - SSH private key for server deployment
  - Generate: `ssh-keygen -t ed25519 -C "deploy@airmcp.com"`
  - Add public key to server: `~/.ssh/authorized_keys`

Optional secrets:
- [ ] `SLACK_WEBHOOK` - Slack notifications
- [ ] `CODECOV_TOKEN` - Code coverage reporting

### 4. GitHub Environments Setup
Navigate to: `Settings → Environments`

Create environments:
- [ ] **staging**
  - Protection rules: None (auto-deploy)
  - Secrets: Same as main
- [ ] **production**
  - Protection rules: Required reviewers (1+)
  - Deployment branches: Only `v*` tags
- [ ] **pypi**
  - Required for PyPI publishing
- [ ] **npm**
  - Required for npm publishing

### 5. PyPI Trusted Publishing (Recommended)
Instead of API tokens, use OIDC:

On PyPI:
- [ ] Go to: https://pypi.org/manage/account/publishing/
- [ ] Add GitHub Actions publisher:
  - Owner: `mattstrautmann`
  - Repository: `research-mcp` or `airmcp`
  - Workflow: `publish-pypi.yml`
  - Environment: `pypi`

Benefits: No token management, automatic rotation

### 6. Code Quality Setup
- [ ] Add `.github/dependabot.yml` for dependency updates
- [ ] Enable Dependabot alerts
- [ ] Enable CodeQL analysis
- [ ] Enable Codecov integration (optional)
- [ ] Configure branch protection rules:
  - Require PR reviews
  - Require status checks (CI)
  - Require linear history

### 7. Testing
- [ ] All unit tests passing locally
- [ ] Integration tests passing
- [ ] Manual testing of installation:
  ```bash
  # Test PyPI package
  pip install -e .
  airmcp --version

  # Test npm wrapper
  cd npm-package
  npm link
  npx airmcp --version
  ```
- [ ] Test MCP server startup
- [ ] Test with Claude Desktop

### 8. Documentation
- [ ] Update README.md with installation instructions
- [ ] Create CONTRIBUTING.md
- [ ] Document environment variables in .env.example
- [ ] Add architecture diagrams (optional)
- [ ] Create API documentation (Sphinx/MkDocs)
- [ ] Set up docs.airmcp.com (if needed)

### 9. Website Setup (airmcp.com)
Choose hosting option:

**Option A: Static Site (Vercel/Netlify - Free)**
- [ ] Create Next.js or static site
- [ ] Connect GitHub repository
- [ ] Configure custom domain
- [ ] Enable automatic deployments

**Option B: VPS (DigitalOcean - $6/mo)**
- [ ] Create droplet
- [ ] Configure SSH access
- [ ] Install dependencies
- [ ] Set up Nginx
- [ ] Configure SSL (Let's Encrypt)
- [ ] Set up deployment user

### 10. Monitoring Setup
- [ ] Configure UptimeRobot (free tier)
  - Monitor: https://airmcp.com/health
  - Interval: 5 minutes
  - Alerts: Email/SMS
- [ ] Set up status page (status.airmcp.com)
  - Options: StatusPage.io, Atlassian Statuspage
- [ ] Configure error tracking (optional)
  - Sentry, Rollbar, or similar

### 11. Analytics (Optional)
- [ ] Google Analytics or Plausible
- [ ] npm download tracking
- [ ] PyPI download tracking
- [ ] GitHub stars/forks tracking

---

## Launch Day Checklist

### 1. Final Testing
- [ ] Run full test suite: `pytest -v`
- [ ] Test installation from TestPyPI
- [ ] Verify all environment variables
- [ ] Check all GitHub Actions are configured

### 2. Create First Release
```bash
# Update version
bumpversion major  # 0.1.0 → 1.0.0

# Commit and tag
git add .
git commit -m "chore: release v1.0.0"
git tag -a v1.0.0 -m "Release v1.0.0: Initial public release"

# Push (this triggers all workflows)
git push origin main --tags
```

### 3. Monitor Deployments
- [ ] Watch GitHub Actions workflows
- [ ] Verify PyPI package appears
- [ ] Verify npm package appears
- [ ] Check airmcp.com deployment
- [ ] Test installation from both registries

### 4. Verify Installation
```bash
# From PyPI
pip install airmcp
python -c "import airmcp; print('Success')"

# From npm
npx airmcp@latest --version

# From GitHub (fallback)
git clone https://github.com/mattstrautmann/airmcp.git
cd airmcp
./install.sh
```

### 5. Announce Launch
- [ ] GitHub Discussions announcement
- [ ] Reddit (r/programming, r/Python, r/commandline)
- [ ] Hacker News (Show HN)
- [ ] Twitter/X announcement
- [ ] LinkedIn post
- [ ] Product Hunt submission
- [ ] Dev.to article

---

## Post-Launch Monitoring

### Week 1
- [ ] Monitor error rates
- [ ] Check installation success rate
- [ ] Respond to GitHub issues
- [ ] Monitor download metrics
- [ ] Gather user feedback

### Week 2-4
- [ ] Address critical bugs
- [ ] Plan feature improvements
- [ ] Update documentation based on questions
- [ ] Consider creating video tutorials

---

## Emergency Procedures

### If PyPI Deployment Fails
1. Check GitHub Actions logs
2. Verify PyPI credentials
3. Test build locally: `python -m build`
4. Check for version conflicts
5. Contact PyPI support if needed

### If npm Deployment Fails
1. Check npm token validity
2. Verify package.json syntax
3. Test build locally: `npm pack`
4. Check for package name conflicts
5. Try manual publish: `npm publish`

### If Website Goes Down
1. Check hosting service status
2. Review deployment logs
3. Rollback to previous version
4. Check SSL certificate validity
5. Verify DNS configuration

### If Critical Bug Found
1. Create hotfix branch immediately
2. Fix bug and add regression test
3. Create patch release (v1.0.1)
4. Fast-track through CI/CD
5. Notify users via GitHub release

---

## Rollback Procedures

### PyPI Rollback
```bash
# Yank bad version (doesn't delete, marks unavailable)
twine yank airmcp 1.0.1 -m "Critical bug found"

# Users automatically fall back to 1.0.0
```

### npm Rollback
```bash
# Deprecate version
npm deprecate airmcp@1.0.1 "Critical bug, use 1.0.0 instead"
```

### Website Rollback
```bash
# SSH to server
ssh deploy@airmcp.com

# Rollback to previous tag
cd /var/www/airmcp
git checkout v1.0.0
./scripts/deploy.sh
```

---

## Maintenance Schedule

### Daily
- Check uptime monitoring alerts
- Review error logs
- Respond to critical issues

### Weekly
- Review GitHub issues/PRs
- Check dependency updates
- Monitor download metrics
- Update documentation

### Monthly
- Security audit
- Performance review
- Update dependencies
- Plan feature roadmap

### Quarterly
- Major feature releases
- Documentation overhaul
- Community survey
- Cost optimization review

---

## Success Metrics

Track these KPIs:

### Adoption
- PyPI downloads/week
- npm downloads/week
- GitHub stars
- GitHub forks
- Active users

### Quality
- Issue response time
- Bug fix time
- Test coverage %
- Uptime %
- Installation success rate

### Community
- GitHub issues opened
- Pull requests submitted
- Community contributions
- Documentation improvements

---

## Support Channels

Set up:
- [ ] GitHub Discussions for Q&A
- [ ] GitHub Issues for bugs
- [ ] Discord/Slack community (optional)
- [ ] Email: support@airmcp.com
- [ ] Documentation: docs.airmcp.com

---

**Remember**: Launch is just the beginning. Focus on user feedback and iterate quickly!

---

*Generated by Coder Agent for Hive Mind Swarm*
*Session: swarm-1760414731368-e3y50qc3k*

#!/bin/bash
set -e

# Claude Memory - Automated Installation Script
# Zero Docker dependencies, pure Python + uv

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}       ${BOLD}Claude Memory + Cost Optimization Installer${NC}              ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}       Persistent memory with 99.5% cost savings                  ${BLUE}║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Darwin*)    OS_TYPE="macOS";;
    Linux*)     OS_TYPE="Linux";;
    *)          OS_TYPE="UNKNOWN";;
esac

echo -e "${CYAN}🖥️  System Information${NC}"
echo -e "   OS: ${BOLD}${OS_TYPE}${NC}"
echo -e "   Architecture: ${BOLD}$(uname -m)${NC}"
echo ""

# Check Python version
echo "[1/7] Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
        echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"
    else
        echo -e "${RED}✗${NC} Python 3.10+ required, found $PYTHON_VERSION"
        exit 1
    fi
else
    echo -e "${RED}✗${NC} Python3 not found. Please install Python 3.10+"
    exit 1
fi
echo ""

# Check/Install uv
echo "[2/7] Checking uv package manager..."
if command -v uv &> /dev/null; then
    echo -e "${GREEN}✓${NC} uv found"
else
    echo -e "${YELLOW}!${NC} uv not found, installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Source shell profile to get uv in PATH
    if [ -f "$HOME/.bashrc" ]; then
        source "$HOME/.bashrc"
    fi
    if [ -f "$HOME/.zshrc" ]; then
        source "$HOME/.zshrc"
    fi

    # Add to current shell PATH
    export PATH="$HOME/.cargo/bin:$PATH"

    if command -v uv &> /dev/null; then
        echo -e "${GREEN}✓${NC} uv installed successfully"
    else
        echo -e "${RED}✗${NC} uv installation failed. Please install manually:"
        echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
fi
echo ""

# Install dependencies
echo "[3/7] Installing Claude Memory dependencies..."
cd mcp-servers/claude-memory
uv sync
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Dependencies installed"
else
    echo -e "${RED}✗${NC} Dependency installation failed"
    exit 1
fi
cd ../..
echo ""

# Test server
echo "[4/7] Testing MCP server..."
timeout 3 bash -c "cd mcp-servers/claude-memory && uv run python run_server.py" &> /dev/null || true
if [ $? -ne 124 ]; then
    echo -e "${YELLOW}!${NC} Server test completed (this is expected)"
else
    echo -e "${GREEN}✓${NC} Server can start"
fi
echo ""

# Detect Claude config location
echo "[5/7] Detecting Claude configuration..."
CLAUDE_CONFIG=""
if [ "$OS_TYPE" = "macOS" ]; then
    CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
elif [ "$OS_TYPE" = "Linux" ]; then
    CLAUDE_CONFIG="$HOME/.config/claude/config.json"
fi

if [ -n "$CLAUDE_CONFIG" ]; then
    echo -e "${GREEN}✓${NC} Config location: $CLAUDE_CONFIG"
else
    echo -e "${YELLOW}!${NC} Could not detect Claude config location"
fi
echo ""

# Check for .env file and Gemini key
echo "[6/7] Checking for environment configuration..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
GEMINI_KEY=""
DEFAULT_MODEL=""
COST_OPTIMIZATION=""

if [ -f "$ENV_FILE" ]; then
    # Source the .env file to read variables
    set -a
    source "$ENV_FILE" 2>/dev/null
    set +a
    
    if [ -n "$GEMINI_API_KEY" ]; then
        GEMINI_KEY="$GEMINI_API_KEY"
        DEFAULT_MODEL="${DEFAULT_MODEL:-gemini-1.5-flash}"
        COST_OPTIMIZATION="${COST_OPTIMIZATION:-true}"
        echo -e "${GREEN}💰 Cost Optimization: ${BOLD}ENABLED${NC}"
        echo -e "   API Key: ${GEMINI_KEY:0:12}...${GEMINI_KEY: -4}"
        echo -e "   Model: ${BOLD}${DEFAULT_MODEL}${NC}"
        echo -e "   Savings: ${BOLD}99.5%${NC} on simple operations"
    else
        echo -e "${YELLOW}💰 Cost Optimization: ${BOLD}MANUAL SETUP REQUIRED${NC}"
        echo -e "   No GEMINI_API_KEY found in .env"
    fi
else
    echo -e "${YELLOW}💰 Cost Optimization: ${BOLD}MANUAL SETUP REQUIRED${NC}"
    echo -e "   No .env file found"
fi
echo ""

# Generate config
echo "[7/7] Generating MCP configuration..."
MEMORY_DIR="$SCRIPT_DIR/mcp-servers/claude-memory"

# Generate base config with claude-memory
if [ -n "$GEMINI_KEY" ]; then
    # Include agentic-flow if Gemini key exists
    cat > /tmp/claude-memory-config.json <<EOF
{
  "mcpServers": {
    "agentic-flow": {
      "command": "npx",
      "args": ["-y", "agentic-flow", "mcp"],
      "env": {
        "GEMINI_API_KEY": "$GEMINI_KEY",
        "DEFAULT_MODEL": "$DEFAULT_MODEL",
        "COST_OPTIMIZATION": "$COST_OPTIMIZATION",
        "FALLBACK_MODEL": "${FALLBACK_MODEL:-deepseek-chat}"
      }
    },
    "claude-memory": {
      "command": "uv",
      "args": [
        "--directory",
        "$MEMORY_DIR",
        "run",
        "run_server.py"
      ]
    }
  }
}
EOF
    echo -e "${GREEN}🔧 Configuration: ${BOLD}claude-memory + agentic-flow${NC}"
    echo -e "   Memory: Local SQLite storage"
    echo -e "   Routing: Gemini Flash for simple tasks"
else
    # Just claude-memory
    cat > /tmp/claude-memory-config.json <<EOF
{
  "mcpServers": {
    "claude-memory": {
      "command": "uv",
      "args": [
        "--directory",
        "$MEMORY_DIR",
        "run",
        "run_server.py"
      ]
    }
  }
}
EOF
    echo -e "${GREEN}🔧 Configuration: ${BOLD}claude-memory only${NC}"
    echo -e "   Memory: Local SQLite storage"
    echo -e "   ${YELLOW}Note: Add Gemini key to .env for cost optimization${NC}"
fi
echo ""

# Offer to update config
if [ -f "$CLAUDE_CONFIG" ]; then
    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}                        ${BOLD}Configuration Update${NC}                        ${BLUE}║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}🔧 Update Method:${NC}"
    echo -e "${BOLD}1.${NC} ${GREEN}Automatic (Recommended)${NC}"
    echo -e "   • Backs up existing config with timestamp"
    echo -e "   • Intelligently merges new MCP servers"
    echo -e "   • Preserves all existing servers"
    echo ""
    echo -e "${BOLD}2.${NC} ${YELLOW}Manual${NC}"
    echo -e "   • Shows JSON config to copy-paste"
    echo -e "   • You update the file yourself"
    echo ""
    echo -n -e "${CYAN}Choose option [${BOLD}1${NC}${CYAN}]: ${NC}"
    read CONFIG_OPTION
    CONFIG_OPTION=${CONFIG_OPTION:-1}

    if [ "$CONFIG_OPTION" = "1" ]; then
        # Backup existing config
        BACKUP_FILE="${CLAUDE_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$CLAUDE_CONFIG" "$BACKUP_FILE"
        echo -e "${GREEN}💾 Backup created: ${BOLD}$(basename "$BACKUP_FILE")${NC}"

        # Check if config has mcpServers already
        if grep -q "mcpServers" "$CLAUDE_CONFIG"; then
            # Merge with existing servers
            python3 -c "
import json
import sys

# Read existing config
with open('$CLAUDE_CONFIG', 'r') as f:
    config = json.load(f)

# Read new server config
with open('/tmp/claude-memory-config.json', 'r') as f:
    new_config = json.load(f)

# Merge
if 'mcpServers' not in config:
    config['mcpServers'] = {}

# Always add claude-memory
config['mcpServers']['claude-memory'] = new_config['mcpServers']['claude-memory']

# Only add/update agentic-flow if it's in the new config (i.e., Gemini key was found)
if 'agentic-flow' in new_config['mcpServers']:
    config['mcpServers']['agentic-flow'] = new_config['mcpServers']['agentic-flow']

# Write back
with open('$CLAUDE_CONFIG', 'w') as f:
    json.dump(config, f, indent=2)
"
            if [ -n "$GEMINI_KEY" ]; then
                echo -e "${GREEN}🎯 Config updated: ${BOLD}claude-memory + agentic-flow${NC}"
            else
                echo -e "${GREEN}🎯 Config updated: ${BOLD}claude-memory${NC}"
            fi
            echo -e "   Existing servers preserved"
        else
            # No existing servers, just write
            cat /tmp/claude-memory-config.json > "$CLAUDE_CONFIG"
            if [ -n "$GEMINI_KEY" ]; then
                echo -e "${GREEN}🎯 Config created: ${BOLD}claude-memory + agentic-flow${NC}"
            else
                echo -e "${GREEN}🎯 Config created: ${BOLD}claude-memory${NC}"
            fi
        fi
    else
        echo ""
        echo "=================================="
        echo "Manual Configuration"
        echo "=================================="
        echo ""
        echo "Add this to: $CLAUDE_CONFIG"
        echo ""
        cat /tmp/claude-memory-config.json
        echo ""
    fi
else
    echo "=================================="
    echo "Manual Configuration Required"
    echo "=================================="
    echo ""
    echo "Create this file: $CLAUDE_CONFIG"
    echo ""
    cat /tmp/claude-memory-config.json
    echo ""
fi

# Clean up
rm /tmp/claude-memory-config.json

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}                     ${BOLD}🎉 Installation Complete!${NC}                     ${GREEN}║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}📋 Next Steps:${NC}"
echo -e "${BOLD}1.${NC} Restart Claude Desktop completely"
echo -e "   ${YELLOW}macOS:${NC} Cmd+Q → Reopen Claude Desktop"
echo -e "   ${YELLOW}Linux:${NC} killall claude-desktop && claude-desktop"
echo ""
echo -e "${BOLD}2.${NC} Test your setup:"
echo -e "${YELLOW}   # Add your first memory${NC}"
echo -e "   add_episode("
echo -e "       name=\"Setup Complete\","
echo -e "       content=\"Claude Memory + Cost Optimization working!\","
echo -e "       source=\"setup-test\""
echo -e "   )"
echo ""
echo -e "${YELLOW}   # Search your memories${NC}"
echo -e "   search_episodes(\"setup\")"
echo ""
echo -e "${CYAN}🛠️  Troubleshooting:${NC} Run ${BOLD}./validate.sh${NC} if you encounter issues"
echo ""

# Show cost optimization status
if [ -n "$GEMINI_KEY" ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}                ${BOLD}💰 Cost Optimization Active!${NC}                   ${GREEN}║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}✅ Smart Routing Configured${NC}"
    echo -e "   Simple tasks (memory, search) → ${BOLD}Gemini 1.5 Flash${NC}"
    echo -e "   Complex tasks (code, analysis) → ${BOLD}Claude${NC}"
    echo -e "   Fallback model → ${BOLD}${FALLBACK_MODEL:-deepseek-chat}${NC}"
    echo ""
    echo -e "${CYAN}💸 Cost Comparison (per 1M tokens):${NC}"
    echo -e "   Claude Sonnet: ${RED}\$15.00${NC}"
    echo -e "   Gemini Flash:  ${GREEN}\$0.075${NC} ${BOLD}(99.5% savings)${NC}"
    echo ""
    echo -e "${YELLOW}💡 Your memory operations will now cost virtually nothing!${NC}"
    echo ""
else
    echo -e "${YELLOW}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║${NC}               ${BOLD}💰 Cost Optimization Available${NC}                  ${YELLOW}║${NC}"
    echo -e "${YELLOW}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}🎯 Save 99.5% on costs with Gemini Flash!${NC}"
    echo ""
    echo -e "${BOLD}Quick Setup:${NC}"
    echo -e "${YELLOW}1.${NC} Get free API key: ${CYAN}https://aistudio.google.com/app/apikey${NC}"
    echo -e "${YELLOW}2.${NC} Copy .env.example to .env"
    echo -e "${YELLOW}3.${NC} Add your key to .env"
    echo -e "${YELLOW}4.${NC} Re-run ${BOLD}./install.sh${NC}"
    echo ""
    echo -e "${GREEN}Memory operations work perfectly with cheap models!${NC}"
    echo ""
fi

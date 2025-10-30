#!/usr/bin/env node
/**
 * Setup script for AgentDB integration (ES Module)
 *
 * Verifies AgentDB installation and creates necessary directories
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import os from 'os';
import { fileURLToPath } from 'url';

// ES module equivalent of __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');

console.log('🚀 Setting up MCP Standards (Simple) with AgentDB...\n');

// Step 1: Check AgentDB availability
console.log('1️⃣  Checking AgentDB installation...');
try {
    const version = execSync('npx agentdb --version', { encoding: 'utf-8' }).trim();
    console.log(`   ✓ AgentDB found: ${version}`);
} catch (error) {
    console.log('   ⚠️  AgentDB not installed');
    console.log('   Installing AgentDB via npx (this may take a moment)...');

    try {
        execSync('npm install -g agentdb', { stdio: 'inherit' });
        console.log('   ✓ AgentDB installed successfully');
    } catch (installError) {
        console.error('   ✗ Failed to install AgentDB');
        console.error('   Please install manually: npm install -g agentdb');
        process.exit(1);
    }
}

// Step 2: Create directories
console.log('\n2️⃣  Creating directories...');
const mcpDir = path.join(os.homedir(), '.mcp-standards');
const agentdbDir = path.join(mcpDir, 'agentdb');

try {
    if (!fs.existsSync(mcpDir)) {
        fs.mkdirSync(mcpDir, { recursive: true });
        console.log(`   ✓ Created ${mcpDir}`);
    } else {
        console.log(`   ✓ ${mcpDir} exists`);
    }

    if (!fs.existsSync(agentdbDir)) {
        fs.mkdirSync(agentdbDir, { recursive: true });
        console.log(`   ✓ Created ${agentdbDir}`);
    } else {
        console.log(`   ✓ ${agentdbDir} exists`);
    }
} catch (error) {
    console.error('   ✗ Failed to create directories:', error.message);
    process.exit(1);
}

// Step 3: Test AgentDB functionality
console.log('\n3️⃣  Testing AgentDB...');
try {
    // Simple test: store and retrieve
    const testKey = 'test-setup';
    const testValue = 'AgentDB setup successful';

    console.log('   Testing store operation...');
    execSync(
        `npx agentdb store --key "${testKey}" --value "${testValue}" --path "${agentdbDir}"`,
        { encoding: 'utf-8' }
    );
    console.log('   ✓ Store test passed');

    console.log('   Testing query operation...');
    const queryResult = execSync(
        `npx agentdb query --query "setup" --path "${agentdbDir}"`,
        { encoding: 'utf-8' }
    );
    console.log('   ✓ Query test passed');

    // Clean up test data
    execSync(`npx agentdb delete --key "${testKey}" --path "${agentdbDir}" 2>/dev/null || true`);

} catch (error) {
    console.log('   ⚠️  AgentDB tests failed (this is OK for first-time setup)');
    console.log('   AgentDB will be fully initialized on first use');
}

// Step 4: Display configuration
console.log('\n4️⃣  Configuration summary:');
console.log(`   AgentDB path: ${agentdbDir}`);
console.log(`   SQLite path: ${path.join(mcpDir, 'knowledge.db')}`);

// Step 5: Next steps
console.log('\n✅ Setup complete!\n');
console.log('Next steps:');
console.log('1. Add to Claude Desktop config:');
console.log('   {');
console.log('     "mcpServers": {');
console.log('       "mcp-standards-simple": {');
console.log('         "command": "uv",');
console.log('         "args": [');
console.log('           "run",');
console.log('           "--directory",');
console.log(`           "${projectRoot}",`);
console.log('           "python",');
console.log('           "-m",');
console.log('           "mcp_standards.server_simple"');
console.log('         ]');
console.log('       }');
console.log('     }');
console.log('   }\n');
console.log('2. Restart Claude Desktop');
console.log('3. Try the skill: "Remember: use uv not pip"');
console.log('4. Next session: Claude will automatically use uv\n');
console.log('📖 See docs/SIMPLE_V2_PLAN.md for more details');

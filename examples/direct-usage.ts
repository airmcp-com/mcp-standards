/**
 * Example: Using mcp-standards as a library in your code
 * Perfect for Claude Code or any TypeScript/Node.js project
 */

import { SimpleMemoryClient, quickRecall, quickRemember } from 'mcp-standards';

// Example 1: Using the client class
async function exampleWithClient() {
  const memory = new SimpleMemoryClient();
  await memory.init();

  // Store preferences
  console.log('Storing preferences...');
  await memory.remember('Use uv instead of pip for Python', 'python', 9);
  await memory.remember('Always create feature branches', 'git', 8);
  await memory.remember('Prefer conventional commits', 'git', 7);
  await memory.remember('Use docker compose not docker-compose', 'docker', 6);

  // Recall preferences
  console.log('\nRecalling Python preferences...');
  const pythonPrefs = await memory.recall('python package manager', { category: 'python' });
  pythonPrefs.forEach((result) => {
    console.log(`- ${result.memory.content} (score: ${result.score.toFixed(2)})`);
  });

  // List all git preferences
  console.log('\nListing all Git preferences...');
  const { memories, total } = await memory.list({ category: 'git' });
  console.log(`Found ${total} git preferences:`);
  memories.forEach((m) => {
    console.log(`- [${m.importance}/10] ${m.content}`);
  });

  // Count all memories
  const count = await memory.count();
  console.log(`\nTotal memories stored: ${count}`);
}

// Example 2: Using quick helper functions
async function exampleWithHelpers() {
  // Quick store
  await quickRemember('Use vitest for testing', 'general', 7);

  // Quick recall
  const results = await quickRecall('testing framework');
  if (results.length > 0) {
    console.log('Found preference:', results[0].memory.content);
  }
}

// Example 3: Integration with Claude Code workflow
async function claudeCodeWorkflow() {
  const memory = new SimpleMemoryClient();
  await memory.init();

  // Before suggesting a command, check for preferences
  const gitPrefs = await memory.recall('git workflow');

  if (gitPrefs.length > 0) {
    console.log('User preferences for git:');
    gitPrefs.forEach((pref) => {
      console.log(`  - ${pref.memory.content}`);
    });
  }

  // Use the preferences to inform suggestions
  // ...
}

// Run examples
if (import.meta.url === `file://${process.argv[1]}`) {
  console.log('=== Example 1: Using Client Class ===');
  await exampleWithClient();

  console.log('\n=== Example 2: Using Helper Functions ===');
  await exampleWithHelpers();

  console.log('\n=== Example 3: Claude Code Workflow ===');
  await claudeCodeWorkflow();
}

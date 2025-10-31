#!/usr/bin/env node
/**
 * Test the library mode - verifies shared memory access
 */

import { SimpleMemoryClient, quickRecall, quickRemember } from '../dist/lib.js';

console.log('🧪 Testing Simple Personal Memory Library\n');

// Test 1: Quick recall (should find memory from Claude Desktop)
console.log('Test 1: Quick Recall (from shared memory)');
try {
  const results = await quickRecall('git workflow');
  console.log(`✅ Found ${results.length} git preferences:`);
  results.forEach(r => {
    console.log(`   - ${r.memory.content} (score: ${r.score.toFixed(2)})`);
  });
} catch (error) {
  console.error('❌ Quick recall failed:', error.message);
}

console.log('\nTest 2: Full Client Usage');
try {
  const memory = new SimpleMemoryClient();
  await memory.init();

  // Store a new preference
  console.log('Storing new preference: "Use vitest for testing"');
  await memory.remember('Use vitest for testing', 'general', 7);
  console.log('✅ Stored successfully');

  // Recall it
  const testPrefs = await memory.recall('testing framework');
  if (testPrefs.length > 0) {
    console.log(`✅ Recalled: "${testPrefs[0].memory.content}"`);
  }

  // List all memories
  const { total } = await memory.list();
  console.log(`✅ Total memories in store: ${total}`);

  // Test category filtering
  const { memories: gitMemories } = await memory.list({ category: 'git' });
  console.log(`✅ Git-specific memories: ${gitMemories.length}`);

} catch (error) {
  console.error('❌ Client test failed:', error.message);
}

console.log('\nTest 3: Cross-Category Search');
try {
  const pythonResults = await quickRecall('python package');
  console.log(`Python preferences found: ${pythonResults.length}`);
  pythonResults.forEach(r => {
    console.log(`   - ${r.memory.content}`);
  });
} catch (error) {
  console.error('❌ Search failed:', error.message);
}

console.log('\n✅ All tests complete!\n');
console.log('Next: Test in Claude Desktop to verify shared storage');
console.log('Ask: "What testing framework do I prefer?"');
console.log('Expected: "Use vitest for testing"');

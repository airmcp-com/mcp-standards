#!/bin/bash
# Test cross-environment shared memory

echo "🔄 Testing Cross-Environment Shared Memory"
echo "==========================================="
echo ""

echo "Step 1: Store preference via library (Claude Code mode)"
node -e "import('../dist/lib.js').then(async ({quickRemember}) => {
  await quickRemember('Use pnpm for package management', 'general', 8);
  console.log('✅ Stored: Use pnpm for package management');
})"

echo ""
echo "Step 2: Verify in shared memory file"
if [ -f ~/.mcp-memory/memories.json ]; then
  echo "✅ Memory file exists"
  PNPM_COUNT=$(cat ~/.mcp-memory/memories.json | grep -c "pnpm")
  if [ $PNPM_COUNT -gt 0 ]; then
    echo "✅ Found 'pnpm' preference in file"
  else
    echo "❌ 'pnpm' preference not found in file"
  fi
else
  echo "❌ Memory file not found"
fi

echo ""
echo "Step 3: Recall via library"
node -e "import('../dist/lib.js').then(async ({quickRecall}) => {
  const results = await quickRecall('package management');
  if (results.length > 0) {
    console.log('✅ Recalled:', results[0].memory.content);
  } else {
    console.log('❌ No results found');
  }
})"

echo ""
echo "Step 4: TEST IN CLAUDE DESKTOP"
echo "Ask: 'What is my preference for package management?'"
echo "Expected: 'Use pnpm for package management'"
echo ""
echo "✅ Cross-environment test complete!"

# Testing Guide

## Quick Start

Run all tests:
```bash
# Test library mode
node tests/test-library.js

# Verify shared memory
./tests/verify-shared-memory.sh

# Test cross-environment
./tests/test-cross-environment.sh
```

## Test Scenarios

### 1. Library Mode Test (`test-library.js`)

Tests the library import and functionality:
- ✅ Quick recall from shared memory
- ✅ Full client usage (init, remember, recall, list)
- ✅ Category filtering
- ✅ Cross-category search

**Run**: `node tests/test-library.js`

**Expected Output**:
```
✅ Found git preferences from Claude Desktop
✅ Stored new testing preference
✅ Total memories counted correctly
```

### 2. Shared Memory Verification (`verify-shared-memory.sh`)

Inspects the shared memory file:
- Shows total count
- Lists all preferences
- Groups by category

**Run**: `./tests/verify-shared-memory.sh`

### 3. Cross-Environment Test (`test-cross-environment.sh`)

Tests shared storage between library and MCP server:
1. Stores via library (Claude Code mode)
2. Verifies in JSON file
3. Recalls via library
4. Instructions to test in Claude Desktop

**Run**: `./tests/test-cross-environment.sh`

## Manual Testing

### Test in Claude Desktop (MCP Mode)

1. Open Claude Desktop
2. Test remember: "Remember: use conventional commits"
3. Test recall: "What's my git workflow preference?"
4. Verify: Should mention both "feature branches" and "conventional commits"

### Test in Claude Code (Library Mode)

Create a test file:
```typescript
import { quickRecall } from 'mcp-standards';
const results = await quickRecall('git workflow');
console.log(results[0]?.memory.content);
```

Run: `node your-test.js`

### Verify Shared Storage

Both tests should access the same memories from:
```
~/.mcp-memory/memories.json
```

Check with:
```bash
cat ~/.mcp-memory/memories.json | jq '.[].content'
```

## Expected Results

✅ **Library finds memories stored in Claude Desktop**
✅ **Claude Desktop finds memories stored via library**
✅ **Total count matches across both modes**
✅ **Same preferences appear in both environments**

## Troubleshooting

**No memories found**:
- Run `npm start` first to initialize
- Or store a memory in Claude Desktop

**Import errors**:
- Run `npm run build` first
- Check `dist/lib.js` exists

**Permission errors**:
- Make scripts executable: `chmod +x tests/*.sh`

## Success Criteria

- [x] Library imports without errors
- [x] Can store and recall memories
- [x] Shared memory file exists
- [x] Cross-environment access works
- [x] Both Claude Desktop and library see same data

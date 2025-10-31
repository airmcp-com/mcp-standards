#!/bin/bash
# Verify shared memory file

echo "📁 Verifying Shared Memory Storage"
echo "===================================="
echo ""

MEMORY_FILE="$HOME/.mcp-memory/memories.json"

if [ -f "$MEMORY_FILE" ]; then
  echo "✅ Memory file exists: $MEMORY_FILE"
  echo ""

  # Count total memories
  TOTAL=$(cat "$MEMORY_FILE" | jq '. | length')
  echo "Total memories stored: $TOTAL"
  echo ""

  # List all preferences
  echo "All stored preferences:"
  cat "$MEMORY_FILE" | jq -r '.[] | "  - [\(.category)] \(.content) (importance: \(.importance))"'
  echo ""

  # Show by category
  echo "By category:"
  for category in python git docker general; do
    COUNT=$(cat "$MEMORY_FILE" | jq "[.[] | select(.category==\"$category\")] | length")
    if [ $COUNT -gt 0 ]; then
      echo "  $category: $COUNT"
    fi
  done

else
  echo "❌ Memory file not found at: $MEMORY_FILE"
  echo "Run 'npm start' or test the library first to create it"
fi

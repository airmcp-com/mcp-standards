#!/bin/bash
# Memory monitoring script for Claude Memory MCP server
# Usage: ./monitor-memory.sh [interval_seconds]

set -e

INTERVAL=${1:-300}  # Default: check every 5 minutes
LOG_FILE="$HOME/.claude-memory/memory-monitor.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Starting Claude Memory MCP Monitor"
echo "Interval: ${INTERVAL}s"
echo "Log file: ${LOG_FILE}"
echo ""

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Function to get memory usage
get_memory_usage() {
    ps aux | grep -E "(python.*run_.*server\.py)" | grep -v grep | awk '{
        total_rss += $6
        total_vsz += $5
        count++
        printf "%s,%s,%s,%s\n", $2, $11, $6, $5
    } END {
        if (count > 0) {
            printf "TOTAL,%d,%d,%d\n", count, total_rss, total_vsz
        }
    }'
}

# Function to get database stats
get_db_stats() {
    local db="$HOME/.claude-memory/knowledge.db"

    if [ -f "$db" ]; then
        local size=$(du -k "$db" | cut -f1)
        local counts=$(sqlite3 "$db" "
            SELECT COUNT(*) FROM episodes
            UNION ALL
            SELECT COUNT(*) FROM tool_logs
            UNION ALL
            SELECT COUNT(*) FROM pattern_frequency
            UNION ALL
            SELECT COUNT(*) FROM tool_preferences
        " 2>/dev/null | tr '\n' ',' | sed 's/,$//')

        echo "${size},${counts}"
    else
        echo "0,0,0,0,0"
    fi
}

# Function to check for issues
check_health() {
    local rss_kb=$1
    local vsz_kb=$2

    # Warning thresholds
    local RSS_WARNING=524288  # 512 MB
    local RSS_CRITICAL=1048576  # 1 GB

    if [ $rss_kb -gt $RSS_CRITICAL ]; then
        echo -e "${RED}CRITICAL${NC}"
        return 2
    elif [ $rss_kb -gt $RSS_WARNING ]; then
        echo -e "${YELLOW}WARNING${NC}"
        return 1
    else
        echo -e "${GREEN}OK${NC}"
        return 0
    fi
}

# Header for log file
if [ ! -f "$LOG_FILE" ]; then
    echo "timestamp,pid,process,rss_kb,vsz_kb,proc_count,db_size_kb,episodes,tool_logs,patterns,preferences,status" > "$LOG_FILE"
fi

# Monitoring loop
echo "Monitoring... (Press Ctrl+C to stop)"
echo ""

iteration=0
while true; do
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # Get process memory
    memory_data=$(get_memory_usage)

    if [ -z "$memory_data" ]; then
        echo "[$timestamp] No MCP server processes found"
        sleep "$INTERVAL"
        continue
    fi

    # Get database stats
    db_stats=$(get_db_stats)

    # Parse totals
    total_line=$(echo "$memory_data" | grep "^TOTAL")
    if [ -n "$total_line" ]; then
        proc_count=$(echo "$total_line" | cut -d',' -f2)
        total_rss=$(echo "$total_line" | cut -d',' -f3)
        total_vsz=$(echo "$total_line" | cut -d',' -f4)

        # Check health
        health_status=$(check_health "$total_rss" "$total_vsz")
        health_code=$?

        # Log each process
        echo "$memory_data" | grep -v "^TOTAL" | while IFS=',' read -r pid process rss vsz; do
            echo "${timestamp},${pid},${process},${rss},${vsz},${proc_count},${db_stats},${health_status}" >> "$LOG_FILE"
        done

        # Display summary every 10 iterations
        if [ $((iteration % 10)) -eq 0 ]; then
            echo "[$timestamp] Status: ${health_status}"
            echo "  Processes: $proc_count"
            echo "  Memory (RSS): $((total_rss / 1024)) MB"
            echo "  Memory (VSZ): $((total_vsz / 1024)) MB"
            echo "  Database: $(echo "$db_stats" | cut -d',' -f1) KB"
            echo "  Records: $(echo "$db_stats" | cut -d',' -f2-5)"
            echo ""
        fi

        # Alert on critical status
        if [ $health_code -eq 2 ]; then
            echo -e "${RED}CRITICAL: Memory usage exceeds 1GB!${NC}"
            echo -e "${RED}Consider restarting the MCP server.${NC}"
            echo ""
        fi
    fi

    iteration=$((iteration + 1))
    sleep "$INTERVAL"
done

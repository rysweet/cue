#!/bin/bash
# Performance monitoring script to track execution times

PERF_LOG=".git/precommit-performance.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] Pre-commit execution started" >> "$PERF_LOG"

# Track individual pipeline performance
if [ -f "/tmp/ts-duration" ]; then
    TS_DURATION=$(cat /tmp/ts-duration)
    echo "[$TIMESTAMP] TypeScript pipeline: ${TS_DURATION}s" >> "$PERF_LOG"
    rm -f /tmp/ts-duration
fi

if [ -f "/tmp/py-duration" ]; then
    PY_DURATION=$(cat /tmp/py-duration)
    echo "[$TIMESTAMP] Python pipeline: ${PY_DURATION}s" >> "$PERF_LOG"
    rm -f /tmp/py-duration
fi

# Calculate total execution time
if [ -n "$PRECOMMIT_START_TIME" ]; then
    END_TIME=$(date +%s)
    TOTAL_DURATION=$((END_TIME - PRECOMMIT_START_TIME))
    echo "[$TIMESTAMP] Total pre-commit execution: ${TOTAL_DURATION}s" >> "$PERF_LOG"
fi
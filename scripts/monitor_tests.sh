#!/usr/bin/env bash
# Monitor progress of flaky test detection runs

# Get script directory and load .env
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

# Load .env variables
if [ -f "$REPO_ROOT/.env" ]; then
    while IFS='=' read -r key value; do
        # Skip empty lines and comments
        [[ -z "$key" || "$key" =~ ^[[:space:]]*# ]] && continue
        # Remove inline comments and whitespace
        value=$(echo "$value" | sed 's/#.*//' | xargs)
        export "$key=$value"
    done < <(grep -E '^[A-Z_]+=' "$REPO_ROOT/.env")
fi

# Default values if not set
PYTHON_TEST_ROUNDS=${PYTHON_TEST_ROUNDS:-50}
JAVA_PROJECTS_COUNT=$(echo "$JAVA_PROJECTS" | wc -w)
PYTHON_PROJECTS_COUNT=$(echo "$PYTHON_PROJECTS" | wc -w)

echo "=========================================="
echo "Flaky Test Detection - Progress Monitor"
echo "=========================================="
echo ""

# Java tests status
echo "=== JAVA TESTS (NonDex) ==="
if tmux has-session -t flaky-java 2>/dev/null; then
    echo "Status: RUNNING"
    if [ -f /tmp/make_java.log ]; then
        # Count projects started
        started=$(grep -c "=== Running NonDex on" /tmp/make_java.log 2>/dev/null || echo "0")
        echo "Projects started: $started / $JAVA_PROJECTS_COUNT"
        echo "Current:"
        tail -3 /tmp/make_java.log | grep -E "\[INFO\]|Running NonDex|===" || echo "  (building...)"
    fi
else
    echo "Status: COMPLETED or NOT STARTED"
    if [ -f /tmp/make_java.log ] && grep -q "=== Java tests completed ===" /tmp/make_java.log 2>/dev/null; then
        echo "✅ Java tests finished successfully"
    fi
fi

echo ""

# Python tests status
echo "=== PYTHON TESTS (pytest) ==="
if tmux has-session -t flaky-python 2>/dev/null; then
    echo "Status: RUNNING"
    if [ -f /tmp/make_python.log ]; then
        # Count projects started
        started=$(grep -c "=== Running pytest" /tmp/make_python.log 2>/dev/null || echo "0")
        # Count current round
        current_round=$(grep -oP "Run #\K\d+" /tmp/make_python.log 2>/dev/null | tail -1 || echo "0")
        echo "Projects started: $started / $PYTHON_PROJECTS_COUNT"
        echo "Current round: $current_round / $PYTHON_TEST_ROUNDS"
        echo "Current:"
        tail -3 /tmp/make_python.log | grep -E "Run #|Running pytest|===" || echo "  (installing dependencies...)"
    fi
else
    echo "Status: COMPLETED or NOT STARTED"
    if [ -f /tmp/make_python.log ] && grep -q "=== Python tests completed ===" /tmp/make_python.log 2>/dev/null; then
        echo "✅ Python tests finished successfully"
    fi
fi

echo ""
echo "=========================================="
echo "To attach to sessions:"
echo "  tmux attach -t flaky-java"
echo "  tmux attach -t flaky-python"
echo ""
echo "To view full logs:"
echo "  tail -f /tmp/make_java.log"
echo "  tail -f /tmp/make_python.log"
echo "=========================================="

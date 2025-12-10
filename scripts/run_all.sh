#!/usr/bin/env bash
set -e

# Get script directory and repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$REPO_ROOT"

# Load .env if it exists
if [ -f .env ]; then
    set -a
    # Only source lines that are valid variable assignments (not comments or empty)
    while IFS='=' read -r key value; do
        # Skip empty lines and comments
        [[ -z "$key" || "$key" =~ ^[[:space:]]*# ]] && continue
        # Remove inline comments and whitespace
        value=$(echo "$value" | sed 's/#.*//' | xargs)
        export "$key=$value"
    done < <(grep -E '^[A-Z_]+=' .env)
    set +a
fi

echo "=========================================="
echo "Starting Flaky Test Detection - All Projects"
echo "=========================================="
echo ""

# Start Java tests in tmux
echo "Starting Java (NonDex) tests in background..."
tmux new-session -d -s flaky-java 'make java 2>&1 | tee /tmp/make_java.log; echo "=== Java tests completed ===" >> /tmp/make_java.log'
echo "✅ Java tests started (session: flaky-java)"

echo ""

# Start Python tests in tmux
echo "Starting Python (pytest) tests in background..."
tmux new-session -d -s flaky-python 'make python 2>&1 | tee /tmp/make_python.log; echo "=== Python tests completed ===" >> /tmp/make_python.log'
echo "✅ Python tests started (session: flaky-python)"

echo ""
echo "=========================================="
echo "All test sessions started!"
echo "=========================================="
echo ""
echo "Monitor progress:"
echo "  make monitor          # Quick status check"
echo "  make auto-visualize   # Auto-run visualization when done"
echo ""
echo "Attach to sessions:"
echo "  tmux attach -t flaky-java"
echo "  tmux attach -t flaky-python"
echo ""
echo "View logs:"
echo "  tail -f /tmp/make_java.log"
echo "  tail -f /tmp/make_python.log"
echo "=========================================="
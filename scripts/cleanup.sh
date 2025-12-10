#!/usr/bin/env bash
set -e

echo "=========================================="
echo "Project Cleanup and Optimization"
echo "=========================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$REPO_ROOT"

# 1. Remove old test results from projects we're no longer testing
echo "[1/6] Removing old test results..."
OLD_PROJECTS="pandas requests mockito"
for proj in $OLD_PROJECTS; do
    if [ -d "results/$proj" ]; then
        echo "  Removing results/$proj"
        rm -rf "results/$proj"
    fi
done

# 2. Clean Python cache files
echo "[2/6] Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type f -name "*.pyd" -delete 2>/dev/null || true

# 3. Clean pytest cache
echo "[3/6] Cleaning pytest cache..."
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

# 4. Remove temporary log files (but keep test results)
echo "[4/6] Removing temporary logs..."
rm -f /tmp/make_*.log 2>/dev/null || true

# 5. Clean up duplicate or empty directories
echo "[5/6] Cleaning empty directories..."
find visualization/reports -type d -empty -delete 2>/dev/null || true
find visualization/exports -type d -empty -delete 2>/dev/null || true

# 6. Optimize visualization reports (keep only latest)
echo "[6/6] Cleaning old visualization artifacts..."
# Keep visualization/__pycache__ but remove unnecessary bytecode
find visualization -name "*.pyc" -delete 2>/dev/null || true

echo ""
echo "=========================================="
echo "Cleanup Summary"
echo "=========================================="
echo "Removed:"
echo "  - Old test results (pandas, requests, mockito)"
echo "  - Python cache files (__pycache__, *.pyc)"
echo "  - Pytest cache directories"
echo "  - Temporary log files"
echo ""

# Show current disk usage
echo "Current results size:"
du -sh results/* 2>/dev/null | sort -h || echo "  (no results yet)"
echo ""

echo "✅ Cleanup complete!"

#!/usr/bin/env bash
set -euo pipefail

# Script to run only failed/incomplete projects
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

# Source environment variables (safely handle spaces in values)
if [ -f "$REPO_ROOT/.env" ]; then
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        [[ "$key" =~ ^#.*$ ]] && continue
        [[ -z "$key" ]] && continue
        # Export the variable
        export "$key=$value"
    done < "$REPO_ROOT/.env"
fi

# Set defaults if not in .env
EXPERIMENT_DIR="${EXPERIMENT_DIR:-../flaky-tests-experiments}"
FLAKY_TESTS_PYTHON_EXPERIMENTS_DIR="${FLAKY_TESTS_PYTHON_EXPERIMENTS_DIR:-$EXPERIMENT_DIR}"
FLAKY_TESTS_JAVA_EXPERIMENTS_DIR="${FLAKY_TESTS_JAVA_EXPERIMENTS_DIR:-$EXPERIMENT_DIR}"
PYTHON_TEST_ROUNDS="${PYTHON_TEST_ROUNDS:-20}"

echo "=========================================="
echo "Running Failed/Incomplete Projects Only"
echo "=========================================="
echo ""

# Python projects to retry (fixed with proper extras)
PYTHON_FAILED=("black" "celery" "httpx")

# Java projects to retry (excluding guava and retrofit - see KNOWN_ISSUES.md)
JAVA_FAILED=("commons-lang" "commons-collections")

# Check if user wants to run specific type
RUN_TYPE="${1:-all}"  # all, python, java

run_python_projects() {
    echo "=== Running Failed Python Projects ==="
    for project in "${PYTHON_FAILED[@]}"; do
        project_path="${FLAKY_TESTS_PYTHON_EXPERIMENTS_DIR}/${project}"
        if [ ! -d "$project_path" ]; then
            echo "⚠️  Project not found: $project_path"
            continue
        fi
        
        echo ""
        echo "🐍 Testing $project..."
        bash "$SCRIPT_DIR/run_py_flaky_detection.sh" "$project_path" "${PYTHON_TEST_ROUNDS:-20}" || {
            echo "❌ $project failed"
        }
    done
}

run_java_projects() {
    echo "=== Running Failed Java Projects ==="
    for project in "${JAVA_FAILED[@]}"; do
        project_path="${FLAKY_TESTS_JAVA_EXPERIMENTS_DIR}/${project}"
        if [ ! -d "$project_path" ]; then
            echo "⚠️  Project not found: $project_path"
            continue
        fi
        
        echo ""
        echo "☕ Testing $project..."
        bash "$SCRIPT_DIR/run_nondex.sh" "$project_path" || {
            echo "❌ $project failed (this might be expected for some projects)"
        }
    done
}

case "$RUN_TYPE" in
    python)
        run_python_projects
        ;;
    java)
        run_java_projects
        ;;
    all|*)
        run_python_projects
        echo ""
        run_java_projects
        ;;
esac

echo ""
echo "=========================================="
echo "✅ Retest complete!"
echo "=========================================="

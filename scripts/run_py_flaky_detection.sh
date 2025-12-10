#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$1"   # e.g. ../flaky-tests-experiments/pandas

# Get absolute path for results directory before changing directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
PROJECT_NAME=$(basename "$PROJECT_DIR")
OUTDIR="$REPO_ROOT/results/$PROJECT_NAME/pytest-rerun/$(date +%F_%H-%M-%S)"
mkdir -p "$OUTDIR"

# Create isolated virtual environment for this project
PROJECT_VENV="$REPO_ROOT/.venv-$PROJECT_NAME"
echo "🔧 Setting up isolated environment for $PROJECT_NAME..."

if [ ! -d "$PROJECT_VENV" ]; then
    echo "   Creating new virtual environment: $PROJECT_VENV"
    python3 -m venv "$PROJECT_VENV"
fi

# Activate project-specific virtual environment
source "$PROJECT_VENV/bin/activate"

# Install pytest and plugins in this isolated venv
echo "   Installing pytest and plugins..."
pip install -q pytest>=8.3.4 pytest-rerunfailures pytest-randomly

# Verify pytest is from the venv
PYTEST_PATH=$(which pytest)
if [[ "$PYTEST_PATH" != "$PROJECT_VENV"* ]]; then
    echo "⚠️  Warning: pytest not from project venv ($PYTEST_PATH)"
fi

pushd "$PROJECT_DIR" >/dev/null

# record commit
git rev-parse HEAD > "$OUTDIR/commit.txt" || true

# Install project dependencies
echo "Installing project dependencies..."
# Install project dependencies
echo "Installing project dependencies..."

# Try to install test dependencies first (common patterns)
for test_reqs in requirements-dev.txt test-requirements.txt test_requirements.txt requirements/dev.txt; do
    if [ -f "$test_reqs" ]; then
        echo "   Installing test dependencies from $test_reqs..."
        pip install -q -r "$test_reqs" 2>&1 | grep -v "Requirement already satisfied" || true
    fi
done

# Then install the project itself with smart extras detection
INSTALL_SUCCESS=false

# Project-specific extras and dependencies needed for testing
declare -A PROJECT_EXTRAS
PROJECT_EXTRAS["black"]="d,test,dev"
PROJECT_EXTRAS["httpx"]="http2,brotli"
PROJECT_EXTRAS["celery"]=""  # Uses requirements/dev.txt instead

# Additional packages to install after project setup
declare -A EXTRA_PACKAGES
EXTRA_PACKAGES["httpx"]="trio anyio"
EXTRA_PACKAGES["celery"]="pytest-celery pytest-sugar case"

# Get extras for current project
EXTRAS="${PROJECT_EXTRAS[$PROJECT_NAME]:-dev,test}"

if [ -f "pyproject.toml" ]; then
    echo "   Installing project from pyproject.toml..."
    # Try with project-specific extras first, then fallback
    for extra_combo in "$EXTRAS" "dev,test" "test" ""; do
        if [ -z "$extra_combo" ]; then
            cmd="pip install -q -e ."
        else
            cmd="pip install -q -e .[$extra_combo]"
        fi
        
        if $cmd 2>&1 | tee /tmp/pip_install.log | grep -v "Requirement already satisfied" | grep -v "does not provide the extra"; then
            INSTALL_SUCCESS=true
            break
        fi
    done
elif [ -f "setup.py" ]; then
    echo "   Installing project in development mode..."
    for extra_combo in "$EXTRAS" "dev,test" "test" ""; do
        if [ -z "$extra_combo" ]; then
            cmd="pip install -q -e ."
        else
            cmd="pip install -q -e .[$extra_combo]"
        fi
        
        if $cmd 2>&1 | tee /tmp/pip_install.log | grep -v "Requirement already satisfied" | grep -v "does not provide the extra"; then
            INSTALL_SUCCESS=true
            break
        fi
    done
elif [ -f "requirements.txt" ]; then
    echo "   Installing dependencies from requirements.txt..."
    if pip install -q -r requirements.txt 2>&1 | tee /tmp/pip_install.log | grep -v "Requirement already satisfied"; then
        INSTALL_SUCCESS=true
    fi
fi

if [ "$INSTALL_SUCCESS" = false ]; then
    echo "⚠️  Project installation had issues, but continuing with tests..."
    # Show last few lines of install log for debugging
    tail -5 /tmp/pip_install.log 2>/dev/null || true
fi

# Install additional packages if needed
if [ -n "${EXTRA_PACKAGES[$PROJECT_NAME]:-}" ]; then
    echo "   Installing additional dependencies: ${EXTRA_PACKAGES[$PROJECT_NAME]}..."
    pip install -q ${EXTRA_PACKAGES[$PROJECT_NAME]} 2>&1 | grep -v "Requirement already satisfied" || true
fi

echo "✅ Environment ready for $PROJECT_NAME"
# We'll run the whole test-suite N times and capture per-test failures.
ROUNDS=${2:-${PYTHON_TEST_ROUNDS:-50}}   # number of full test-suite runs (default 50, configurable via .env)
RESULT_CSV="$OUTDIR/runs.csv"
echo "run,failed_tests_count,failed_tests_list" > "$RESULT_CSV"

for i in $(seq 1 $ROUNDS); do
  echo "=========================================="
  echo "Run #$i/$ROUNDS ($(awk "BEGIN {printf \"%.1f\", ($i/$ROUNDS)*100}")% complete)"
  echo "=========================================="
  # Run pytest once, collect failing test nodeids (no reruns here — single run)
  # Use -q to keep machine-friendly output; --maxfail=0 runs through all tests
  TIMESTAMP=$(date +%s)
  LOG="$OUTDIR/run_${i}.log"
  pytest -q --maxfail=0 2>&1 | tee "$LOG" || true

  # extract failed test ids from junit or pytest output (simple parse below)
  FAILS=$(grep -Po '(?<=FAILED\s)([^ ]+::[^ ]+)' "$LOG" 2>/dev/null | tr '\n' ';' | sed 's/;$//' || echo "")
  # Fallback: count 'failed' line in summary:
  FAIL_COUNT=$(grep -Eo '[0-9]+ failed' "$LOG" 2>/dev/null | grep -Po '^\d+' || echo 0)

  echo "${i},${FAIL_COUNT},\"${FAILS}\"" >> "$RESULT_CSV"
  echo "Run $i complete. Failed tests: $FAIL_COUNT"
done

echo "{\"project\":\"$(basename "$PROJECT_DIR")\",\"date\":\"$(date --iso-8601=seconds)\",\"rounds\":$ROUNDS}" > "$OUTDIR/metadata.json"

popd >/dev/null
echo "=========================================="
echo "✓ All $ROUNDS rounds complete!"
echo "Results in $OUTDIR (summary CSV: $RESULT_CSV)"
echo "=========================================="

# Generate a compact summary to make terminal inspection easier
SUMMARY_FILE="$OUTDIR/summary.txt"
{
  echo "project: $(basename "$PROJECT_DIR")"
  echo "rounds: $ROUNDS"
  echo "summary_csv: $RESULT_CSV"
  echo
  # aggregate failure counts per test nodeid
  declare -A counts
  while IFS=, read -r run fail_count fail_list; do
    # remove surrounding quotes from fail_list
    fail_list=$(echo "$fail_list" | sed 's/^"//; s/"$//')
    IFS=';' read -ra items <<< "$fail_list"
    for t in "${items[@]}"; do
      t=$(echo "$t" | sed 's/^\s*//; s/\s*$//')
      if [ -n "$t" ]; then
        counts["$t"]=$(( ${counts["$t"]:-0} + 1 ))
      fi
    done
  done < <(tail -n +2 "$RESULT_CSV")

  total_failed_tests=0
  flaky_count=0
  tmp_counts="$OUTDIR/_py_counts.tmp"
  : > "$tmp_counts"
  for t in "${!counts[@]}"; do
    echo "${counts[$t]}|$t" >> "$tmp_counts"
    total_failed_tests=$((total_failed_tests+1))
    if [ ${counts[$t]} -gt 0 ] && [ ${counts[$t]} -lt $ROUNDS ]; then
      flaky_count=$((flaky_count+1))
    fi
  done

  echo "distinct_failed_tests: $total_failed_tests"
  echo "flaky_tests (failed in some but not all runs): $flaky_count"
  echo
  if [ -s "$tmp_counts" ]; then
    echo "top flaky / failing tests (count | test)"
    sort -t'|' -nr -k1 "$tmp_counts" | head -n 10 | sed 's/|/ | /g'
  else
    echo "no failing tests recorded in CSV"
  fi
} > "$SUMMARY_FILE"

# Print a short terminal-friendly summary (5 lines max + location)
echo "---- Short summary ----"
sed -n '1,20p' "$SUMMARY_FILE" | sed -n '1,8p'
echo "(Full summary file: $SUMMARY_FILE)"
echo "-----------------------"

popd >/dev/null

# Deactivate the project-specific venv
deactivate

echo "✅ $PROJECT_NAME testing complete (isolated environment: $PROJECT_VENV)"
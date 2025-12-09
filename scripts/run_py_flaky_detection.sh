#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$1"   # e.g. ../flaky-tests-experiments/pandas

# Get absolute path for results directory before changing directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
OUTDIR="$REPO_ROOT/results/$(basename "$PROJECT_DIR")/pytest-rerun/$(date +%F_%H-%M-%S)"
mkdir -p "$OUTDIR"

pushd "$PROJECT_DIR" >/dev/null

# record commit
git rev-parse HEAD > "$OUTDIR/commit.txt" || true

# Ensure venv activated or python from PATH has pytest and plugins
# We'll run the whole test-suite N times and capture per-test failures.
ROUNDS=${2:-20}   # number of full test-suite runs (default 20)
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
  FAILS=$(grep -Po '(?<=FAILED\s)([^ ]+::[^ ]+)' "$LOG" | tr '\n' ';' | sed 's/;$//')
  # Fallback: count 'failed' line in summary:
  FAIL_COUNT=$(grep -Eo '==.*failed' "$LOG" | grep -Po '\d+' || echo 0)

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

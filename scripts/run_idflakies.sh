#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$1"   # e.g. ../flaky-tests-experiments/mockito

# Get absolute path for results directory before changing directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
OUTDIR="$REPO_ROOT/results/$(basename "$PROJECT_DIR")/idflakies/$(date +%F_%H-%M-%S)"
mkdir -p "$OUTDIR"

pushd "$PROJECT_DIR" >/dev/null

git rev-parse HEAD > "$OUTDIR/commit.txt" || true

# iDFlakies is a framework; typically cloned/run as a separate repo.
# If you have iDFlakies installed/checked-out next to your projects, run its script pointing at project.
# Example (you'll need to adapt path to your clone of iDFlakies):
IFL_ROOT="../tools/iDFlakies"   # set to where you cloned iDFlakies framework
if [ ! -d "$IFL_ROOT" ]; then
  echo "Please clone iDFlakies into $IFL_ROOT (see https://github.com/iDFlakies/iDFlakies)"
  exit 1
fi

# Example command: run detection for X rounds (iDFlakies docs explain exact CLI)
# This is a template — adapt to the iDFlakies wrapper scripts in the iDFlakies repo.
echo "=========================================="
echo "Starting iDFlakies for $(basename "$PROJECT_DIR")"
echo "Rounds: 100"
echo "Output Directory: $OUTDIR"
echo "=========================================="

"$IFL_ROOT"/run_idflakies.sh "$PROJECT_DIR" --rounds 100 2>&1 | tee "$OUTDIR/idflakies.log"

echo "=========================================="
echo "✓ iDFlakies complete for $(basename "$PROJECT_DIR")"
echo "=========================================="

echo "{\"project\":\"$(basename "$PROJECT_DIR")\",\"date\":\"$(date --iso-8601=seconds)\",\"cmd\":\"iDFlakies rounds=100\"}" > "$OUTDIR/metadata.json"

popd >/dev/null
echo "Results in $OUTDIR"

# Create compact summary of idflakies output
SUMMARY="$OUTDIR/summary.txt"
{
  echo "project: $(basename "$PROJECT_DIR")"
  echo "tool: iDFlakies"
  echo "log: $OUTDIR/idflakies.log"
  echo
  # heuristic counts for occurrences of 'flaky' or 'detected' lines
  flaky_lines=$(grep -i "flaky" "$OUTDIR/idflakies.log" | wc -l || true)
  detected_lines=$(grep -i "detected" "$OUTDIR/idflakies.log" | wc -l || true)
  echo "lines_with_flaky_word: $flaky_lines"
  echo "lines_with_detected_word: $detected_lines"
  echo
  echo "last 10 relevant lines from log:"
  grep -Ei "flaky|detected|FAILED|ERROR|WARN|WARNING" "$OUTDIR/idflakies.log" | tail -n 10 || true
} > "$SUMMARY"

echo "---- Short summary ----"
sed -n '1,20p' "$SUMMARY" | sed -n '1,8p'
echo "(Full summary file: $SUMMARY)"
echo "-----------------------"

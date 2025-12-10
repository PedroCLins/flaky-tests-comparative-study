# Test Execution Status Report

## Overview
This document tracks the status of flaky test detection experiments across Java and Python projects.

## ✅ Currently Running (Automated)

### Background Processes
1. **Java Tests**: tmux session `flaky-java` → `/tmp/make_java.log`
2. **Python Tests**: tmux session `flaky-python` → `/tmp/make_python.log`  
3. **Auto-Visualize**: Background process → `/tmp/auto_visualize.log`
   - Waiting for tests to complete
   - Will auto-run visualization + cleanup

### Progress (Updated: Check with `bash scripts/monitor_tests.sh`)
- **Java**: 1/5 projects started (commons-lang running)
- **Python**: 1/5 projects, round 8/50 (httpie running)

## Test Configuration

### Java Projects (NonDex)
- **Tool**: NonDex Maven Plugin 2.1.7
- **Projects**: commons-lang, commons-collections, commons-codec, guava, retrofit (5 total)
- **Method**: Non-deterministic execution order detection

### Python Projects (pytest)
- **Tool**: pytest with reruns
- **Projects**: httpie, flask, black, celery, httpx (5 total)
- **Rounds**: 50 iterations per project
- **Total Runs**: 250 (50 rounds × 5 projects)

## Current Status

### Java Tests (NonDex)
- **Session**: `tmux attach -t flaky-java`
- **Log**: `/tmp/make_java.log`
- **Status**: RUNNING ✅
- **Progress**: commons-lang in progress
- **Findings**: Multiple flaky tests detected in commons-lang:
  - `DurationFormatUtilsTest.testFourYears` - Timing-related failure
  - `HashCodeBuilderAndEqualsBuilderTest` - 2 errors due to non-deterministic order
  - `ToStringBuilderTest` - 87 failures, 6 errors (HashMap iteration order)

### Python Tests (pytest)
- **Session**: `tmux attach -t flaky-python`
- **Log**: `/tmp/make_python.log`
- **Status**: RUNNING ✅
- **Progress**: httpie - round 5/50
- **Findings**: Encoding-related failures detected in httpie

## Monitoring

**Quick Status Check:**
```bash
bash scripts/monitor_tests.sh
```

**View Live Logs:**
```bash
tail -f /tmp/make_java.log          # Java tests
tail -f /tmp/make_python.log        # Python tests  
tail -f /tmp/auto_visualize.log     # Auto-visualize process
```

**Attach to Test Sessions:**
```bash
tmux attach -t flaky-java      # Watch Java tests
tmux attach -t flaky-python    # Watch Python tests
# Press Ctrl+B then D to detach
```

## Next Steps

**Everything is automated!** The system will:
1. ⏳ Wait for all tests to complete (tmux sessions to finish)
2. 📊 Auto-generate visualization reports
3. 🧹 Auto-run cleanup to optimize disk usage
4. ✅ Save all results and reports

**When Complete:**
- Reports will be in: `visualization/reports/`
- View dashboard: `make dashboard`
- Open HTML report: `xdg-open visualization/reports/flaky_tests_report.html`

**Manual Override:**
If you want to run visualization manually (without waiting):
```bash
make visualize    # Run now with current results
make cleanup      # Clean up old data
```

## Expected Completion Time

- **Java Tests**: ~30-60 minutes (depending on project size)
- **Python Tests**: ~2-4 hours (50 rounds × 5 projects)

## Results Location

All results are saved to:
- Java: `results/{project}/nondex/{timestamp}/`
- Python: `results/{project}/pytest-rerun/{timestamp}/`

Each contains:
- Individual test run logs
- Summary CSV with failure counts
- Metadata (commit hash, timestamps)
- Git commit information

#!/usr/bin/env bash
set -euo pipefail

echo "=========================================="
echo "📊 Running Flaky Test Analysis & Visualization"
echo "=========================================="

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Activate virtual environment
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo "❌ Virtual environment not found. Run 'make setup' first."
    exit 1
fi

source "$PROJECT_ROOT/.venv/bin/activate"

# Default values
RESULTS_DIR="${1:-results}"
OUTPUT_DIR="${2:-visualization/reports}"
MODE="${3:-all}"
WAIT_FOR_TESTS="${4:-false}"  # New parameter: wait for tests to complete

cd "$PROJECT_ROOT"

# Wait for tests to complete if requested
if [ "$WAIT_FOR_TESTS" = "true" ] || [ "$WAIT_FOR_TESTS" = "1" ]; then
    echo "⏳ Waiting for tests to complete..."
    echo ""
    
    # Record start time
    START_TIME=$(date +%s)
    
    check_session() {
        # Check both old and new session name formats
        tmux has-session -t "$1" 2>/dev/null || tmux has-session -t "flaky-tests-${1#flaky-}" 2>/dev/null
    }
    
    get_elapsed_time() {
        local current=$(date +%s)
        local elapsed=$((current - START_TIME))
        local hours=$((elapsed / 3600))
        local minutes=$(((elapsed % 3600) / 60))
        local seconds=$((elapsed % 60))
        printf "%02d:%02d:%02d" $hours $minutes $seconds
    }
    
    get_current_java_project() {
        if [ -f /tmp/make_java.log ] && [ -s /tmp/make_java.log ]; then
            # Get the last "Running NonDex on" line from log
            grep "=== Running NonDex on" /tmp/make_java.log 2>/dev/null | tail -1 | sed 's/.*on //' | sed 's/ ===//'
        elif tmux has-session -t flaky-java 2>/dev/null; then
            # Fallback: extract from tmux pane
            local proj=$(tmux capture-pane -t flaky-java -p 2>/dev/null | grep -oE "(commons-lang|commons-collections|commons-codec|guava|retrofit)" | tail -1)
            echo "$proj"
        fi
    }
    
    get_current_python_project() {
        if [ -f /tmp/make_python.log ] && [ -s /tmp/make_python.log ]; then
            # Get the last "Running pytest" line from log
            grep "=== Running pytest" /tmp/make_python.log 2>/dev/null | tail -1 | sed 's/.*on //' | sed 's/ ===//'
        elif tmux has-session -t flaky-python 2>/dev/null; then
            # Fallback: extract from tmux pane
            local proj=$(tmux capture-pane -t flaky-python -p 2>/dev/null | grep -oP "/\K(httpie|flask|black|celery|httpx)(?=/)" | tail -1)
            echo "$proj"
        fi
    }
    
    print_test_status() {
        local elapsed=$(get_elapsed_time)
        echo "=========================================="
        echo "⏱️  Elapsed Time: $elapsed"
        echo "Status Check: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "=========================================="
        echo ""
        
        if check_session flaky-java; then
            local current_proj=$(get_current_java_project)
            echo "☕ Java (NonDex): RUNNING"
            if [ -f /tmp/make_java.log ] && [ -s /tmp/make_java.log ]; then
                started=$(grep -c "=== Running NonDex on" /tmp/make_java.log 2>/dev/null || echo "0")
                echo "   Progress: $started / 5 projects"
            fi
            if [ -n "$current_proj" ]; then
                echo "   Current: $current_proj"
            fi
        else
            echo "☕ Java (NonDex): COMPLETED ✅"
        fi
        
        echo ""
        
        if check_session flaky-python; then
            local current_proj=$(get_current_python_project)
            echo "🐍 Python (pytest): RUNNING"
            if [ -f /tmp/make_python.log ] && [ -s /tmp/make_python.log ]; then
                started=$(grep -c "=== Running pytest" /tmp/make_python.log 2>/dev/null || echo "0")
                current_round=$(grep -oP "Run #\K\d+" /tmp/make_python.log 2>/dev/null | tail -1 || echo "0")
                echo "   Progress: $started / 5 projects"
                echo "   Round: $current_round / 20"
            elif tmux has-session -t flaky-python 2>/dev/null; then
                # Extract round from tmux pane
                current_round=$(tmux capture-pane -t flaky-python -p 2>/dev/null | grep -oP "Run #\K\d+" | tail -1 || echo "?")
                echo "   Round: $current_round / 20"
            fi
            if [ -n "$current_proj" ]; then
                echo "   Current: $current_proj"
            fi
        else
            echo "🐍 Python (pytest): COMPLETED ✅"
        fi
        
        echo ""
        echo "=========================================="
        echo ""
    }
    
    print_test_status
    
    # Wait loop
    while check_session flaky-java || check_session flaky-python; do
        sleep 60
        print_test_status
    done
    
    local total_elapsed=$(get_elapsed_time)
    echo "=========================================="
    echo "✅ All tests completed!"
    echo "⏱️  Total Time: $total_elapsed"
    echo "=========================================="
    echo ""
    sleep 5  # Let logs flush
fi

echo ""
echo "Configuration:"
echo "  Results directory: $RESULTS_DIR"
echo "  Output directory: $OUTPUT_DIR"
echo "  Mode: $MODE"
echo ""

# Run analysis based on mode
case "$MODE" in
    analyze|all)
        echo "📝 Generating analysis reports..."
        python visualization/analyze_results.py \
            --results-dir "$RESULTS_DIR" \
            --output-dir "$OUTPUT_DIR"
        ;;
esac

case "$MODE" in
    html|all)
        echo ""
        echo "🌐 Generating HTML report..."
        python visualization/html_report.py \
            --results-dir "$RESULTS_DIR" \
            --output "$OUTPUT_DIR/flaky_tests_report.html"
        ;;
esac

case "$MODE" in
    dashboard)
        echo ""
        echo "🚀 Starting interactive dashboard..."
        echo "🌐 Dashboard will open in your browser"
        echo "Press Ctrl+C to stop"
        echo ""
        streamlit run visualization/dashboard.py
        ;;
esac

if [ "$MODE" = "all" ]; then
    echo ""
    echo "=========================================="
    echo "✅ Analysis complete!"
    echo "=========================================="
    echo ""
    echo "📂 Results saved in: $OUTPUT_DIR"
    echo ""
    echo "📖 Available files:"
    echo "  - summary_report.md         : Markdown summary"
    echo "  - flaky_tests_report.html   : Interactive HTML report"
    echo "  - flaky_tests_data.csv      : Raw data export"
    echo "  - project_summary.csv       : Project summary"
    echo ""
    echo "💡 Next steps:"
    echo "  - View dashboard: make dashboard"
    echo "  - Open HTML report: xdg-open $OUTPUT_DIR/flaky_tests_report.html"
    echo "  - Run cleanup: make cleanup"
    echo ""
    
    # Auto-cleanup if tests were waited for
    if [ "$WAIT_FOR_TESTS" = "true" ] || [ "$WAIT_FOR_TESTS" = "1" ]; then
        echo "🧹 Running automatic cleanup..."
        echo ""
        if [ -f "$SCRIPT_DIR/cleanup.sh" ]; then
            bash "$SCRIPT_DIR/cleanup.sh"
        fi
    fi
fi

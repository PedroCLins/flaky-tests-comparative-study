#!/bin/bash
clear
echo "=========================================="
echo "RETRY PROGRESS MONITOR"
echo "=========================================="
echo ""

echo "=== PYTHON RETRY ==="
if ps aux | grep -q "[r]un_failed_only.sh python"; then
    echo "Status: 🏃 RUNNING"
    tail -5 /tmp/retry_python_bg.log 2>/dev/null | grep -E "Run #|Testing|complete|passed|failed" | tail -3
else
    echo "Status: ✅ COMPLETED or ❌ STOPPED"
fi

echo ""
echo "=== JAVA RETRY ==="
if ps aux | grep -q "[r]un_failed_only.sh java"; then
    echo "Status: 🏃 RUNNING"
    tail -5 /tmp/retry_java_bg.log 2>/dev/null | grep -E "Running|Testing|Building" | tail -3
else
    echo "Status: ✅ COMPLETED or ❌ STOPPED"
fi

echo ""
echo "=== CURRENT RESULTS ==="
for proj in black celery httpx commons-lang commons-collections; do
    latest=$(find results/$proj -name "runs.csv" -o -name "summary.txt" 2>/dev/null | sort | tail -1)
    if [ -n "$latest" ]; then
        if [[ "$latest" == *.csv ]]; then
            rounds=$(($(wc -l < "$latest") - 1))
            echo "$proj: ✅ $rounds rounds"
        else
            echo "$proj: ✅ Completed"
        fi
    else
        echo "$proj: ⏳ Pending"
    fi
done

echo ""
echo "Run: watch -n 5 bash scripts/check_retry_progress.sh"

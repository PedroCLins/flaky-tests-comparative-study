# Running Flaky Test Detection - Guide

## Running in Background (Detached)

### Option 1: Basic Background Execution
Run the entire suite in the background and redirect output to a log file:

```bash
make all > make_output.log 2>&1 &
```

Monitor progress in real-time:
```bash
tail -f make_output.log
```

### Option 2: Using nohup (Persistent)
Keep the process running even if you close the terminal:

```bash
nohup make all > make_output.log 2>&1 &
```

Check the process:
```bash
jobs           # See background jobs
ps aux | grep make   # Find the process
```

Monitor progress:
```bash
tail -f make_output.log
```

Kill if needed:
```bash
kill %1        # Kill job 1
# or
kill <PID>     # Kill by process ID
```

### Option 3: Using tmux (Recommended for Long Runs)

Create a detachable session:
```bash
# Install tmux if needed
sudo apt-get install tmux

# Create new session
tmux new -s flaky-tests

# Inside tmux, run your command
make all

# Detach: Press Ctrl+b, then press d
# Your process continues running in the background

# Reattach later
tmux attach -t flaky-tests

# List all sessions
tmux ls

# Kill session when done
tmux kill-session -t flaky-tests
```

### Option 4: Using screen (Alternative to tmux)

```bash
# Install screen if needed
sudo apt-get install screen

# Create new session
screen -S flaky-tests

# Run your command
make all

# Detach: Press Ctrl+a, then press d

# Reattach later
screen -r flaky-tests

# List sessions
screen -ls
```

## Running Individual Targets

Run specific tools only:

```bash
# In background
nohup make nondex > nondex.log 2>&1 &
nohup make idflakies > idflakies.log 2>&1 &
nohup make python > python.log 2>&1 &
```

## Monitoring Progress

### Check what's running:
```bash
ps aux | grep -E "(make|mvn|gradle|pytest)"
```

### Watch log files:
```bash
# Follow main log
tail -f make_output.log

# Follow specific tool logs
tail -f results/*/nondex/*/nondex.log
tail -f results/*/idflakies/*/idflakies.log
tail -f results/*/pytest-rerun/*/run_*.log
```

### Check results directory:
```bash
# See what's been created
tree results/

# Count completed runs
ls -la results/*/pytest-rerun/*/run_*.log | wc -l
```

## Tips

1. **Estimate time**: These tests can take hours to complete
2. **Check disk space**: Results can be large
3. **Use tmux/screen** for long-running tests
4. **Monitor system resources**: `htop` or `top`
5. **Background + nohup** is good for overnight runs

## Quick Reference

```bash
# Start detached with tmux (RECOMMENDED)
tmux new -s flaky-tests
make all
# Ctrl+b, then d to detach

# Or simple background
nohup make all > output.log 2>&1 &

# Monitor
tail -f output.log

# Reattach tmux
tmux attach -t flaky-tests
```

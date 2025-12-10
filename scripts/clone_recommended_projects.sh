#!/usr/bin/env bash
set -e

# Get the experiments directory from .env or use default
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

# Load .env if exists (but don't execute it as bash commands)
if [ -f "$REPO_ROOT/.env" ]; then
    export $(grep -v '^#' "$REPO_ROOT/.env" | grep 'EXPERIMENT_DIR' | xargs)
fi

EXPERIMENT_DIR="${EXPERIMENT_DIR:-../flaky-tests-experiments}"
EXPERIMENTS_PATH="$REPO_ROOT/$EXPERIMENT_DIR"

echo "=========================================="
echo "Cloning Recommended Projects"
echo "=========================================="
echo "Target directory: $EXPERIMENTS_PATH"
echo ""

mkdir -p "$EXPERIMENTS_PATH"
cd "$EXPERIMENTS_PATH"

# Function to clone or skip if exists
clone_if_not_exists() {
    local url=$1
    local name=$(basename "$url" .git)
    
    if [ -d "$name" ]; then
        echo "⏭️  Skipping $name (already exists)"
    else
        echo "📥 Cloning $name..."
        git clone "$url"
        echo "✅ $name cloned"
    fi
}

echo "=========================================="
echo "Java Projects (for NonDex)"
echo "=========================================="
echo ""

echo "--- Apache Commons (Known for order-dependent tests) ---"
clone_if_not_exists "https://github.com/apache/commons-collections.git"
clone_if_not_exists "https://github.com/apache/commons-codec.git"
clone_if_not_exists "https://github.com/apache/commons-io.git"

echo ""
echo "--- Other Popular Projects ---"
clone_if_not_exists "https://github.com/google/guava.git"
clone_if_not_exists "https://github.com/square/retrofit.git"

echo ""
echo "=========================================="
echo "Python Projects (for pytest)"
echo "=========================================="
echo ""

echo "--- Web Frameworks & Tools (Smaller, manageable) ---"
clone_if_not_exists "https://github.com/httpie/httpie.git"
clone_if_not_exists "https://github.com/pallets/flask.git"
clone_if_not_exists "https://github.com/psf/black.git"

echo ""
echo "--- Async & Task Queues (Timing-related flakiness) ---"
clone_if_not_exists "https://github.com/celery/celery.git"
clone_if_not_exists "https://github.com/encode/httpx.git"

echo ""
echo "=========================================="
echo "✅ All recommended projects cloned!"
echo "=========================================="
echo ""
echo "📝 Next steps:"
echo "1. Update your .env file with the projects you want to test:"
echo "   JAVA_PROJECTS=commons-lang commons-collections commons-codec guava"
echo "   PYTHON_PROJECTS=httpie flask black"
echo ""
echo "2. Run the tests:"
echo "   make java    # Run NonDex on Java projects"
echo "   make python  # Run pytest on Python projects (50 rounds)"
echo ""
echo "3. View results:"
echo "   make visualize   # Generate reports"
echo "   make dashboard   # Interactive dashboard"

#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$1"   # e.g. ../flaky-tests-experiments/mockito

# Get absolute path for results directory before changing directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
OUTDIR="$REPO_ROOT/results/$(basename "$PROJECT_DIR")/nondex/$(date +%F_%H-%M-%S)"
mkdir -p "$OUTDIR"

pushd "$PROJECT_DIR" >/dev/null

# record commit
git rev-parse HEAD > "$OUTDIR/commit.txt" || true

# Detect build system (Maven or Gradle)
if [ -f "pom.xml" ]; then
  BUILD_SYSTEM="maven"
  echo "Detected Maven project"
elif [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then
  BUILD_SYSTEM="gradle"
  echo "Detected Gradle project"
else
  echo "ERROR: No pom.xml or build.gradle found. Cannot determine build system."
  exit 1
fi

# Run NonDex based on build system
echo "=========================================="
echo "Starting NonDex for $(basename "$PROJECT_DIR")"
echo "Build System: $BUILD_SYSTEM"
echo "Output Directory: $OUTDIR"
echo "=========================================="

if [ "$BUILD_SYSTEM" = "maven" ]; then
  echo "Running NonDex (mvn edu.illinois:nondex-maven-plugin:2.1.7:nondex) on $(pwd)"
  mvn edu.illinois:nondex-maven-plugin:2.1.7:nondex \
    -DskipTests=false \
    | tee "$OUTDIR/nondex.log"
else
  # Gradle
  echo "Running NonDex (Gradle plugin) on $(pwd)"
  # Use gradlew if available, otherwise gradle
  if [ -f "./gradlew" ]; then
    GRADLE_CMD="./gradlew"
  else
    GRADLE_CMD="gradle"
  fi
  
  # Run NonDex with Gradle
  $GRADLE_CMD nondexTest \
    | tee "$OUTDIR/nondex.log"
fi

echo "=========================================="
echo "✓ NonDex complete for $(basename "$PROJECT_DIR")"
echo "=========================================="

# Copy useful artifacts (if plugin produced them)
# Maven: copy surefire-reports
if [ -d "target/surefire-reports" ]; then
  cp -r target/surefire-reports "$OUTDIR"/ || true
fi

# Gradle: copy test results
if [ -d "build/test-results" ]; then
  cp -r build/test-results "$OUTDIR"/ || true
fi
if [ -d "build/reports/tests" ]; then
  cp -r build/reports/tests "$OUTDIR"/ || true
fi

# Save metadata
echo "{\"project\":\"$(basename "$PROJECT_DIR")\",\"date\":\"$(date --iso-8601=seconds)\",\"build_system\":\"$BUILD_SYSTEM\"}" > "$OUTDIR/metadata.json"

popd >/dev/null
echo "Results in $OUTDIR"

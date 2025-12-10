#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$1"   # e.g. ../flaky-tests-experiments/mockito

# Get absolute path for results directory before changing directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
OUTDIR="$REPO_ROOT/results/$(basename "$PROJECT_DIR")/nondex/$(date +%F_%H-%M-%S)"
mkdir -p "$OUTDIR"

# Ensure a usable Java runtime on macOS (fixes "Unable to locate a Java Runtime" from /usr/bin/java
# and helps avoid plugin errors caused by too-new JDKs). This will try to find JDK 21 then 17,
# then Homebrew-installed OpenJDK locations. If none found, we print a clear message.
set_java_home_macos() {
  # prefer specific modern LTS/JDK versions that tooling supports
  for ver in 21 17; do
    if command -v /usr/libexec/java_home >/dev/null 2>&1; then
      jhome=$(/usr/libexec/java_home -v "$ver" 2>/dev/null || true)
      if [ -n "$jhome" ]; then
        export JAVA_HOME="$jhome"
        export PATH="$JAVA_HOME/bin:$PATH"
        echo "Using Java from /usr/libexec/java_home: $JAVA_HOME"
        return 0
      fi
    fi
  done

  # Check Homebrew versioned JDK installations (prefer 21, then 17)
  for ver in 21 17; do
    if [ -d "/opt/homebrew/opt/openjdk@${ver}/libexec/openjdk.jdk/Contents/Home" ]; then
      export JAVA_HOME="/opt/homebrew/opt/openjdk@${ver}/libexec/openjdk.jdk/Contents/Home"
      export PATH="$JAVA_HOME/bin:$PATH"
      echo "Using Homebrew openjdk@${ver}: $JAVA_HOME"
      return 0
    fi
  done

  # fallback to Homebrew opt path (latest version)
  if [ -d "/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home" ]; then
    export JAVA_HOME="/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home"
    export PATH="$JAVA_HOME/bin:$PATH"
    echo "Using Homebrew openjdk: $JAVA_HOME"
    return 0
  fi

  # try Cellar locations (pick the newest if present)
  if ls /opt/homebrew/Cellar/openjdk/*/libexec/openjdk.jdk/Contents/Home >/dev/null 2>&1; then
    candidate=$(ls -d /opt/homebrew/Cellar/openjdk/*/libexec/openjdk.jdk/Contents/Home | tail -n 1)
    export JAVA_HOME="$candidate"
    export PATH="$JAVA_HOME/bin:$PATH"
    echo "Using Homebrew Cellar openjdk: $JAVA_HOME"
    return 0
  fi

  return 1
}

# On macOS try to set a usable JAVA_HOME if /usr/bin/java is missing or broken
if [ "$(uname -s)" = "Darwin" ]; then
  # Always try to use Java 17 or 21 for better tool compatibility (NonDex has issues with Java 25+)
  if ! set_java_home_macos; then
    echo "ERROR: No usable Java runtime found. Please install a JDK (preferably 17 or 21)"
    echo "  - Homebrew: brew install openjdk@17  (or openjdk@21 if available)"
    echo "  - Or install Temurin/Adoptium/Oracle JDK and ensure /usr/libexec/java_home -v 17 works"
    exit 1
  fi
fi

# change into project dir
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
  # Allow NonDex to fail - test failures are expected when flaky tests are found
  mvn edu.illinois:nondex-maven-plugin:2.1.7:nondex \
    -DskipTests=false \
    | tee "$OUTDIR/nondex.log" || true
else
  # Gradle
  echo "Running NonDex (Gradle plugin) on $(pwd)"
  # Use gradlew if available, otherwise gradle
  if [ -f "./gradlew" ]; then
    GRADLE_CMD="./gradlew"
  else
    GRADLE_CMD="gradle"
  fi
  
  # Check if nondexTest task exists
  if $GRADLE_CMD tasks --all | grep -q "nondexTest"; then
    echo "Found nondexTest task, running NonDex..."
    $GRADLE_CMD nondexTest \
      | tee "$OUTDIR/nondex.log"
  else
    echo "WARNING: NonDex plugin not configured for this Gradle project."
    echo "The nondexTest task is not available. You may need to:"
    echo "1. Add the NonDex plugin to build.gradle(.kts):"
    echo "   plugins { id 'edu.illinois.nondex' version '2.1.7' }"
    echo "2. Or check if the project uses a different NonDex configuration"
    echo ""
    echo "Running regular test suite instead as fallback..."
    $GRADLE_CMD test \
      | tee "$OUTDIR/nondex.log"
    
    # Add a note to the log about the fallback
    echo "" >> "$OUTDIR/nondex.log"
    echo "NOTE: This was a fallback run using regular 'test' task because NonDex plugin was not configured." >> "$OUTDIR/nondex.log"
    echo "To enable NonDx for this project, add the NonDx plugin to build.gradle(.kts)" >> "$OUTDIR/nondx.log"
  fi
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

# Small summary of NonDex run
SUMMARY="$OUTDIR/summary.txt"
{
  echo "project: $(basename "$PROJECT_DIR")"
  echo "tool: NonDex"
  echo "log: $OUTDIR/nondex.log"
  echo
  # count common keywords
  errors=$(grep -Ei "error|exception" "$OUTDIR/nondex.log" | wc -l || true)
  warns=$(grep -Ei "warn|warning" "$OUTDIR/nondex.log" | wc -l || true)
  fails=$(grep -Ei "FAILED|FAILURES" "$OUTDIR/nondex.log" | wc -l || true)
  echo "error_lines: $errors"
  echo "warning_lines: $warns"
  echo "failed_lines: $fails"
  echo
  # report presence of test result artifacts
  if [ -d "$OUTDIR/surefire-reports" ]; then
    echo "artifacts: surefire-reports (copied)"
  fi
  if [ -d "$OUTDIR/test-results" ] || [ -d "$OUTDIR/reports/tests" ]; then
    echo "artifacts: gradle test results/reports (copied)"
  fi
  echo
  echo "last 10 relevant lines from log:"
  grep -Ei "ERROR|EXCEPTION|FAILED|WARN|WARNING|Exception in thread" "$OUTDIR/nondex.log" | tail -n 10 || true
} > "$SUMMARY"

echo "---- Short summary ----"
sed -n '1,20p' "$SUMMARY" | sed -n '1,8p'
echo "(Full summary file: $SUMMARY)"
echo "-----------------------"

# 📊 Flaky Test Metrics Documentation

This document explains the comprehensive metrics system implemented for analyzing the effectiveness of flaky test detection tools (NonDex and pytest-rerun).

## Table of Contents
1. [Overview](#overview)
2. [Individual Test Metrics](#individual-test-metrics)
3. [Project-Level Metrics](#project-level-metrics)
4. [Tool Comparison Metrics](#tool-comparison-metrics)
5. [Statistical Significance](#statistical-significance)
6. [Interpretation Guide](#interpretation-guide)

---

## Overview

The metrics system provides **four approaches** to evaluate flaky test detection without requiring ground truth:

1. **Self-Comparison** - Uses multiple runs to identify tests with inconsistent behavior
2. **Statistical Analysis** - Validates flakiness isn't random noise
3. **Severity Classification** - Categorizes how problematic each flaky test is
4. **Cross-Tool Validation** - Compares results between NonDex and pytest

---

## Individual Test Metrics

For each test that shows flaky behavior, we calculate:

### 1. Failure Rate
**Formula**: `failures / total_runs`

**Meaning**: The proportion of test executions that resulted in failure.

**Interpretation**:
- `0%` = Always passes (deterministic, stable)
- `1-10%` = Low flakiness (occasional failures)
- `10-40%` = Medium flakiness (frequent failures)
- `40-60%` = High flakiness (highly unstable)
- `>90%` = Likely a consistent bug, not flakiness
- `100%` = Always fails (deterministic failure)

**Why it matters**: Tests with 40-60% failure rates are the most concerning as they're unpredictable.

### 2. Variance & Standard Deviation
**Formula**: 
- Variance = `p(1-p)` where p = failure rate (Bernoulli distribution)
- Std Dev = `√variance`

**Meaning**: Measures the consistency of test behavior.

**Interpretation**:
- Low variance (near 0 or 1) = Deterministic
- High variance (around 0.5) = Unpredictable

### 3. Confidence Interval (95%)
**Method**: Wilson score interval

**Meaning**: Statistical range where the true failure rate likely falls.

**Example**: `[0.145, 0.519]` means we're 95% confident the real failure rate is between 14.5% and 51.9%.

**Why Wilson over normal approximation**: More accurate for:
- Small sample sizes (< 30 runs)
- Extreme proportions (near 0% or 100%)

### 4. P-Value (Statistical Significance)
**Test**: Two-sided binomial test

**Null Hypothesis (H0)**: Test is deterministic (always passes OR always fails)

**Alternative Hypothesis (H1)**: Test is truly flaky

**Interpretation**:
- `p < 0.05` → Statistically significant flakiness (reject H0)
- `p ≥ 0.05` → Could be random noise or insufficient data

**Why it matters**: Prevents false positives from random environmental issues.

### 5. Flakiness Severity
**Categories**:

| Severity | Failure Rate | Meaning |
|----------|--------------|---------|
| `stable_pass` | 0-1% | Always/almost always passes |
| `low` | 1-10% | Occasional flakiness |
| `medium` | 10-40% | Frequent flakiness |
| `high` | 40-60% | Critical instability |
| `unstable` | Varies | Borderline flakiness (not statistically significant) |
| `stable_fail` | 90-100% | Always/almost always fails (likely a bug) |

**Action Items by Severity**:
- **High**: Immediate attention required
- **Medium**: Should be investigated soon
- **Low**: Monitor and fix when convenient
- **Stable Fail**: Not flaky - it's a consistent bug that needs fixing

---

## Project-Level Metrics

Aggregated statistics for each project:

### 1. Total Tests Analyzed
Number of unique tests that were executed across all runs.

### 2. Flaky Tests Detected
Count of tests that:
- Failed in some runs but not all
- Are statistically significantly flaky (p < 0.05)

### 3. Flaky Percentage
`(flaky_tests / total_tests) × 100`

**Benchmarks**:
- < 1%: Excellent test suite health
- 1-5%: Normal for large codebases
- 5-10%: Concerning, investigation needed
- > 10%: Critical test suite health issue

### 4. Average/Median Failure Rate
Central tendency of failure rates across all flaky tests.

**Interpretation**:
- Median < 20%: Most flaky tests fail occasionally
- Median > 40%: Many highly unstable tests

### 5. Severity Distribution
Breakdown of flaky tests by severity level.

**Example**:
```
High: 2 tests
Medium: 15 tests
Low: 33 tests
```

**Ideal Distribution**: Most tests in "low" category, few/none in "high".

---

## Tool Comparison Metrics

When comparing NonDex (Java) vs pytest-rerun (Python):

### 1. Agreement Rate
**Formula**: `common_detections / total_unique_detections`

**Meaning**: What proportion of detected flaky tests do both tools agree on?

**Interpretation**:
- High agreement (> 70%) = Tools are consistent
- Low agreement (< 30%) = Tools detect different types of flakiness

### 2. Jaccard Similarity
**Formula**: `|A ∩ B| / |A ∪ B|` (intersection over union)

**Meaning**: Overall similarity between tool results.

**Range**: 0.0 to 1.0
- 1.0 = Perfect agreement
- 0.5 = Moderate overlap
- 0.0 = No overlap

### 3. Unique Detections
Tests found by only one tool.

**Why this matters**:
- Shows complementary strengths
- Tool A unique detections might indicate specific flakiness types (e.g., nondeterministic collections)
- Tool B unique detections might catch different issues (e.g., timing-dependent tests)

---

## Statistical Significance

### Why We Need It
Running tests multiple times will naturally produce some failures due to:
- Random hardware glitches
- Network timeouts
- Race conditions in parallel test execution

**Statistical tests help distinguish** between:
- **True flakiness**: Inherent test instability
- **Random noise**: Environmental factors

### Our Approach: Binomial Test

**Assumptions**:
- Each test run is independent
- Test has two outcomes: pass or fail
- Follows Bernoulli/binomial distribution

**Process**:
1. Count failures across N runs
2. Test if failure rate is significantly different from 0% (always passes) or 100% (always fails)
3. If p-value < 0.05, we reject the hypothesis that the test is deterministic

**Example**:
```
Test: calculate_total()
Runs: 20
Failures: 6 (30% failure rate)
P-value: 0.0001

Conclusion: This is statistically significant flakiness (p << 0.05)
```

---

## Interpretation Guide

### Scenario 1: High Failure Rate but High P-Value
```
Failure Rate: 80%
P-Value: 0.15
```
**Interpretation**: Likely a consistent bug, not flakiness. The test almost always fails.

**Action**: Fix the bug or update the test.

### Scenario 2: Medium Failure Rate, Low P-Value
```
Failure Rate: 35%
P-Value: 0.001
```
**Interpretation**: True medium-severity flakiness.

**Action**: Investigate root cause (timing issues, shared state, etc.).

### Scenario 3: Low Failure Rate, Wide Confidence Interval
```
Failure Rate: 5%
Confidence Interval: [0.01, 0.25]
P-Value: 0.04
```
**Interpretation**: Flaky but uncertain due to few runs. Need more data.

**Action**: Run more iterations to narrow confidence interval.

### Scenario 4: Both Tools Detect Same Tests
```
NonDex: 15 flaky tests
Pytest: 15 flaky tests
Common: 12 tests
```
**Interpretation**: High agreement (80%) suggests robust detection.

**Action**: Focus on the 12 commonly detected tests first.

### Scenario 5: Tools Find Different Tests
```
NonDex: 20 flaky tests (Java projects)
Pytest: 15 flaky tests (Python projects)
Common: 0 tests
```
**Interpretation**: Can't directly compare - different languages/projects.

**Action**: Compare metrics within each ecosystem separately.

---

## Practical Usage

### 1. Prioritizing Test Fixes

**Sort by severity:**
```sql
SELECT test_name, failure_rate, severity, p_value
FROM flaky_tests_metrics
WHERE is_flaky = TRUE
ORDER BY 
  CASE severity
    WHEN 'high' THEN 1
    WHEN 'medium' THEN 2
    WHEN 'low' THEN 3
  END,
  failure_rate DESC;
```

### 2. Identifying Patterns

Look for common prefixes in flaky test names:
```python
# Are all database tests flaky?
db_tests = [t for t in flaky_tests if 'database' in t.lower()]
```

### 3. Measuring Improvement

Compare metrics over time:
```python
# Before fix: 45 flaky tests, 8.2% average failure rate
# After fix: 32 flaky tests, 4.1% average failure rate
# Improvement: 29% reduction in flaky tests
```

### 4. Confidence in Results

**High Confidence (Reliable Results)**:
- ≥ 20 test runs per project
- P-value < 0.01
- Narrow confidence intervals (< 20% width)

**Low Confidence (Need More Data)**:
- < 10 test runs
- P-value close to 0.05
- Wide confidence intervals (> 40% width)

---

## Data Export Formats

### 1. `test_metrics_detailed.csv`
All tests (flaky and stable) with complete metrics.

**Columns**: project, test_name, total_runs, failures, failure_rate, is_flaky, severity, variance, std_dev, ci_lower, ci_upper, p_value

### 2. `flaky_tests_metrics.csv`
Only statistically significant flaky tests.

**Use**: Quick analysis of problematic tests.

### 3. `project_summary.csv`
Project-level aggregate metrics.

**Use**: High-level comparison across projects.

---

## References

- **Wilson Score Interval**: Brown, L. D., Cai, T. T., & DasGupta, A. (2001). Interval estimation for a binomial proportion. Statistical Science, 16(2), 101-133.
- **Binomial Test**: Clopper, C. J., & Pearson, E. S. (1934). The use of confidence or fiducial limits illustrated in the case of the binomial. Biometrika, 26(4), 404-413.
- **Flaky Test Detection**: Luo, Q., Hariri, F., Eloussi, L., & Marinov, D. (2014). An empirical analysis of flaky tests. In Proceedings of the 22nd ACM SIGSOFT International Symposium on Foundations of Software Engineering (pp. 643-653).

---

## Questions & Answers

**Q: Why 20 test runs instead of more/less?**  
A: 20 provides a good balance between statistical power (detecting flakiness) and execution time. With 20 runs, we can detect flakiness with 10% failure rate with reasonable confidence.

**Q: Can I trust results with only 5 test runs?**  
A: Results are less reliable with fewer runs. P-values and confidence intervals will be less accurate. Aim for at least 10-15 runs minimum.

**Q: What if a test has 50% failure rate?**  
A: This is the most problematic case - the test is maximally unpredictable. It's equally likely to pass or fail, making it useless for regression detection.

**Q: Should I fix all flaky tests?**  
A: Prioritize based on:
1. Severity (high → medium → low)
2. Impact (critical tests vs. edge cases)
3. Frequency (how often the test runs in CI)

**Q: How do I know if my metrics are meaningful?**  
A: Check these indicators:
- ✅ Enough runs (≥ 15 per project)
- ✅ Statistical significance (p < 0.05)
- ✅ Consistent detection across runs
- ✅ Matches manual observations

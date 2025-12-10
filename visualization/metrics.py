#!/usr/bin/env python3
"""
Metrics calculation module for flaky test analysis.

This module provides statistical and comparative metrics for evaluating
the effectiveness of flaky test detection tools.
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class TestMetrics:
    """Metrics for a single test across multiple runs."""
    test_name: str
    total_runs: int
    failures: int
    failure_rate: float
    is_flaky: bool
    variance: float
    std_dev: float
    confidence_interval_95: Tuple[float, float]
    p_value: float  # Statistical significance
    flakiness_severity: str  # 'low', 'medium', 'high', 'deterministic'


@dataclass
class ToolComparisonMetrics:
    """Comparative metrics between detection tools."""
    tool_a_name: str
    tool_b_name: str
    tool_a_detections: int
    tool_b_detections: int
    common_detections: int
    tool_a_unique: int
    tool_b_unique: int
    agreement_rate: float
    jaccard_similarity: float


class FlakinessMetrics:
    """
    Calculate comprehensive metrics for flaky test detection analysis.
    
    This class provides methods to:
    1. Calculate per-test flakiness metrics (failure rate, variance, significance)
    2. Compare different detection tools
    3. Perform statistical significance tests
    4. Categorize flakiness severity
    """
    
    # Thresholds for flakiness severity classification
    SEVERITY_THRESHOLDS = {
        'deterministic_pass': (0.0, 0.01),      # 0-1% failure rate
        'low': (0.01, 0.10),                     # 1-10% failure rate
        'medium': (0.10, 0.40),                  # 10-40% failure rate
        'high': (0.40, 0.60),                    # 40-60% failure rate (highly unstable)
        'deterministic_fail': (0.90, 1.01)       # 90-100% failure rate
    }
    
    SIGNIFICANCE_LEVEL = 0.05  # Alpha for statistical tests
    
    @staticmethod
    def calculate_test_metrics(test_name: str, failure_runs: List[bool]) -> TestMetrics:
        """
        Calculate comprehensive metrics for a single test across multiple runs.
        
        Args:
            test_name: Name/identifier of the test
            failure_runs: List of boolean values (True if test failed in that run)
            
        Returns:
            TestMetrics object with all calculated metrics
        """
        total_runs = len(failure_runs)
        failures = sum(failure_runs)
        failure_rate = failures / total_runs if total_runs > 0 else 0.0
        
        # Variance and standard deviation
        # Treating as Bernoulli distribution: var = p(1-p)
        variance = failure_rate * (1 - failure_rate)
        std_dev = np.sqrt(variance)
        
        # 95% Confidence Interval using Wilson score interval
        # More accurate than normal approximation for proportions
        ci_lower, ci_upper = FlakinessMetrics._wilson_confidence_interval(
            failures, total_runs
        )
        
        # Statistical significance test (binomial test)
        # H0: test is deterministic (p=0 or p=1)
        # H1: test is flaky (0 < p < 1)
        p_value = FlakinessMetrics._test_flakiness_significance(
            failures, total_runs
        )
        
        # Determine if test is truly flaky (not just random noise)
        is_flaky = (
            0 < failures < total_runs and  # Failed in some but not all runs
            p_value < FlakinessMetrics.SIGNIFICANCE_LEVEL  # Statistically significant
        )
        
        # Categorize severity
        severity = FlakinessMetrics._categorize_severity(failure_rate, is_flaky)
        
        return TestMetrics(
            test_name=test_name,
            total_runs=total_runs,
            failures=failures,
            failure_rate=failure_rate,
            is_flaky=is_flaky,
            variance=variance,
            std_dev=std_dev,
            confidence_interval_95=(ci_lower, ci_upper),
            p_value=p_value,
            flakiness_severity=severity
        )
    
    @staticmethod
    def _wilson_confidence_interval(successes: int, total: int, 
                                    confidence: float = 0.95) -> Tuple[float, float]:
        """
        Calculate Wilson score confidence interval for a proportion.
        
        More accurate than normal approximation, especially for small samples
        or extreme proportions.
        """
        if total == 0:
            return (0.0, 0.0)
        
        z = stats.norm.ppf((1 + confidence) / 2)
        p = successes / total
        denominator = 1 + z**2 / total
        
        center = (p + z**2 / (2 * total)) / denominator
        margin = z * np.sqrt((p * (1 - p) + z**2 / (4 * total)) / total) / denominator
        
        return (max(0, center - margin), min(1, center + margin))
    
    @staticmethod
    def _test_flakiness_significance(failures: int, total_runs: int) -> float:
        """
        Test if observed failures are statistically significant (not random).
        
        Uses binomial test with H0: test is deterministic (p=0 or p=1).
        Returns p-value.
        """
        if total_runs == 0:
            return 1.0
        
        if failures == 0 or failures == total_runs:
            # Deterministic test - not flaky
            return 1.0
        
        # Two-sided binomial test
        # Test against both extremes (p=0 and p=1)
        p_value_zero = stats.binomtest(failures, total_runs, p=0.0, alternative='two-sided').pvalue
        p_value_one = stats.binomtest(failures, total_runs, p=1.0, alternative='two-sided').pvalue
        
        # Return the more conservative (higher) p-value
        return max(p_value_zero, p_value_one)
    
    @staticmethod
    def _categorize_severity(failure_rate: float, is_flaky: bool) -> str:
        """
        Categorize the severity of flakiness based on failure rate.
        
        Args:
            failure_rate: Proportion of runs where test failed (0.0 to 1.0)
            is_flaky: Whether the test is statistically significantly flaky
            
        Returns:
            Severity category: 'deterministic_pass', 'low', 'medium', 'high', 
                              'deterministic_fail', or 'stable'
        """
        if not is_flaky:
            if failure_rate < 0.01:
                return 'stable_pass'
            elif failure_rate > 0.99:
                return 'stable_fail'
            else:
                return 'unstable'  # Borderline case
        
        for severity, (lower, upper) in FlakinessMetrics.SEVERITY_THRESHOLDS.items():
            if lower <= failure_rate < upper:
                return severity
        
        # Middle range (most concerning flakiness)
        if 0.10 <= failure_rate <= 0.90:
            if 0.40 <= failure_rate <= 0.60:
                return 'high'
            else:
                return 'medium'
        
        return 'low'
    
    @staticmethod
    def compare_tools(tool_a_tests: set, tool_b_tests: set, 
                     tool_a_name: str = "Tool A", 
                     tool_b_name: str = "Tool B") -> ToolComparisonMetrics:
        """
        Compare two tools based on the sets of flaky tests they detected.
        
        Args:
            tool_a_tests: Set of test names detected as flaky by tool A
            tool_b_tests: Set of test names detected as flaky by tool B
            tool_a_name: Name of first tool (e.g., "NonDex")
            tool_b_name: Name of second tool (e.g., "pytest-rerun")
            
        Returns:
            ToolComparisonMetrics with comparative statistics
        """
        common = tool_a_tests & tool_b_tests
        unique_a = tool_a_tests - tool_b_tests
        unique_b = tool_b_tests - tool_a_tests
        union = tool_a_tests | tool_b_tests
        
        # Agreement rate: what proportion of total detections do they agree on?
        agreement_rate = len(common) / len(union) if union else 0.0
        
        # Jaccard similarity: intersection over union
        jaccard = len(common) / len(union) if union else 0.0
        
        return ToolComparisonMetrics(
            tool_a_name=tool_a_name,
            tool_b_name=tool_b_name,
            tool_a_detections=len(tool_a_tests),
            tool_b_detections=len(tool_b_tests),
            common_detections=len(common),
            tool_a_unique=len(unique_a),
            tool_b_unique=len(unique_b),
            agreement_rate=agreement_rate,
            jaccard_similarity=jaccard
        )
    
    @staticmethod
    def chi_square_independence_test(test_a_results: List[bool], 
                                     test_b_results: List[bool]) -> Dict[str, float]:
        """
        Test if two tests are independent or if they tend to fail together.
        
        Useful for identifying tests with correlated failures.
        
        Args:
            test_a_results: List of pass/fail results for test A
            test_b_results: List of pass/fail results for test B
            
        Returns:
            Dictionary with chi-square statistic, p-value, and correlation
        """
        if len(test_a_results) != len(test_b_results):
            raise ValueError("Test results must have same length")
        
        # Create contingency table
        both_fail = sum(a and b for a, b in zip(test_a_results, test_b_results))
        a_fail_b_pass = sum(a and not b for a, b in zip(test_a_results, test_b_results))
        a_pass_b_fail = sum(not a and b for a, b in zip(test_a_results, test_b_results))
        both_pass = sum(not a and not b for a, b in zip(test_a_results, test_b_results))
        
        contingency_table = np.array([
            [both_fail, a_fail_b_pass],
            [a_pass_b_fail, both_pass]
        ])
        
        # Chi-square test
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
        
        # Phi coefficient (measure of correlation for binary variables)
        n = len(test_a_results)
        phi = np.sqrt(chi2 / n) if n > 0 else 0.0
        
        return {
            'chi_square': chi2,
            'p_value': p_value,
            'phi_coefficient': phi,
            'independent': p_value > FlakinessMetrics.SIGNIFICANCE_LEVEL
        }
    
    @staticmethod
    def calculate_project_metrics(test_metrics_list: List[TestMetrics]) -> Dict:
        """
        Calculate aggregate metrics for an entire project.
        
        Args:
            test_metrics_list: List of TestMetrics for all tests in project
            
        Returns:
            Dictionary with project-level statistics
        """
        if not test_metrics_list:
            return {
                'total_tests': 0,
                'flaky_tests': 0,
                'flaky_percentage': 0.0,
                'severity_distribution': {},
                'avg_failure_rate': 0.0,
                'median_failure_rate': 0.0
            }
        
        flaky_tests = [tm for tm in test_metrics_list if tm.is_flaky]
        
        # Severity distribution
        severity_counts = {}
        for tm in test_metrics_list:
            severity_counts[tm.flakiness_severity] = \
                severity_counts.get(tm.flakiness_severity, 0) + 1
        
        # Failure rates (only for flaky tests)
        flaky_failure_rates = [tm.failure_rate for tm in flaky_tests]
        
        return {
            'total_tests': len(test_metrics_list),
            'flaky_tests': len(flaky_tests),
            'flaky_percentage': 100 * len(flaky_tests) / len(test_metrics_list),
            'severity_distribution': severity_counts,
            'avg_failure_rate': np.mean(flaky_failure_rates) if flaky_failure_rates else 0.0,
            'median_failure_rate': np.median(flaky_failure_rates) if flaky_failure_rates else 0.0,
            'min_p_value': min(tm.p_value for tm in flaky_tests) if flaky_tests else 1.0,
            'max_failure_rate': max(tm.failure_rate for tm in flaky_tests) if flaky_tests else 0.0
        }


def parse_pytest_runs_csv(csv_path: str) -> Dict[str, List[bool]]:
    """
    Parse pytest runs.csv file to extract per-test failure information.
    
    Args:
        csv_path: Path to runs.csv file
        
    Returns:
        Dictionary mapping test names to list of failure booleans (True = failed, False = passed)
    """
    df = pd.read_csv(csv_path)
    
    # First pass: collect all unique tests that failed at least once
    all_tests = set()
    for _, row in df.iterrows():
        if pd.notna(row['failed_tests_list']) and row['failed_tests_list']:
            failed_tests = [t.strip() for t in str(row['failed_tests_list']).split(';') if t.strip()]
            all_tests.update(failed_tests)
    
    # Initialize test_failures dict with all tests
    test_failures = {test: [] for test in all_tests}
    
    # Second pass: mark pass/fail for each test in each run
    for _, row in df.iterrows():
        failed_in_run = set()
        if pd.notna(row['failed_tests_list']) and row['failed_tests_list']:
            failed_tests = [t.strip() for t in str(row['failed_tests_list']).split(';') if t.strip()]
            failed_in_run = set(failed_tests)
        
        # Mark each test as passed or failed for this run
        for test in all_tests:
            test_failures[test].append(test in failed_in_run)
    
    return test_failures


if __name__ == "__main__":
    # Example usage and testing
    print("Flakiness Metrics Module")
    print("=" * 50)
    
    # Example: A test that fails 30% of the time
    example_runs = [True, False, False, True, False, False, False, True, False, False] * 2
    metrics = FlakinessMetrics.calculate_test_metrics("example_test", example_runs)
    
    print(f"\nTest: {metrics.test_name}")
    print(f"Failure Rate: {metrics.failure_rate:.1%}")
    print(f"Is Flaky: {metrics.is_flaky}")
    print(f"Severity: {metrics.flakiness_severity}")
    print(f"P-value: {metrics.p_value:.4f}")
    print(f"95% CI: [{metrics.confidence_interval_95[0]:.3f}, {metrics.confidence_interval_95[1]:.3f}]")

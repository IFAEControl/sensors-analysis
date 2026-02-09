"""Sweepfile-level sanity checks"""
from characterization.helpers import get_logger
from ..helpers import SanityCheckResult

logger = get_logger()

class SweepFileSanityChecker:
    level_name = 'sweepfile'

    def __init__(self, sweep_file):
        self.sw = sweep_file
        self.level_header = sweep_file.level_header

    def san_check_minimum_linreg_points(self, minimum_linreg_points: int, severity='warning') -> SanityCheckResult:
        df = self.sw.df_analysis
        n = 0 if df is None else int(df.shape[0])
        passed = n >= minimum_linreg_points
        return SanityCheckResult(
            severity=severity,
            check_name='minimum_linreg_points',
            check_args=minimum_linreg_points,
            passed=passed,
            info=f"points={n}",
            check_explanation='Minimum points used in linear regression'
        )

    def san_check_low_total_counts(self, min_total_counts: int = 250, severity='warning') -> SanityCheckResult:
        df = self.sw.df_full
        if df is None or df.empty:
            return SanityCheckResult(severity, 'low_total_counts', min_total_counts, False, info='No data', exec_error=True)
        low = df['total_counts'] < min_total_counts
        count = int(low.sum())
        passed = count == 0
        return SanityCheckResult(
            severity=severity,
            check_name='low_total_counts',
            check_args=min_total_counts,
            passed=passed,
            info=f"low_counts={count}",
            check_explanation='Check if total_counts has values below threshold'
        )

    def san_check_total_square_sum_overflow(self, max_total_square_sum: int = 2**31, severity='warning') -> SanityCheckResult:
        df = self.sw.df_full
        if df is None or df.empty:
            return SanityCheckResult(severity, 'total_square_sum_overflow', max_total_square_sum, False, info='No data', exec_error=True)
        over = df['total_square_sum'] >= max_total_square_sum
        count = int(over.sum())
        passed = count == 0
        return SanityCheckResult(
            severity=severity,
            check_name='total_square_sum_overflow',
            check_args=max_total_square_sum,
            passed=passed,
            info=f"overflow_points={count}",
            check_explanation='Check if total_square_sum exceeds 2**31'
        )

    def san_check_minimum_saturated_points(self, minimum_saturated_points: int = 3, severity='error') -> SanityCheckResult:
        df = self.sw.df_sat
        if df is None or df.empty:
            return SanityCheckResult(severity, 'minimum_saturated_points', minimum_saturated_points, False, info='No data', exec_error=True)
        count = int(df.shape[0])
        passed = count >= minimum_saturated_points
        return SanityCheckResult(
            severity=severity,
            check_name='minimum_saturated_points',
            check_args=minimum_saturated_points,
            passed=passed,
            info=f"saturated_points={count}",
            check_explanation='Require at least N saturated points'
        )

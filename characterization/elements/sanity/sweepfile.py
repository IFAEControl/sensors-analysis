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
        df = self.sw.df
        n = 0 if df is None else int(df.shape[0])
        passed = n >= minimum_linreg_points
        return SanityCheckResult(
            severity=severity,
            check_name='minimum_linreg_points',
            check_args=minimum_linreg_points,
            passed=passed,
            info=f"The linear regression uses {n} points, minimum required is {minimum_linreg_points}",
            check_explanation=f'Verifies if there are at least {minimum_linreg_points} points used in linear regression'
        )

    def san_info_minimum_linreg_points(self, minimum_linreg_points: int, severity='warning') -> dict:
        return {
            'check_name': 'minimum_linreg_points',
            'check_args': minimum_linreg_points,
            'severity': severity,
            'check_explanation': f'Verifies if there are at least {minimum_linreg_points} points used in linear regression',
        }

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
            info=f"There are {count} total_counts values below {min_total_counts}",
            check_explanation=f'Verifies if the total_counts has values below the threshold of {min_total_counts}'
        )

    def san_info_low_total_counts(self, min_total_counts: int = 250, severity='warning') -> dict:
        return {
            'check_name': 'low_total_counts',
            'check_args': min_total_counts,
            'severity': severity,
            'check_explanation': f'Verifies if the total_counts has values below the threshold of {min_total_counts}',
        }

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
            info=f"There are {count} saturated points, minimum required is {minimum_saturated_points}",
            check_explanation=f'Verifies if there are at least {minimum_saturated_points} saturated points'
        )

    def san_info_minimum_saturated_points(self, minimum_saturated_points: int = 3, severity='error') -> dict:
        return {
            'check_name': 'minimum_saturated_points',
            'check_args': minimum_saturated_points,
            'severity': severity,
            'check_explanation': f'Verifies if there are at least {minimum_saturated_points} saturated points',
        }

    def san_check_minimum_linreg_r(self, minimum_linreg_r: float, severity='error') -> SanityCheckResult:
        linreg = self.sw.anal.lr_refpd_vs_adc
        if linreg is None or linreg.linreg is None:
            return SanityCheckResult(severity, 'minimum_linreg_r', minimum_linreg_r, False, info='No linear regression found', exec_error=True)
        r_value = float(linreg.r_value)
        passed = r_value >= minimum_linreg_r
        return SanityCheckResult(
            severity=severity,
            check_name='minimum_linreg_r',
            check_args=minimum_linreg_r,
            passed=passed,
            info=f"The linear regression r value is {r_value:.6f}, minimum required is {minimum_linreg_r}",
            check_explanation=f'Verifies if the linear regression r value is at least {minimum_linreg_r}'
        )

    def san_info_minimum_linreg_r(self, minimum_linreg_r: float, severity='error') -> dict:
        return {
            'check_name': 'minimum_linreg_r',
            'check_args': minimum_linreg_r,
            'severity': severity,
            'check_explanation': f'Verifies if the linear regression r value is at least {minimum_linreg_r}',
        }

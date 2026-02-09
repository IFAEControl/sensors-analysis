"""Fileset-level sanity checks"""
from characterization.helpers import get_logger
from ..helpers import SanityCheckResult

logger = get_logger()

class FilesetSanityChecker:
    level_name = 'fileset'

    def __init__(self, fileset):
        self.fs = fileset
        self.level_header = fileset.level_header

    def san_check_minimum_files_in_set(self, minimum_files_in_set: int, severity='warning') -> SanityCheckResult:
        passed = len(self.fs.files) >= minimum_files_in_set
        return SanityCheckResult(
            severity=severity,
            check_name='minimum_files_in_set',
            check_args=minimum_files_in_set,
            passed=passed,
            info=f"files={len(self.fs.files)}",
            check_explanation='Minimum number of runs in the fileset'
        )

    def san_check_minimum_linreg_points(self, minimum_linreg_points: int, severity='warning') -> SanityCheckResult:
        df = self.fs.df_analysis
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

    def san_check_max_temperature_change(self, max_temperature_change: float, severity='warning') -> SanityCheckResult:
        df = self.fs.df_full
        if df is None or df.empty:
            return SanityCheckResult(severity, 'max_temperature_change', max_temperature_change, False, info='No data', exec_error=True)
        delta = float(df['temperature'].max() - df['temperature'].min())
        passed = delta <= max_temperature_change
        return SanityCheckResult(
            severity=severity,
            check_name='max_temperature_change',
            check_args=max_temperature_change,
            passed=passed,
            info=f"temperature change={delta:.3f}",
            check_explanation='Max temperature swing in fileset'
        )

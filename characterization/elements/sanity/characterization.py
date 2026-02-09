"""Characterization-level sanity checks"""
from characterization.helpers import get_logger
from characterization.config import config
from ..helpers import SanityCheckResult

logger = get_logger()

class CharacterizationSanityChecker:
    level_name = 'calibration'

    def __init__(self, characterization):
        self.char = characterization
        self.level_header = characterization.level_header

    def san_check_max_temperature_change(self, max_temperature_change: float, severity='warning') -> SanityCheckResult:
        df = self.char.df_full
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
            check_explanation='Max temperature swing in dataset'
        )

    def san_check_all_files_analyzed(self, severity='warning') -> SanityCheckResult:
        missing = []
        for pdh in self.char.photodiodes.values():
            for fs in pdh.filesets.values():
                for sw in fs.files:
                    if sw.anal.lr_refpd_vs_adc.linreg is None:
                        missing.append(sw.file_info.get('filename'))
        passed = len(missing) == 0
        return SanityCheckResult(
            severity=severity,
            check_name='all_files_analyzed',
            check_args={'missing': missing},
            passed=passed,
            info='' if passed else f"Missing linreg in {len(missing)} files",
            check_explanation='Each sweep file should have a valid linear regression.'
        )

    def san_check_all_sensors_scanned(self, severity='warning') -> SanityCheckResult:
        expected = set(config.sensor_config.keys())
        scanned = set(self.char.photodiodes.keys())
        missing = sorted(list(expected - scanned))
        extra = sorted(list(scanned - expected))
        passed = len(missing) == 0 and len(extra) == 0
        return SanityCheckResult(
            severity=severity,
            check_name='all_sensors_scanned',
            check_args= None,
            passed=passed,
            info='' if passed else f"Missing sensors: {missing}, unexpected sensors: {extra}",
            check_explanation='All sensors should be scanned.'
        )

    def san_check_expected_runs_acquired(self, severity='warning') -> SanityCheckResult:
        missing_by_sensor = {}
        for sensor_id, pdh in self.char.photodiodes.items():
            expected = config.sensor_config.get(sensor_id, {}).get('expected_runs', [])
            acquired = sorted(list(pdh.filesets.keys()))
            missing = [r for r in expected if r not in acquired]
            if missing:
                missing_by_sensor[sensor_id] = {'missing': missing, 'acquired': acquired}
        passed = len(missing_by_sensor) == 0
        return SanityCheckResult(
            severity=severity,
            check_name='expected_runs_acquired',
            check_args=missing_by_sensor,
            passed=passed,
            info='' if passed else f"Missing runs for {len(missing_by_sensor)} sensors",
            check_explanation='Each sensor should have all expected runs acquired.'
        )

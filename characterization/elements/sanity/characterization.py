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

    def san_info_max_temperature_change(self, max_temperature_change: float, severity='warning') -> dict:
        return {
            'check_name': 'max_temperature_change',
            'check_args': max_temperature_change,
            'severity': severity,
            'check_explanation': f'Max temperature swing in dataset allowed: {max_temperature_change} degrees',
        }

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

    def san_info_all_files_analyzed(self, severity='warning') -> dict:
        return {
            'check_name': 'all_files_analyzed',
            'check_args': None,
            'severity': severity,
            'check_explanation': 'Verifies if each sweep file has a valid linear regression.',
        }

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

    def san_info_all_sensors_scanned(self, severity='warning') -> dict:
        return {
            'check_name': 'all_sensors_scanned',
            'check_args': None,
            'severity': severity,
            'check_explanation': 'Verify if all sensors in the board are scanned.',
        }

    def san_check_setup_confs_acquired(self, severity='warning') -> SanityCheckResult:
        missing_by_sensor = {}
        for sensor_id, pdh in self.char.photodiodes.items():
            expected = config.sensor_config.get(sensor_id, {}).get('valid_setups', [])
            acquired = sorted(list(pdh.filesets.keys()))
            missing = [r for r in expected if r not in acquired]
            if missing:
                missing_by_sensor[sensor_id] = {'missing': missing, 'acquired': acquired}
        passed = len(missing_by_sensor) == 0
        return SanityCheckResult(
            severity=severity,
            check_name='setup_confs_acquired',
            check_args=missing_by_sensor,
            passed=passed,
            info='' if passed else f"Missing runs for {len(missing_by_sensor)} sensors",
            check_explanation='Each sensor should have all expected runs acquired.'
        )

    def san_info_setup_confs_acquired(self, severity='warning') -> dict:
        return {
            'check_name': 'setup_confs_acquired',
            'check_args': None,
            'severity': severity,
            'check_explanation': 'Each sensor should have all expected runs acquired.',
        }

    def san_check_pd_single_1064_fw5(self, severity='error') -> SanityCheckResult:
        violations = {}
        for sensor_id, pdh in self.char.photodiodes.items():
            acquired_1064 = sorted([k for k in pdh.filesets.keys() if k.startswith('1064_')])
            if len(acquired_1064) != 1 or acquired_1064[0] != '1064_FW5':
                violations[sensor_id] = {'acquired_1064': acquired_1064}
        passed = len(violations) == 0
        return SanityCheckResult(
            severity=severity,
            check_name='pd_single_1064_fw5',
            check_args=violations,
            passed=passed,
            info='' if passed else f"{len(violations)} sensors violate 1064_FW5 uniqueness",
            check_explanation='Each sensor must have exactly one 1064 fileset and it must be 1064_FW5.'
        )

    def san_info_pd_single_1064_fw5(self, severity='error') -> dict:
        return {
            'check_name': 'pd_single_1064_fw5',
            'check_args': None,
            'severity': severity,
            'check_explanation': 'Each sensor must have exactly one 1064 fileset: 1064_FW5.',
        }

    def san_check_pd_single_532_fileset(self, severity='error') -> SanityCheckResult:
        violations = {}
        for sensor_id, pdh in self.char.photodiodes.items():
            acquired_532 = sorted([k for k in pdh.filesets.keys() if k.startswith('532_')])
            if len(acquired_532) != 1:
                violations[sensor_id] = {'acquired_532': acquired_532}
        passed = len(violations) == 0
        return SanityCheckResult(
            severity=severity,
            check_name='pd_single_532_fileset',
            check_args=violations,
            passed=passed,
            info='' if passed else f"{len(violations)} sensors violate single-532-fileset rule",
            check_explanation='Each sensor must have exactly one 532 fileset.'
        )

    def san_info_pd_single_532_fileset(self, severity='error') -> dict:
        return {
            'check_name': 'pd_single_532_fileset',
            'check_args': None,
            'severity': severity,
            'check_explanation': 'Each sensor must have exactly one 532 fileset.',
        }

    def san_check_pd_532_matches_expected_mapping(self, severity='error') -> SanityCheckResult:
        violations = {}
        for sensor_id, pdh in self.char.photodiodes.items():
            valid_setups = config.sensor_config.get(sensor_id, {}).get('valid_setups', [])
            expected_532 = [r for r in valid_setups if r.startswith('532_')]
            acquired_532 = sorted([k for k in pdh.filesets.keys() if k.startswith('532_')])
            if len(expected_532) != 1:
                violations[sensor_id] = {
                    'reason': 'invalid_expected_532_mapping',
                    'expected_532': expected_532,
                    'acquired_532': acquired_532,
                }
                continue
            if len(acquired_532) != 1 or acquired_532[0] != expected_532[0]:
                violations[sensor_id] = {
                    'reason': 'acquired_532_mismatch',
                    'expected_532': expected_532[0],
                    'acquired_532': acquired_532,
                }
        passed = len(violations) == 0
        return SanityCheckResult(
            severity=severity,
            check_name='pd_532_matches_expected_mapping',
            check_args=violations,
            passed=passed,
            info='' if passed else f"{len(violations)} sensors violate 532 expected mapping",
            check_explanation='Sensor 532 fileset must match expected run mapping from configuration.'
        )

    def san_info_pd_532_matches_expected_mapping(self, severity='error') -> dict:
        return {
            'check_name': 'pd_532_matches_expected_mapping',
            'check_args': None,
            'severity': severity,
            'check_explanation': 'Sensor 532 fileset must match expected run mapping from configuration.',
        }

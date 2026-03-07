"""Characterization-level sanity checks"""
import math
import numpy as np
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

    def san_check_pd_has_slope_intercept_for_all_wavelengths(self, severity='error') -> SanityCheckResult:
        violations = {}
        for sensor_id, pdh in self.char.photodiodes.items():
            expected_setups = config.sensor_config.get(sensor_id, {}).get('valid_setups', [])
            expected_wavelengths = sorted({s.split('_', 1)[0] for s in expected_setups if isinstance(s, str) and s})
            if not expected_wavelengths:
                expected_wavelengths = sorted({k.split('_', 1)[0] for k in pdh.filesets.keys() if isinstance(k, str) and k})

            missing_details = {}
            for wavelength in expected_wavelengths:
                matching = [(k, fs) for k, fs in pdh.filesets.items() if str(k).startswith(f"{wavelength}_")]
                if not matching:
                    missing_details[wavelength] = {"reason": "missing_wavelength_fileset"}
                    continue

                has_complete_lr = False
                has_complete_power = False
                for _, fs in matching:
                    anal = getattr(fs, "anal", None)
                    lr = getattr(anal, "lr_refpd_vs_adc", None)
                    if lr is not None and getattr(lr, "linreg", None) is not None:
                        if getattr(lr, "slope", None) is not None and getattr(lr, "intercept", None) is not None:
                            has_complete_lr = True
                    adc_to_power = getattr(anal, "adc_to_power", None)
                    if isinstance(adc_to_power, dict):
                        if adc_to_power.get("slope") is not None and adc_to_power.get("intercept") is not None:
                            has_complete_power = True

                if not has_complete_lr or not has_complete_power:
                    missing_fields = []
                    if not has_complete_lr:
                        missing_fields.append("lr_refpd_vs_adc.slope/intercept")
                    if not has_complete_power:
                        missing_fields.append("adc_to_power.slope/intercept")
                    missing_details[wavelength] = {
                        "reason": "missing_fit_parameters",
                        "missing_fields": missing_fields,
                        "candidate_filesets": [k for k, _ in matching],
                    }

            if missing_details:
                violations[sensor_id] = missing_details

        passed = len(violations) == 0
        return SanityCheckResult(
            severity=severity,
            check_name='pd_has_slope_intercept_for_all_wavelengths',
            check_args=violations,
            passed=passed,
            info='' if passed else f"{len(violations)} sensors missing slope/intercept for one or more wavelengths",
            check_explanation='Each photodiode must have slope/intercept computed for all expected wavelengths.',
        )

    def san_info_pd_has_slope_intercept_for_all_wavelengths(self, severity='error') -> dict:
        return {
            'check_name': 'pd_has_slope_intercept_for_all_wavelengths',
            'check_args': None,
            'severity': severity,
            'check_explanation': 'Each photodiode must have slope/intercept computed for all expected wavelengths.',
        }

    def san_check_pd_slope_deviation_from_group_median_pct(
        self,
        max_abs_deviation_pct: float,
        severity='warning',
    ) -> SanityCheckResult:
        grouped: dict[str, list[dict]] = {}
        for sensor_id, pdh in self.char.photodiodes.items():
            gain = str(config.sensor_config.get(sensor_id, {}).get("gain", "UNK"))
            for cfg_key, fs in pdh.filesets.items():
                wavelength = str(cfg_key).split('_', 1)[0]
                group_key = f"{wavelength}_{gain}"
                anal = getattr(fs, "anal", None)
                lr = getattr(anal, "lr_refpd_vs_adc", None)
                if lr is None or getattr(lr, "linreg", None) is None:
                    continue
                slope = getattr(lr, "slope", None)
                if slope is None:
                    continue
                grouped.setdefault(group_key, []).append(
                    {"sensor_id": sensor_id, "slope": float(slope), "cfg_key": str(cfg_key)}
                )

        violations = {}
        skipped_groups = []
        for group_key, rows in grouped.items():
            slopes = [r["slope"] for r in rows]
            median = float(np.median(slopes))
            if math.isclose(median, 0.0, abs_tol=1e-20):
                skipped_groups.append(group_key)
                continue
            for row in rows:
                dev_pct = abs((row["slope"] - median) / median) * 100.0
                if dev_pct > float(max_abs_deviation_pct):
                    violations.setdefault(row["sensor_id"], []).append(
                        {
                            "group": group_key,
                            "configuration": row["cfg_key"],
                            "slope": row["slope"],
                            "group_median_slope": median,
                            "abs_rel_dev_pct": dev_pct,
                            "threshold_pct": float(max_abs_deviation_pct),
                        }
                    )

        passed = len(violations) == 0
        info = ""
        if not passed:
            info = f"{len(violations)} sensors exceed {max_abs_deviation_pct}% slope deviation vs group median"
        if skipped_groups:
            suffix = f"; skipped zero-median groups: {sorted(skipped_groups)}"
            info = (info + suffix) if info else suffix.lstrip("; ")
        return SanityCheckResult(
            severity=severity,
            check_name='pd_slope_deviation_from_group_median_pct',
            check_args={"max_abs_deviation_pct": max_abs_deviation_pct, "violations": violations},
            passed=passed,
            info=info,
            check_explanation='Checks absolute slope deviation from wavelength+gain group median.',
        )

    def san_info_pd_slope_deviation_from_group_median_pct(
        self,
        max_abs_deviation_pct: float,
        severity='warning',
    ) -> dict:
        return {
            'check_name': 'pd_slope_deviation_from_group_median_pct',
            'check_args': max_abs_deviation_pct,
            'severity': severity,
            'check_explanation': (
                'Checks whether absolute slope deviation versus wavelength+gain group median '
                f'exceeds {max_abs_deviation_pct}%.'
            ),
        }

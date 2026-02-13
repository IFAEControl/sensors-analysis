"""Module for performing sanity checks on characterization data and analysis results"""
import os
import sys
from typing import TYPE_CHECKING

import yaml

from characterization.helpers import get_logger
from .helpers import SanityCheckResult

from .sanity.characterization import CharacterizationSanityChecker
from .sanity.fileset import FilesetSanityChecker
from .sanity.sweepfile import SweepFileSanityChecker

if TYPE_CHECKING:
    from .characterization import Characterization

logger = get_logger()

file_path = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.abspath(os.path.join(file_path, '..', 'sanity_checks_config.yaml'))


class Counter:
    """Simple counter class to keep track of passed and failed checks"""
    def __init__(self):
        self._checks = {}

    def check(self, severity: str, passed: bool):
        key = f"{severity}_{'passed' if passed else 'failed'}"
        self._checks.setdefault(key, 0)
        self._checks[key] += 1

    def to_dict(self) -> dict:
        passed = sum(v for k, v in self._checks.items() if 'passed' in k)
        failed = sum(v for k, v in self._checks.items() if 'failed' in k)
        total = passed + failed
        return {
            'total_passed': passed,
            'total_failed': failed,
            'total_checks': total,
            'details': dict(self._checks)
        }


class SanityChecks:
    """Class to perform sanity checks on characterization data"""
    def __init__(self, characterization: 'Characterization'):
        self.char = characterization
        self.config = {}
        self.results = {}
        self._c = Counter()
        self._load_config()

    def _load_config(self):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            logger.info("Loaded sanity checks configuration from %s", config_file)
        except Exception as e:
            logger.error("Failed to load sanity checks configuration: %s", str(e))
            sys.exit(1)

    @property
    def characterization_checks_config(self) -> dict:
        return self.config.get('characterization', {})

    @property
    def fileset_checks_config(self) -> dict:
        return self.config.get('fileset', {})

    @property
    def sweepfile_checks_config(self) -> dict:
        return self.config.get('sweepfile', {})

    def _run_check_methods(self, severity, checks, checker):
        results = {}
        for check_name, check_params in checks.items():
            method_name = f"san_check_{check_name}"
            check_method = getattr(checker, method_name, None)
            if check_method is None:
                logger.warning("Sanity check method %s not found in %s", method_name, checker.level_name)
                result = SanityCheckResult(
                    severity=severity,
                    check_name=check_name,
                    check_args=check_params,
                    passed=False,
                    info="Sanity check method not found",
                    exec_error=True
                )
                results[f"{severity}.{check_name}"] = result.to_dict()
                self._c.check(severity, False)
                continue
            try:
                if check_params is None:
                    result = check_method(severity=severity)
                elif isinstance(check_params, dict):
                    result = check_method(**check_params, severity=severity)
                elif isinstance(check_params, list):
                    result = check_method(*check_params, severity=severity)
                else:
                    result = check_method(check_params, severity=severity)
                results[f"{severity}.{check_name}"] = result.to_dict()
                self._c.check(severity, result.passed)
            except Exception as e:
                result = SanityCheckResult(
                    severity=severity,
                    check_name=check_name,
                    check_args=check_params,
                    passed=False,
                    info=str(e),
                    exec_error=True
                )
                self._c.check(severity, False)
                results[f"{severity}.{check_name}"] = result.to_dict()
                logger.warning("Failed to execute check: %s, %s", check_name, str(e))
        return results

    def _run_info_methods(self, severity, checks, checker) -> dict:
        results = {}
        for check_name, check_params in checks.items():
            method_name = f"san_info_{check_name}"
            info_method = getattr(checker, method_name, None)
            if info_method is None:
                logger.warning("Sanity info method %s not found in %s", method_name, checker.level_name)
                results[f"{severity}.{check_name}"] = {
                    'check_name': check_name,
                    'check_args': check_params,
                    'severity': severity,
                    'check_explanation': "Sanity info method not found",
                    'exec_error': True,
                }
                continue
            try:
                if check_params is None:
                    info = info_method(severity=severity)
                elif isinstance(check_params, dict):
                    info = info_method(**check_params, severity=severity)
                elif isinstance(check_params, list):
                    info = info_method(*check_params, severity=severity)
                else:
                    info = info_method(check_params, severity=severity)
                results[f"{severity}.{check_name}"] = info
            except Exception as e:
                results[f"{severity}.{check_name}"] = {
                    'check_name': check_name,
                    'check_args': check_params,
                    'severity': severity,
                    'check_explanation': str(e),
                    'exec_error': True,
                }
                logger.warning("Failed to execute info check: %s, %s", check_name, str(e))
        return results

    def run_checks(self):
        logger.info("Running sanity checks...")
        self.results = {}
        defined_checks = {}

        checker = CharacterizationSanityChecker(self.char)
        self.results[checker.level_header] = {'checks': {}, 'photodiodes': {}}
        defined_checks['characterization_checks'] = {}
        for severity, checks in self.characterization_checks_config.items():
            results = self._run_check_methods(severity, checks, checker)
            self.results[checker.level_header]['checks'].update(results)
            info_results = self._run_info_methods(severity, checks, checker)
            defined_checks['characterization_checks'].update(info_results)

        photodiodes_results = self.results[checker.level_header]['photodiodes']
        filesets_defined = defined_checks.setdefault('fileset_checks', {})
        first_fs = True
        first_sw = True
        for pdh in self.char.photodiodes.values():
            pd_res = photodiodes_results.setdefault(pdh.level_header, {'checks': {}, 'filesets': {}})
            filesets_results = pd_res['filesets']
            for fs in pdh.filesets.values():
                checker = FilesetSanityChecker(fs)
                fs_res = filesets_results.setdefault(fs.level_header, {'checks': {}})
                for severity, checks in self.fileset_checks_config.items():
                    results = self._run_check_methods(severity, checks, checker)
                    fs_res['checks'].update(results)
                    info_results = self._run_info_methods(severity, checks, checker)
                    if first_fs:
                        filesets_defined.update(info_results)
                first_fs = False
                sweep_results = fs_res.setdefault('sweepfiles', {})
                sweep_defined = defined_checks.setdefault('sweepfile_checks', {})
                for sw in fs.files:
                    checker = SweepFileSanityChecker(sw)
                    sweep_results.setdefault(sw.level_header, {})
                    for severity, checks in self.sweepfile_checks_config.items():
                        results = self._run_check_methods(severity, checks, checker)
                        sweep_results[sw.level_header].update(results)
                        info_results = self._run_info_methods(severity, checks, checker)
                        if first_sw:
                            sweep_defined.update(info_results)
                    first_sw = False

        self.results['summary'] = self._c.to_dict()
        self.results['defined_checks'] = defined_checks
        c_d = self._c.to_dict()
        if c_d['total_failed'] > 0:
            logger.warning("Sanity checks completed. %s passed, %s failed out of %s checks.", c_d['total_passed'], c_d['total_failed'], c_d['total_checks'])
        else:
            logger.info("Sanity checks completed. %s passed, %s failed out of %s checks.", c_d['total_passed'], c_d['total_failed'], c_d['total_checks'])

        return self.results

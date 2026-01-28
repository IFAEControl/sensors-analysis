"""Module for performing sanity checks on calibration data and analysis results"""
import os
import sys
from typing import TYPE_CHECKING

import yaml

from calibration.helpers import get_logger
from .helpers import SanityCheckResult

from .sanity.calibration_sanity import CalibrationSanityChecker
from .sanity.fileset_sanity import FileSetSanityChecker
from .sanity.file_sanity import FileSanityChecker

if TYPE_CHECKING:
    from .calibration import Calibration

logger = get_logger()

file_path = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.abspath(os.path.join(file_path,'..','sanity_checks_config.yaml'))

class Counter:
    """Simple counter class to keep track of passed and failed checks"""
    def __init__(self):
        self._checks = {}
    
    def check(self, severity:str, passed:bool):
        """Increment the counter based on severity and pass/fail status"""
        key = f"{severity}_{'passed' if passed else 'failed'}"
        self._checks.setdefault(key, 0)
        self._checks[key] += 1
    
    def to_dict(self) -> dict:
        """Return the counter values as a dictionary"""
        passed = sum([v for k,v in self._checks.items() if 'passed' in k])
        failed = sum([v for k,v in self._checks.items() if 'failed' in k])
        total = passed + failed
        tmp = self._checks.copy()
        tmp = {
            'total_passed': passed,
            'total_failed': failed,
            'total_checks': total,
            'details': tmp
        }
        return tmp
    

class SanityChecks:
    """Class to perform sanity checks on calibration data"""
    def __init__(self, calibration:'Calibration'):
        self.calibration = calibration
        self.config = {}
        self.results = {}
        self._c = Counter()
        self.initialize()
    
    def initialize(self):
        """Initialize sanity checks by loading configuration"""
        self._load_config()
    
    def _load_config(self):
        """Load sanity checks configuration from YAML file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            logger.info("Loaded sanity checks configuration from %s", config_file)
        except Exception as e:
            logger.error("Failed to load sanity checks configuration: %s", str(e))
            sys.exit(1)
    
    @property
    def calibration_checks_config(self) -> dict:
        """Return the calibration checks configuration"""
        return self.config.get('calibration', {})
    
    @property
    def file_checks_config(self) -> dict:
        """Return the file checks configuration"""
        return self.config.get('file', {})
    
    @property
    def fileset_checks_config(self) -> dict:
        """Return the file checks configuration"""
        return self.config.get('fileset', {})
    
    def _run_check_methods(self, severity, checks, checker) -> SanityCheckResult:
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
                results[check_name] = result.to_dict()
                self._c.check(severity, False)
                continue
            try:
                if isinstance(check_params, dict):
                    result:SanityCheckResult = check_method(**check_params, severity=severity)
                elif isinstance(check_params, list):
                    result:SanityCheckResult = check_method(*check_params, severity=severity)
                else:
                    result:SanityCheckResult = check_method(check_params, severity=severity)
                results[check_name] = result.to_dict()
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
                results[check_name] = result.to_dict()
                logger.warning("Failed to execute check: %s, %s", check_name, str(e))
        return results

    def run_checks(self):
        """Run all configured sanity checks"""
        logger.info("Running sanity checks...")
        self.results = {}
        
        checker = CalibrationSanityChecker(self.calibration)
        self.results[checker.level_header] = {}
        for severity, checks in self.calibration_checks_config.items():
            results = self._run_check_methods(severity, checks, checker)
            self.results[checker.level_header]['checks'] = results
        
        filesets_results = self.results[checker.level_header].setdefault('filesets', {})
        
        for _, fs in self.calibration.filesets.items():
            checker = FileSetSanityChecker(fs)
            fs_res = filesets_results.setdefault(fs.level_header, {})
            for severity, checks in self.fileset_checks_config.items():
                results = self._run_check_methods(severity, checks, checker)
                fs_res['checks'] = results
            file_results = fs_res.setdefault('files', {})
            for calfile in fs.files:
                checker = FileSanityChecker(calfile)
                for severity, checks in self.file_checks_config.items():
                    results = self._run_check_methods(severity, checks, checker)
                    file_results[calfile.level_header] = results
        
        c_d = self._c.to_dict()
        self.results['summary'] = c_d
        if c_d['total_failed'] > 0:
            logger.warning(f"Sanity checks completed. {c_d['total_passed']} passed, {c_d['total_failed']} failed out of {c_d['total_checks']} checks.")
        else:
            logger.info(f"Sanity checks completed. {c_d['total_passed']} passed, {c_d['total_failed']} failed out of {c_d['total_checks']} checks.")
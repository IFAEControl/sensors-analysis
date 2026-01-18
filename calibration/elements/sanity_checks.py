"""Module for performing sanity checks on calibration data and analysis results"""
import os
import sys
from typing import TYPE_CHECKING

import yaml

from calibration.helpers import get_logger
from .data_holders import SanityCheckResult

if TYPE_CHECKING:
    from .calibration import Calibration

logger = get_logger()

file_path = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.abspath(os.path.join(file_path,'..','sanity_checks_config.yaml'))


class SanityChecks:
    """Class to perform sanity checks on calibration data"""
    def __init__(self, calibration:'Calibration'):
        self.calibration = calibration
        self.config = {}
        self.results = {}
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
        return self.config.get('file', {})
    

    def run_checks(self):
        """Run all configured sanity checks"""
        logger.info("Running sanity checks...")
        self.results = {}
        for severity, checks in self.calibration_checks_config.items():
            for check_name, check_params in checks.items():
                method_name = f"san_check_{check_name}"
                check_method = getattr(self.calibration, method_name, None)
                if callable(check_method):
                    logger.info("Running check: %s", check_name)
                    result:SanityCheckResult = check_method(severity=severity, **check_params)
                    self.results[check_name] = result.to_dict()
                else:
                    result = SanityCheckResult(
                            severity=severity,
                            check_name=check_name,
                            check_args=check_params,
                            passed=False,
                            info=f"No method found for calibration check: {check_name}",
                            error=True
                        )
                    self.results[f"calibration_{check_name}"] = result.to_dict()
                    logger.warning("No method found for check: %s", check_name)
        
        for fs_key, fs in self.calibration.file_sets.items():
            for severity, checks in self.fileset_checks_config.items():
                for check_name, check_params in checks.items():
                    method_name = f"san_check_{check_name}"
                    check_method = getattr(fs, method_name, None)
                    if callable(check_method):
                        logger.info("Running fileset check: %s for fileset %s", check_name, fs_key)
                        result:SanityCheckResult = check_method(severity=severity, **check_params)
                        self.results[f"fileset_{fs_key}_{check_name}"] = result.to_dict()
                    else:
                        result = SanityCheckResult(
                            severity=severity,
                            check_name=check_name,
                            check_args=check_params,
                            passed=False,
                            info=f"No method found for fileset check: {check_name}",
                            error=True
                        )
                        self.results[f"fileset_{fs_key}_{check_name}"] = result.to_dict()
                        logger.warning("No method found for fileset check: %s", check_name)

            for calfile in fs.files:
                for severity, checks in self.file_checks_config.items():
                    for check_name, check_params in checks.items():
                        method_name = f"san_check_{check_name}"
                        check_method = getattr(calfile.anal, method_name, None)
                        if callable(check_method):
                            logger.info("Running file check: %s for file %s", check_name, calfile.meta['filename'])
                            result:SanityCheckResult = check_method(severity=severity, **check_params)
                            self.results[f"file_{calfile.meta['filename']}_{check_name}"] = result.to_dict()
                        else:
                            result = SanityCheckResult(
                                severity=severity,
                                check_name=check_name,
                                check_args=check_params,
                                passed=False,
                                info=f"No method found for file check: {check_name}",
                                error=True
                            )
                            self.results[f"file_{calfile.meta['filename']}_{check_name}"] = result.to_dict()
                            logger.warning("No method found for file check: %s", check_name)
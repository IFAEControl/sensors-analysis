"""Sanity checks for characterization data"""

from characterization.helpers import get_logger
from .helpers import SanityCheckResult

logger = get_logger()

class Counter:
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

class PhotodiodeSanityChecker:
    level_name = 'photodiode'

    def __init__(self, photodiode):
        self.photodiode = photodiode
        self.level_header = photodiode.level_header

    def san_check_has_files(self, severity='warning') -> SanityCheckResult:
        passed = len(self.photodiode.files) > 0
        return SanityCheckResult(
            severity=severity,
            check_name='has_files',
            check_args={'min_files': 1},
            passed=passed,
            info='' if passed else 'No files found for this photodiode',
            internal=True,
            check_explanation='Photodiode should have at least one run file.'
        )

    def san_check_all_files_analyzed(self, severity='warning') -> SanityCheckResult:
        missing = []
        for cf in self.photodiode.files:
            if cf.anal.lr_refpd_vs_adc.linreg is None:
                missing.append(cf.file_info.get('filename'))
        passed = len(missing) == 0
        return SanityCheckResult(
            severity=severity,
            check_name='all_files_analyzed',
            check_args={'missing': missing},
            passed=passed,
            info='' if passed else f"Missing linreg in {len(missing)} files",
            internal=True,
            check_explanation='Each run file should have a valid linear regression.'
        )

class PhotodiodeSanity:
    def __init__(self, photodiode):
        self.photodiode = photodiode
        self.results = {}
        self._c = Counter()

    def run_checks(self):
        checker = PhotodiodeSanityChecker(self.photodiode)
        checks = [
            checker.san_check_has_files,
            checker.san_check_all_files_analyzed,
        ]
        self.results = {'checks': {}}
        for check in checks:
            res = check()
            self.results['checks'][res.check_name] = res.to_dict()
            self._c.check(res.severity, res.passed)
        self.results['summary'] = self._c.to_dict()
        return self.results

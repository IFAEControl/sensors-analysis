
from typing import Any
from .sanity_base import SanityBase
from ..helpers import SanityCheckResult
from ..calib_fileset import FileSet


class FileSetSanityChecker(SanityBase):
    """File Set sanity checker class."""
    def __init__(self, fileset: FileSet):
        super().__init__(fileset, fileset.level)
        self.fileset = fileset
        self.df = fileset.df
        self.level_name = fileset.label

    def san_check_min_files(self, min_files, severity) -> SanityCheckResult:
        """Check that the number of files in the fileset is at least min_files."""
        num_files = len(self.fileset.files)
        passed = num_files >= min_files
        info = f"Number of files: {num_files}, Minimum required: {min_files}"
        return SanityCheckResult(
            severity=severity,
            check_name='min_files',
            check_args={'min_files': min_files},
            passed=passed,
            info=info,
            check_explanation=f"Checks if there are at least {min_files} files in the fileset."
        )

    def san_info_min_files(self, min_files, severity) -> dict:
        """Return info for minimum files check."""
        num_files = len(self.fileset.files)
        info = f"Number of files: {num_files}, Minimum required: {min_files}"
        return {
            'check_name': 'min_files',
            'check_args': {'min_files': min_files},
            'severity': severity,
            'info': info,
            'check_explanation': f"Checks if there are at least {min_files} files in the fileset.",
        }

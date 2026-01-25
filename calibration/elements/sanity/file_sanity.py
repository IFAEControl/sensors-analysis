
from typing import Any
from ..calib_file import CalibFile
from ..helpers import SanityCheckResult
from .sanity_base import SanityBase

class FileSanityChecker(SanityBase):
    """File sanity checker class."""
    def __init__(self, calibfile: CalibFile):
        super().__init__(calibfile, calibfile.level)
        self.level_name = f"{calibfile.base_filename}"

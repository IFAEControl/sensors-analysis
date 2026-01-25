"""Calibration sanity checks module"""

from ..helpers import SanityCheckResult
from ..calibration import Calibration

from .sanity_base import SanityBase


class CalibrationSanityChecker(SanityBase):
    """Calibration sanity checker class It contains specific methods for high level calibration checks """

    def __init__(self, calibration: Calibration):
        super().__init__(calibration, calibration.level)
        self.level_name = calibration.level_name
        


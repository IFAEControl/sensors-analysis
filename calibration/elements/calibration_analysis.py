import os

from typing import TYPE_CHECKING

from calibration.helpers import get_logger

if TYPE_CHECKING:
    from .calibration import Calibration
    from .calib_file import CalibFile

logger = get_logger()


class CalibrationAnalysis:
    """
    CalibrationAnalysis

    Launches file sets analysis and generates plots interrelating data from all sets of calibration files.
    """
    def __init__(self, calibration:Calibration):
        self.cal = calibration
        self.outpath = calibration.output_path
        self.sets = calibration.file_sets
        self.plots = {}
        self.results = {}

    def analyze(self):
        for (wl, fw), fileset in self.sets.items():
            fileset.analyze()
        self.gen_plots()

    def gen_plots(self):
        """Generate plots interrelating data from all sets of calibration files."""
        # plot of whole calibration data acquisition tempeerature and humidity
        pass


"""Calibration analysis across multiple file sets"""

from typing import TYPE_CHECKING

import pandas as pd

from calibration.config import config
from calibration.helpers import get_logger


if TYPE_CHECKING:
    from ..calibration import Calibration
    from ..calib_file import CalibFile

logger = get_logger()


class CalibrationAnalysis:
    """
    CalibrationAnalysis

    Launches file sets analysis and generates plots interrelating data from all sets of calibration files.
    """
    def __init__(self, calibration:Calibration):
        self.cal = calibration
        self.outpath = calibration.output_path
        self.filesets = calibration.filesets
        self.plots = {}
        self.results = {}

    def analyze(self):
        """Analyze all file sets and generate interrelated plots"""
        for _, fileset in self.filesets.items():
            fileset.analyze()
        self._find_elapsed_time_range()
    #     self._find_sets()


    # def _find_sets(self) -> dict:
    #     """Find all unique (wavelength, filterwheel) combinations across calibration files."""
    #     fset = {}
    #     for (wl, fw), fs in self.sets.items():
    #         tmp = []
    #         for calib_file in fs.files:
    #             tmp.append(calib_file.meta['filename'])
    #         fset[f"{wl}_{fw}"] = tmp
    #     self.results['file_sets'] = fset
    
    def _find_elapsed_time_range(self) -> tuple[float, float]:
        """Find the overall elapsed time range across all calibration files."""
        min_time = float('inf')
        max_time = float('-inf')
        for fileset in self.filesets.values():
            for calib_file in fileset.files:
                df = calib_file.df
                if not df.empty:
                    start_time = df['timestamp'].min()
                    end_time = df['timestamp'].max()
                    if start_time < min_time:
                        min_time = start_time
                    if end_time > max_time:
                        max_time = end_time
        t_res = {
            'min_ts': int(min_time),
            'max_ts': int(max_time),
            'elapsed_time_s': int(max_time - min_time),
            'min_dt': pd.to_datetime(min_time, unit='s').strftime('%Y-%m-%d %H:%M:%S'),
            'max_dt': pd.to_datetime(max_time, unit='s').strftime('%Y-%m-%d %H:%M:%S')
        }
        self.results['time'] = t_res
        return (min_time, max_time)

    def to_dict(self) -> dict:
        """Convert analysis results to a dictionary."""
        tmp = {
            'time_info': self.results['time'],
            'filesets': {f"{wl}_{fw}": fs.to_dict() for (wl, fw), fs in self.filesets.items()},

        }
        return tmp



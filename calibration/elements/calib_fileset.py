import os

from typing import TYPE_CHECKING

import pandas as pd

from calibration.helpers import get_logger
from .analysis import FileSetAnalysis
from .plots.fileset_plots import FileSetPlots
from .base_element import BaseElement, DataHolderLevel

if TYPE_CHECKING:
    from .calibration import Calibration
    from .calib_file import CalibFile

logger = get_logger()


class FileSet(BaseElement):
    """Class to represent a set of calibration files with the same wavelength and filter wheel"""

    def __init__(self, wave_length: str, filter_wheel: str, calibration: Calibration | None = None):
        super().__init__(DataHolderLevel.FILESET)
        self.wl = wave_length
        self.fw = filter_wheel
        self.label = f"{self.wl}_{self.fw}"
        self.dh_parent = calibration
        self.files: list['CalibFile'] = []
        self.anal = FileSetAnalysis(self)
        self.plotter = FileSetPlots(self)
        self.generate_plots = self.plotter.generate_plots

        self.output_path = os.path.join(
            calibration.output_path,
            f"{self.wl}_{self.fw}"
        )
        self.level_header = self.label
        self.long_label = f"{self.dh_parent.level_header} - {self.label}"

    @property
    def df(self):
        """Concatenated DataFrame of all calibration files in the set."""
        if self._df is None:
            self._df = pd.concat(
                [calfile.df for calfile in self.files if calfile.df is not None], ignore_index=True)
        return self._df

    @property
    def df_pedestals(self):
        """Concatenated DataFrame of all calibration files in the set."""
        if self._df_pedestals is None:
            self._df_pedestals = pd.concat(
                [calfile.df_pedestals for calfile in self.files if calfile.df_pedestals is not None], ignore_index=True)
        return self._df_pedestals

    @property
    def df_full(self):
        """Concatenated DataFrame of all calibration files in the set."""
        if self._df_full is None:
            self._df_full = pd.concat(
                [calfile.df_full for calfile in self.files if calfile.df_full is not None], ignore_index=True)
        return self._df_full

    def add_calib_file(self, calib_file: 'CalibFile'):
        """Add a calibration file to the set."""
        if calib_file.wavelength != self.wl or calib_file.filter_wheel != self.fw:
            logger.error(
                "Calibration file wavelength or filter wheel does not match the set.")
            return
        self.files.append(calib_file)
        calib_file.set_file_set(self)

    def analyze(self):
        """Analyze the set of calibration files."""
        os.makedirs(self.output_path, exist_ok=True)
        self.anal.analyze()

    def to_dict(self):
        """Convert file set data to dictionary."""
        return {
            'meta': {'wave_length': self.wl,
                     'filter_wheel': self.fw},
            'analysis': self.anal.to_dict(),
            'files': {cf.file_label: cf.to_dict() for cf in self.files}
        }

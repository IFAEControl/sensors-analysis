import os

from typing import TYPE_CHECKING

import pandas as pd

from calibration.helpers import get_logger
from .analysis import FileSetAnalysis

if TYPE_CHECKING:
    from .calibration import Calibration
    from .calib_file import CalibFile

logger = get_logger()


class FileSet:
    """Class to represent a set of calibration files with the same wavelength and filter wheel"""

    def __init__(self, wave_length: str, filter_wheel: str, calibration: Calibration | None = None):
        self.wl = wave_length
        self.fw = filter_wheel
        self.cal = calibration
        self.files: list['CalibFile'] = []
        self.anal = FileSetAnalysis(self)
        self.output_path = os.path.join(
            calibration.output_path,
            f"{self.wl}_{self.fw}"
        )
        self._concat_df: pd.DataFrame | None = None
        self._concat_ped_df: pd.DataFrame | None = None

    @property
    def concat_df(self):
        """Concatenated DataFrame of all calibration files in the set."""
        if self._concat_df is None:
            self._concat_df = pd.concat(
                [calfile.df for calfile in self.files if calfile.df is not None], ignore_index=True)
        return self._concat_df

    @property
    def concat_pedestal_df(self):
        """Concatenated DataFrame of all calibration files in the set."""
        if self._concat_ped_df is None:
            self._concat_ped_df = pd.concat(
                [calfile.df_pedestal for calfile in self.files if calfile.df_pedestal is not None], ignore_index=True)
        return self._concat_ped_df

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
            'wave_length': self.wl,
            'filter_wheel': self.fw,
            'analysis': self.anal.to_dict(),
            'files': {cf.meta['filename']: cf.to_dict() for cf in self.files}
        }



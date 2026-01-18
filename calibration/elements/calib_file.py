"""Calibration file representation and data handling"""

import os
import re

from typing import TYPE_CHECKING

import pandas as pd

from calibration.helpers import get_logger

from .analysis.calib_file_analysis import CalibFileAnalysis

logger = get_logger()

if TYPE_CHECKING:
    from .calibration import FileSet


file_name_pattern = re.compile(
    r"^calibration_(?P<day>\d{2})(?P<month>\d{2})(?P<year>\d{4})_PD_"
    r"(?P<wavelength>\d+)_"
    r"(?P<power>\d+(?:\.\d+)?[u,m]W)_"
    r"(?P<filterwheel>FW\d+)_"
    r"(?P<run>\d+)\.txt$"
)



class CalibFile:
    """Calibration file representation and data handling"""
    def __init__(self, file_path:str, file_set:FileSet|None=None):
        self.file_path = file_path
        self.fs = file_set
        self.output_path = self._calc_output_path()
        self._df: pd.DataFrame | None = None
        self._df_pedestal: pd.DataFrame | None = None
        self._df_full: pd.DataFrame | None = None
        self.valid = True
        self.anal = CalibFileAnalysis(self)
        self.meta = {
            'filename': os.path.basename(file_path),
        }
        self.initialize()
    
    @property
    def df(self)-> pd.DataFrame:
        """Return the main DataFrame with calibration data"""
        if self._df is not None:
            return self._df
        raise ValueError("DataFrame not loaded yet.")

    @property
    def df_pedestal(self) -> pd.DataFrame:
        """Return the pedestal DataFrame with calibration data"""
        if self._df_pedestal is not None:
            return self._df_pedestal
        raise ValueError("Pedestal DataFrame not loaded yet.")

    @property
    def df_full(self) -> pd.DataFrame:
        """Return the full DataFrame with calibration data"""
        if self._df_full is not None:
            return self._df_full
        raise ValueError("Full DataFrame not loaded yet.")

    def _calc_output_path(self):
        if self.fs:
            return os.path.join(
                self.fs.output_path,
                f"{self.set_label}_run{self.meta['run']}"
            )
        return None
    
    def set_file_set(self, file_set:FileSet|None):
        """Set the file set for this calibration file and update the output path accordingly"""
        self.fs = file_set
        self.output_path = self._calc_output_path()
    
    def initialize(self):
        """Parse filename and load data"""
        gd = file_name_pattern.match(self.meta['filename'])
        if gd:
            self.meta.update(gd.groupdict())
        else:
            logger.error("Filename '%s' does not match expected pattern.", self.meta['filename'])
            self.valid = False
            return
        self.load_data()

    def load_data(self):
        """Load calibration file data into a DataFrame"""
        self._df = pd.read_csv(self.file_path, delimiter ='\t', header=None)
        self._df.columns = ['datetime', 'L', 'meanPM', 'stdPM', 'meanRefPD', 'stdRefPD', 'Temp', 'RH', 'samples']
        self._df["datetime"] = pd.to_datetime(
            self._df["datetime"],
            format="%Y-%m-%d-%H:%M:%S",
            utc=True
        )
        self._df["timestamp"] = self._df["datetime"].astype("int64") // 1_000_000_000
        self._df_pedestal = pd.concat([self._df.iloc[[0]], self._df.iloc[[-1]]], ignore_index=True)
        self._df_full = self._df.copy()
        self._df = self._df.iloc[1:-1].reset_index(drop=True)
        logger.info("Loaded data for calibration file: %s", self.meta['filename'])


    def analyze(self):
        """Analyze the calibration file data"""
        if self.output_path:
            os.makedirs(self.output_path, exist_ok=True)
        self.anal.analyze()
        self.set_file_info()

    def set_file_info(self):
        """Set file info metadata"""
        self.meta['num_points'] = len(self._df)
        self.meta['file_size_bytes'] = os.path.getsize(self.file_path)
        self.meta['time_info'] = {}
        self._set_time_info()

    def _set_time_info(self):
        min_time = self.df['timestamp'].min()
        max_time = self.df['timestamp'].max()
        t_res = {
            'min_ts': int(min_time),
            'max_ts': int(max_time),
            'elapsed_time_s': int(max_time - min_time),
            'min_dt': pd.to_datetime(min_time, unit='s').strftime('%Y-%m-%d %H:%M:%S'),
            'max_dt': pd.to_datetime(max_time, unit='s').strftime('%Y-%m-%d %H:%M:%S')
        }
        self.meta['time_info'] = t_res

    @property
    def power(self) -> str:
        """Return power parsing from file name"""
        return self.meta['power']
    
    @property
    def filter_wheel(self) -> str:
        """Return filter wheel"""
        return self.meta['filterwheel']
    
    @property
    def wavelength(self) -> str:
        """Return wavelength"""
        return self.meta['wavelength']

    @property
    def set_label(self) -> str:
        """Return set label based on wavelength and filter wheel"""
        return f"{self.meta['wavelength']}nm_{self.meta['filterwheel']}"

    @property
    def file_label(self) -> str:
        """Return file label based on set label and run number"""
        return f"{self.set_label}_run{self.meta['run']}"
    
    @property
    def laser_label(self) -> str:
        """Return laser label based on wavelength"""
        if self.meta['wavelength'] == '1064':
            return 'Laser Power (mW)'
        if self.meta['wavelength'] == '532':
            return 'Laser Current (mA)'
        return 'Laser Parameter'

    def to_dict(self):
        """Convert calibration file data and analysis results to dictionary"""
        if self._df is not None:
            self.meta['num_points'] = len(self._df)
        tmp = self.meta.copy()
        tmp['analysis'] = self.anal.to_dict()
        return tmp

    def generate_plots(self):
        """Generate plots for the calibration file data"""
        self.anal.generate_plots()
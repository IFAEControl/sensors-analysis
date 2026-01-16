import os
import re

from typing import TYPE_CHECKING

import pandas as pd
from scipy.stats import linregress
import matplotlib.pyplot as plt

from calibration.helpers import get_logger
logger = get_logger()

if TYPE_CHECKING:
    from .calibration import FileSet

from .data_holders import CalibLinReg
from .calib_file_analysis import CalibFileAnalysis

file_name_pattern = re.compile(
    r"^calibration_(?P<day>\d{2})(?P<month>\d{2})(?P<year>\d{4})_PD_"
    r"(?P<wavelength>\d+)_"
    r"(?P<power>\d+(?:\.\d+)?[u,m]W)_"
    r"(?P<filterwheel>FW\d+)_"
    r"(?P<run>\d+)\.txt$"
)



class CalibFile:
    def __init__(self, file_path:str, file_set:FileSet|None=None):
        self.file_path = file_path
        self.fs = file_set
        self.output_path = self._calc_output_path()
        self.df: pd.DataFrame | None = None
        self.df_pedestal: pd.DataFrame | None = None
        self.df_full: pd.DataFrame | None = None
        self.valid = True
        self.anal = CalibFileAnalysis(self)
        self.meta = {
            'filename': os.path.basename(file_path),
            'size': os.path.getsize(file_path),
        }
        self.initialize()
    
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
        self.df = pd.read_csv(self.file_path, delimiter ='\t', header=None)
        self.df.columns = ['datetime', 'L', 'meanPM', 'stdPM', 'meanRefPD', 'stdRefPD', 'Temp', 'RH', 'samples']
        self.df["datetime"] = pd.to_datetime(
            self.df["datetime"],
            format="%Y-%m-%d-%H:%M:%S",
            utc=True
        )
        self.df["timestamp"] = self.df["datetime"].astype("int64") // 1_000_000_000
        self.df_pedestal = pd.concat([self.df.iloc[[0]], self.df.iloc[[-1]]], ignore_index=True)
        self.df_full = self.df.copy()
        self.df = self.df.iloc[1:-1].reset_index(drop=True)
        logger.info("Loaded data for calibration file: %s", self.meta['filename'])

    def analyze(self):
        """Analyze the calibration file data"""
        if self.output_path:
            os.makedirs(self.output_path, exist_ok=True)
        self.anal.analyze()
    
    @property
    def power(self):
        return self.meta['power']
    
    @property
    def filter_wheel(self):
        return self.meta['filterwheel']
    
    @property
    def wavelength(self):
        return self.meta['wavelength']

    @property
    def set_label(self):
        return f"{self.meta['wavelength']}nm_{self.meta['filterwheel']}"

    @property
    def file_label(self):
        return f"{self.set_label}_run{self.meta['run']}"
    
    @property
    def laser_label(self):
        if self.meta['wavelength'] == '1064':
            return 'Laser Power (mW)'
        if self.meta['wavelength'] == '532':
            return 'Laser Current (mA)'
        return 'Laser Parameter'

    def to_dict(self):
        if self.df is not None:
            self.meta['num_points'] = len(self.df)
        tmp = self.meta.copy()
        tmp['analysis'] = self.anal.to_dict()
        return tmp

    def generate_plots(self):
        """Generate plots for the calibration file data"""
        self.anal.generate_plots()
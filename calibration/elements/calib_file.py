"""Calibration file representation and data handling"""

import os
import re

from typing import TYPE_CHECKING

import pandas as pd

from calibration.helpers import get_logger
from calibration.config import config

from .analysis.file_analysis import CalibFileAnalysis
from .plots import FilePlots
from .base_element import BaseElement, DataHolderLevel

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



class CalibFile(BaseElement):
    """Calibration file representation and data handling"""
    def __init__(self, file_path:str, file_set:FileSet|None=None):
        super().__init__(DataHolderLevel.FILE)
        self.file_path = file_path
        self.dh_parent = file_set
        self.output_path = self._calc_output_path()
        self.valid = True
        self.anal = CalibFileAnalysis(self)
        self.plotter = FilePlots(self)
        
        self.file_info = {
            'filename': os.path.basename(file_path),
        }
        self.initialize()
        if self.valid:
            self.level_header = self.file_label
            self.long_label = f"{self.dh_parent.long_label} - run {self.file_info['run']}" if self.dh_parent else self.file_label

    @property
    def base_filename(self) -> str:
        """Return the base filename without path"""
        return '.'.join(os.path.basename(self.file_path).split('.')[:-1])
    
    @property
    def df(self)-> pd.DataFrame:
        """Return the main DataFrame with calibration data"""
        if self._df is not None:
            return self._df
        raise ValueError("DataFrame not loaded yet.")

    @property
    def df_pedestals(self) -> pd.DataFrame:
        """Return the pedestal DataFrame with calibration data"""
        if self._df_pedestals is not None:
            return self._df_pedestals
        raise ValueError("Pedestal DataFrame not loaded yet.")

    @property
    def df_full(self) -> pd.DataFrame:
        """Return the full DataFrame with calibration data"""
        if self._df_full is not None:
            return self._df_full
        raise ValueError("Full DataFrame not loaded yet.")

    def _calc_output_path(self):
        if self.dh_parent:
            return os.path.join(
                self.dh_parent.output_path,
                f"{self.set_label}_run{self.file_info['run']}"
            )
        return None
    
    def set_file_set(self, file_set:FileSet|None):
        """Set the file set for this calibration file and update the output path accordingly"""
        self.dh_parent = file_set
        self.output_path = self._calc_output_path()
        self.long_label = f"{self.dh_parent.long_label} - run {self.file_info['run']}" if self.dh_parent else self.file_label
    
    def initialize(self):
        """Parse filename and load data"""
        gd = file_name_pattern.match(self.file_info['filename'])
        if gd:
            self.file_info.update(gd.groupdict())
        else:
            logger.error("Filename '%s' does not match expected pattern.", self.file_info['filename'])
            self.valid = False
            return
        self.load_data()

    def _subs_pm_zero_stds(self):
        zero_std_count = (self._df['pm_std'] == 0).sum()
        self.data_prep_info['original_pm_std_zero_count'] = int(zero_std_count)
        self.data_prep_info['replace_zero_pm_std'] = config.replace_zero_pm_stds
        if config.replace_zero_pm_stds:
            resolution = config.power_meter_resolutions.get(f"{self.wavelength}-{self.filter_wheel}")
            self.data_prep_info['num_pm_std_replaced'] = int(zero_std_count)
            self.data_prep_info['pm_std_replacement_value'] = resolution
            if zero_std_count > 0:
                logger.info("Replacing %d zero PM std values with resolution %g for file %s", zero_std_count, resolution, self.file_info['filename'])
                self._df.loc[self._df['pm_std'] == 0, 'pm_std'] = resolution
        else:
            self.data_prep_info['num_pm_std_replaced'] = 0
            self.data_prep_info['pm_std_replacement_value'] = None

    def _subtract_pedestals(self):
        self.anal.analyze_pedestals()
        pm_ped = self.anal.pedestal_stats.pm.w_mean if self.anal.pedestal_stats.pm.weighted else self.anal.pedestal_stats.pm.mean
        ref_pd_ped = self.anal.pedestal_stats.refpd.w_mean if self.anal.pedestal_stats.refpd.weighted else self.anal.pedestal_stats.refpd.mean
        self._df['pm_zeroed'] = self._df['pm_mean'] - pm_ped
        self._df['ref_pd_zeroed'] = self._df['ref_pd_mean'] - ref_pd_ped
        self.data_prep_info['pedestal_subtraction'] = {
            'pm_pedestal': pm_ped,
            'refpd_pedestal': ref_pd_ped
        }

    def load_data(self):
        """Load calibration file data into a DataFrame"""
        self._df = pd.read_csv(self.file_path, delimiter ='\t', header=None)
        self._df.columns = ['datetime', 'laser_setpoint', 'pm_mean', 'pm_std', 'ref_pd_mean', 'ref_pd_std', 'temperature', 'RH', 'samples']
        self._df['laser_sp_1064'] = pd.Series([pd.NA] * len(self._df), dtype='Float64')
        self._df['laser_sp_532'] = pd.Series([pd.NA] * len(self._df), dtype='Float64')
        self._df[f'laser_sp_{self.wavelength}'] = self._df['laser_setpoint'].astype('Float64')
        self.data_prep_info['original_num_rows'] = len(self._df)
        self.data_prep_info['use_uW_as_power_units'] = config.use_uW_as_power_units
        if config.use_uW_as_power_units:
            self._df['pm_mean'] = self._df['pm_mean'] * 1e6
        self._df["datetime"] = pd.to_datetime(
            self._df["datetime"],
            format="%Y-%m-%d-%H:%M:%S",
            utc=True
        )
        self._df["timestamp"] = self._df["datetime"].astype("int64") // 1_000_000_000
        self._subs_pm_zero_stds()

        self._df_pedestals = pd.concat([self._df.iloc[[0]], self._df.iloc[[-1]]], ignore_index=True)
        self.data_prep_info['original_num_pedestals'] = len(self._df_pedestals)
        self._subtract_pedestals()

        self._df_full = self._df.copy()
        if config.use_first_pedestal_in_linreg:
            self._df = self._df.iloc[0:-1].reset_index(drop=True)
        else:
            self._df = self._df.iloc[1:-1].reset_index(drop=True)
        logger.info("Loaded data for calibration file: %s", self.file_info['filename'])


    def analyze(self):
        """Analyze the calibration file data"""
        if self.output_path:
            os.makedirs(self.output_path, exist_ok=True)
        self.anal.analyze()
        self.set_file_info()
        self.set_time_info()

    def set_file_info(self):
        """Set file info metadata"""
        self.file_info['num_points'] = len(self._df)
        self.file_info['file_size_bytes'] = os.path.getsize(self.file_path)

    @property
    def power(self) -> str:
        """Return power parsing from file name"""
        return self.file_info['power']
    
    @property
    def filter_wheel(self) -> str:
        """Return filter wheel"""
        return self.file_info['filterwheel']
    
    @property
    def wavelength(self) -> str:
        """Return wavelength"""
        return self.file_info['wavelength']

    @property
    def set_label(self) -> str:
        """Return set label based on wavelength and filter wheel"""
        return f"{self.file_info['wavelength']}nm_{self.file_info['filterwheel']}"

    @property
    def file_label(self) -> str:
        """Return file label based on set label and run number"""
        return f"{self.set_label}_run{self.file_info['run']}"
    
    @property
    def laser_label(self) -> str:
        """Return laser label based on wavelength"""
        if self.file_info['wavelength'] == '1064':
            return 'Laser SetPoint (mW)'
        if self.file_info['wavelength'] == '532':
            return 'Laser SetPoint (mA)'
        return 'Laser Parameter'

    def to_dict(self):
        """Convert calibration file data and analysis results to dictionary"""
        tmp = {
            'file_info': self.file_info,
            'time_info': self.time_info,
            'analysis': self.anal.to_dict(),
            'data_preparation': self.data_prep_info
        }
        return tmp

    def generate_plots(self):
        """Generate plots for the calibration file data"""
        self.plotter.generate_plots()
    

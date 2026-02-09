"""Sweep file representation and data handling"""

import os
import re
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from characterization.helpers import get_logger
from characterization.config import config

from .analysis.sweep_file_analysis import SweepFileAnalysis
from .plots.file_plots import FilePlots
from .base_element import BaseElement, DataHolderLevel

logger = get_logger()

if TYPE_CHECKING:
    from .photodiode import Photodiode

file_name_pattern = re.compile(
    r"^(?P<date>\d{8})_"
    r"(?P<board>[A-Za-z0-9_]+)_"
    r"(?P<sensor_id>\d+\.\d+)_"
    r"(?P<wavelength>\d+)_"
    r"(?P<filterwheel>FW\d+)_"
    r"(?P<run>\d+)\.txt$"
)

class SweepFile(BaseElement):
    def __init__(self, file_path: str, photodiode: 'Photodiode|None' = None):
        super().__init__(DataHolderLevel.RUN)
        self.file_path = file_path
        self.dh_parent = photodiode
        self.fileset = None
        self.output_path = self._calc_output_path()
        self.valid = True
        self.anal = SweepFileAnalysis(self)
        self.plotter = FilePlots(self)
        self.file_info = {
            'filename': os.path.basename(file_path),
        }
        self._df_sat = None
        self.initialize()
        if self.valid:
            self.level_header = self.file_label
            self.long_label = f"{self.dh_parent.long_label} - run {self.file_info['run']}" if self.dh_parent else self.file_label
        self._set_plot_label()

    @property
    def base_filename(self) -> str:
        return '.'.join(os.path.basename(self.file_path).split('.')[:-1])

    @property
    def df(self) -> pd.DataFrame:
        if self._df is not None:
            return self._df
        raise ValueError("DataFrame not loaded yet.")

    @property
    def df_pedestals(self) -> pd.DataFrame:
        if self._df_pedestals is not None:
            return self._df_pedestals
        raise ValueError("Pedestal DataFrame not loaded yet.")

    @property
    def df_full(self) -> pd.DataFrame:
        if self._df_full is not None:
            return self._df_full
        raise ValueError("Full DataFrame not loaded yet.")

    @property
    def df_sat(self) -> pd.DataFrame:
        if self._df_sat is not None:
            return self._df_sat
        raise ValueError("Saturated DataFrame not loaded yet.")


    def _calc_output_path(self):
        if self.fileset:
            return os.path.join(
                self.fileset.output_path,
                f"run{self.file_info.get('run', 'NA')}"
            )
        if self.dh_parent:
            return os.path.join(
                self.dh_parent.output_path,
                f"{self.wavelength}nm_{self.filter_wheel}_run{self.file_info.get('run', 'NA')}"
            )
        return None

    def set_photodiode(self, photodiode: 'Photodiode|None'):
        self.dh_parent = photodiode
        self.output_path = self._calc_output_path()
        self.long_label = f"{self.dh_parent.long_label} - run {self.file_info['run']}" if self.dh_parent else self.file_label
        self._set_plot_label()

    def set_fileset(self, fileset):
        self.fileset = fileset
        self.output_path = self._calc_output_path()
        self._set_plot_label()

    def _set_plot_label(self):
        if self.dh_parent and self.dh_parent.dh_parent:
            char_id = self.dh_parent.dh_parent.level_header
            self.plot_label = f"{char_id} - PD{self.sensor_id} - {self.wavelength} - {self.filter_wheel} - run{self.run}"
        else:
            self.plot_label = self.file_label

    def initialize(self):
        gd = file_name_pattern.match(self.file_info['filename'])
        if gd:
            self.file_info.update(gd.groupdict())
        else:
            logger.error("Filename '%s' does not match expected pattern.", self.file_info['filename'])
            self.valid = False
            return
        self.load_data()

    def load_data(self):
        self._df = pd.read_csv(self.file_path, delimiter='\t', header=None)
        self._df.columns = [
            'datetime', 'laser_setpoint', 'total_sum', 'total_square_sum',
            'ref_pd_mean', 'ref_pd_std', 'temperature', 'RH', 'total_counts'
        ]
        numeric_cols = [c for c in self._df.columns if c != 'datetime']
        self._df[numeric_cols] = self._df[numeric_cols].astype('Float64')

        counts = self._df['total_counts']
        mean_adc = self._df['total_sum'] / counts
        var_adc = (self._df['total_square_sum']/counts - mean_adc**2) 
        # var_adc = var_adc.clip(lower=0)
        std_adc = np.sqrt(var_adc)
        std_adc[counts <= 1] = np.nan

        self._df['mean_adc'] = mean_adc
        self._df['std_adc'] = std_adc
        self._df['laser_sp_1064'] = pd.Series([pd.NA] * len(self._df), dtype='Float64')
        self._df['laser_sp_532'] = pd.Series([pd.NA] * len(self._df), dtype='Float64')
        if self.wavelength == '1064':
            self._df['laser_sp_1064'] = self._df['laser_setpoint']
        elif self.wavelength == '532':
            self._df['laser_sp_532'] = self._df['laser_setpoint']
        self._df['run'] = pd.Series([self.run] * len(self._df), dtype='string')
        self._df['sweep_id'] = pd.Series([f"{self.wavelength}_{self.filter_wheel}_run{self.run}"] * len(self._df), dtype='string')

        self._df['datetime'] = pd.to_datetime(
            self._df['datetime'],
            format="%Y-%m-%d-%H:%M:%S",
            utc=True
        )
        self._df['timestamp'] = self._df['datetime'].astype('int64') // 1_000_000_000

        self.data_prep_info['original_num_rows'] = len(self._df)

        is_pedestal = np.isclose(self._df['laser_setpoint'], 0.0)
        is_saturated = self._df['mean_adc'] >= 4095
        self._df_pedestals = self._df[is_pedestal].copy().reset_index(drop=True)
        self._df_full = self._df.copy()
        self._df_sat = self._df[is_saturated].copy().reset_index(drop=True)
        self._df = self._df[~is_pedestal & ~is_saturated].reset_index(drop=True)

        self.data_prep_info['original_num_pedestals'] = int(is_pedestal.sum())
        self.data_prep_info['original_num_saturated'] = int(is_saturated.sum())
        logger.info("Loaded data for sweep file: %s", self.file_info['filename'])

    def analyze(self):
        if self.output_path:
            os.makedirs(self.output_path, exist_ok=True)
        self.anal.analyze()
        self.set_file_info()
        self.set_time_info()

    def set_file_info(self):
        self.file_info['num_points'] = len(self._df)
        self.file_info['file_size_bytes'] = os.path.getsize(self.file_path)

    @property
    def sensor_id(self) -> str:
        return self.file_info['sensor_id']

    @property
    def filter_wheel(self) -> str:
        return self.file_info['filterwheel']

    @property
    def wavelength(self) -> str:
        return self.file_info['wavelength']

    @property
    def run(self) -> str:
        return self.file_info['run']

    @property
    def board(self) -> str:
        return self.file_info['board']

    @property
    def date(self) -> str:
        return self.file_info['date']

    @property
    def set_label(self) -> str:
        return f"{self.wavelength}nm_{self.filter_wheel}"

    @property
    def file_label(self) -> str:
        return f"{self.sensor_id}_{self.set_label}_run{self.run}"

    @property
    def laser_label(self) -> str:
        if self.wavelength == '1064':
            return 'Laser Power (mW)'
        if self.wavelength == '532':
            return 'Laser Current (mA)'
        return 'Laser Parameter'

    def to_dict(self):
        return {
            'file_info': self.file_info,
            'time_info': self.time_info,
            'analysis': self.anal.to_dict(),
            'data_preparation': self.data_prep_info
        }

    def generate_plots(self):
        self.plotter.generate_plots()

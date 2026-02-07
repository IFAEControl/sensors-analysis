import os
from typing import TYPE_CHECKING

import pandas as pd

from characterization.helpers import get_logger
from .analysis.sweep_file_analysis import SweepFileAnalysis
from .plots.fileset_plots import FilesetPlots
from .base_element import BaseElement, DataHolderLevel

if TYPE_CHECKING:
    from .photodiode import Photodiode
    from .sweep_file import SweepFile

logger = get_logger()


class Fileset(BaseElement):
    """Group of sweep files for one (wavelength, filter wheel)."""

    def __init__(self, wavelength: str, filter_wheel: str, photodiode: 'Photodiode|None' = None):
        super().__init__(DataHolderLevel.RUN)
        self.wavelength = wavelength
        self.filter_wheel = filter_wheel
        self.label = f"{self.wavelength}_{self.filter_wheel}"
        self.dh_parent = photodiode
        self.board_id = photodiode.board_id if photodiode else None
        self.files: list['SweepFile'] = []
        self.anal = SweepFileAnalysis(self)
        self.plotter = FilesetPlots(self)
        self.output_path = os.path.join(
            photodiode.output_path,
            self.label
        ) if photodiode else None
        self.level_header = self.label
        self.long_label = f"{self.dh_parent.level_header} - {self.label}" if self.dh_parent else self.label
        if self.dh_parent and self.dh_parent.dh_parent:
            self.plot_label = f"{self.dh_parent.dh_parent.level_header} - PD{self.dh_parent.sensor_id} - {self.wavelength} - {self.filter_wheel}"
        self._df_analysis = None

    @property
    def df(self):
        if self._df is None:
            if not self.files:
                return pd.DataFrame()
            self._df = pd.concat([cf.df for cf in self.files if cf.df is not None], ignore_index=True)
            self._df = self._df.sort_values(by='timestamp').reset_index(drop=True)
        return self._df

    @property
    def df_pedestals(self):
        if self._df_pedestals is None:
            if not self.files:
                return pd.DataFrame()
            self._df_pedestals = pd.concat([cf.df_pedestals for cf in self.files if cf.df_pedestals is not None], ignore_index=True)
            self._df_pedestals = self._df_pedestals.sort_values(by='timestamp').reset_index(drop=True)
        return self._df_pedestals

    @property
    def df_full(self):
        if self._df_full is None:
            if not self.files:
                return pd.DataFrame()
            self._df_full = pd.concat([cf.df_full for cf in self.files if cf.df_full is not None], ignore_index=True)
            self._df_full = self._df_full.sort_values(by='timestamp').reset_index(drop=True)
        return self._df_full

    @property
    def df_analysis(self):
        if self._df_analysis is not None:
            return self._df_analysis
        return self.df

    def set_analysis_df(self, df: pd.DataFrame):
        self._df_analysis = df

    def add_file(self, sweep_file: 'SweepFile'):
        if sweep_file.wavelength != self.wavelength or sweep_file.filter_wheel != self.filter_wheel:
            logger.error("Sweep file configuration does not match fileset %s", self.label)
            return
        self.files.append(sweep_file)
        if self.board_id is None:
            self.board_id = sweep_file.file_info.get('board')
        sweep_file.set_fileset(self)

    def analyze(self):
        if self.output_path:
            os.makedirs(self.output_path, exist_ok=True)
        for cf in self.files:
            cf.analyze()
        self.anal.analyze()
        self.set_time_info()

    def generate_plots(self):
        self.plotter.generate_plots()

    def to_dict(self):
        return {
            'meta': {'wavelength': self.wavelength, 'filter_wheel': self.filter_wheel},
            'time_info': self.time_info,
            'analysis': self.anal.to_dict(),
            'files': {cf.file_label: cf.to_dict() for cf in self.files},
            'plots': self.plotter.plots
        }

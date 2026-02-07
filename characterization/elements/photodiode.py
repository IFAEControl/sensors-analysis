import os
from typing import TYPE_CHECKING
import pandas as pd

from characterization.helpers import get_logger
from .analysis.photodiode_analysis import PhotodiodeAnalysis
from .plots.photodiode_plots import PhotodiodePlots
from .sanity_checks import PhotodiodeSanity
from .fileset import Fileset
from .base_element import BaseElement, DataHolderLevel

if TYPE_CHECKING:
    from .characterization import Characterization
    from .sweep_file import SweepFile

logger = get_logger()

class Photodiode(BaseElement):
    def __init__(self, sensor_id: str, characterization: 'Characterization|None' = None):
        super().__init__(DataHolderLevel.PHOTODIODE)
        self.sensor_id = sensor_id
        self.dh_parent = characterization
        self.board_id = None
        self.files: list['SweepFile'] = []
        self.filesets: dict[str, Fileset] = {}
        self.anal = PhotodiodeAnalysis(self)
        self.plotter = PhotodiodePlots(self)
        self.sanity = PhotodiodeSanity(self)
        self.output_path = os.path.join(
            characterization.output_path,
            f"sensor_{sensor_id}"
        ) if characterization else None
        self.level_header = sensor_id
        self.long_label = f"{self.dh_parent.level_header} - {sensor_id}" if self.dh_parent else sensor_id
        if self.dh_parent:
            self.plot_label = f"{self.dh_parent.level_header} - PD{sensor_id}"
        else:
            self.plot_label = f"PD{sensor_id}"

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

    def add_file(self, sweep_file: 'SweepFile'):
        if sweep_file.sensor_id != self.sensor_id:
            logger.error("File sensor id does not match photodiode id: %s", sweep_file.file_info['filename'])
            return
        self.files.append(sweep_file)
        sweep_file.set_photodiode(self)
        if self.board_id is None:
            self.board_id = sweep_file.file_info.get('board')
        key = f"{sweep_file.wavelength}_{sweep_file.filter_wheel}"
        self.filesets.setdefault(key, Fileset(sweep_file.wavelength, sweep_file.filter_wheel, photodiode=self)).add_file(sweep_file)

    def analyze(self):
        if self.output_path:
            os.makedirs(self.output_path, exist_ok=True)
        self.anal.analyze()
        self.sanity.run_checks()
        self.set_time_info()

    def generate_plots(self):
        self.plotter.generate_plots()

    def to_dict(self):
        return {
            'meta': {'sensor_id': self.sensor_id},
            'time_info': self.time_info,
            'analysis': self.anal.to_dict(),
            'sanity_checks': self.sanity.results,
            'filesets': {key: fs.to_dict() for key, fs in self.filesets.items()},
            'plots': self.plotter.plots
        }

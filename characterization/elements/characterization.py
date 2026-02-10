"""Characterization top-level element"""
import os
import json
from datetime import datetime, timezone
import pandas as pd

from characterization.helpers import file_manage, get_logger, system_info
from .sweep_file import SweepFile
from .analysis.characterization_analysis import CharacterizationAnalysis
from .plots.characterization_plots import CharacterizationPlots
from .base_element import BaseElement, DataHolderLevel
from .photodiode import Photodiode
from characterization.config import config

logger = get_logger()

class Characterization(BaseElement):
    def __init__(self, call_args):
        super().__init__(DataHolderLevel.CHARACTERIZATION)
        cfpath, opath, char_name = file_manage.setup_paths(call_args.char_files_path, call_args.output_path, overwrite=call_args.overwrite)
        self.char_files_path = cfpath
        self.reports_path = os.path.join(opath)
        self.output_path = os.path.join(opath, 'characterization_outputs')
        self.photodiodes: dict[str, Photodiode] = {}
        self.meta = {
            'calling_arguments': vars(call_args),
            'charact_id': char_name,
            'charact_files_path': cfpath,
            'root_output_path': opath,
            'characterization_outputs_path': self.output_path,
            'reports_path': self.reports_path,
            'execution_date': datetime.now(timezone.utc).isoformat(),
            'system': system_info.get_system_info(),
            'config': config.to_dict()
        }
        self.anal = CharacterizationAnalysis(self)
        self.plotter = CharacterizationPlots(self)
        self.level_header = char_name
        self.long_label = char_name
        self.initialize()

    def initialize(self):
        os.makedirs(self.output_path, exist_ok=True)
        self.plot_label = self.level_header

    @property
    def df(self):
        if self._df is None:
            if not self.photodiodes:
                return pd.DataFrame()
            self._df = pd.concat(
                [cf.df for pdh in self.photodiodes.values() for cf in pdh.files if cf.df is not None],
                ignore_index=True
            )
            self._df = self._df.sort_values(by='timestamp').reset_index(drop=True)
            self._df = self._na_adc_columns(self._df)
        return self._df

    @property
    def df_pedestals(self):
        if self._df_pedestals is None:
            if not self.photodiodes:
                return pd.DataFrame()
            self._df_pedestals = pd.concat(
                [cf.df_pedestals for pdh in self.photodiodes.values() for cf in pdh.files if cf.df_pedestals is not None],
                ignore_index=True
            )
            self._df_pedestals = self._df_pedestals.sort_values(by='timestamp').reset_index(drop=True)
            self._df_pedestals = self._na_adc_columns(self._df_pedestals)
        return self._df_pedestals

    @property
    def df_full(self):
        if self._df_full is None:
            if not self.photodiodes:
                return pd.DataFrame()
            self._df_full = pd.concat(
                [cf.df_full for pdh in self.photodiodes.values() for cf in pdh.files if cf.df_full is not None],
                ignore_index=True
            )
            self._df_full = self._df_full.sort_values(by='timestamp').reset_index(drop=True)
            self._df_full = self._na_adc_columns(self._df_full)
        return self._df_full

    @staticmethod
    def _na_adc_columns(df: pd.DataFrame) -> pd.DataFrame:
        adc_cols = ['total_sum', 'total_square_sum', 'total_counts', 'mean_adc', 'std_adc']
        existing = [col for col in adc_cols if col in df.columns]
        if existing:
            df = df.copy()
            df[existing] = pd.NA
        return df

    def load_characterization_files(self):
        for file_name in sorted(os.listdir(self.char_files_path)):
            file_path = os.path.join(self.char_files_path, file_name)
            if os.path.isfile(file_path):
                sweepfile = SweepFile(file_path)
                if sweepfile.valid:
                    self.photodiodes.setdefault(sweepfile.sensor_id, Photodiode(sweepfile.sensor_id, characterization=self)).add_file(sweepfile)
                else:
                    logger.warning("Skipping invalid characterization file: %s", file_name)
                    continue

    def analyze(self):
        os.makedirs(self.output_path, exist_ok=True)
        self.anal.analyze()
        self.set_time_info()

    def generate_plots(self):
        os.makedirs(self.output_path, exist_ok=True)
        pd_plots = self.plotter.plots.setdefault('photodiodes', {})
        for pdh in self.photodiodes.values():
            pdh.generate_plots()
            pd_plots[pdh.level_header] = pdh.plotter.plots
            logger.debug("Generated plots for photodiode %s", pdh.sensor_id)
        self.plotter.generate_plots()

    def to_dict(self):
        return {
            'meta': self.meta,
            'analysis': self.anal.to_dict(),
            'time_info': self.time_info,
            'plots': self.plotter.plots
        }

    def export_data_summary(self, meta: dict | None = None):
        results_path = os.path.join(self.reports_path, config.summary_file_name)
        outdata = self.to_dict()
        if meta:
            outdata.update(meta)
        with open(results_path, 'w', encoding='utf-8') as f:
            try:
                json.dump(outdata, f, indent=2)
            except TypeError as e:
                logger.error("Failed to serialize characterization data to JSON: %s", str(e))
                print(outdata)
        logger.info("Characterization results saved to %s", results_path)

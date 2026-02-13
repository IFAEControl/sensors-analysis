"""Characterization file analysis"""

from typing import TYPE_CHECKING
import numpy as np
from scipy.stats import linregress

from characterization.helpers import get_logger
from characterization.config import config

from ..helpers import CharLinReg
from .analysis_base import BaseAnal

if TYPE_CHECKING:
    from ..sweep_file import SweepFile

logger = get_logger()

class SweepFileAnalysis(BaseAnal):
    def __init__(self, char_file: 'SweepFile'):
        super().__init__()
        self._data_holder = char_file
        self._data_info = {}
        # self.saturation_adc = None

    def analyze(self):
        if self.df is None or self.df.empty:
            logger.error("Dataframe is not loaded for file: %s", self._data_holder.file_info['filename'])
            print(self._data_holder._df)
            return
        self._calc_pedestal_stats()
        self._calc_saturation_stats()
        # Saturation derivative method disabled for now
        # df_filtered, sat_adc = self._find_saturation_from_derivative(self.df)
        # self.saturation_adc = sat_adc
        if len(self.df) >= 2:
            self.lr_refpd_vs_adc.linreg = linregress(self.df['mean_adc'], self.df['ref_pd_mean'])
        else:
            logger.warning("Not enough points for linreg in file: %s", self._data_holder.file_info['filename'])
        self._analyzed = True

    # def _find_saturation_from_derivative(self, df):
    #     x = df['ref_pd_mean'].values
    #     y = df['mean_adc'].values
    #     if len(x) < 2:
    #         return df, None
    #     dy_dx = np.gradient(y, x)
    #     df = df.copy()
    #     df['dy_dx'] = dy_dx
    #     threshold = config.saturation_derivative_threshold
    #     flat_indices = np.where(np.abs(dy_dx) < threshold)[0]
    #     non_flat_indices = np.where(np.abs(dy_dx) >= threshold)[0]
    #     saturation_adc = y[flat_indices[0]] if flat_indices.size > 0 else None
    #     if non_flat_indices.size > 0:
    #         df_filtered = df.iloc[non_flat_indices].reset_index(drop=True)
    #     else:
    #         df_filtered = df
    #     return df_filtered, saturation_adc

    def to_dict(self) -> dict:
        if not self._analyzed:
            logger.warning("Analysis has not been performed yet for file: %s", self._data_holder.file_info['filename'])
        return {
            'linreg_refpd_vs_adc': self.lr_refpd_vs_adc.to_dict() if self.lr_refpd_vs_adc.linreg else None,
            # 'saturation_adc': None if self.saturation_adc is None else float(self.saturation_adc),
            'pedestal_stats': self._pedestal_stats,
            'saturation_stats': self._saturation_stats,
        }

from abc import ABC, abstractmethod
import numpy as np
import pandas as pd

from characterization.helpers import get_logger
from ..helpers import CharLinReg

logger = get_logger()

class BaseAnal(ABC):
    def __init__(self) -> None:
        self._data_holder = None
        self._analyzed = False
        self.lr_refpd_vs_adc = CharLinReg('mean_adc', 'ref_pd_mean', None)
        self._pedestal_stats = {}
        self._saturation_stats = {}

    @property
    def df(self) -> pd.DataFrame:
        return self._data_holder.df

    @property
    def df_pedestals(self) -> pd.DataFrame:
        return self._data_holder.df_pedestals

    @property
    def df_full(self) -> pd.DataFrame:
        return self._data_holder.df_full

    @property
    def df_sat(self) -> pd.DataFrame:
        return self._data_holder.df_sat

    @abstractmethod
    def analyze(self):
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    def _calc_pedestal_stats(self) -> dict:
        if self.df_pedestals is None or self.df_pedestals.empty:
            return {}
        self._pedestal_stats = {
            'mean_adc': {
                'mean': float(self.df_pedestals['mean_adc'].mean()),
                'std': float(self.df_pedestals['mean_adc'].std()),
                'samples': int(self.df_pedestals['mean_adc'].shape[0]),
            },
            'ref_pd_mean': {
                'mean': float(self.df_pedestals['ref_pd_mean'].mean()),
                'std': float(self.df_pedestals['ref_pd_mean'].std()),
                'samples': int(self.df_pedestals['ref_pd_mean'].shape[0]),
            },
        }
        return self._pedestal_stats

    def _calc_saturation_stats(self, threshold: int = 4095) -> dict:
        # Can't be called from Characterization level since it relies on df_sat which is only defined at sweep file and fileset level

        if self.df_full is None or self.df_full.empty:
            return {}
        self._saturation_stats = {
            'threshold': threshold,
            'num_saturated': 0 if self.df_sat is None else int(self.df_sat.shape[0]),
            'total_points': int(self.df_full.shape[0]),
        }
        return self._saturation_stats

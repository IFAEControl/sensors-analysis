from abc import ABC, abstractmethod
import numpy as np
import pandas as pd

from characterization.helpers import get_logger
from characterization.config import config
from ..helpers import CharLinReg

logger = get_logger()

class BaseAnal(ABC):
    def __init__(self) -> None:
        self._data_holder = None
        self._analyzed = False
        if config.subtract_pedestals:
            self.lr_refpd_vs_adc = CharLinReg('mean_adc_zeroed', 'ref_pd_zeroed', None)
        else:
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

    def _calc_single_pedestal_stat(self, value_col: str, std_col: str) -> dict | None:
        if self.df_pedestals is None or self.df_pedestals.empty:
            return None
        if value_col not in self.df_pedestals.columns:
            return None
        vals = self.df_pedestals[value_col].astype(float)
        out = {
            "mean": float(vals.mean()),
            "std": float(vals.std()),
            "samples": int(vals.shape[0]),
            "weighted": False,
            "w_mean": 0.0,
            "w_stderr": 0.0,
            "ndof": 0,
            "chi2": 0.0,
            "chi2_reduced": 0.0,
            "exec_error": False,
        }
        if std_col not in self.df_pedestals.columns:
            return out
        std = self.df_pedestals[std_col].astype(float)
        mask = std > 0
        vals = vals[mask]
        std = std[mask]
        ndof = int(vals.shape[0] - 1)
        out["ndof"] = ndof
        if ndof <= 0:
            out["exec_error"] = True
            return out
        w = 1.0 / (std ** 2)
        w_mean = float((w * vals).sum() / w.sum())
        w_stderr = float(np.sqrt(1.0 / w.sum()))
        chi2 = float(np.sum(((vals - w_mean) ** 2) / (std ** 2)))
        out["weighted"] = True
        out["w_mean"] = w_mean
        out["w_stderr"] = w_stderr
        out["chi2"] = chi2
        out["chi2_reduced"] = float(chi2 / ndof)
        return out

    def _calc_pedestal_stats(self) -> dict:
        ## We have to use the raw values for the pedestals as the zeroed values are all zero
        # and would not give us any information. (We need the pedestals stats to calculate the zeroed columns)
        out = {}
        adc_stats = self._calc_single_pedestal_stat("mean_adc", "std_adc")
        refpd_stats = self._calc_single_pedestal_stat("ref_pd_mean", "ref_pd_std")
        if adc_stats is not None:
            out["mean_adc"] = adc_stats
        if refpd_stats is not None:
            out["ref_pd_mean"] = refpd_stats
        self._pedestal_stats = out
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

from abc import ABC, abstractmethod

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

from ..helpers import SanityCheckResult, MeanStats, PedestalStats
from calibration.helpers import get_logger

logger = get_logger()


class BaseAnal(ABC):
    """Abstract base class for analysis components."""

    def __init__(self, *args, **kwargs) -> None:
        self._results = {}
        self._data_holder = None
        self._ped_stats: PedestalStats | None = None
    
    @property
    def pedestal_stats(self) -> PedestalStats:
        """Pedestal analysis results."""
        if self._ped_stats is None:
            logger.warning("Pedestal analysis has not been performed yet for %s", self._data_holder.level_header)
            self.analyze_pedestals()
        return self._ped_stats

    @property
    def df(self) -> pd.DataFrame:
        """DataFrame containing the data to be analyzed."""
        return self._data_holder.df
    
    @property
    def df_pedestals(self) -> pd.DataFrame:
        """DataFrame containing the pedestal data to be analyzed."""
        return self._data_holder.df_pedestals
    
    @property
    def df_full(self) -> pd.DataFrame:
        """DataFrame containing the full data to be analyzed."""
        return self._data_holder.df_full

    @abstractmethod
    def analyze(self):
        """Perform the analysis."""

    @abstractmethod
    def to_dict(self) -> dict:
        """Convert analysis results to a dictionary."""

    def get_mean(self, df:pd.DataFrame, val_col: str, std_col: str, weighted: bool = True) -> MeanStats:
        """Calculate mean statistics from a DataFrame column.

        Args:
            df (pd.DataFrame): DataFrame containing the data.
            val_col (str): Column name for the values.
            std_col (str): Column name for the standard deviations.
            weighted (bool): Whether to calculate weighted mean and std
        """
        mean = MeanStats(df[val_col].mean(), df[val_col].std(), df[val_col].size)
        if weighted:
            mean.weighted = True
            zero_std_points = df[df[std_col]==0]
            if len(zero_std_points) > 0:
                logger.warning("[%s] There are %d points with std=0. These points will be ignored in weighted mean", self._data_holder.level_header, len(zero_std_points))
                df_filtered = df[df[std_col]>0]
            df = df if len(zero_std_points) == 0 else df_filtered
            ndof = len(df[val_col]) - 1
            mean.ndof = ndof
            if ndof > 0:
                # to check, xxxx_chi2_reduced should be in the range  1 +- sqrt(2/ndf)
                w = 1.0 / df[std_col]**2
                w_mean = (w * df[val_col]).sum() / w.sum()
                w_std = np.sqrt(1.0 / w.sum())
                w_chi2 = np.sum((df[val_col]-w_mean)**2 / df[std_col]**2)
                w_chi2_reduced = w_chi2 / ndof
                
                mean.w_mean = w_mean
                mean.w_stderr = w_std
                mean.chi2 = w_chi2
                mean.chi2_reduced = w_chi2_reduced
                
            else:
                mean.exec_error = True
                logger.warning(f"[{self._data_holder.level_header}] Not enough data [{val_col}] points to analyze weighted mean")
            
        return mean

    def analyze_pedestals(self):
        """Analyze pedestals across the set of calibration files"""
        
        pm_pedestals = self.get_mean(self.df_pedestals, 'pm_mean', 'pm_std', weighted=True)
        refpd_pedestals = self.get_mean(self.df_pedestals, 'ref_pd_mean', 'ref_pd_std', weighted=True)
        self._ped_stats = PedestalStats(pm=pm_pedestals, refpd=refpd_pedestals)
        

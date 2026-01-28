import os

from typing import TYPE_CHECKING

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy.stats import linregress

from calibration.helpers import get_logger
from calibration.config import config

from .analysis_base import BaseAnal
from ..helpers import CalibLinReg, PedestalStats, MeanStats

if TYPE_CHECKING:
    from ..calibration import Calibration
    from ..calib_file import CalibFile
    from ..calib_fileset import FileSet

logger = get_logger()

class FileSetAnalysis(BaseAnal):
    """Class to analyze a set of calibration files."""

    def __init__(self, file_set: FileSet):
        super().__init__()
        self.fs = file_set
        self.results = {}
        self._data_holder:FileSet = file_set

        self.slopes = []
        self.slopes_std = []
        self.intercepts = []
        self.intercepts_std = []
        self.mean_temp = []
        self.mean_rh = []
        
        self.lr_slopes_mean: MeanStats | None = None
        self.lr_intercepts_mean: MeanStats | None = None
        self.lr_refpd_vs_pm: CalibLinReg | None = None
        self._analyzed = False

    @property
    def df(self):
        """Concatenated DataFrame of all calibration files in the set."""
        # This has to be set like this so we can use the base class methods that use self.df
        # mostly for plotting time series
        # It will be used also to:
        #  - calculate histograms of temperature and humidity
        #  - calculate linear regressions across the set of files
        return self.fs.df
    
    @property
    def df_pedestals(self):
        """Concatenated DataFrame of all pedestal data in the set."""
        return self.fs.df_pedestals

    @property
    def output_path(self):
        """Output path for the file set analysis."""
        return self.fs.output_path

    @property
    def analyzed(self) -> bool:
        """Whether the analysis has been performed."""
        return self._analyzed

    def analyze(self):
        """Analyze the set of calibration files."""
        for calfile in self.fs.files:
            calfile.analyze()
            logger.info("Analyzed calibration file: %s",
                        calfile.file_info['filename'])
        
        self.build_arrays()
        self.calc_means_of_lin_regs()
        # self.analyze_mean_of_lin_regs()
        # self.analyze_weighted_mean_of_lin_regs()
        self.analyze_concatenated_data_sets()
        self.analyze_pedestals()
        self.results['pedestals'] = self._ped_stats.to_dict()
        self._analyzed = True

    def build_arrays(self):
        for calfile in self.fs.files:
            self.slopes.append(calfile.anal.lr_refpd_vs_pm.slope)
            self.slopes_std.append(calfile.anal.lr_refpd_vs_pm.stderr)
            self.intercepts.append(
                calfile.anal.lr_refpd_vs_pm.intercept)
            self.intercepts_std.append(
                calfile.anal.lr_refpd_vs_pm.intercept_stderr)
            self.mean_temp.append(calfile._df['temperature'].mean())
            self.mean_rh.append(calfile._df['RH'].mean())
        self.slopes = np.array(self.slopes)
        self.slopes_std = np.array(self.slopes_std)
        self.intercepts = np.array(self.intercepts)
        self.intercepts_std = np.array(self.intercepts_std)

    def analyze_concatenated_data_sets(self):
        """Analyze the full concatenated data set of the file set."""
        linreg = linregress(self.df['ref_pd_mean'], self.df['pm_mean'])
        self.lr_refpd_vs_pm = CalibLinReg(
            'ref_pd_mean', 'pm_mean', linreg)
        self.results['lr_refpd_vs_pm'] = self.lr_refpd_vs_pm.to_dict()

    def calc_means_of_lin_regs(self):
        """Analyze weighted mean of linear regressions of the calibration files"""
        # has to be executed after analyze_mean_of_lin_regs
        self.lr_slopes_mean = self.get_mean(
            pd.DataFrame({
                'slope': self.slopes,
                'slope_std': self.slopes_std
            }),
            'slope',
            'slope_std',
            weighted=True
        )
        self.lr_intercepts_mean = self.get_mean(
            pd.DataFrame({
                'intercept': self.intercepts,
                'intercept_std': self.intercepts_std
            }),
            'intercept',
            'intercept_std',
            weighted=True
        )

    # def analyze_weighted_mean_of_lin_regs(self):
    #     """Analyze weighted mean of linear regressions of the calibration files"""
    #     # has to be executed after analyze_mean_of_lin_regs
    #     weights = 1 / self.slopes_std**2
    #     weighted_mean = np.sum(weights * self.slopes) / np.sum(weights)
    #     weighted_mean_error = np.sqrt(1 / np.sum(weights))
    #     weighted_variance = np.sum(weights * (self.slopes - weighted_mean)**2) / np.sum(weights)
    #     weighted_std_dev = np.sqrt(weighted_variance)
    #     intervariability = np.std(self.slopes, ddof=1)  # Standard deviation (sample)
    #     combined_sigma = np.sqrt(weighted_std_dev**2+intervariability**2)

    #     self.results['weighted_linreg_means'] = {
    #         'slope': weighted_mean,
    #         'slope_error': weighted_mean_error,
    #         'weighted_std_dev': weighted_std_dev,
    #         'intervariability': intervariability,
    #         'combined_sigma': combined_sigma
    #     }


    # def analyze_mean_of_lin_regs(self):
    #     """Analyze linear regressions across the set of calibration files."""
    #     self.results['linreg_means'] = {
    #         'slope': self.slopes.mean(),
    #         'slope_std': self.slopes.std(),
    #         'intercept': self.intercepts.mean(),
    #         'intercept_std': self.intercepts.std(),
    #         'slope_dispersion': (self.slopes.max() - self.slopes.min())/self.slopes.max()*100
    #     }


    def to_dict(self):
        """Convert file set analysis results to dictionary."""
        if self._analyzed is False:
            logger.warning("Analysis has not been performed yet for file set: %s", self.fs.label)
        return self.results

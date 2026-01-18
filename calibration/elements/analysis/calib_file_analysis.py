"""
Docstring for calibration.elements.calib_file_analysis
"""

from typing import TYPE_CHECKING
import pandas as pd
from scipy.stats import linregress
import matplotlib.pyplot as plt


from calibration.helpers import get_logger
from calibration.helpers.file_manage import get_generate_plots

from ..data_holders import CalibLinReg
from .analysis_base import BaseAnal

if TYPE_CHECKING:
    from ..calib_file import CalibFile


logger = get_logger()


class CalibFileAnalysis(BaseAnal):
    """
    Docstring for CalibFileAnalysis
    """
    def __init__(self, calib_file:CalibFile):
        super().__init__()
        self.cf:CalibFile = calib_file
        self.file_info = {}
        self.linreg_refPD_vs_meanPM = CalibLinReg('meanRefPD', 'meanPM', None)
        self.linreg_meanPM_vs_L = CalibLinReg('L', 'meanPM', None)
        self.linreg_refPD_vs_L = CalibLinReg('L', 'meanRefPD', None)

    @property
    def anal_label(self) -> str:
        return self.cf.file_label

    @property
    def laser_label(self) -> str:
        return self.cf.laser_label

    @property
    def df(self) -> pd.DataFrame:
        """
        df: DataFrame with calibration data
        """
        return self.cf.df

    @property
    def output_path(self) -> str:
        """
        output_path: where to store plots and results for this set of files
        Filename should contain the run number
        """
        return self.cf.output_path if self.cf.output_path else '.'

    def analyze(self):
        """
        Docstring for analyze
        """

        self.calc_lin_regs()
        if get_generate_plots():
            self.generate_plots()

    def calc_lin_regs(self):
        """Calculate linear regressions for the calibration file data."""
        if self.df is None:
            logger.error("Dataframe is not loaded for file: %s", self.cf.meta['filename'])
            return
        
        # Perform linear regressions
        self.linreg_refPD_vs_meanPM.linreg = linregress(self.df['meanRefPD'], self.df['meanPM'])
        self.linreg_meanPM_vs_L.linreg = linregress(self.df['L'], self.df['meanPM'])
        self.linreg_refPD_vs_L.linreg = linregress(self.df['L'], self.df['meanRefPD'])
    

    def generate_plots(self):
        """Generate plots for the calibration file data."""
        if self.df is None:
            logger.error("Dataframe is not loaded for file: %s", self.cf.meta['filename'])
            return
        
        self._gen_temp_humidity_hists_plot()
        self._gen_timeseries_plot()

        # Plot Mean PM vs L
        fig_id = "meanPM_vs_L"
        fig = plt.figure(figsize=(10, 6))
        plt.errorbar(self.df['L'], self.df['meanPM'], yerr=self.df['stdPM'], fmt='.', markersize=10, linewidth=1)
        plt.ylabel('Mean Optical Power (W)')
        plt.xlabel(self.laser_label)
        plt.grid()
        plt.title(f'{self.anal_label} - Mean PM vs {self.laser_label}')
        plt.tight_layout()
        self.savefig(fig_id)
        plt.close(fig)
        # logger.debug("Plot saved to %s", fig_path)


        fig_id = "meanRefPD_vs_L"
        fig = plt.figure(figsize=(10, 6))
        plt.errorbar(self.df['L'], self.df['meanRefPD'], yerr=self.df['stdRefPD'], fmt='.', markersize=10, linewidth=1)
        plt.ylabel('Mean ref PD (V)')
        plt.xlabel(self.laser_label)
        plt.grid()
        plt.title(f'{self.anal_label} - Mean Ref PD vs {self.laser_label}')
        plt.tight_layout()
        self.savefig(fig_id)
        plt.close(fig)
        # logger.debug("Plot saved to %s", fig_path)

        intercept = self.linreg_refPD_vs_meanPM.intercept
        slope = self.linreg_refPD_vs_meanPM.slope

        fig_id = "meanPM_vs_meanRefPD"
        fig = plt.figure(figsize=(10, 6))
        plt.errorbar(self.df['meanRefPD'], self.df['meanPM'], yerr=self.df['stdPM'], fmt='.', markersize=10, linewidth=1)
        plt.plot(self.df['meanRefPD'], intercept + slope*self.df['meanRefPD'], 'r', label='fitted line')
        plt.ylabel('Mean Optical Power (W)')
        plt.xlabel('Mean ref PD (V)')
        plt.legend([f'intercept={intercept:.6f}, slope={slope:.6f}'])
        plt.grid()
        plt.title(f'{self.anal_label} - Mean PM vs Mean Ref PD')
        plt.tight_layout()
        self.savefig(fig_id)
        plt.close(fig)

    def to_dict(self):
        """Return analysis results as a dictionary."""
        return {
            'linregs': {
                'meanRefPD vs meanPM': self.linreg_refPD_vs_meanPM.to_dict(),
                'meanPM vs L': self.linreg_meanPM_vs_L.to_dict(),
                'meanRefPD vs L': self.linreg_refPD_vs_L.to_dict(),
            },
            'plots': self.plots,
        }
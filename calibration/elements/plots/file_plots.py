"""
Docstring for calibration.elements.calib_file_analysis
"""

from typing import TYPE_CHECKING
import pandas as pd
from scipy.stats import linregress
import matplotlib.pyplot as plt


from calibration.helpers import get_logger
from calibration.config import config

from ..helpers import CalibLinReg
from .plot_base import BasePlots

if TYPE_CHECKING:
    from ..calib_file import CalibFile


logger = get_logger()


class FilePlots(BasePlots):
    """
    Docstring for FilePlots
    """
    def __init__(self, calib_file:CalibFile):
        super().__init__()
        self._data_holder:CalibFile = calib_file
        self.cf:CalibFile = calib_file
        self._anal = calib_file.anal
        self.file_info = {}

    @property
    def laser_label(self) -> str:
        return self.cf.laser_label

    @property
    def output_path(self) -> str:
        """
        output_path: where to store plots and results for this set of files
        Filename should contain the run number
        """
        return self.cf.output_path if self.cf.output_path else '.'

    def generate_plots(self):
        """Generate plots for the calibration file data."""
        if self.df is None:
            logger.error("Dataframe is not loaded for file: %s", self.cf.meta['filename'])
            return
        
        self._gen_temp_humidity_hists_plot()
        self._gen_timeseries_plot()

        # Plot Mean pm vs laser_setpoint
        fig_id = "pm_vs_L"
        fig = plt.figure(figsize=(10, 6))
        plt.errorbar(self.df['laser_setpoint'], self.df['pm_mean'], yerr=self.df['pm_std'], 
                     fmt='.', markersize=10, linewidth=1, label='Power Meter')
        plt.ylabel('Power Meter (W)')
        plt.xlabel(self.laser_label)
        plt.legend()
        plt.grid()
        plt.title(f'{self.level_label} - Power Meter vs {self.laser_label}')
        plt.tight_layout()
        self.savefig(fig, fig_id)
        plt.close(fig)
        # logger.debug("Plot saved to %s", fig_path)


        fig_id = "refPD_vs_L"
        fig = plt.figure(figsize=(10, 6))
        plt.errorbar(self.df['laser_setpoint'], self.df['ref_pd_mean'], yerr=self.df['ref_pd_std'], 
                     fmt='.', markersize=10, linewidth=1, label='Ref PD')
        plt.ylabel('Ref PD (V)')
        plt.xlabel(self.laser_label)
        plt.legend()
        plt.grid()
        plt.title(f'{self.level_label} - Ref PD vs {self.laser_label}')
        plt.tight_layout()
        self.savefig(fig, fig_id)
        plt.close(fig)
        # logger.debug("Plot saved to %s", fig_path)

        intercept = self._anal.lr_refpd_vs_pm.intercept
        slope = self._anal.lr_refpd_vs_pm.slope
        slope_err = self._anal.lr_refpd_vs_pm.stderr

        fig_id = "pm_vs_refPD"
        fig = plt.figure(figsize=(10, 6))
        plt.errorbar(self.df['ref_pd_mean'], self.df['pm_mean'], yerr=self.df['pm_std'], 
                     fmt='.', markersize=10, linewidth=1, label='Power Meter')
        plt.plot(self.df['ref_pd_mean'], intercept + slope*self.df['ref_pd_mean'], 'r', label='fitted line')
        plt.ylabel('Power Meter (W)')
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        plt.xlabel('Ref PD (V)')
        plt.legend([f'intercept={intercept:.2} (W), slope={slope:.2}+/-{slope_err:.2} (W/V)', 'Power Meter'])
        plt.grid()
        plt.title(f'{self.level_label} - Power Meter vs Ref PD')
        plt.tight_layout()
        self.savefig(fig, fig_id)
        plt.close(fig)

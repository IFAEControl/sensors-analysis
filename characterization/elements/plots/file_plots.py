"""Characterization file plots"""

from typing import TYPE_CHECKING
import matplotlib.pyplot as plt
import numpy as np

from characterization.helpers import get_logger
from .plot_base import BasePlots

if TYPE_CHECKING:
    from ..sweep_file import SweepFile

logger = get_logger()

class FilePlots(BasePlots):
    def __init__(self, char_file: 'SweepFile'):
        super().__init__()
        self._data_holder = char_file
        self.cf = char_file

    @property
    def laser_label(self) -> str:
        if self.cf.wavelength == '532':
            return '532nm laser setpoint (mA)'
        if self.cf.wavelength == '1064':
            return '1064nm laser setpoint (mW)'
        return self.cf.laser_label

    @property
    def output_path(self) -> str:
        return self.cf.output_path if self.cf.output_path else '.'

    def generate_plots(self):
        if self.cf.df is None or self.cf.df.empty:
            logger.error("No analysis dataframe for file: %s", self.cf.file_info['filename'])
            return

        df = self.cf.df
        self._gen_timeseries_plot()

        fig_id = "dut_vs_laser_setpoint"
        fig = plt.figure(figsize=(10, 6))
        df_full = self.cf.df_full
        run_label = f"{self._pd_label()} run{self.cf.run}"
        plt.errorbar(df_full['laser_setpoint'], df_full['mean_adc'], yerr=df_full['std_adc'],
                     fmt='.', markersize=8, linewidth=1, label=run_label)
        plt.ylabel(f'{self._pd_label()} (ADC counts)')
        plt.xlabel(self.laser_label)
        plt.grid()
        plt.title(f'{self.level_label} - DUT vs {self.laser_label}')
        plt.legend(loc='best')
        plt.tight_layout()
        self.savefig(fig, fig_id)
        plt.close(fig)

        fig_id = "refpd_vs_laser_setpoint"
        fig = plt.figure(figsize=(10, 6))
        run_label = f"{self._pd_label()} run{self.cf.run}"
        plt.errorbar(df_full['laser_setpoint'], df_full['ref_pd_mean'], yerr=df_full['ref_pd_std'],
                     fmt='.', markersize=8, linewidth=1, label=run_label)
        plt.ylabel('RefPD (V)')
        plt.xlabel(self.laser_label)
        plt.grid()
        plt.title(f'{self.level_label} - RefPD vs {self.laser_label}')
        plt.legend(loc='best')
        plt.tight_layout()
        self.savefig(fig, fig_id)
        plt.close(fig)

        fig_id = "refpd_vs_dut"
        fig = plt.figure(figsize=(10, 6))
        df_full = self.cf.df_full
        plt.errorbar(df_full['mean_adc'], df_full['ref_pd_mean'], yerr=df_full['ref_pd_std'],
                     fmt='.', markersize=8, linewidth=1, label='data')
        plt.axvspan(0, 4095, color='green', alpha=0.08, label='linear region')
        plt.axvspan(4095, 4300, color='magenta', alpha=0.08, label='saturation')
        if self.cf.anal.lr_refpd_vs_adc.linreg is not None:
            intercept = self.cf.anal.lr_refpd_vs_adc.intercept
            slope = self.cf.anal.lr_refpd_vs_adc.slope
            xline = np.linspace(0, 4095, 200)
            fit_label = f"fit: y={slope:.2e}x+{intercept:.2e}"
            plt.plot(xline, intercept + slope * xline, color='black', linewidth=2, label=fit_label)
        plt.ylabel('RefPD (V)')
        plt.xlabel(f'{self._pd_label()} (ADC counts)')
        plt.grid()
        plt.xlim(-50, 4200)
        plt.title(f'{self.level_label} - Ref PD vs DUT')
        plt.legend(loc='best')
        plt.tight_layout()
        self.savefig(fig, fig_id)
        plt.close(fig)
